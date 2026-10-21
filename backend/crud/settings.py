from __future__ import annotations

import re

from sqlalchemy.orm import Session

from .. import models, schemas


DEFAULT_DESCRIPTION = (
    "CommerceMind adalah template storefront ecommerce untuk menampilkan produk, "
    "harga, stok, dan detail katalog secara rapi."
)
DEFAULT_HOMEPAGE_DESCRIPTION = (
    "Gunakan storefront ini sebagai template toko untuk skincare, fashion, "
    "aksesoris, atau brand lain."
)


def get_brands(db: Session, skip: int = 0, limit: int = 100):
    ensure_default_brand(db)
    return db.query(models.Brand).order_by(models.Brand.id.asc()).offset(skip).limit(limit).all()


def get_brand(db: Session, brand_id: int):
    return db.query(models.Brand).filter(models.Brand.id == brand_id).first()


def get_brand_by_slug(db: Session, slug: str):
    return db.query(models.Brand).filter(models.Brand.slug == slug).first()


def create_brand(
    db: Session,
    brand: schemas.BrandCreate,
    actor: str = "system",
    role: str = "system",
):
    slug = _unique_brand_slug(db, brand.slug)
    db_brand = models.Brand(
        name=brand.name,
        slug=slug,
        status=brand.status,
        plan=brand.plan,
        primary_domain=brand.primary_domain,
    )
    db.add(db_brand)
    db.flush()
    ensure_platform_settings(db, brand_id=db_brand.id)
    _add_audit_log(
        db,
        brand_id=db_brand.id,
        actor=actor,
        role=role,
        action="brand.create",
        target_type="brand",
        target_id=db_brand.id,
        before_value=None,
        after_value=_snapshot(db_brand, ["name", "slug", "status", "plan", "primary_domain"]),
    )
    db.commit()
    db.refresh(db_brand)
    return db_brand


def update_brand(
    db: Session,
    brand_id: int,
    brand: schemas.BrandUpdate,
    actor: str = "system",
    role: str = "system",
):
    db_brand = get_brand(db, brand_id)
    if db_brand is None:
        return None

    update_data = brand.model_dump(exclude_unset=True)
    if "slug" in update_data and update_data["slug"] is not None:
        update_data["slug"] = _unique_brand_slug(
            db,
            update_data["slug"],
            brand_id=brand_id,
        )
    before_value = _snapshot(db_brand, update_data.keys())
    for field, value in update_data.items():
        setattr(db_brand, field, value)
    after_value = _snapshot(db_brand, update_data.keys())
    _add_audit_log(
        db,
        brand_id=db_brand.id,
        actor=actor,
        role=role,
        action="brand.update",
        target_type="brand",
        target_id=db_brand.id,
        before_value=before_value,
        after_value=after_value,
    )
    db.commit()
    db.refresh(db_brand)
    return db_brand


def ensure_default_brand(db: Session):
    brand = get_brand_by_slug(db, "default")
    if brand is not None:
        return brand

    brand = models.Brand(
        id=1,
        name="CommerceMind",
        slug="default",
        status="active",
        plan="starter",
    )
    db.add(brand)
    db.flush()
    return brand


def ensure_platform_settings(db: Session, brand_id: int | None = None):
    tenant_brand = get_brand(db, brand_id) if brand_id is not None else ensure_default_brand(db)
    if tenant_brand is None:
        return None

    brand = _ensure_row(
        db,
        models.BrandSettings,
        tenant_brand.id,
        brand_name=tenant_brand.name or "CommerceMind",
        tagline="Template toko online untuk katalog produk yang rapi.",
    )
    storefront = _ensure_row(
        db,
        models.StorefrontSettings,
        tenant_brand.id,
        storefront_enabled=True,
        homepage_headline="Katalog produk dengan stok dan harga yang jelas.",
        homepage_description=DEFAULT_HOMEPAGE_DESCRIPTION,
        featured_product_limit=3,
        show_out_of_stock_products=True,
        show_sku=True,
    )
    seo = _ensure_row(
        db,
        models.SeoSettings,
        tenant_brand.id,
        site_url="http://localhost:5173",
        default_title=tenant_brand.name or "CommerceMind",
        default_description=DEFAULT_DESCRIPTION,
    )
    modules = _ensure_row(
        db,
        models.ModuleSettings,
        tenant_brand.id,
        products_enabled=True,
        inventory_enabled=True,
        cart_enabled=False,
        guest_checkout_enabled=False,
        customer_accounts_enabled=False,
        payments_enabled=True,
        shipping_enabled=False,
        reports_enabled=True,
    )
    system = _ensure_row(
        db,
        models.SystemSettings,
        tenant_brand.id,
        maintenance_mode=False,
        test_mode=True,
        public_catalog_enabled=True,
        allow_checkout=False,
    )
    db.commit()
    for row in (tenant_brand, brand, storefront, seo, modules, system):
        db.refresh(row)
    return tenant_brand, brand, storefront, seo, modules, system


def get_platform_settings(
    db: Session,
    brand_id: int | None = None,
) -> schemas.PlatformSettings:
    settings = ensure_platform_settings(db, brand_id=brand_id)
    if settings is None:
        return None
    tenant_brand, brand, storefront, seo, modules, system = settings
    return schemas.PlatformSettings(
        tenant_brand=tenant_brand,
        brand=brand,
        storefront=storefront,
        seo=seo,
        modules=modules,
        system=system,
    )


