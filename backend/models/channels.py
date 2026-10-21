from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database import Base
from .common import TimestampMixin


class Channel(TimestampMixin, Base):
    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint("brand_id", "code", name="uq_channels_brand_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    code = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    brand = relationship("Brand")
    price_set_items = relationship("PriceSetItem", back_populates="channel")
