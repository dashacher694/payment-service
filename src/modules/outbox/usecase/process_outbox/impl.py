from datetime import datetime
from decimal import Decimal
from loguru import logger

from src.clients.producer.payment_dto import PaymentCreatedDTO
from src.clients.producer.rabbitmq_producer import RabbitMQBrokerProducer
from src.modules.outbox.infrastructure.dto import SchedulerOutboxResponse
from src.modules.outbox.infrastructure.uow import OutboxUnitOfWork


class ProcessOutboxUseCase:
    def __init__(self, rabbitmq_producer: RabbitMQBrokerProducer, uow: OutboxUnitOfWork):
        self.rabbitmq_producer = rabbitmq_producer
        self.uow = uow

    async def invoke(self) -> SchedulerOutboxResponse:
        async with self.uow:
            unsent_events = await self.uow.repository.get_unsent_events()
            success_sent_events_count = 0
            error_sent_events_count = 0

            for event in unsent_events:
                try:
                    payment_dto = PaymentCreatedDTO(
                        payment_id=event.payment_id,
                        amount=Decimal(str(event.data["amount"])),
                        currency=event.data["currency"],
                        webhook_url=event.data["webhook_url"],
                    )

                    await self.rabbitmq_producer.send_payment_created(payment_dto)
                    event.send_status = True
                    event.processed_at = datetime.utcnow()
                    await self.uow.commit()
                    success_sent_events_count += 1
                except Exception as e:
                    logger.error(f"Failed to send outbox event: {e}")
                    error_sent_events_count += 1

            return SchedulerOutboxResponse(
                success_sent_events_count=success_sent_events_count,
                error_sent_events_count=error_sent_events_count,
            )
