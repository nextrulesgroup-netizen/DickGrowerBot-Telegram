from __future__ import annotations

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _

from app.core.container import container

router = Router()


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery) -> None:
    bot_username = container.get("bot_username", "DickGrowerBot")
    results = [
        InlineQueryResultArticle(
            id="grow",
            title=_("inline_grow_title"),
            input_message_content=InputTextMessageContent(
                message_text=_("inline_grow_message"),
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=_("inline_play_now"), url=f"https://t.me/{bot_username}?start=join")],
            ]),
        ),
        InlineQueryResultArticle(
            id="stats",
            title=_("inline_stats_title"),
            input_message_content=InputTextMessageContent(
                message_text=_("inline_stats_message"),
            ),
        ),
    ]
    await inline_query.answer(results=results, cache_time=30, is_personal=True)
