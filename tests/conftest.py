import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import clear_mappers

from src.application import create_app
from src.core.fastapi.mapper import start_mapper
from src.db.base import metadata
from src.db.connection import get_engine
from src.core.config import settings
from src.dependency.container import Container


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def container() -> Container:
    """Create dependency injection container for tests"""
    return Container()


@pytest_asyncio.fixture(scope="function")
async def test_engine(container: Container) -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine using Container"""
    engine = get_engine(settings.db.asyncpg_uri)
    
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(container: Container) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session using Container"""
    async with container.session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client"""
    start_mapper()
    app = create_app()
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    clear_mappers()
