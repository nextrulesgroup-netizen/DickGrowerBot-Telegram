from __future__ import annotations

from pydantic import BaseModel


class PVPResult(BaseModel):
    attacker_power: int
    defender_power: int
    critical: bool = False
    elo_delta: int | None = None
    result: str
