from __future__ import annotations

import re

from sqlalchemy.orm import Session

from .. import models, schemas


class ProductLifecycleError(Exception):
    pass


class ProductDeleteBlockedError(ProductLifecycleError):
    pass


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "product"


def _unique_slug(
    db: Session,
    desired_slug: str,
    brand_id: int = 1,
    product_id: int | None = None,
) -> str:
    base_slug = _slugify(desired_slug)
    slug = base_slug
    suffix = 2

    while True:
        query = db.query(models.Product).filter(
            models.Product.brand_id == brand_id,
            models.Product.slug == slug,
        )
        if product_id is not None:
            query = query.filter(models.Product.id != product_id)
        if query.first() is None:
            return slug
        slug = f"{base_slug}-{suffix}"
        suffix += 1


def get_product(db: Session, product_id: int, brand_id: int | None = None):
    query = db.query(models.Product).filter(models.Product.id == product_id)
    if brand_id is not None:
        query = query.filter(models.Product.brand_id == brand_id)
    return query.first()


def get_product_by_slug(db: Session, slug: str, brand_id: int = 1):
    return (
        db.query(models.Product)
        .filter(models.Product.brand_id == brand_id, models.Product.slug == slug)
        .first()
    )


def get_products(db: Session, skip: int = 0, limit: int = 100, brand_id: int = 1):
    return (
        db.query(models.Product)
        .filter(models.Product.brand_id == brand_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_product_catalog(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    include_non_public: bool = False,
    brand_id: int = 1,
):
    query = db.query(models.Product).filter(models.Product.brand_id == brand_id)
    if not include_non_public:
        query = query.filter(models.Product.status == "active")

    return [
        build_product_availability(db, product)
        for product in query.offset(skip).limit(limit).all()
    ]


def get_product_availability(db: Session, product_id: int, brand_id: int | None = None):
    product = get_product(db, product_id=product_id, brand_id=brand_id)
    if product is None:
        return None
    return build_product_availability(db, product)


def get_product_availability_by_slug(db: Session, slug: str, brand_id: int = 1):
    product = get_product_by_slug(db, slug=slug, brand_id=brand_id)
    if product is None or product.status != "active":
        return None
    return build_product_availability(db, product)


def get_product_storefront_detail_by_slug(db: Session, slug: str, brand_id: int = 1):
    product = get_product_by_slug(db, slug=slug, brand_id=brand_id)
    if product is None or product.status != "active":
        return None
    return build_product_storefront_detail(db, product)


def create_product(db: Session, product: schemas.ProductCreate):
    product_data = product.model_dump()
    brand_id = product_data.get("brand_id") or 1
    product_data["slug"] = _unique_slug(
        db,
        product_data.get("slug") or product_data["name"],
        brand_id=brand_id,
    )
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product is None:
        return None

    update_data = product.model_dump(exclude_unset=True)
    brand_id = update_data.get("brand_id") or db_product.brand_id or 1
    if "slug" in update_data or "name" in update_data or "brand_id" in update_data:
        update_data["slug"] = _unique_slug(
            db,
            update_data.get("slug") or update_data.get("name") or db_product.name,
            brand_id=brand_id,
            product_id=product_id,
        )
    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def build_product_availability(db: Session, product: models.Product):
    inventory_item = (
        db.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product.id)
        .first()
    )
    primary_image = (
        db.query(models.ProductImage)
        .filter(
            models.ProductImage.product_id == product.id,
            models.ProductImage.is_primary.is_(True),
        )
        .order_by(models.ProductImage.sort_order.asc(), models.ProductImage.id.asc())
        .first()
    )
    if primary_image is None:
        primary_image = (
            db.query(models.ProductImage)
            .filter(models.ProductImage.product_id == product.id)
            .order_by(models.ProductImage.sort_order.asc(), models.ProductImage.id.asc())
            .first()
        )

    effective_price = _get_effective_price(db, product)
    on_hand_quantity = inventory_item.on_hand_quantity if inventory_item else 0
    reserved_quantity = inventory_item.reserved_quantity if inventory_item else 0
    available_quantity = inventory_item.available_quantity if inventory_item else 0
    is_low_stock = inventory_item.is_low_stock if inventory_item else False
    not_purchasable_reason = _not_purchasable_reason(
        product=product,
        available_quantity=available_quantity,
        effective_price=effective_price,
    )

    return schemas.ProductAvailability(
        id=product.id,
        brand_id=product.brand_id,
        name=product.name,
        slug=product.slug,
        sku=product.sku,
        description=product.description,
        status=product.status,
        base_price=product.base_price,
        effective_price=effective_price,
        primary_image=primary_image,
        on_hand_quantity=on_hand_quantity,
        reserved_quantity=reserved_quantity,
        available_quantity=available_quantity,
        is_low_stock=is_low_stock,
        is_purchasable=not_purchasable_reason is None,
        not_purchasable_reason=not_purchasable_reason,
    )


def build_product_storefront_detail(db: Session, product: models.Product):
    availability = build_product_availability(db, product)
    images = (
        db.query(models.ProductImage)
        .filter(models.ProductImage.product_id == product.id)
        .order_by(models.ProductImage.sort_order.asc(), models.ProductImage.id.asc())
        .all()
    )
    return schemas.ProductStorefrontDetail(
        **availability.model_dump(),
        bpom_number=product.bpom_number,
        usage_instructions=product.usage_instructions,
        ingredients=product.ingredients,
        storage_instructions=product.storage_instructions,
        warnings=product.warnings,
        net_weight=product.net_weight,
        images=images,
    )


def archive_product(db: Session, product_id: int):
    return _set_product_status(db, product_id=product_id, status="archived")


def discontinue_product(db: Session, product_id: int):
    return _set_product_status(db, product_id=product_id, status="discontinued")


def reactivate_product(db: Session, product_id: int):
    return _set_product_status(db, product_id=product_id, status="active")


def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product is None:
        return None

    blockers = get_product_delete_blockers(db, product_id=product_id)
    if db_product.status != "draft":
        blockers.insert(0, f"status is {db_product.status}")
    if blockers:
        raise ProductDeleteBlockedError(
            "Product cannot be hard-deleted. Use archive or discontinue instead. "
            f"Blockers: {', '.join(blockers)}"
        )

    db.delete(db_product)
    db.commit()
    return db_product


def get_product_delete_blockers(db: Session, product_id: int) -> list[str]:
    blockers: list[str] = []
    dependency_checks = (
        ("order items", models.OrderItem),
        ("inventory item", models.InventoryItem),
        ("inventory movements", models.InventoryMovement),
        ("inventory reservations", models.InventoryReservation),
        ("price sets", models.PriceSet),
    )

    for label, model in dependency_checks:
        exists = db.query(model.id).filter(model.product_id == product_id).first()
        if exists is not None:
            blockers.append(label)

    return blockers


def _set_product_status(db: Session, product_id: int, status: str):
    db_product = get_product(db, product_id)
    if db_product is None:
        return None

    db_product.status = status
    db.commit()
    db.refresh(db_product)
    return db_product


def _get_effective_price(db: Session, product: models.Product):
    price_set_item = (
        db.query(models.PriceSetItem)
        .join(models.PriceSet)
        .filter(
            models.PriceSet.product_id == product.id,
            models.PriceSet.is_active.is_(True),
            models.PriceSetItem.is_active.is_(True),
        )
        .order_by(models.PriceSetItem.priority.desc(), models.PriceSetItem.id.desc())
        .first()
    )
    if price_set_item is not None:
        return price_set_item.price
    return product.base_price


def _not_purchasable_reason(
    product: models.Product,
    available_quantity: int,
    effective_price,
) -> str | None:
    if product.status != "active":
        return f"Product status is {product.status}"
    if available_quantity <= 0:
        return "Product is out of stock"
    if effective_price is None:
        return "Product does not have a valid sell price"
    return None
