from datetime import datetime
from types import SimpleNamespace

import pytest
from redis.asyncio import Redis

from app.models.user import User
from app.repositories.chat import ChatRepository
from app.repositories.stats import StatsRepository
from app.repositories.user import UserRepository
from app.services.game import GameService


class FakeRedis:
    def __init__(self):
        self.store = {}

    async def ttl(self, key):
        return -2 if key not in self.store else self.store[key][1]

    async def set(self, key, value, ex=None):
        self.store[key] = (value, ex)


@pytest.mark.asyncio
async def test_grow_creates_user_and_stats(session, fake_settings):
    redis_client = FakeRedis()
    service = GameService(UserRepository(session), ChatRepository(session), StatsRepository(session), redis_client, fake_settings)

    message = SimpleNamespace(
        from_user=SimpleNamespace(id=1, username="tester", full_name="Tester", language_code="en"),
        chat=SimpleNamespace(id=100, type="group", title="Test Chat"),
    )
    user = await service.register_user(message)
    assert user.telegram_id == 1

    change, reason, total = await service.grow(user, message.chat.id)
    assert isinstance(change, int)
    assert total.endswith("cm")
    assert reason in {"daily growth", "shrinkage surprise"}

    stats_text = await service.get_stats_text(user, message.chat.id)
    assert "Size:" in stats_text
