from sqlalchemy import select

from src.db.base_repository import BaseAsyncRepository
from src.modules.outbox.domain.aggregate.model import Outbox
from src.modules.outbox.infrastructure.entity import OutboxEntity


class OutboxRepository(BaseAsyncRepository[Outbox]):
    model = Outbox

    async def get_unsent_events(self) -> list[Outbox]:
        stmt = select(Outbox).where(
            Outbox.send_status.is_(False),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())