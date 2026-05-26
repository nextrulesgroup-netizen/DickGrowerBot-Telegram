from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Cooldown(Base):
    __tablename__ = "cooldowns"
    __table_args__ = (Index("ix_cooldowns_user_action", "user_id", "action"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str]
    expires_at: Mapped[datetime]

    user: Mapped["User"] = relationship(back_populates="cooldowns")
