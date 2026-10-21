from sqlalchemy.orm import Session

from .. import models, schemas
from .orders import build_order_item_for_order


def get_order_item(db: Session, order_item_id: int):
    return (
        db.query(models.OrderItem)
        .filter(models.OrderItem.id == order_item_id)
        .first()
    )


def get_order_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.OrderItem).offset(skip).limit(limit).all()


def get_order_items_by_order_id(db: Session, order_id: int):
    return db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()


def create_order_item(db: Session, order_id: int, order_item: schemas.OrderItemCreate):
    db_order_item = build_order_item_for_order(db, order_item)
    db_order_item.order_id = order_id
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item


def update_order_item(
    db: Session,
    order_item_id: int,
    order_item: schemas.OrderItemUpdate,
):
    db_order_item = get_order_item(db, order_item_id)
    if db_order_item is None:
        return None

    update_data = order_item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order_item, field, value)

    db.commit()
    db.refresh(db_order_item)
    return db_order_item


def delete_order_item(db: Session, order_item_id: int):
    db_order_item = get_order_item(db, order_item_id)
    if db_order_item is None:
        return None

    db.delete(db_order_item)
    db.commit()
    return db_order_item
