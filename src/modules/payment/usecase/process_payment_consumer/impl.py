import asyncio
import random
import uuid
from datetime import datetime

import httpx
from loguru import logger

from src.db.transaction import async_transactional
from src.modules.payment.infrastructure.dto import WebhookPayloadDTO
from src.modules.payment.infrastructure.uow import PaymentUnitOfWork
from src.modules.utils.enums import PaymentStatus

PROCESSING_MIN_DELAY = 2
PROCESSING_MAX_DELAY = 5
SUCCESS_RATE = 0.9
WEBHOOK_TIMEOUT = 10
RETRY_ATTEMPTS = 3


class ProcessPaymentConsumerUseCase:
    def __init__(self, uow: PaymentUnitOfWork):
        self.uow = uow

    async def _send_webhook(self, url: str, payload: dict) -> bool:
        """Отправка webhook уведомления с retry"""
        for attempt in range(RETRY_ATTEMPTS):
            try:
                async with httpx.AsyncClient(timeout=WEBHOOK_TIMEOUT) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    logger.info(f"Webhook sent to {url}")
                    return True
            except Exception as e:
                logger.error(f"Webhook attempt {attempt + 1} failed: {e}")
                if attempt < RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(2 ** attempt)
        return False

    @async_transactional()
    async def invoke(self, body: dict) -> None:
        """Обработка сообщения о создании платежа"""
        payment_id = uuid.UUID(body["payment_id"])

        payment = await self.uow.repository.get_by_id(payment_id)

        if not payment:
            logger.error(f"Payment not found: {payment_id}")
            return

        processing_time = random.uniform(PROCESSING_MIN_DELAY, PROCESSING_MAX_DELAY)
        await asyncio.sleep(processing_time)

        success_rate = random.random()
        if success_rate < SUCCESS_RATE:
            logger.info(f"Payment processing simulation successful: {payment_id}")
            payload_data = WebhookPayloadDTO(
                payment_id=str(payment.id),
                amount=str(payment.amount),
                currency=str(payment.currency),
                status=str(payment.status),
                created_at=payment.created_at.isoformat(),
            )

            webhook_success = await self._send_webhook(payment.webhook_url, payload_data.model_dump())

            if webhook_success:
                payment.status = PaymentStatus.succeeded
                payment.processed_at = datetime.utcnow()
                logger.info(f"Payment processed: {payment_id}")
            else:
                payment.status = PaymentStatus.failed
                payment.processed_at = datetime.utcnow()
                logger.error(f"Payment webhook failed: {payment_id}")
        else:
            logger.error(f"Payment processing simulation failed: {payment_id}")
            payment.status = PaymentStatus.failed
            payment.processed_at = datetime.utcnow()
