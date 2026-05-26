from __future__ import annotations

pytest_plugins = ["pytest_asyncio"]

import asyncio
from types import SimpleNamespace

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine() -> AsyncEngine:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncSession:
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


@pytest.fixture
def fake_settings() -> SimpleNamespace:
    return SimpleNamespace(
        growth_min=-2,
        growth_max=4,
        shrink_chance=0.15,
        daily_bonus_min=1,
        daily_bonus_max=3,
        pvp_cooldown=86400,
        default_language="en",
    )