def get_public_storefront_config(
    db: Session,
    brand_slug: str | None = None,
) -> schemas.PublicStorefrontConfig:
    if brand_slug is None:
        settings = ensure_platform_settings(db)
    else:
        brand = get_brand_by_slug(db, brand_slug)
        if brand is None:
            return None
        settings = ensure_platform_settings(db, brand_id=brand.id)

    if settings is None:
        return None

    tenant_brand, brand, storefront, seo, modules, system = settings
    return schemas.PublicStorefrontConfig(
        brand_id=tenant_brand.id,
        brand_slug=tenant_brand.slug,
        brand_name=brand.brand_name,
        tagline=brand.tagline,
        logo_url=brand.logo_url,
        contact_whatsapp=brand.contact_whatsapp,
        storefront_enabled=storefront.storefront_enabled,
        homepage_headline=storefront.homepage_headline,
        homepage_description=storefront.homepage_description,
        featured_product_limit=storefront.featured_product_limit,
        show_out_of_stock_products=storefront.show_out_of_stock_products,
        show_sku=storefront.show_sku,
        site_url=seo.site_url,
        default_title=seo.default_title,
        default_description=seo.default_description,
        social_image_url=seo.social_image_url,
        public_catalog_enabled=system.public_catalog_enabled,
        allow_checkout=system.allow_checkout,
        modules=schemas.PublicStorefrontModules(
            products_enabled=modules.products_enabled,
            inventory_enabled=modules.inventory_enabled,
            cart_enabled=modules.cart_enabled,
            guest_checkout_enabled=modules.guest_checkout_enabled,
            customer_accounts_enabled=modules.customer_accounts_enabled,
            payments_enabled=modules.payments_enabled,
            shipping_enabled=modules.shipping_enabled,
        ),
    )


def update_brand_settings(
    db: Session,
    settings: schemas.BrandSettingsUpdate,
    brand_id: int | None = None,
    actor: str = "system",
    role: str = "system",
):
    rows = ensure_platform_settings(db, brand_id=brand_id)
    if rows is None:
        return None
    _, brand, _, _, _, _ = rows
    return _update_row(db, brand, settings, actor=actor, role=role)


def update_storefront_settings(
    db: Session,
    settings: schemas.StorefrontSettingsUpdate,
    brand_id: int | None = None,
    actor: str = "system",
    role: str = "system",
):
    rows = ensure_platform_settings(db, brand_id=brand_id)
    if rows is None:
        return None
    _, _, storefront, _, _, _ = rows
    return _update_row(db, storefront, settings, actor=actor, role=role)


def update_seo_settings(
    db: Session,
    settings: schemas.SeoSettingsUpdate,
    brand_id: int | None = None,
    actor: str = "system",
    role: str = "system",
):
    rows = ensure_platform_settings(db, brand_id=brand_id)
    if rows is None:
        return None
    _, _, _, seo, _, _ = rows
    return _update_row(db, seo, settings, actor=actor, role=role)


def update_module_settings(
    db: Session,
    settings: schemas.ModuleSettingsUpdate,
    brand_id: int | None = None,
    actor: str = "system",
    role: str = "system",
):
    rows = ensure_platform_settings(db, brand_id=brand_id)
    if rows is None:
        return None
    _, _, _, _, modules, _ = rows
    return _update_row(db, modules, settings, actor=actor, role=role)


def update_system_settings(
    db: Session,
    settings: schemas.SystemSettingsUpdate,
    brand_id: int | None = None,
    actor: str = "system",
    role: str = "system",
):
    rows = ensure_platform_settings(db, brand_id=brand_id)
    if rows is None:
        return None
    _, _, _, _, _, system = rows
    return _update_row(db, system, settings, actor=actor, role=role)


def get_audit_logs(
    db: Session,
    brand_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(models.AuditLog)
    if brand_id is not None:
        query = query.filter(models.AuditLog.brand_id == brand_id)
    return query.order_by(models.AuditLog.id.desc()).offset(skip).limit(limit).all()


def _ensure_row(db: Session, model, brand_id: int, **defaults):
    row = db.query(model).filter(model.brand_id == brand_id).first()
    if row is not None:
        return row
    row = model(brand_id=brand_id, **defaults)
    db.add(row)
    db.flush()
    return row


def _update_row(
    db: Session,
    row,
    settings,
    actor: str = "system",
    role: str = "system",
):
    update_data = settings.model_dump(exclude_unset=True)
    before_value = _snapshot(row, update_data.keys())
    for field, value in update_data.items():
        setattr(row, field, value)
    after_value = _snapshot(row, update_data.keys())
    if update_data:
        _add_audit_log(
            db,
            brand_id=getattr(row, "brand_id", None),
            actor=actor,
            role=role,
            action=f"{row.__tablename__}.update",
            target_type=row.__tablename__,
            target_id=getattr(row, "id", None),
            before_value=before_value,
            after_value=after_value,
        )
    db.commit()
    db.refresh(row)
    return row


def _snapshot(row, fields) -> dict:
    return {field: getattr(row, field) for field in fields}


def _add_audit_log(
    db: Session,
    brand_id: int | None,
    actor: str,
    role: str,
    action: str,
    target_type: str,
    target_id: int | None,
    before_value: dict | None,
    after_value: dict | None,
):
    db.add(
        models.AuditLog(
            brand_id=brand_id,
            actor=actor,
            role=role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            before_value=before_value,
            after_value=after_value,
        )
    )


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "brand"


def _unique_brand_slug(db: Session, desired_slug: str, brand_id: int | None = None) -> str:
    base_slug = _slugify(desired_slug)
    slug = base_slug
    suffix = 2

    while True:
        query = db.query(models.Brand).filter(models.Brand.slug == slug)
        if brand_id is not None:
            query = query.filter(models.Brand.id != brand_id)
        if query.first() is None:
            return slug
        slug = f"{base_slug}-{suffix}"
        suffix += 1
