from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from ..database import Base
from .common import TimestampMixin


class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'awaiting_payment', 'paid', 'processing', 'fulfilled', 'completed', 'cancelled')",
            name="ck_orders_status_allowed",
        ),
        CheckConstraint("total_amount >= 0", name="ck_orders_total_amount_non_negative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(String(50), nullable=False, index=True, default="pending")
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)

    brand = relationship("Brand")
    customer = relationship("Customer", back_populates="orders")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payment = relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan",
        uselist=False,
    )


class OrderItem(TimestampMixin, Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_order_items_unit_price_non_negative"),
        CheckConstraint("subtotal >= 0", name="ck_order_items_subtotal_non_negative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)
    product_cost_price_snapshot = Column(Numeric(12, 2), nullable=False, default=0)
    product_name_snapshot = Column(String(255), nullable=False)
    product_sku_snapshot = Column(String(100), nullable=True)
    product_slug_snapshot = Column(String(255), nullable=False)
    price_source = Column(String(50), nullable=False, default="base_price")

    order = relationship("Order", back_populates="items")
    brand = relationship("Brand")
    product = relationship("Product")
