from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.config import settings

engine = create_async_engine(settings.db.asyncpg_uri, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def get_engine(database_url: str):
    return create_async_engine(database_url, echo=False)


async def get_session():
    async with async_session_maker() as session:
        yield session
