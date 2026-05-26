from __future__ import annotations

from datetime import datetime
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.growth_history import GrowthHistory
from app.models.player_stats import PlayerStats
from app.models.user import User


class StatsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_player_stats(self, user_id: int, chat_id: int) -> PlayerStats | None:
        result = await self.session.execute(select(PlayerStats).where(PlayerStats.user_id == user_id, PlayerStats.chat_id == chat_id))
        return result.scalar_one_or_none()

    async def create_player_stats(self, user_id: int, chat_id: int) -> PlayerStats:
        stats = PlayerStats(user_id=user_id, chat_id=chat_id)
        self.session.add(stats)
        await self.session.flush()
        return stats

    async def add_growth(self, user_id: int, chat_id: int, change: int, reason: str, now: datetime) -> PlayerStats:
        stats = await self.get_player_stats(user_id, chat_id)
        if not stats:
            stats = await self.create_player_stats(user_id, chat_id)
        stats.total_size += change
        stats.growth_count += 1
        if change > 0:
            stats.streak += 1
        else:
            stats.streak = 0
        stats.last_grow_at = now
        self.session.add(stats)
        self.session.add(GrowthHistory(user_id=user_id, chat_id=chat_id, change=change, reason=reason))
        await self.session.flush()
        return stats

    async def top_players(self, chat_id: int, limit: int = 10) -> list[PlayerStats]:
        result = await self.session.execute(select(PlayerStats).where(PlayerStats.chat_id == chat_id).order_by(PlayerStats.total_size.desc()).limit(limit))
        return result.scalars().all()

    async def global_top(self, limit: int = 10) -> list[PlayerStats]:
        result = await self.session.execute(select(PlayerStats).order_by(PlayerStats.total_size.desc()).limit(limit))
        return result.scalars().all()
