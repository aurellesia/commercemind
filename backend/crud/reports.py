from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas

REVENUE_ORDER_STATUSES = ("paid", "processing", "fulfilled", "completed")


def get_product_reporting_dashboard(db: Session, limit: int = 10, brand_id: int = 1):
    return schemas.ProductReportingDashboard(
        summary=get_product_reporting_summary(db, brand_id=brand_id),
        gross_revenue_per_product=get_gross_revenue_per_product(db, limit=limit, brand_id=brand_id),
        slow_moving_products=get_slow_moving_products(db, limit=limit, brand_id=brand_id),
        low_stock_active_products=get_low_stock_active_products(db, limit=limit, brand_id=brand_id),
        discontinued_products_with_remaining_stock=get_discontinued_products_with_remaining_stock(
            db,
            limit=limit,
            brand_id=brand_id,
        ),
    )


def get_product_reporting_summary(db: Session, brand_id: int = 1):
    revenue_row = _revenue_base_query(db, brand_id=brand_id).one()
    gross_revenue = _decimal_or_zero(revenue_row.gross_revenue)
    estimated_cost = _decimal_or_zero(revenue_row.estimated_cost)
    products_with_sales = (
        db.query(func.count(func.distinct(models.OrderItem.product_id)))
        .join(models.Order, models.Order.id == models.OrderItem.order_id)
        .filter(models.Order.brand_id == brand_id, models.Order.status.in_(REVENUE_ORDER_STATUSES))
        .scalar()
        or 0
    )
    return schemas.ProductReportingSummary(
        gross_revenue=gross_revenue,
        total_quantity_sold=int(revenue_row.quantity_sold or 0),
        estimated_gross_margin=gross_revenue - estimated_cost,
        products_with_sales=int(products_with_sales),
        low_stock_active_products=len(
            get_low_stock_active_products(db, limit=100000, brand_id=brand_id)
        ),
        discontinued_products_with_stock=len(
            get_discontinued_products_with_remaining_stock(
                db,
                limit=100000,
                brand_id=brand_id,
            )
        ),
    )


def get_gross_revenue_per_product(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
):
    rows = (
        db.query(
            models.Product.id.label("product_id"),
            models.Product.name,
            models.Product.sku,
            models.Product.slug,
            func.coalesce(func.sum(models.OrderItem.quantity), 0).label("quantity_sold"),
            func.coalesce(func.sum(models.OrderItem.subtotal), 0).label("gross_revenue"),
            func.coalesce(
                func.sum(models.OrderItem.product_cost_price_snapshot * models.OrderItem.quantity),
                0,
            ).label("estimated_cost"),
        )
        .join(models.OrderItem, models.OrderItem.product_id == models.Product.id)
        .join(models.Order, models.Order.id == models.OrderItem.order_id)
        .filter(models.Product.brand_id == brand_id, models.Order.status.in_(REVENUE_ORDER_STATUSES))
        .group_by(models.Product.id, models.Product.name, models.Product.sku, models.Product.slug)
        .order_by(func.sum(models.OrderItem.subtotal).desc(), models.Product.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_revenue_report_from_row(row) for row in rows]


def get_slow_moving_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
):
    sales_subquery = (
        db.query(
            models.OrderItem.product_id.label("product_id"),
            func.coalesce(func.sum(models.OrderItem.quantity), 0).label("quantity_sold"),
        )
        .join(models.Order, models.Order.id == models.OrderItem.order_id)
        .filter(models.Order.brand_id == brand_id, models.Order.status.in_(REVENUE_ORDER_STATUSES))
        .group_by(models.OrderItem.product_id)
        .subquery()
    )

    rows = (
        db.query(models.Product, models.InventoryItem, func.coalesce(sales_subquery.c.quantity_sold, 0))
        .join(models.InventoryItem, models.InventoryItem.product_id == models.Product.id)
        .outerjoin(sales_subquery, sales_subquery.c.product_id == models.Product.id)
        .filter(
            models.Product.brand_id == brand_id,
            models.Product.status == "active",
            models.InventoryItem.on_hand_quantity > 0,
        )
        .order_by(func.coalesce(sales_subquery.c.quantity_sold, 0).asc(), models.InventoryItem.on_hand_quantity.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_stock_report_from_models(product, inventory_item) for product, inventory_item, _ in rows]


def get_low_stock_active_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
):
    rows = (
        db.query(models.Product, models.InventoryItem)
        .join(models.InventoryItem, models.InventoryItem.product_id == models.Product.id)
        .filter(
            models.Product.status == "active",
            models.Product.brand_id == brand_id,
            (models.InventoryItem.on_hand_quantity - models.InventoryItem.reserved_quantity)
            <= models.InventoryItem.low_stock_threshold,
        )
        .order_by(
            (models.InventoryItem.on_hand_quantity - models.InventoryItem.reserved_quantity).asc(),
            models.Product.id.asc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_stock_report_from_models(product, inventory_item) for product, inventory_item in rows]


def get_discontinued_products_with_remaining_stock(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
):
    rows = (
        db.query(models.Product, models.InventoryItem)
        .join(models.InventoryItem, models.InventoryItem.product_id == models.Product.id)
        .filter(
            models.Product.brand_id == brand_id,
            models.Product.status == "discontinued",
            models.InventoryItem.on_hand_quantity > 0,
        )
        .order_by(models.InventoryItem.on_hand_quantity.desc(), models.Product.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_stock_report_from_models(product, inventory_item) for product, inventory_item in rows]


def _revenue_base_query(db: Session, brand_id: int = 1):
    return (
        db.query(
            func.coalesce(func.sum(models.OrderItem.quantity), 0).label("quantity_sold"),
            func.coalesce(func.sum(models.OrderItem.subtotal), 0).label("gross_revenue"),
            func.coalesce(
                func.sum(models.OrderItem.product_cost_price_snapshot * models.OrderItem.quantity),
                0,
            ).label("estimated_cost"),
        )
        .join(models.Order, models.Order.id == models.OrderItem.order_id)
        .filter(models.Order.brand_id == brand_id, models.Order.status.in_(REVENUE_ORDER_STATUSES))
    )


def _revenue_report_from_row(row):
    gross_revenue = _decimal_or_zero(row.gross_revenue)
    estimated_cost = _decimal_or_zero(row.estimated_cost)
    return schemas.ProductRevenueReport(
        product_id=row.product_id,
        name=row.name,
        sku=row.sku,
        slug=row.slug,
        quantity_sold=int(row.quantity_sold or 0),
        gross_revenue=gross_revenue,
        estimated_cost=estimated_cost,
        estimated_gross_margin=gross_revenue - estimated_cost,
    )


def _stock_report_from_models(product: models.Product, inventory_item: models.InventoryItem):
    return schemas.ProductStockReport(
        product_id=product.id,
        name=product.name,
        sku=product.sku,
        slug=product.slug,
        status=product.status,
        on_hand_quantity=inventory_item.on_hand_quantity,
        reserved_quantity=inventory_item.reserved_quantity,
        available_quantity=inventory_item.available_quantity,
        low_stock_threshold=inventory_item.low_stock_threshold,
    )


def _decimal_or_zero(value):
    if value is None:
        return Decimal("0")
    return value
