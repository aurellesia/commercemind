from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models, schemas


def get_channel(db: Session, channel_id: int, brand_id: int | None = None):
    query = db.query(models.Channel).filter(models.Channel.id == channel_id)
    if brand_id is not None:
        query = query.filter(models.Channel.brand_id == brand_id)
    return query.first()


def get_channel_by_code(db: Session, code: str, brand_id: int = 1):
    return (
        db.query(models.Channel)
        .filter(models.Channel.brand_id == brand_id, models.Channel.code == code)
        .first()
    )


def get_channels(db: Session, skip: int = 0, limit: int = 100, brand_id: int = 1):
    return (
        db.query(models.Channel)
        .filter(models.Channel.brand_id == brand_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_channel(db: Session, channel: schemas.ChannelCreate):
    db_channel = models.Channel(**channel.model_dump())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


def update_channel(db: Session, channel_id: int, channel: schemas.ChannelUpdate):
    db_channel = get_channel(db, channel_id)
    if db_channel is None:
        return None

    update_data = channel.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_channel, field, value)

    db.commit()
    db.refresh(db_channel)
    return db_channel


def delete_channel(db: Session, channel_id: int):
    db_channel = get_channel(db, channel_id)
    if db_channel is None:
        return None

    db.delete(db_channel)
    db.commit()
    return db_channel
