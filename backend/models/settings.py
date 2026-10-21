from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from ..database import Base
from .common import TimestampMixin


class Brand(TimestampMixin, Base):
    __tablename__ = "brands"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'active', 'suspended', 'archived')",
            name="ck_brands_status_allowed",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    plan = Column(String(100), nullable=False, default="starter")
    primary_domain = Column(String(255), nullable=True, unique=True, index=True)

    brand_settings = relationship(
        "BrandSettings",
        back_populates="brand",
        cascade="all, delete-orphan",
        uselist=False,
    )
    storefront_settings = relationship(
        "StorefrontSettings",
        back_populates="brand",
        cascade="all, delete-orphan",
        uselist=False,
    )
    seo_settings = relationship(
        "SeoSettings",
        back_populates="brand",
        cascade="all, delete-orphan",
        uselist=False,
    )
    module_settings = relationship(
        "ModuleSettings",
        back_populates="brand",
        cascade="all, delete-orphan",
        uselist=False,
    )
    system_settings = relationship(
        "SystemSettings",
        back_populates="brand",
        cascade="all, delete-orphan",
        uselist=False,
    )


class BrandSettings(TimestampMixin, Base):
    __tablename__ = "brand_settings"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, unique=True, index=True)
    brand_name = Column(String(255), nullable=False, default="CommerceMind")
    tagline = Column(String(500), nullable=True)
    logo_url = Column(Text, nullable=True)
    contact_whatsapp = Column(String(50), nullable=True)
    support_email = Column(String(255), nullable=True)
    business_address = Column(Text, nullable=True)
    brand = relationship("Brand", back_populates="brand_settings")


class StorefrontSettings(TimestampMixin, Base):
    __tablename__ = "storefront_settings"
    __table_args__ = (
        CheckConstraint(
            "featured_product_limit >= 0",
            name="ck_storefront_settings_featured_product_limit_non_negative",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, unique=True, index=True)
    storefront_enabled = Column(Boolean, nullable=False, default=True)
    homepage_headline = Column(
        String(500),
        nullable=False,
        default="Katalog produk dengan stok dan harga yang jelas.",
    )
    homepage_description = Column(Text, nullable=True)
    featured_product_limit = Column(Integer, nullable=False, default=3)
    show_out_of_stock_products = Column(Boolean, nullable=False, default=True)
    show_sku = Column(Boolean, nullable=False, default=True)
    brand = relationship("Brand", back_populates="storefront_settings")


class SeoSettings(TimestampMixin, Base):
    __tablename__ = "seo_settings"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, unique=True, index=True)
    site_url = Column(String(500), nullable=False, default="http://localhost:5173")
    default_title = Column(String(255), nullable=False, default="CommerceMind")
    default_description = Column(Text, nullable=True)
    social_image_url = Column(Text, nullable=True)
    brand = relationship("Brand", back_populates="seo_settings")


class ModuleSettings(TimestampMixin, Base):
    __tablename__ = "module_settings"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, unique=True, index=True)
    products_enabled = Column(Boolean, nullable=False, default=True)
    inventory_enabled = Column(Boolean, nullable=False, default=True)
    cart_enabled = Column(Boolean, nullable=False, default=False)
    guest_checkout_enabled = Column(Boolean, nullable=False, default=False)
    customer_accounts_enabled = Column(Boolean, nullable=False, default=False)
    payments_enabled = Column(Boolean, nullable=False, default=True)
    shipping_enabled = Column(Boolean, nullable=False, default=False)
    reports_enabled = Column(Boolean, nullable=False, default=True)
    brand = relationship("Brand", back_populates="module_settings")


class SystemSettings(TimestampMixin, Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, unique=True, index=True)
    maintenance_mode = Column(Boolean, nullable=False, default=False)
    test_mode = Column(Boolean, nullable=False, default=True)
    public_catalog_enabled = Column(Boolean, nullable=False, default=True)
    allow_checkout = Column(Boolean, nullable=False, default=False)
    brand = relationship("Brand", back_populates="system_settings")


class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True, index=True)
    actor = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    target_type = Column(String(100), nullable=False)
    target_id = Column(Integer, nullable=True)
    before_value = Column(JSON, nullable=True)
    after_value = Column(JSON, nullable=True)

    brand = relationship("Brand")
