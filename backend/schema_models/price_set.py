from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from .common import Money, ORMBase


def _validate_price_set_date_range(starts_at: datetime | None, ends_at: datetime | None) -> None:
    if starts_at is not None and ends_at is not None and ends_at < starts_at:
        raise ValueError("ends_at must be greater than or equal to starts_at")


class PriceSetBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    product_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    starts_at: datetime = Field(...)
    ends_at: datetime = Field(...)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_date_range(self) -> "PriceSetBase":
        _validate_price_set_date_range(self.starts_at, self.ends_at)
        return self


class PriceSetCreate(PriceSetBase):
    pass


class PriceSetUpdate(BaseModel):
    brand_id: Optional[int] = Field(default=None, ge=1)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "PriceSetUpdate":
        _validate_price_set_date_range(self.starts_at, self.ends_at)
        return self


class PriceSetItemBase(BaseModel):
    channel_id: int = Field(..., ge=1)
    region_id: int = Field(..., ge=1)
    price: Money
    currency: str = Field(..., min_length=3, max_length=3)
    priority: int = Field(0, ge=0)
    is_active: bool = True


class PriceSetItemCreate(PriceSetItemBase):
    price_set_id: int = Field(..., ge=1)


class PriceSetItemUpdate(BaseModel):
    channel_id: Optional[int] = Field(None, ge=1)
    region_id: Optional[int] = Field(None, ge=1)
    price: Optional[Money] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    priority: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class PriceSetItem(PriceSetItemBase, ORMBase):
    id: int
    price_set_id: int
    created_at: datetime
    updated_at: datetime


class PriceSet(PriceSetBase, ORMBase):
    id: int
    items: List[PriceSetItem] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


__all__ = [
    "PriceSetBase",
    "PriceSetCreate",
    "PriceSetUpdate",
    "PriceSetItemBase",
    "PriceSetItemCreate",
    "PriceSetItemUpdate",
    "PriceSetItem",
    "PriceSet",
]
