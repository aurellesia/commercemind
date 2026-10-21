import re

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy import event, select
from sqlalchemy.orm import relationship

from ..database import Base
from .common import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("base_price >= 0", name="ck_products_base_price_non_negative"),
        CheckConstraint("cost_price >= 0", name="ck_products_cost_price_non_negative"),
        CheckConstraint(
            "status IN ('draft', 'active', 'archived', 'discontinued')",
            name="ck_products_status_allowed",
        ),
        UniqueConstraint("brand_id", "slug", name="uq_products_brand_slug"),
        UniqueConstraint("brand_id", "sku", name="uq_products_brand_sku"),
    )

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False, default=1, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    bpom_number = Column(String(100), nullable=True)
    usage_instructions = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=True)
    storage_instructions = Column(Text, nullable=True)
    warnings = Column(Text, nullable=True)
    net_weight = Column(String(100), nullable=True)
    cost_price = Column(Numeric(12, 2), nullable=False, default=0)
    base_price = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), nullable=False, index=True, default="draft")

    brand = relationship("Brand")
    inventory_item = relationship(
        "InventoryItem",
        back_populates="product",
        cascade="all, delete-orphan",
        uselist=False,
    )
    price_sets = relationship(
        "PriceSet",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order",
    )


class ProductImage(TimestampMixin, Base):
    __tablename__ = "product_images"
    __table_args__ = (
        CheckConstraint("sort_order >= 0", name="ck_product_images_sort_order_non_negative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    image_url = Column(Text, nullable=False)
    alt_text = Column(String(255), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    is_primary = Column(Boolean, nullable=False, default=False, index=True)

    product = relationship("Product", back_populates="images")


def _slugify_product_name(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "product"


@event.listens_for(Product, "before_insert")
def _set_product_slug_before_insert(mapper, connection, target: Product) -> None:
    if target.slug:
        target.slug = _slugify_product_name(target.slug)
    else:
        target.slug = _slugify_product_name(target.name)

    base_slug = target.slug
    slug = base_slug
    suffix = 2
    existing_slugs = set(
        connection.execute(
            select(Product.__table__.c.slug).where(
                Product.__table__.c.brand_id == (target.brand_id or 1)
            )
        )
        .scalars()
        .all()
    )
    while slug in existing_slugs:
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    target.slug = slug
