from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict


Money = Decimal


class OrderStatus(str, Enum):
    pending = "pending"
    awaiting_payment = "awaiting_payment"
    paid = "paid"
    processing = "processing"
    fulfilled = "fulfilled"
    completed = "completed"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(str, Enum):
    manual = "manual"
    bank_transfer = "bank_transfer"
    cash = "cash"


class ProductStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"
    discontinued = "discontinued"


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "Money",
    "OrderStatus",
    "PaymentStatus",
    "PaymentMethod",
    "ProductStatus",
    "ORMBase",
]
