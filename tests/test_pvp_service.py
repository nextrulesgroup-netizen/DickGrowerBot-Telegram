import pytest
from types import SimpleNamespace

from app.repositories.pvp import PVPRepository
from app.services.pvp import PVPService


@pytest.mark.asyncio
async def test_pvp_battle(session):
    pvp_repo = PVPRepository(session)
    settings = SimpleNamespace()
    service = PVPService(pvp_repo, settings)

    result, details = await service.battle(1, 2)
    assert result in {"attacker", "defender", "draw"}
    assert "attacker_power" in details
    assert "defender_power" in details
