import uuid

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Path

from src.core.fastapi.security import verify_api_key
from src.dependency.container import Container
from src.modules.payment.infrastructure.dto import PaymentResponse
from src.modules.payment.usecase import router
from src.modules.payment.usecase.get_payment.impl import GetPaymentUseCase


@router.get(
    "/{payment_id}",
    name="Get Payment",
    summary="Получение информации о платеже",
    response_model=PaymentResponse,
    dependencies=[Depends(verify_api_key)],
)
@inject
async def get_payment(
    payment_id: uuid.UUID = Path(description="UUID платежа"),
    uc: GetPaymentUseCase = Depends(Provide[Container.get_payment_use_case]),
):
    result = await uc.invoke(payment_id)
    return result
