from __future__ import annotations

from aiogram import types
from aiogram.utils.i18n import I18n, I18nMiddleware


class LocalizationMiddleware(I18nMiddleware):
    def __init__(self, default: str = "en", path: str | None = None) -> None:
        self.default = default
        self.path = path
        i18n = I18n(path=path, default_locale=self.default)
        super().__init__(i18n=i18n)

    async def get_locale(self, event, data: dict[str, object]) -> str:
        # event can be Update or specific Telegram objects (Message, CallbackQuery, InlineQuery)
        # try message
        user = None
        if hasattr(event, "message") and event.message is not None:
            user = event.message.from_user
        elif hasattr(event, "callback_query") and event.callback_query is not None:
            user = event.callback_query.from_user
        elif hasattr(event, "inline_query") and event.inline_query is not None:
            user = event.inline_query.from_user
        elif hasattr(event, "from_user"):
            user = event.from_user

        if user and getattr(user, "language_code", None):
            return user.language_code
        return self.default
