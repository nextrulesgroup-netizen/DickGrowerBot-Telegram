from __future__ import annotations

from pydantic import BaseModel


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None
    full_name: str | None
    language: str
