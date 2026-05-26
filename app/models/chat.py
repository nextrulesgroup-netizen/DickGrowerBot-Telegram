from __future__ import annotations

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Chat(Base):
    __tablename__ = "chats"
    __table_args__ = (Index("ix_chats_chat_id", "chat_id"),)

    chat_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str | None]
    type: Mapped[str]

    player_stats: Mapped[list["PlayerStats"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    growth_history: Mapped[list["GrowthHistory"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    daily_events: Mapped[list["DailyEvent"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
