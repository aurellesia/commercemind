from typing import List, Optional

from pydantic import BaseModel, Field

from .common import Money


class ProductRevenueReport(BaseModel):
    product_id: int = Field(..., ge=1)
    name: str
    sku: Optional[str]
    slug: str
    quantity_sold: int = Field(..., ge=0)
    gross_revenue: Money = Field(..., ge=0)
    estimated_cost: Money = Field(..., ge=0)
    estimated_gross_margin: Money


class ProductStockReport(BaseModel):
    product_id: int = Field(..., ge=1)
    name: str
    sku: Optional[str]
    slug: str
    status: str
    on_hand_quantity: int = Field(..., ge=0)
    reserved_quantity: int = Field(..., ge=0)
    available_quantity: int
    low_stock_threshold: int = Field(..., ge=0)


class ProductReportingSummary(BaseModel):
    gross_revenue: Money = Field(..., ge=0)
    total_quantity_sold: int = Field(..., ge=0)
    estimated_gross_margin: Money
    products_with_sales: int = Field(..., ge=0)
    low_stock_active_products: int = Field(..., ge=0)
    discontinued_products_with_stock: int = Field(..., ge=0)


class ProductReportingDashboard(BaseModel):
    summary: ProductReportingSummary
    gross_revenue_per_product: List[ProductRevenueReport]
    slow_moving_products: List[ProductStockReport]
    low_stock_active_products: List[ProductStockReport]
    discontinued_products_with_remaining_stock: List[ProductStockReport]


__all__ = [
    "ProductRevenueReport",
    "ProductStockReport",
    "ProductReportingSummary",
    "ProductReportingDashboard",
]
