from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class GrowthHistory(Base):
    __tablename__ = "growth_history"
    __table_args__ = (Index("ix_growth_history_user_id", "user_id"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    change: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="growth_history")
    chat: Mapped["Chat"] = relationship(back_populates="growth_history")
