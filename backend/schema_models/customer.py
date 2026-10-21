from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .common import ORMBase


class CustomerBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(
        default=None,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    customer_type: Literal["guest", "registered"] = "guest"


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    brand_id: Optional[int] = Field(default=None, ge=1)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[str] = Field(
        default=None,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    customer_type: Optional[Literal["guest", "registered"]] = None


class Customer(CustomerBase, ORMBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CustomerAddressBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    customer_id: int = Field(..., ge=1)
    recipient_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=50)
    address_line: str = Field(..., min_length=1)
    district: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=255)
    province: str = Field(..., min_length=1, max_length=255)
    postal_code: str = Field(..., min_length=1, max_length=20)
    notes: Optional[str] = None
    is_default: bool = False


class CustomerAddressCreate(BaseModel):
    recipient_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=50)
    address_line: str = Field(..., min_length=1)
    district: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=255)
    province: str = Field(..., min_length=1, max_length=255)
    postal_code: str = Field(..., min_length=1, max_length=20)
    notes: Optional[str] = None
    is_default: bool = False


class CheckoutCustomerData(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=50)
    email: Optional[str] = Field(
        default=None,
        max_length=255,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )


class CustomerAddressUpdate(BaseModel):
    recipient_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=50)
    address_line: Optional[str] = Field(default=None, min_length=1)
    district: Optional[str] = Field(default=None, min_length=1, max_length=255)
    city: Optional[str] = Field(default=None, min_length=1, max_length=255)
    province: Optional[str] = Field(default=None, min_length=1, max_length=255)
    postal_code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    notes: Optional[str] = None
    is_default: Optional[bool] = None


class CustomerAddress(CustomerAddressBase, ORMBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CustomerSummary(Customer):
    total_orders: int = 0
    last_order_date: Optional[datetime] = None
    total_spent: Decimal = Decimal("0")


class CustomerOrderSummary(BaseModel):
    id: int
    status: str
    total_amount: Decimal
    created_at: datetime


class CustomerDetail(Customer):
    addresses: List[CustomerAddress] = Field(default_factory=list)
    recent_orders: List[CustomerOrderSummary] = Field(default_factory=list)


__all__ = [
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "Customer",
    "CustomerAddressBase",
    "CustomerAddressCreate",
    "CheckoutCustomerData",
    "CustomerAddressUpdate",
    "CustomerAddress",
    "CustomerSummary",
    "CustomerOrderSummary",
    "CustomerDetail",
]
