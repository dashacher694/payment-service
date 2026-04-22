from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Singleton

from src.adapters.rabbitmq.client import RabbitMQClient
from src.core.config import settings
from src.db.connection import get_engine
from src.modules.outbox.infrastructure.uow import OutboxUnitOfWork
from src.modules.payment.infrastructure.uow import PaymentUnitOfWork


class UowContainer(DeclarativeContainer):
    engine = Singleton(get_engine, database_url=settings.db.asyncpg_uri)

    rabbitmq_client = Singleton(RabbitMQClient)

    payment_uow = Factory(PaymentUnitOfWork, engine=engine)
    outbox_uow = Factory(OutboxUnitOfWork, engine=engine)
