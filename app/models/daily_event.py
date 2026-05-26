from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class DailyEvent(Base):
    __tablename__ = "daily_events"
    __table_args__ = (
        UniqueConstraint("chat_id", "event_date", name="uq_daily_events_chat_date"),
        Index("ix_daily_events_chat_id", "chat_id"),
    )

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    event_date: Mapped[str]
    winner_id: Mapped[int | None]
    bonus: Mapped[int] = mapped_column(nullable=False, server_default="0")
    announced_at: Mapped[datetime] = mapped_column(server_default=func.now())

    chat: Mapped["Chat"] = relationship(back_populates="daily_events")
