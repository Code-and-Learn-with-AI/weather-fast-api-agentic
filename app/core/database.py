from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings


@lru_cache
def get_engine() -> AsyncEngine:
    return create_async_engine(Settings().DATABASE_URL)  # type: ignore[call-arg]


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    async with async_sessionmaker(get_engine(), expire_on_commit=False)() as session:
        yield session
