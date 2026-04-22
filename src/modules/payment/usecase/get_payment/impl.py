import uuid

from src.db.transaction import async_transactional
from src.modules.payment.infrastructure.uow import PaymentUnitOfWork
from src.modules.payment.infrastructure.dto import PaymentResponse
from src.modules.utils.erorr import NotFoundError


class GetPaymentUseCase:
    def __init__(self, uow: PaymentUnitOfWork):
        self.uow = uow

    @async_transactional(read_only=True)
    async def invoke(self, payment_id: uuid.UUID) -> PaymentResponse | None:
        payment = await self.uow.repository.get_by_id(payment_id)

        if not payment:
            raise NotFoundError("Payment not found")

        return PaymentResponse(
            id=payment.id,
            amount=payment.amount,
            currency=str(payment.currency),
            description=payment.description,
            meta=payment.meta,
            status=str(payment.status),
            webhook_url=payment.webhook_url,
            created_at=payment.created_at,
            processed_at=payment.processed_at,
        )
