from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models, schemas


def get_inventory_item(db: Session, inventory_item_id: int, brand_id: int | None = None):
    query = db.query(models.InventoryItem).filter(models.InventoryItem.id == inventory_item_id)
    if brand_id is not None:
        query = query.filter(models.InventoryItem.brand_id == brand_id)
    return query.first()


def get_inventory_item_by_product_id(db: Session, product_id: int, brand_id: int | None = None):
    query = db.query(models.InventoryItem).filter(models.InventoryItem.product_id == product_id)
    if brand_id is not None:
        query = query.filter(models.InventoryItem.brand_id == brand_id)
    return query.first()


def get_inventory_items(db: Session, skip: int = 0, limit: int = 100, brand_id: int = 1):
    return (
        db.query(models.InventoryItem)
        .filter(models.InventoryItem.brand_id == brand_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_low_stock_inventory_items(db: Session, skip: int = 0, limit: int = 100, brand_id: int = 1):
    return (
        db.query(models.InventoryItem)
        .filter(
            models.InventoryItem.brand_id == brand_id,
            models.InventoryItem.on_hand_quantity
            - models.InventoryItem.reserved_quantity
            <= models.InventoryItem.low_stock_threshold
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_inventory_movements_by_product_id(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    brand_id: int | None = None,
):
    query = db.query(models.InventoryMovement).filter(models.InventoryMovement.product_id == product_id)
    if brand_id is not None:
        query = query.filter(models.InventoryMovement.brand_id == brand_id)
    return (
        query
        .order_by(models.InventoryMovement.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_active_inventory_reservations_by_product_id(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    brand_id: int | None = None,
):
    filters = [
        models.InventoryReservation.product_id == product_id,
        models.InventoryReservation.status == "active",
    ]
    if brand_id is not None:
        filters.append(models.InventoryReservation.brand_id == brand_id)
    return (
        db.query(models.InventoryReservation)
        .filter(*filters)
        .order_by(models.InventoryReservation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_active_inventory_reservations_by_order_id(
    db: Session,
    order_id: int,
    skip: int = 0,
    limit: int = 100,
    brand_id: int | None = None,
):
    filters = [
        models.InventoryReservation.order_id == order_id,
        models.InventoryReservation.status == "active",
    ]
    if brand_id is not None:
        filters.append(models.InventoryReservation.brand_id == brand_id)
    return (
        db.query(models.InventoryReservation)
        .filter(*filters)
        .order_by(models.InventoryReservation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_inventory_item(db: Session, inventory_item: schemas.InventoryItemCreate):
    db_inventory_item = models.InventoryItem(**inventory_item.model_dump())
    db.add(db_inventory_item)
    db.commit()
    db.refresh(db_inventory_item)
    return db_inventory_item


def update_inventory_item(
    db: Session,
    inventory_item_id: int,
    inventory_item: schemas.InventoryItemUpdate,
):
    db_inventory_item = get_inventory_item(db, inventory_item_id)
    if db_inventory_item is None:
        return None

    update_data = inventory_item.model_dump(exclude_unset=True)
    next_on_hand_quantity = update_data.get(
        "on_hand_quantity",
        db_inventory_item.on_hand_quantity,
    )
    next_reserved_quantity = update_data.get(
        "reserved_quantity",
        db_inventory_item.reserved_quantity,
    )
    if next_reserved_quantity > next_on_hand_quantity:
        return None

    for field, value in update_data.items():
        setattr(db_inventory_item, field, value)

    db.commit()
    db.refresh(db_inventory_item)
    return db_inventory_item


def delete_inventory_item(db: Session, inventory_item_id: int):
    db_inventory_item = get_inventory_item(db, inventory_item_id)
    if db_inventory_item is None:
        return None

    db.delete(db_inventory_item)
    db.commit()
    return db_inventory_item
