from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=schemas.Payment, status_code=201)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id=payment.order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    _require_payments_enabled(db, brand_id=order.brand_id)

    existing_payment = crud.get_payment_by_order_id(db, order_id=payment.order_id)
    if existing_payment is not None:
        raise HTTPException(status_code=400, detail="Payment already exists for order")

    try:
        return crud.create_payment(db=db, payment=payment)
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc


@router.get("/", response_model=List[schemas.Payment])
def read_payments(
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    _require_payments_enabled(db, brand_id=brand_id)
    return crud.get_payments(db, skip=skip, limit=limit, brand_id=brand_id)


@router.get("/{payment_id}", response_model=schemas.Payment)
def read_payment(payment_id: int, brand_id: int = 1, db: Session = Depends(get_db)):
    _require_payments_enabled(db, brand_id=brand_id)
    payment = crud.get_payment(db, payment_id=payment_id, brand_id=brand_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("/by-order/{order_id}", response_model=schemas.Payment)
def read_payment_by_order(order_id: int, brand_id: int = 1, db: Session = Depends(get_db)):
    _require_payments_enabled(db, brand_id=brand_id)
    payment = crud.get_payment_by_order_id(db, order_id=order_id, brand_id=brand_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.put("/{payment_id}", response_model=schemas.Payment)
def update_payment(
    payment_id: int,
    payment: schemas.PaymentUpdate,
    db: Session = Depends(get_db),
):
    current_payment = crud.get_payment(db, payment_id=payment_id)
    if current_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    _require_payments_enabled(db, brand_id=current_payment.brand_id)
    try:
        updated_payment = crud.update_payment(
            db,
            payment_id=payment_id,
            payment=payment,
        )
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc
    if updated_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return updated_payment


@router.patch("/{payment_id}/status", response_model=schemas.Payment)
def update_payment_status(
    payment_id: int,
    status: schemas.PaymentStatus,
    db: Session = Depends(get_db),
):
    current_payment = crud.get_payment(db, payment_id=payment_id)
    if current_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    _require_payments_enabled(db, brand_id=current_payment.brand_id)
    try:
        updated_payment = crud.update_payment_status(
            db,
            payment_id=payment_id,
            status=status,
        )
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc
    if updated_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return updated_payment


@router.delete("/{payment_id}", response_model=schemas.Payment)
def delete_payment(payment_id: int, brand_id: int = 1, db: Session = Depends(get_db)):
    _require_payments_enabled(db, brand_id=brand_id)
    deleted_payment = crud.delete_payment(db, payment_id=payment_id)
    if deleted_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return deleted_payment


def _inventory_service_http_exception(exc: crud.InventoryServiceError) -> HTTPException:
    if isinstance(exc, crud.InventoryOrderNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, crud.InventoryProductNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=400, detail=str(exc))


def _require_payments_enabled(db: Session, brand_id: int) -> None:
    settings = crud.get_platform_settings(db, brand_id=brand_id)
    if settings is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    if not settings.modules.payments_enabled:
        raise HTTPException(status_code=403, detail="Payments module is disabled")
