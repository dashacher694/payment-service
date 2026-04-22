from typing import Generic, Type, TypeVar
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseAsyncRepository(Generic[T]):
    model: Type[T]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def add(self, entity: T) -> None:
        self.session.add(entity)

    async def get_by_id(self, entity_id: UUID) -> T | None:
        result = await self.session.execute(
            sa.select(self.model).where(self.model.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        result = await self.session.execute(
            sa.select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)
