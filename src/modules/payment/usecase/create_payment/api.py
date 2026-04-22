from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Header, status

from src.dependency.container import Container
from src.modules.payment.infrastructure.dto import CreatePaymentRequest, CreatePaymentResponse
from src.modules.payment.usecase import router
from src.modules.payment.usecase.create_payment.impl import CreatePaymentUseCase


@router.post(
    "",
    name="Create Payment",
    summary="Создание платежа",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=CreatePaymentResponse,
)
@inject
async def create_payment(
    request: CreatePaymentRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", description="Ключ идемпотентности"),
    uc: CreatePaymentUseCase = Depends(Provide[Container.create_payment_use_case]),
):
    """
    Создание платежа
    
    При создании платежа публикуется событие в RabbitMQ.
    """
    result = await uc.invoke(request, idempotency_key)
    return result
