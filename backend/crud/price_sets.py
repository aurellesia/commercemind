from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas


def get_price_set(db: Session, price_set_id: int, brand_id: int | None = None):
    query = db.query(models.PriceSet).filter(models.PriceSet.id == price_set_id)
    if brand_id is not None:
        query = query.filter(models.PriceSet.brand_id == brand_id)
    return query.first()


def get_price_sets(db: Session, skip: int = 0, limit: int = 100, brand_id: int = 1):
    return (
        db.query(models.PriceSet)
        .filter(models.PriceSet.brand_id == brand_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_price_sets_by_product_id(db: Session, product_id: int, brand_id: int | None = None):
    query = db.query(models.PriceSet).filter(models.PriceSet.product_id == product_id)
    if brand_id is not None:
        query = query.filter(models.PriceSet.brand_id == brand_id)
    return (
        query.all()
    )


def get_active_price_sets_by_product_id(
    db: Session,
    product_id: int,
    at: datetime = None,
    brand_id: int | None = None,
):
    at = at or datetime.utcnow()
    query = db.query(models.PriceSet).filter(
        models.PriceSet.product_id == product_id,
        models.PriceSet.is_active.is_(True),
        or_(models.PriceSet.starts_at.is_(None), models.PriceSet.starts_at <= at),
        or_(models.PriceSet.ends_at.is_(None), models.PriceSet.ends_at >= at),
    )
    if brand_id is not None:
        query = query.filter(models.PriceSet.brand_id == brand_id)
    return (
        query.all()
    )


def create_price_set(db: Session, price_set: schemas.PriceSetCreate):
    db_price_set = models.PriceSet(**price_set.model_dump())
    db.add(db_price_set)
    db.commit()
    db.refresh(db_price_set)
    return db_price_set


def update_price_set(
    db: Session,
    price_set_id: int,
    price_set: schemas.PriceSetUpdate,
):
    db_price_set = get_price_set(db, price_set_id)
    if db_price_set is None:
        return None

    update_data = price_set.model_dump(exclude_unset=True)
    next_starts_at = update_data.get("starts_at", db_price_set.starts_at)
    next_ends_at = update_data.get("ends_at", db_price_set.ends_at)
    if next_starts_at is not None and next_ends_at is not None:
        if next_ends_at < next_starts_at:
            return None

    for field, value in update_data.items():
        setattr(db_price_set, field, value)

    db.commit()
    db.refresh(db_price_set)
    return db_price_set


def delete_price_set(db: Session, price_set_id: int):
    db_price_set = get_price_set(db, price_set_id)
    if db_price_set is None:
        return None

    db.delete(db_price_set)
    db.commit()
    return db_price_set
