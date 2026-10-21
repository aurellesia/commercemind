from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models, schemas


def get_product_image(db: Session, product_image_id: int):
    return (
        db.query(models.ProductImage)
        .filter(models.ProductImage.id == product_image_id)
        .first()
    )


def get_product_images_by_product_id(db: Session, product_id: int):
    return (
        db.query(models.ProductImage)
        .filter(models.ProductImage.product_id == product_id)
        .order_by(models.ProductImage.sort_order.asc(), models.ProductImage.id.asc())
        .all()
    )


def create_product_image(db: Session, product_image: schemas.ProductImageCreate):
    db_product_image = models.ProductImage(**product_image.model_dump())
    db.add(db_product_image)
    if db_product_image.is_primary:
        _unset_other_primary_images(db, db_product_image.product_id)
    db.commit()
    db.refresh(db_product_image)
    return db_product_image


def update_product_image(
    db: Session,
    product_image_id: int,
    product_image: schemas.ProductImageUpdate,
):
    db_product_image = get_product_image(db, product_image_id)
    if db_product_image is None:
        return None

    update_data = product_image.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product_image, field, value)

    if update_data.get("is_primary") is True:
        _unset_other_primary_images(
            db,
            db_product_image.product_id,
            exclude_image_id=db_product_image.id,
        )

    db.commit()
    db.refresh(db_product_image)
    return db_product_image


def delete_product_image(db: Session, product_image_id: int):
    db_product_image = get_product_image(db, product_image_id)
    if db_product_image is None:
        return None

    db.delete(db_product_image)
    db.commit()
    return db_product_image


def set_primary_product_image(db: Session, product_image_id: int):
    db_product_image = get_product_image(db, product_image_id)
    if db_product_image is None:
        return None

    _unset_other_primary_images(
        db,
        db_product_image.product_id,
        exclude_image_id=db_product_image.id,
    )
    db_product_image.is_primary = True
    db.commit()
    db.refresh(db_product_image)
    return db_product_image


def _unset_other_primary_images(
    db: Session,
    product_id: int,
    exclude_image_id: int | None = None,
) -> None:
    query = db.query(models.ProductImage).filter(
        models.ProductImage.product_id == product_id,
        models.ProductImage.is_primary.is_(True),
    )
    if exclude_image_id is not None:
        query = query.filter(models.ProductImage.id != exclude_image_id)
    query.update({models.ProductImage.is_primary: False}, synchronize_session=False)
