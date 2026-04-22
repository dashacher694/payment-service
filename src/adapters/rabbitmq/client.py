import orjson
from aio_pika import connect_robust, ExchangeType
from loguru import logger

from src.core.config import settings


class RabbitMQClient:
    """Клиент для RabbitMQ"""

    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        """Подключение к RabbitMQ"""
        self.connection = await connect_robust(settings.rabbitmq.rabbitmq_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            "payments",
            ExchangeType.TOPIC,
            durable=True,
        )
        logger.info("RabbitMQ client connected")

    async def disconnect(self):
        """Отключение от RabbitMQ"""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ client disconnected")

    async def publish(self, message: dict, routing_key: str):
        """Публикация сообщения"""
        if not self.exchange:
            await self.connect()

        from aio_pika import Message, DeliveryMode

        msg = Message(
            body=orjson.dumps(message),
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        await self.exchange.publish(msg, routing_key=routing_key)
        logger.info(f"Published message to {routing_key}: {message}")
