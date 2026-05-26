from __future__ import annotations

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_or_update(self, telegram_id: int, username: str | None, full_name: str | None, language: str) -> User:
        statement = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(statement)
        user = result.scalar_one_or_none()
        if user:
            user.username = username
            user.full_name = full_name
            user.language = language
            return user
        user = User(telegram_id=telegram_id, username=username, full_name=full_name, language=language)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username.strip("@")))
        return result.scalar_one_or_none()

    async def list_active(self, limit: int = 50) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.created_at.desc()).limit(limit))
        return result.scalars().all()
