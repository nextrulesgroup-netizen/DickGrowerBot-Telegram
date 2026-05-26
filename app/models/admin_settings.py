from __future__ import annotations

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AdminSettings(Base):
    __tablename__ = "admin_settings"
    __table_args__ = (Index("ix_admin_settings_key", "key"),)

    key: Mapped[str]
    value: Mapped[str]
