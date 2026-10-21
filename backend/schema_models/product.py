from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .common import Money, ORMBase, ProductStatus
from .product_image import ProductImage


class ProductBase(BaseModel):
    brand_id: int = Field(default=1, ge=1)
    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    sku: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    bpom_number: Optional[str] = Field(default=None, max_length=100)
    usage_instructions: Optional[str] = None
    ingredients: Optional[str] = None
    storage_instructions: Optional[str] = None
    warnings: Optional[str] = None
    net_weight: Optional[str] = Field(default=None, max_length=100)
    cost_price: Money = Field(default=0, ge=0)
    base_price: Money = Field(...)
    status: ProductStatus = Field(default=ProductStatus.active)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    brand_id: Optional[int] = Field(default=None, ge=1)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    sku: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    bpom_number: Optional[str] = Field(default=None, max_length=100)
    usage_instructions: Optional[str] = None
    ingredients: Optional[str] = None
    storage_instructions: Optional[str] = None
    warnings: Optional[str] = None
    net_weight: Optional[str] = Field(default=None, max_length=100)
    cost_price: Optional[Money] = Field(default=None, ge=0)
    base_price: Optional[Money] = Field(default=None)
    status: Optional[ProductStatus] = Field(default=None)


class Product(ProductBase, ORMBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime


class ProductAvailability(BaseModel):
    id: int
    brand_id: int
    name: str
    slug: str
    sku: Optional[str]
    description: Optional[str]
    status: ProductStatus
    base_price: Money
    effective_price: Optional[Money]
    primary_image: Optional[ProductImage]
    on_hand_quantity: int
    reserved_quantity: int
    available_quantity: int
    is_low_stock: bool
    is_purchasable: bool
    not_purchasable_reason: Optional[str]


class ProductStorefrontDetail(ProductAvailability):
    bpom_number: Optional[str]
    usage_instructions: Optional[str]
    ingredients: Optional[str]
    storage_instructions: Optional[str]
    warnings: Optional[str]
    net_weight: Optional[str]
    images: List[ProductImage]


__all__ = [
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "Product",
    "ProductAvailability",
    "ProductStorefrontDetail",
]
