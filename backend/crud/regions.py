from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models, schemas


def get_region(db: Session, region_id: int, brand_id: int | None = None):
    query = db.query(models.Region).filter(models.Region.id == region_id)
    if brand_id is not None:
        query = query.filter(models.Region.brand_id == brand_id)
    return query.first()


def get_region_by_code(db: Session, code: str, brand_id: int = 1):
    return (
        db.query(models.Region)
        .filter(models.Region.brand_id == brand_id, models.Region.code == code)
        .first()
    )


def get_regions(db: Session, skip: int = 0, limit: int = 100, brand_id: int = 1):
    return (
        db.query(models.Region)
        .filter(models.Region.brand_id == brand_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_region(db: Session, region: schemas.RegionCreate):
    db_region = models.Region(**region.model_dump())
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region


def update_region(db: Session, region_id: int, region: schemas.RegionUpdate):
    db_region = get_region(db, region_id)
    if db_region is None:
        return None

    update_data = region.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_region, field, value)

    db.commit()
    db.refresh(db_region)
    return db_region


def delete_region(db: Session, region_id: int):
    db_region = get_region(db, region_id)
    if db_region is None:
        return None

    db.delete(db_region)
    db.commit()
    return db_region
