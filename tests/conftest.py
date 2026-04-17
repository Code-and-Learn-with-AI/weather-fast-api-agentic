# Shared pytest fixtures — populated as the project grows.

import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.core.database import get_db_session
from app.main import app
from app.models.base import Base


@pytest.fixture(scope="session", autouse=True)
def set_session_env() -> None:
    """Set env vars required by session-scoped fixtures (e.g. db_engine)."""
    from app.core.config import Settings
    settings = Settings()  # type: ignore[call-arg]
    os.environ["DATABASE_TEST_URL"] = settings.DATABASE_TEST_URL  # type: ignore[assignment]


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure required env vars are set for all tests."""
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/weather")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture
async def async_client(mocker: MockerFixture) -> AsyncGenerator[AsyncClient]:
    async def _mock_db_session() -> AsyncGenerator[mocker.MagicMock]:  # type: ignore[name-defined]
        yield mocker.MagicMock()

    app.dependency_overrides[get_db_session] = _mock_db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(os.environ["DATABASE_TEST_URL"])
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    async with db_engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        yield session
        await session.close()
        await conn.rollback()
