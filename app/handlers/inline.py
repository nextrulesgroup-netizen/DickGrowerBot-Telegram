from __future__ import annotations

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup

from app.core.container import container

router = Router()


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery) -> None:
    bot_username = container.get("bot_username", "DickGrowerBot")
    results = [
        InlineQueryResultArticle(
            id="grow",
            title="Grow your size",
            input_message_content=InputTextMessageContent(
                message_text="Try /grow in group chats or use this bot to track your progress.",
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Play now", url=f"https://t.me/{bot_username}?start=join")],
            ]),
        ),
        InlineQueryResultArticle(
            id="stats",
            title="Show my stats",
            input_message_content=InputTextMessageContent(
                message_text="Use /stats to see your current score and streak.",
            ),
        ),
    ]
    await inline_query.answer(results=results, cache_time=30, is_personal=True)
