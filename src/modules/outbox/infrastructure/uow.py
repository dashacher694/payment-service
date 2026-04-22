from sqlalchemy.ext.asyncio import AsyncEngine

from src.db.base_uow import AsyncBaseUnitOfWork
from src.modules.outbox.infrastructure.repository import OutboxRepository


class OutboxUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)
        self.repository: OutboxRepository | None = None

    async def __aenter__(self):
        await super().__aenter__()
        self.repository: OutboxRepository = OutboxRepository(self.session)
        return self
