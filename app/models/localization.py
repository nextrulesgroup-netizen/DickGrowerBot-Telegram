from __future__ import annotations

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class LocalizationPreference(Base):
    __tablename__ = "localization_preferences"
    __table_args__ = (Index("ix_localization_preferences_user_id", "user_id"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    locale: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="localization_preferences")
