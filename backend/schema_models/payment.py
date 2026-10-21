from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .common import Money, ORMBase, PaymentMethod, PaymentStatus


class PaymentBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    status: PaymentStatus = Field(default=PaymentStatus.pending)
    method: PaymentMethod
    amount: Money = Field(..., ge=0)
    paid_at: Optional[datetime] = None


class PaymentCreate(PaymentBase):
    order_id: int = Field(..., ge=1)


class PaymentUpdate(BaseModel):
    brand_id: Optional[int] = Field(default=None, ge=1)
    status: Optional[PaymentStatus] = None
    method: Optional[PaymentMethod] = None
    amount: Optional[Money] = Field(default=None, ge=0)
    paid_at: Optional[datetime] = None


class Payment(PaymentBase, ORMBase):
    id: int = Field(..., ge=1)
    order_id: int = Field(..., ge=1)
    created_at: datetime
    updated_at: datetime


__all__ = [
    "PaymentBase",
    "PaymentCreate",
    "PaymentUpdate",
    "Payment",
]
