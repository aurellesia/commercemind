from datetime import datetime

from sqlalchemy import case, or_
from sqlalchemy.orm import Session

from .. import models, schemas


def get_price_set_item(db: Session, price_set_item_id: int):
    return (
        db.query(models.PriceSetItem)
        .filter(models.PriceSetItem.id == price_set_item_id)
        .first()
    )


def get_price_set_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PriceSetItem).offset(skip).limit(limit).all()


def get_price_set_items_by_price_set_id(db: Session, price_set_id: int):
    return (
        db.query(models.PriceSetItem)
        .filter(models.PriceSetItem.price_set_id == price_set_id)
        .all()
    )


def create_price_set_item(db: Session, price_set_item: schemas.PriceSetItemCreate):
    db_price_set_item = models.PriceSetItem(**price_set_item.model_dump())
    db.add(db_price_set_item)
    db.commit()
    db.refresh(db_price_set_item)
    return db_price_set_item


def update_price_set_item(
    db: Session,
    price_set_item_id: int,
    price_set_item: schemas.PriceSetItemUpdate,
):
    db_price_set_item = get_price_set_item(db, price_set_item_id)
    if db_price_set_item is None:
        return None

    update_data = price_set_item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_price_set_item, field, value)

    db.commit()
    db.refresh(db_price_set_item)
    return db_price_set_item


def delete_price_set_item(db: Session, price_set_item_id: int):
    db_price_set_item = get_price_set_item(db, price_set_item_id)
    if db_price_set_item is None:
        return None

    db.delete(db_price_set_item)
    db.commit()
    return db_price_set_item


def get_applicable_price_set_item(
    db: Session,
    product_id: int,
    channel_id: int = None,
    region_id: int = None,
    currency: str = None,
    at: datetime = None,
):
    at = at or datetime.utcnow()

    query = (
        db.query(models.PriceSetItem)
        .join(models.PriceSet)
        .filter(
            models.PriceSet.product_id == product_id,
            models.PriceSet.is_active.is_(True),
            models.PriceSetItem.is_active.is_(True),
            or_(models.PriceSet.starts_at.is_(None), models.PriceSet.starts_at <= at),
            or_(models.PriceSet.ends_at.is_(None), models.PriceSet.ends_at >= at),
        )
    )

    if channel_id is None:
        query = query.filter(models.PriceSetItem.channel_id.is_(None))
    else:
        query = query.filter(
            or_(
                models.PriceSetItem.channel_id == channel_id,
                models.PriceSetItem.channel_id.is_(None),
            )
        )

    if region_id is None:
        query = query.filter(models.PriceSetItem.region_id.is_(None))
    else:
        query = query.filter(
            or_(
                models.PriceSetItem.region_id == region_id,
                models.PriceSetItem.region_id.is_(None),
            )
        )

    if currency is not None:
        query = query.filter(models.PriceSetItem.currency == currency)

    channel_specificity = case(
        (models.PriceSetItem.channel_id.isnot(None), 1),
        else_=0,
    )
    region_specificity = case(
        (models.PriceSetItem.region_id.isnot(None), 1),
        else_=0,
    )

    return (
        query.order_by(
            models.PriceSetItem.priority.desc(),
            channel_specificity.desc(),
            region_specificity.desc(),
            models.PriceSetItem.id.desc(),
        )
        .first()
    )


def get_applicable_product_price(
    db: Session,
    product_id: int,
    channel_id: int = None,
    region_id: int = None,
    currency: str = None,
    at: datetime = None,
):
    price_set_item = get_applicable_price_set_item(
        db,
        product_id=product_id,
        channel_id=channel_id,
        region_id=region_id,
        currency=currency,
        at=at,
    )
    if price_set_item is not None:
        return price_set_item.price

    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        return None
    return product.base_price
