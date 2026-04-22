from sqlalchemy import select

from src.db.base_repository import BaseAsyncRepository
from src.modules.payment.domain.aggregate.model import Payment


class PaymentRepository(BaseAsyncRepository[Payment]):
    model = Payment

    async def get_by_idempotency_key(self, key: str) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.idempotency_key == key)
        )
        return result.scalar_one_or_none()
