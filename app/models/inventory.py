from __future__ import annotations

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (Index("ix_inventory_user_item", "user_id", "item_id"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("shop_items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, server_default="0")

    item: Mapped["ShopItem"] = relationship(back_populates="inventory")
