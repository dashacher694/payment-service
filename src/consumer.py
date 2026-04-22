import asyncio
import random
import uuid
from datetime import datetime

import orjson
from aio_pika import connect_robust, IncomingMessage, ExchangeType, Message, DeliveryMode
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.db.connection import get_engine
from src.modules.payment.domain.aggregate.model import Payment
from src.modules.utils.enums import PaymentStatus
from src.adapters.rabbitmq.client import RabbitMQClient
import httpx


async def send_webhook(url: str, payload: dict) -> bool:
    """Отправка webhook уведомления с retry"""
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info(f"Webhook sent to {url}")
                return True
        except Exception as e:
            logger.error(f"Webhook attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
    return False


async def process_payment_message(message: IncomingMessage, engine):
    """Обработка сообщения о создании платежа"""
    try:
        payload = orjson.loads(message.body)
        payment_id = uuid.UUID(payload["payment_id"])
        
        from src.modules.payment.infrastructure.uow import PaymentUnitOfWork
        uow = PaymentUnitOfWork(engine)
        
        async with uow:
            payment = await uow.repository.get_by_id(payment_id)
            
            if not payment:
                logger.error(f"Payment not found: {payment_id}")
                await message.nack(requeue=False)
                return
            
            payload_data = {
                "payment_id": str(payment.id),
                "amount": str(payment.amount),
                "currency": payment.currency.value,
                "status": payment.status.value,
                "created_at": payment.created_at.isoformat(),
            }
            
            success = await send_webhook(payment.webhook_url, payload_data)
            
            if success:
                payment.status = PaymentStatus.SUCCEEDED
                payment.processed_at = datetime.utcnow()
                await message.ack()
                logger.info(f"Payment processed: {payment_id}")
            else:
                payment.status = PaymentStatus.FAILED
                payment.processed_at = datetime.utcnow()
                await message.nack(requeue=False)
                logger.error(f"Payment webhook failed: {payment_id}")
                
    except Exception as e:
        logger.error(f"Error processing payment: {e}")


async def main():
    """Главная функция consumer"""
    
    engine = get_engine(settings.db.asyncpg_uri)
    
    rabbitmq_client = RabbitMQClient()
    await rabbitmq_client.connect()
    
    channel = rabbitmq_client.channel
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue("payments.new", durable=True)
    dlq = await channel.declare_queue("payments.dlq", durable=True)
    
    await queue.bind(rabbitmq_client.exchange, routing_key="payment.created")
    await dlq.bind(rabbitmq_client.exchange, routing_key="payments.dlq")
    
    await queue.consume(lambda msg: process_payment_message(msg, engine))
    
    logger.info("Consumer started")
    
    try:
        await asyncio.Future()
    finally:
        await rabbitmq_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
