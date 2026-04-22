from dependency_injector.wiring import Provide, inject
from faststream.rabbit import RabbitBroker

from src.dependency.container import Container
from src.modules.payment.usecase.process_payment_consumer.impl import ProcessPaymentConsumerUseCase


@inject
async def process_payment_handler(
    body: dict,
    broker: RabbitBroker,
    use_case: ProcessPaymentConsumerUseCase = Provide[Container.process_payment_consumer_use_case],
) -> None:
    await use_case.invoke(body)
