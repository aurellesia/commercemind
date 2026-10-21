from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .common import ORMBase


class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    status: str = Field(default="active", pattern="^(draft|active|suspended|archived)$")
    plan: str = Field(default="starter", min_length=1, max_length=100)
    primary_domain: Optional[str] = Field(default=None, max_length=255)


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    status: Optional[str] = Field(
        default=None,
        pattern="^(draft|active|suspended|archived)$",
    )
    plan: Optional[str] = Field(default=None, min_length=1, max_length=100)
    primary_domain: Optional[str] = Field(default=None, max_length=255)


class Brand(BrandBase, ORMBase):
    id: int
    created_at: datetime
    updated_at: datetime


class BrandSettingsBase(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=255)
    tagline: Optional[str] = Field(default=None, max_length=500)
    logo_url: Optional[str] = None
    contact_whatsapp: Optional[str] = Field(default=None, max_length=50)
    support_email: Optional[str] = Field(default=None, max_length=255)
    business_address: Optional[str] = None


class BrandSettingsUpdate(BaseModel):
    brand_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    tagline: Optional[str] = Field(default=None, max_length=500)
    logo_url: Optional[str] = None
    contact_whatsapp: Optional[str] = Field(default=None, max_length=50)
    support_email: Optional[str] = Field(default=None, max_length=255)
    business_address: Optional[str] = None


class BrandSettings(BrandSettingsBase, ORMBase):
    id: int
    brand_id: int
    created_at: datetime
    updated_at: datetime


class StorefrontSettingsBase(BaseModel):
    storefront_enabled: bool = True
    homepage_headline: str = Field(..., min_length=1, max_length=500)
    homepage_description: Optional[str] = None
    featured_product_limit: int = Field(default=3, ge=0)
    show_out_of_stock_products: bool = True
    show_sku: bool = True


class StorefrontSettingsUpdate(BaseModel):
    storefront_enabled: Optional[bool] = None
    homepage_headline: Optional[str] = Field(default=None, min_length=1, max_length=500)
    homepage_description: Optional[str] = None
    featured_product_limit: Optional[int] = Field(default=None, ge=0)
    show_out_of_stock_products: Optional[bool] = None
    show_sku: Optional[bool] = None


class StorefrontSettings(StorefrontSettingsBase, ORMBase):
    id: int
    brand_id: int
    created_at: datetime
    updated_at: datetime


class SeoSettingsBase(BaseModel):
    site_url: str = Field(..., min_length=1, max_length=500)
    default_title: str = Field(..., min_length=1, max_length=255)
    default_description: Optional[str] = None
    social_image_url: Optional[str] = None


class SeoSettingsUpdate(BaseModel):
    site_url: Optional[str] = Field(default=None, min_length=1, max_length=500)
    default_title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    default_description: Optional[str] = None
    social_image_url: Optional[str] = None


class SeoSettings(SeoSettingsBase, ORMBase):
    id: int
    brand_id: int
    created_at: datetime
    updated_at: datetime


class ModuleSettingsBase(BaseModel):
    products_enabled: bool = True
    inventory_enabled: bool = True
    cart_enabled: bool = False
    guest_checkout_enabled: bool = False
    customer_accounts_enabled: bool = False
    payments_enabled: bool = True
    shipping_enabled: bool = False
    reports_enabled: bool = True


class ModuleSettingsUpdate(BaseModel):
    products_enabled: Optional[bool] = None
    inventory_enabled: Optional[bool] = None
    cart_enabled: Optional[bool] = None
    guest_checkout_enabled: Optional[bool] = None
    customer_accounts_enabled: Optional[bool] = None
    payments_enabled: Optional[bool] = None
    shipping_enabled: Optional[bool] = None
    reports_enabled: Optional[bool] = None


class ModuleSettings(ModuleSettingsBase, ORMBase):
    id: int
    brand_id: int
    created_at: datetime
    updated_at: datetime


class SystemSettingsBase(BaseModel):
    maintenance_mode: bool = False
    test_mode: bool = True
    public_catalog_enabled: bool = True
    allow_checkout: bool = False


class SystemSettingsUpdate(BaseModel):
    maintenance_mode: Optional[bool] = None
    test_mode: Optional[bool] = None
    public_catalog_enabled: Optional[bool] = None
    allow_checkout: Optional[bool] = None


class SystemSettings(SystemSettingsBase, ORMBase):
    id: int
    brand_id: int
    created_at: datetime
    updated_at: datetime


class PlatformSettings(BaseModel):
    tenant_brand: Brand
    brand: BrandSettings
    storefront: StorefrontSettings
    seo: SeoSettings
    modules: ModuleSettings
    system: SystemSettings


class PublicStorefrontModules(BaseModel):
    products_enabled: bool
    inventory_enabled: bool
    cart_enabled: bool
    guest_checkout_enabled: bool
    customer_accounts_enabled: bool
    payments_enabled: bool
    shipping_enabled: bool


class PublicStorefrontConfig(BaseModel):
    brand_id: int
    brand_slug: str
    brand_name: str
    tagline: Optional[str]
    logo_url: Optional[str]
    contact_whatsapp: Optional[str]
    storefront_enabled: bool
    homepage_headline: str
    homepage_description: Optional[str]
    featured_product_limit: int
    show_out_of_stock_products: bool
    show_sku: bool
    site_url: str
    default_title: str
    default_description: Optional[str]
    social_image_url: Optional[str]
    public_catalog_enabled: bool
    allow_checkout: bool
    modules: PublicStorefrontModules


class AuditLog(ORMBase):
    id: int
    brand_id: Optional[int]
    actor: str
    role: str
    action: str
    target_type: str
    target_id: Optional[int]
    before_value: Optional[Dict[str, Any]]
    after_value: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


__all__ = [
    "BrandSettings",
    "Brand",
    "BrandBase",
    "BrandCreate",
    "BrandUpdate",
    "BrandSettingsBase",
    "BrandSettingsUpdate",
    "StorefrontSettings",
    "StorefrontSettingsBase",
    "StorefrontSettingsUpdate",
    "SeoSettings",
    "SeoSettingsBase",
    "SeoSettingsUpdate",
    "ModuleSettings",
    "ModuleSettingsBase",
    "ModuleSettingsUpdate",
    "SystemSettings",
    "SystemSettingsBase",
    "SystemSettingsUpdate",
    "PlatformSettings",
    "PublicStorefrontModules",
    "PublicStorefrontConfig",
    "AuditLog",
]
