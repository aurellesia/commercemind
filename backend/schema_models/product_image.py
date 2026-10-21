from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .common import ORMBase


class ProductImageBase(BaseModel):
    image_url: str = Field(..., min_length=1, max_length=2000)
    alt_text: Optional[str] = Field(default=None, max_length=255)
    sort_order: int = Field(default=0, ge=0)
    is_primary: bool = Field(default=False)


class ProductImageCreate(ProductImageBase):
    product_id: int = Field(..., ge=1)


class ProductImageUpdate(BaseModel):
    image_url: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    alt_text: Optional[str] = Field(default=None, max_length=255)
    sort_order: Optional[int] = Field(default=None, ge=0)
    is_primary: Optional[bool] = None


class ProductImage(ProductImageBase, ORMBase):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime


__all__ = [
    "ProductImageBase",
    "ProductImageCreate",
    "ProductImageUpdate",
    "ProductImage",
]
