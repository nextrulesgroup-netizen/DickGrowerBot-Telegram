from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_event import DailyEvent


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_date(self, chat_id: int, event_date: str) -> DailyEvent | None:
        result = await self.session.execute(select(DailyEvent).where(DailyEvent.chat_id == chat_id, DailyEvent.event_date == event_date))
        return result.scalar_one_or_none()

    async def create_or_update(self, chat_id: int, event_date: str, winner_id: int | None, bonus: int) -> DailyEvent:
        event = await self.get_by_date(chat_id, event_date)
        if event:
            event.winner_id = winner_id
            event.bonus = bonus
            return event
        event = DailyEvent(chat_id=chat_id, event_date=event_date, winner_id=winner_id, bonus=bonus)
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_chat_winner(self, chat_id: int, event_date: str) -> DailyEvent | None:
        return await self.get_by_date(chat_id, event_date)
