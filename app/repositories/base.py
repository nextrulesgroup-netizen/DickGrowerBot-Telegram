from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity
