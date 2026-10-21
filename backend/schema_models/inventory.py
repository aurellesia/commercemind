from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .common import ORMBase


class InventoryReservationStatus(str, Enum):
    active = "active"
    released = "released"
    committed = "committed"
    expired = "expired"


class InventoryMovementType(str, Enum):
    inbound = "inbound"
    reservation = "reservation"
    release = "release"
    deduction = "deduction"
    adjustment = "adjustment"
    return_ = "return"


class InventoryItemBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    product_id: int = Field(..., ge=1)
    on_hand_quantity: int = Field(..., ge=0)
    reserved_quantity: int = Field(0, ge=0)
    low_stock_threshold: int = Field(0, ge=0)

    @model_validator(mode="after")
    def validate_reserved_quantity(self) -> "InventoryItemBase":
        if self.reserved_quantity > self.on_hand_quantity:
            raise ValueError("reserved_quantity must not exceed on_hand_quantity")
        return self


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    brand_id: Optional[int] = Field(default=None, ge=1)
    product_id: Optional[int] = Field(default=None, ge=1)
    on_hand_quantity: Optional[int] = Field(default=None, ge=0)
    reserved_quantity: Optional[int] = Field(default=None, ge=0)
    low_stock_threshold: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_reserved_quantity(self) -> "InventoryItemUpdate":
        if self.on_hand_quantity is not None and self.reserved_quantity is not None:
            if self.reserved_quantity > self.on_hand_quantity:
                raise ValueError("reserved_quantity must not exceed on_hand_quantity")
        return self


class InventoryItem(InventoryItemBase, ORMBase):
    id: int
    available_quantity: int
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime


class InventoryReservationBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    product_id: int = Field(..., ge=1)
    order_id: int = Field(..., ge=1)
    order_item_id: Optional[int] = Field(default=None, ge=1)
    quantity: int = Field(..., ge=1)
    status: InventoryReservationStatus = Field(default=InventoryReservationStatus.active)
    expires_at: Optional[datetime] = None


class InventoryReservationCreate(InventoryReservationBase):
    pass


class InventoryReservationUpdate(BaseModel):
    brand_id: Optional[int] = Field(default=None, ge=1)
    product_id: Optional[int] = Field(default=None, ge=1)
    order_id: Optional[int] = Field(default=None, ge=1)
    order_item_id: Optional[int] = Field(default=None, ge=1)
    quantity: Optional[int] = Field(default=None, ge=1)
    status: Optional[InventoryReservationStatus] = None
    expires_at: Optional[datetime] = None


class InventoryReservationRead(InventoryReservationBase, ORMBase):
    id: int
    created_at: datetime
    updated_at: datetime


InventoryReservation = InventoryReservationRead


class InventoryMovementBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1)
    movement_type: InventoryMovementType
    reference_type: Optional[str] = Field(default=None, max_length=100)
    reference_id: Optional[int] = Field(default=None, ge=1)
    notes: Optional[str] = None


class InventoryMovementRead(InventoryMovementBase, ORMBase):
    id: int
    created_at: datetime
    updated_at: datetime


InventoryMovement = InventoryMovementRead


class ReceiveStockCommand(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1)
    reference_type: Optional[str] = Field(default=None, max_length=100)
    reference_id: Optional[int] = Field(default=None, ge=1)
    notes: Optional[str] = None


class AdjustStockCommand(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    product_id: int = Field(..., ge=1)
    delta: int
    reference_type: Optional[str] = Field(default=None, max_length=100)
    reference_id: Optional[int] = Field(default=None, ge=1)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_delta(self) -> "AdjustStockCommand":
        if self.delta == 0:
            raise ValueError("delta must not be zero")
        return self


class ReserveStockCommand(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    product_id: int = Field(..., ge=1)
    order_id: int = Field(..., ge=1)
    order_item_id: Optional[int] = Field(default=None, ge=1)
    quantity: int = Field(..., ge=1)
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None


class ReleaseReservationCommand(BaseModel):
    reservation_id: int = Field(..., ge=1)
    notes: Optional[str] = None


class CommitReservationCommand(BaseModel):
    reservation_id: int = Field(..., ge=1)
    notes: Optional[str] = None


__all__ = [
    "InventoryReservationStatus",
    "InventoryMovementType",
    "InventoryItemBase",
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "InventoryItem",
    "InventoryReservationBase",
    "InventoryReservationCreate",
    "InventoryReservationUpdate",
    "InventoryReservationRead",
    "InventoryReservation",
    "InventoryMovementBase",
    "InventoryMovementRead",
    "InventoryMovement",
    "ReceiveStockCommand",
    "AdjustStockCommand",
    "ReserveStockCommand",
    "ReleaseReservationCommand",
    "CommitReservationCommand",
]
