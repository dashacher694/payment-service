from sqlalchemy.ext.asyncio import AsyncEngine

from src.db.base_uow import AsyncBaseUnitOfWork
from src.modules.payment.infrastructure.repository import PaymentRepository


class PaymentUnitOfWork(AsyncBaseUnitOfWork):

    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)
        self.repository: PaymentRepository | None = None

    async def __aenter__(self):
        await super().__aenter__()
        self.repository: PaymentRepository = PaymentRepository(self.session)
        return self
