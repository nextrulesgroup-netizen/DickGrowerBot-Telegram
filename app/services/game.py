from __future__ import annotations

from datetime import datetime, timedelta
import secrets

from aiogram import types
from redis.asyncio import Redis

from app.models.user import User
from app.repositories.chat import ChatRepository
from app.repositories.stats import StatsRepository
from app.repositories.user import UserRepository
from app.utils.secure import secure_random_int
from app.utils.time import utcnow


class GameService:
    def __init__(self, user_repo: UserRepository, chat_repo: ChatRepository, stats_repo: StatsRepository, redis_client: Redis, settings) -> None:
        self.user_repo = user_repo
        self.chat_repo = chat_repo
        self.stats_repo = stats_repo
        self.redis = redis_client
        self.settings = settings

    async def register_user(self, message: types.Message) -> User:
        return await self.user_repo.create_or_update(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            language=message.from_user.language_code or self.settings.default_language,
        )

    async def register_chat(self, message: types.Message) -> None:
        if not message.chat:
            return
        await self.chat_repo.create_or_update(chat_id=message.chat.id, title=message.chat.title, type=message.chat.type)

    async def can_grow(self, telegram_id: int) -> bool:
        key = f"cooldown:grow:{telegram_id}"
        ttl = await self.redis.ttl(key)
        return ttl <= 0

    async def set_grow_cooldown(self, telegram_id: int) -> None:
        key = f"cooldown:grow:{telegram_id}"
        await self.redis.set(key, "1", ex=86400)

    async def grow(self, user: User, chat_id: int) -> tuple[int, str, str]:
        if not await self.can_grow(user.telegram_id):
            raise RuntimeError("cooldown")
        change = secure_random_int(self.settings.growth_min, self.settings.growth_max)
        reason = "daily growth" if change >= 0 else "shrinkage surprise"
        now = utcnow()
        stats = await self.stats_repo.add_growth(user.id, chat_id, change, reason, now)
        await self.set_grow_cooldown(user.telegram_id)
        return change, reason, f"{stats.total_size} cm"

    async def get_stats_text(self, user: User, chat_id: int) -> str:
        stats = await self.stats_repo.get_player_stats(user.id, chat_id)
        if not stats:
            return "No size history found yet. Try /grow to start your streak."
        return (
            f"{user.full_name or user.username or 'Player'}\n"
            f"Size: {stats.total_size} cm\n"
            f"Streak: {stats.streak} days\n"
            f"Growth actions: {stats.growth_count}\n"
            f"ELO: {stats.elo}\n"
        )

    async def get_leaderboard(self, chat_id: int, limit: int = 10) -> str:
        leaderboard = await self.stats_repo.top_players(chat_id, limit)
        if not leaderboard:
            return "No scores in this chat yet. Encourage players to use /grow."
        lines = ["Top dick growers in this chat:"]
        for rank, player in enumerate(leaderboard, start=1):
            username = player.user.username or f"User {player.user.telegram_id}"
            lines.append(f"{rank}. @{username} — {player.total_size} cm")
        return "\n".join(lines)

    async def get_global_leaderboard(self, limit: int = 10) -> str:
        leaderboard = await self.stats_repo.global_top(limit)
        if not leaderboard:
            return "No global stats yet."
        lines = ["Global top dicks:"]
        for rank, player in enumerate(leaderboard, start=1):
            username = player.user.username or f"User {player.user.telegram_id}"
            lines.append(f"{rank}. @{username} — {player.total_size} cm")
        return "\n".join(lines)
