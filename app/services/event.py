from __future__ import annotations

import secrets
from datetime import date

from app.repositories.event import EventRepository
from app.repositories.stats import StatsRepository


class EventService:
    def __init__(self, event_repo: EventRepository, stats_repo: StatsRepository, settings) -> None:
        self.event_repo = event_repo
        self.stats_repo = stats_repo
        self.settings = settings

    async def choose_winner(self, chat_id: int) -> tuple[int | None, int]:
        today = date.today().isoformat()
        top = await self.stats_repo.top_players(chat_id, limit=10)
        if not top:
            event = await self.event_repo.create_or_update(chat_id, today, None, 0)
            return None, 0
        winner = secrets.choice(top)
        bonus = secrets.randbelow(self.settings.daily_bonus_max - self.settings.daily_bonus_min + 1) + self.settings.daily_bonus_min
        await self.event_repo.create_or_update(chat_id, today, winner.user_id, bonus)
        return winner.user_id, bonus

    async def get_today_event(self, chat_id: int) -> str:
        today = date.today().isoformat()
        event = await self.event_repo.get_chat_winner(chat_id, today)
        if not event or not event.winner_id:
            return "No Daily Dick of the Day has been awarded yet."
        return f"Today's Dick of the Day is user {event.winner_id} with a bonus of {event.bonus} cm."
