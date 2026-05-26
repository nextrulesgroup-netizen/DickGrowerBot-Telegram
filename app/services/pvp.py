from __future__ import annotations

import secrets

from app.repositories.pvp import PVPRepository


def _elo_change(winner_rating: int, loser_rating: int) -> int:
    expected = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    return max(1, round(32 * (1 - expected)))


class PVPService:
    def __init__(self, pvp_repo: PVPRepository, settings) -> None:
        self.pvp_repo = pvp_repo
        self.settings = settings

    async def battle(self, attacker_id: int, defender_id: int) -> tuple[str, dict[str, int | bool]]:
        attacker_stats = await self.pvp_repo.get_statistics(attacker_id)
        defender_stats = await self.pvp_repo.get_statistics(defender_id)
        attacker_elo = attacker_stats.mmr if attacker_stats else 1000
        defender_elo = defender_stats.mmr if defender_stats else 1000

        attacker_power = 5 + secrets.randbelow(10)
        defender_power = 5 + secrets.randbelow(10)
        critical = secrets.randbelow(100) < 15
        if critical:
            attacker_power += 5

        if attacker_power == defender_power:
            result = "draw"
            await self.pvp_repo.record_match(attacker_id, defender_id, None, attacker_power, defender_power, critical, result)
            await self.pvp_repo.update_statistics(attacker_id, draw=True, mmr_delta=0)
            await self.pvp_repo.update_statistics(defender_id, draw=True, mmr_delta=0)
            return "draw", {"attacker_power": attacker_power, "defender_power": defender_power, "critical": critical, "result": result}

        winner_id = attacker_id if attacker_power > defender_power else defender_id
        loser_id = defender_id if winner_id == attacker_id else attacker_id
        result = "attacker" if winner_id == attacker_id else "defender"
        delta = _elo_change(attacker_elo, defender_elo) if winner_id == attacker_id else _elo_change(defender_elo, attacker_elo)

        if winner_id == attacker_id:
            await self.pvp_repo.update_statistics(attacker_id, win=True, mmr_delta=delta)
            await self.pvp_repo.update_statistics(defender_id, loss=True, mmr_delta=-delta)
        else:
            await self.pvp_repo.update_statistics(defender_id, win=True, mmr_delta=delta)
            await self.pvp_repo.update_statistics(attacker_id, loss=True, mmr_delta=-delta)

        await self.pvp_repo.record_match(attacker_id, defender_id, winner_id, attacker_power, defender_power, critical, result)
        return result, {
            "attacker_power": attacker_power,
            "defender_power": defender_power,
            "elo_delta": delta,
            "critical": critical,
        }
