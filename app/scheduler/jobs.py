from __future__ import annotations

import asyncio
from datetime import date

from app.repositories.chat import ChatRepository
from app.repositories.event import EventRepository
from app.repositories.stats import StatsRepository
from app.services.event import EventService
from app.utils.time import today_iso


async def run_daily_event_scheduler(sessionmaker, settings, metrics, bot=None):
    last_day = date.today().isoformat()
    while True:
        await asyncio.sleep(settings.scheduler_poll_seconds)
        current_day = today_iso()
        if current_day == last_day:
            continue
        last_day = current_day
        async with sessionmaker() as session:
            chat_repo = ChatRepository(session)
            event_service = EventService(EventRepository(session), StatsRepository(session), settings)
            chats = await chat_repo.list_chats()
            for chat in chats:
                winner_id, bonus = await event_service.choose_winner(chat.chat_id)
                metrics.inc()
                if bot and winner_id:
                    await bot.send_message(
                        chat.chat_id,
                        f"🎉 Daily Dick of the Day: <b>{winner_id}</b> wins {bonus} cm bonus!",
                    )
