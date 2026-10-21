from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from .. import models, schemas
from .inventory_service import release_stock_for_order


def get_payment(db: Session, payment_id: int, brand_id: int | None = None):
    query = db.query(models.Payment).filter(models.Payment.id == payment_id)
    if brand_id is not None:
        query = query.filter(models.Payment.brand_id == brand_id)
    return query.first()


def get_payment_by_order_id(db: Session, order_id: int, brand_id: int | None = None):
    query = db.query(models.Payment).filter(models.Payment.order_id == order_id)
    if brand_id is not None:
        query = query.filter(models.Payment.brand_id == brand_id)
    return query.first()


def get_payments(db: Session, skip: int = 0, limit: int = 100, brand_id: int = 1):
    return (
        db.query(models.Payment)
        .filter(models.Payment.brand_id == brand_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_payment(db: Session, payment: schemas.PaymentCreate):
    try:
        payment_data = payment.model_dump()
        order = db.query(models.Order).filter(models.Order.id == payment.order_id).first()
        if order is not None:
            payment_data["brand_id"] = order.brand_id
        db_payment = models.Payment(**payment_data)
        db.add(db_payment)
        db.flush()
        _apply_payment_lifecycle(db, db_payment)

        db.commit()
        db.refresh(db_payment)
        return db_payment
    except Exception:
        db.rollback()
        raise


def update_payment(db: Session, payment_id: int, payment: schemas.PaymentUpdate):
    try:
        db_payment = get_payment(db, payment_id)
        if db_payment is None:
            return None

        update_data = payment.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_payment, field, value)

        _apply_payment_lifecycle(db, db_payment)

        db.commit()
        db.refresh(db_payment)
        return db_payment
    except Exception:
        db.rollback()
        raise


def update_payment_status(
    db: Session,
    payment_id: int,
    status: schemas.PaymentStatus,
):
    try:
        db_payment = get_payment(db, payment_id)
        if db_payment is None:
            return None

        db_payment.status = status
        _apply_payment_lifecycle(db, db_payment)

        db.commit()
        db.refresh(db_payment)
        return db_payment
    except Exception:
        db.rollback()
        raise


def delete_payment(db: Session, payment_id: int):
    db_payment = get_payment(db, payment_id)
    if db_payment is None:
        return None

    db.delete(db_payment)
    db.commit()
    return db_payment


def _apply_payment_lifecycle(db: Session, payment: models.Payment) -> None:
    order = db.query(models.Order).filter(models.Order.id == payment.order_id).first()
    if order is None:
        return

    if payment.status == schemas.PaymentStatus.paid:
        if payment.paid_at is None:
            payment.paid_at = datetime.utcnow()
        if order.status not in {
            schemas.OrderStatus.cancelled,
            schemas.OrderStatus.fulfilled,
            schemas.OrderStatus.completed,
        }:
            order.status = schemas.OrderStatus.paid
        return

    if payment.status == schemas.PaymentStatus.failed:
        release_stock_for_order(
            db,
            order_id=payment.order_id,
            reason="payment failed",
            commit=False,
        )
        if order.status != schemas.OrderStatus.completed:
            order.status = schemas.OrderStatus.cancelled
        return

    if payment.status == schemas.PaymentStatus.refunded:
        return
