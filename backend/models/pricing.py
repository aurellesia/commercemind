from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from ..database import Base
from .common import TimestampMixin


class PriceSet(TimestampMixin, Base):
    __tablename__ = "price_sets"
    __table_args__ = (
        CheckConstraint(
            "ends_at IS NULL OR starts_at IS NULL OR ends_at >= starts_at",
            name="ck_price_sets_ends_at_after_starts_at",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    starts_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    product = relationship("Product", back_populates="price_sets")
    brand = relationship("Brand")
    items = relationship(
        "PriceSetItem",
        back_populates="price_set",
        cascade="all, delete-orphan",
    )


class PriceSetItem(TimestampMixin, Base):
    __tablename__ = "price_set_items"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_price_set_items_price_non_negative"),
        CheckConstraint(
            "priority >= 0",
            name="ck_price_set_items_priority_non_negative",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    price_set_id = Column(
        Integer,
        ForeignKey("price_sets.id"),
        nullable=False,
        index=True,
    )
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True, index=True)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="IDR")
    priority = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)

    price_set = relationship("PriceSet", back_populates="items")
    channel = relationship("Channel", back_populates="price_set_items")
    region = relationship("Region", back_populates="price_set_items")
