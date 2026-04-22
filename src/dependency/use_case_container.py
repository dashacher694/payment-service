from dependency_injector.containers import copy
from dependency_injector.providers import Factory, Singleton

from src.dependency.uow_container import UowContainer
from src.clients.producer.rabbitmq_producer import RabbitMQBrokerProducer
from src.modules.payment.usecase.create_payment.impl import CreatePaymentUseCase
from src.modules.payment.usecase.get_payment.impl import GetPaymentUseCase
from src.modules.payment.usecase.process_payment_consumer.impl import ProcessPaymentConsumerUseCase
from src.modules.outbox.usecase.process_outbox.impl import ProcessOutboxUseCase


@copy(UowContainer)
class UseCaseContainer(UowContainer):
    rabbitmq_broker_producer = Singleton(
        RabbitMQBrokerProducer,
        rabbitmq_client=UowContainer.rabbitmq_client,
    )

    create_payment_use_case = Factory(
        CreatePaymentUseCase,
        uow=UowContainer.payment_uow,
    )

    get_payment_use_case = Factory(
        GetPaymentUseCase,
        uow=UowContainer.payment_uow,
    )

    process_outbox_use_case = Factory(
        ProcessOutboxUseCase,
        rabbitmq_producer=rabbitmq_broker_producer,
        uow=UowContainer.outbox_uow,
    )

    process_payment_consumer_use_case = Factory(
        ProcessPaymentConsumerUseCase,
        uow=UowContainer.payment_uow,
    )
