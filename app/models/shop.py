from __future__ import annotations

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ShopItem(Base):
    __tablename__ = "shop_items"
    __table_args__ = (Index("ix_shop_items_key", "key"),)

    key: Mapped[str]
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[int] = mapped_column(nullable=False, server_default="0")
    enabled: Mapped[bool] = mapped_column(nullable=False, server_default="true")

    inventory: Mapped[list["Inventory"]] = relationship(back_populates="item")
