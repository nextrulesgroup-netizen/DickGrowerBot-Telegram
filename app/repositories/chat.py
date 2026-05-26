from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_or_update(self, chat_id: int, title: str | None, type: str) -> Chat:
        result = await self.session.execute(select(Chat).where(Chat.chat_id == chat_id))
        chat = result.scalar_one_or_none()
        if chat:
            chat.title = title
            chat.type = type
            return chat
        chat = Chat(chat_id=chat_id, title=title, type=type)
        self.session.add(chat)
        await self.session.flush()
        return chat

    async def get_by_chat_id(self, chat_id: int) -> Chat | None:
        result = await self.session.execute(select(Chat).where(Chat.chat_id == chat_id))
        return result.scalar_one_or_none()

    async def list_chats(self) -> list[Chat]:
        result = await self.session.execute(select(Chat))
        return result.scalars().all()
