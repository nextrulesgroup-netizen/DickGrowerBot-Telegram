from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = (Index("ix_achievements_user_id", "user_id"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str]
    description: Mapped[str | None]
    unlocked_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="achievements")
