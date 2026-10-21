from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from .common import Money, ORMBase, OrderStatus


class OrderItemBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1)
    unit_price: Money = Field(..., ge=0)
    subtotal: Money = Field(..., ge=0)
    product_cost_price_snapshot: Money = Field(..., ge=0)
    product_name_snapshot: str = Field(..., min_length=1, max_length=255)
    product_sku_snapshot: Optional[str] = Field(default=None, max_length=100)
    product_slug_snapshot: str = Field(..., min_length=1, max_length=255)
    price_source: str = Field(..., min_length=1, max_length=50)

    @model_validator(mode="after")
    def _validate_subtotal(self) -> OrderItemBase:
        if self.subtotal != self.unit_price * self.quantity:
            raise ValueError("subtotal must equal unit_price * quantity")
        return self


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1)
    # Accepted for backward compatibility, but ignored by order creation.
    unit_price: Optional[Money] = Field(default=None, ge=0)
    subtotal: Optional[Money] = Field(default=None, ge=0)


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(default=None, ge=1)
    unit_price: Optional[Money] = Field(default=None, ge=0)
    subtotal: Optional[Money] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _validate_subtotal(self) -> OrderItemUpdate:
        if self.quantity is None or self.unit_price is None or self.subtotal is None:
            return self
        if self.subtotal != self.unit_price * self.quantity:
            raise ValueError("subtotal must equal unit_price * quantity")
        return self


class OrderItem(OrderItemBase, ORMBase):
    id: int = Field(..., ge=1)
    order_id: int = Field(..., ge=1)
    created_at: datetime
    updated_at: datetime


class OrderBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    customer_id: int = Field(..., ge=1)
    status: OrderStatus = Field(default=OrderStatus.pending)
    total_amount: Money = Field(default=0, ge=0)


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(default_factory=list)


class OrderUpdate(BaseModel):
    brand_id: Optional[int] = Field(default=None, ge=1)
    status: Optional[OrderStatus] = None
    total_amount: Optional[Money] = Field(default=None, ge=0)


class Order(OrderBase, ORMBase):
    id: int = Field(..., ge=1)
    items: List[OrderItem] = Field(default_factory=list)
    payment: Optional["Payment"] = Field(default=None)
    created_at: datetime
    updated_at: datetime


from .payment import Payment  # noqa: E402  # isort:skip

Order.model_rebuild(_types_namespace={"Payment": Payment})


__all__ = [
    "OrderItemBase",
    "OrderItemCreate",
    "OrderItemUpdate",
    "OrderItem",
    "OrderBase",
    "OrderCreate",
    "OrderUpdate",
    "Order",
]
