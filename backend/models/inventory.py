from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base
from .common import TimestampMixin


class InventoryItem(TimestampMixin, Base):
    __tablename__ = "inventory_items"
    __table_args__ = (
        CheckConstraint(
            "on_hand_quantity >= 0",
            name="ck_inventory_items_on_hand_quantity_non_negative",
        ),
        CheckConstraint(
            "reserved_quantity >= 0",
            name="ck_inventory_items_reserved_quantity_non_negative",
        ),
        CheckConstraint(
            "reserved_quantity <= on_hand_quantity",
            name="ck_inventory_items_reserved_not_greater_than_on_hand_quantity",
        ),
        CheckConstraint(
            "low_stock_threshold >= 0",
            name="ck_inventory_items_low_stock_threshold_non_negative",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True)
    on_hand_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="inventory_item")
    brand = relationship("Brand")

    @property
    def available_quantity(self) -> int:
        return self.on_hand_quantity - self.reserved_quantity

    @property
    def is_low_stock(self) -> bool:
        return self.available_quantity <= self.low_stock_threshold


class InventoryReservation(TimestampMixin, Base):
    __tablename__ = "inventory_reservations"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_inventory_reservations_quantity_positive"),
        CheckConstraint(
            "status IN ('active', 'released', 'committed', 'expired')",
            name="ck_inventory_reservations_status_allowed",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, index=True, default="active")
    expires_at = Column(DateTime, nullable=True)

    product = relationship("Product")
    brand = relationship("Brand")
    order = relationship("Order")
    order_item = relationship("OrderItem")


class InventoryMovement(TimestampMixin, Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_inventory_movements_quantity_positive"),
        CheckConstraint(
            "movement_type IN ('inbound', 'reservation', 'release', 'deduction', 'adjustment', 'return')",
            name="ck_inventory_movements_type_allowed",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    movement_type = Column(String(50), nullable=False, index=True)
    reference_type = Column(String(100), nullable=True, index=True)
    reference_id = Column(Integer, nullable=True, index=True)
    notes = Column(Text, nullable=True)

    product = relationship("Product")
    brand = relationship("Brand")
