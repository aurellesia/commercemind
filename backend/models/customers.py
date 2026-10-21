from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database import Base
from .common import TimestampMixin


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("brand_id", "email", name="uq_customers_brand_email"),
        CheckConstraint(
            "customer_type IN ('guest', 'registered')",
            name="ck_customers_customer_type_allowed",
        ),
        Index("ix_customers_brand_phone", "brand_id", "phone"),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    customer_type = Column(String(50), nullable=False, default="guest", index=True)
    password_hash = Column(String(255), nullable=True)

    brand = relationship("Brand")
    orders = relationship("Order", back_populates="customer")
    addresses = relationship(
        "CustomerAddress",
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class CustomerAddress(TimestampMixin, Base):
    __tablename__ = "customer_addresses"
    __table_args__ = (
        Index("ix_customer_addresses_brand_customer", "brand_id", "customer_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    address_line = Column(Text, nullable=False)
    district = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    province = Column(String(255), nullable=False)
    postal_code = Column(String(20), nullable=False)
    notes = Column(Text, nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)

    brand = relationship("Brand")
    customer = relationship("Customer", back_populates="addresses")
