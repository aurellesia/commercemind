from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from .. import models, schemas
from .inventory_service import (
    InsufficientStockError,
    InventoryProductNotFoundError,
    commit_stock_for_order,
    release_stock_for_order,
    reserve_stock_for_order,
)
from .products import build_product_availability


class ProductOrderingError(Exception):
    pass


class ProductNotOrderableError(ProductOrderingError):
    pass


class ProductPriceUnavailableError(ProductOrderingError):
    pass


def get_order(db: Session, order_id: int, brand_id: int | None = None):
    query = db.query(models.Order).filter(models.Order.id == order_id)
    if brand_id is not None:
        query = query.filter(models.Order.brand_id == brand_id)
    return query.first()


def get_orders(db: Session, skip: int = 0, limit: int = 100, brand_id: int = 1):
    return (
        db.query(models.Order)
        .filter(models.Order.brand_id == brand_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_order(db: Session, order: schemas.OrderCreate):
    try:
        db_order = models.Order(
            brand_id=order.brand_id,
            customer_id=order.customer_id,
            status=order.status,
            total_amount=Decimal("0.00"),
        )

        for item in order.items:
            db_order_item = _build_order_item(db, item, brand_id=order.brand_id)
            db_order.items.append(db_order_item)
            db_order.total_amount += db_order_item.subtotal

        db.add(db_order)
        db.flush()
        reserve_stock_for_order(
            db,
            order_id=db_order.id,
            reason="order created",
            commit=False,
        )
        if db_order.status == schemas.OrderStatus.pending:
            db_order.status = schemas.OrderStatus.awaiting_payment

        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception:
        db.rollback()
        raise


def build_order_item_for_order(db: Session, order_item: schemas.OrderItemCreate):
    return _build_order_item(db, order_item)


def update_order_status(db: Session, order_id: int, status: schemas.OrderStatus):
    if status == schemas.OrderStatus.cancelled:
        return cancel_order(db, order_id)

    db_order = get_order(db, order_id)
    if db_order is None:
        return None

    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order: schemas.OrderUpdate):
    if order.status == schemas.OrderStatus.cancelled:
        return cancel_order(db, order_id)

    db_order = get_order(db, order_id)
    if db_order is None:
        return None

    update_data = order.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)

    db.commit()
    db.refresh(db_order)
    return db_order


def cancel_order(db: Session, order_id: int):
    try:
        db_order = get_order(db, order_id)
        if db_order is None:
            return None

        release_stock_for_order(
            db,
            order_id=order_id,
            reason="order cancelled",
            commit=False,
        )
        db_order.status = schemas.OrderStatus.cancelled
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception:
        db.rollback()
        raise


def fulfill_order(db: Session, order_id: int):
    try:
        db_order = get_order(db, order_id)
        if db_order is None:
            return None

        commit_stock_for_order(
            db,
            order_id=order_id,
            reason="order fulfilled",
            commit=False,
        )
        db_order.status = schemas.OrderStatus.fulfilled
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception:
        db.rollback()
        raise


def delete_order(db: Session, order_id: int):
    db_order = get_order(db, order_id)
    if db_order is None:
        return None

    db.delete(db_order)
    db.commit()
    return db_order


def _build_order_item(db: Session, item: schemas.OrderItemCreate, brand_id: int = 1):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == item.product_id, models.Product.brand_id == brand_id)
        .first()
    )
    if product is None:
        raise InventoryProductNotFoundError(f"Product {item.product_id} not found")

    price, price_source = _get_order_price_quote(db, product)
    availability = build_product_availability(db, product)

    if product.status != "active":
        raise ProductNotOrderableError(f"Product {product.id} status is {product.status}")
    if availability.available_quantity < item.quantity:
        raise InsufficientStockError(f"Product {product.id} has insufficient stock")
    if price is None:
        raise ProductPriceUnavailableError(f"Product {product.id} does not have a valid sell price")

    subtotal = price * item.quantity
    return models.OrderItem(
        brand_id=product.brand_id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=price,
        subtotal=subtotal,
        product_cost_price_snapshot=product.cost_price,
        product_name_snapshot=product.name,
        product_sku_snapshot=product.sku,
        product_slug_snapshot=product.slug,
        price_source=price_source,
    )


def _get_order_price_quote(db: Session, product: models.Product):
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
        return price_set_item.price, "price_set"
    return product.base_price, "base_price"
