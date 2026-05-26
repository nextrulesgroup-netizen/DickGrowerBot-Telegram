from __future__ import annotations

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware


class LocalizationMiddleware(I18nMiddleware):
    def __init__(self, default: str = "en", path: str | None = None) -> None:
        self.default = default
        self.path = path
        super().__init__(domain="messages", path=path, default=self.default)

    async def get_user_locale(self, action: types.Message | types.CallbackQuery | types.InlineQuery, locale: str | None = None) -> str:
        if action.from_user and action.from_user.language_code:
            return action.from_user.language_code
        return self.default
