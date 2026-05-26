from __future__ import annotations

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pvp import PVPMatch, PVPStatistics


class PVPRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_statistics(self, user_id: int) -> PVPStatistics | None:
        result = await self.session.execute(select(PVPStatistics).where(PVPStatistics.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_statistics(self, user_id: int) -> PVPStatistics:
        stats = PVPStatistics(user_id=user_id)
        self.session.add(stats)
        await self.session.flush()
        return stats

    async def record_match(self, attacker_id: int, defender_id: int, winner_id: int | None, attacker_damage: int, defender_damage: int, critical: bool, result: str) -> PVPMatch:
        match = PVPMatch(
            attacker_id=attacker_id,
            defender_id=defender_id,
            winner_id=winner_id,
            attacker_damage=attacker_damage,
            defender_damage=defender_damage,
            critical=critical,
            result=result,
        )
        self.session.add(match)
        await self.session.flush()
        return match

    async def update_statistics(self, user_id: int, win: bool = False, loss: bool = False, draw: bool = False, mmr_delta: int = 0) -> PVPStatistics:
        stats = await self.get_statistics(user_id)
        if not stats:
            stats = await self.create_statistics(user_id)
        stats.total_matches += 1
        if win:
            stats.total_wins += 1
        if loss:
            stats.total_losses += 1
        if draw:
            stats.total_draws += 1
        stats.mmr += mmr_delta
        self.session.add(stats)
        await self.session.flush()
        return stats
