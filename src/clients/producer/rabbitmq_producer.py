from loguru import logger

from src.adapters.rabbitmq.client import RabbitMQClient
from src.clients.producer.payment_dto import PaymentCreatedDTO


class RabbitMQBrokerProducer:
    """RabbitMQ broker producer"""

    def __init__(self, rabbitmq_client: RabbitMQClient):
        self._rabbitmq_client = rabbitmq_client

    async def send_payment_created(self, message: PaymentCreatedDTO) -> None:
        try:
            await self._rabbitmq_client.publish(
                message=message.model_dump(mode="json"),
                routing_key="payment.created",
            )
        except Exception as e:
            logger.error(f"Failed to send payment created event: {e}")
