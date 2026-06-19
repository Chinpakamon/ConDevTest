import asyncio
import datetime
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.booking.rate_limit import reset_rate_limit
from app.core.database.core import Base, get_session
from app.main import create_app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_bookings.db"


@pytest.fixture()
def db_session() -> Iterator[AsyncSession]:
    db_path = Path("test_bookings.db")
    if db_path.exists():
        db_path.unlink()

    engine = create_async_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = async_sessionmaker(
        bind=engine, expire_on_commit=False
    )

    async def setup() -> AsyncSession:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return TestingSessionLocal()

    session = asyncio.run(setup())
    yield session

    async def teardown() -> None:
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    asyncio.run(teardown())
    if db_path.exists():
        db_path.unlink()


@pytest.fixture()
def enqueue_mock(monkeypatch: pytest.MonkeyPatch) -> Mock:
    mock = Mock()
    monkeypatch.setattr("app.tasks.process_booking.delay", mock)
    return mock


@pytest.fixture()
def client(
    db_session: AsyncSession, enqueue_mock: Mock
) -> Iterator[TestClient]:
    app = create_app(enable_lifespan=False)

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    reset_rate_limit()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    reset_rate_limit()


@pytest.fixture()
def future_datetime() -> str:
    return (
        datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
    ).isoformat()
