from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from ..database import Base
from .common import TimestampMixin


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'paid', 'failed', 'refunded')",
            name="ck_payments_status_allowed",
        ),
        CheckConstraint(
            "method IN ('manual', 'bank_transfer', 'cash')",
            name="ck_payments_method_allowed",
        ),
        CheckConstraint("amount >= 0", name="ck_payments_amount_non_negative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    status = Column(String(50), nullable=False, index=True, default="pending")
    method = Column(String(50), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    paid_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="payment")
    brand = relationship("Brand")
