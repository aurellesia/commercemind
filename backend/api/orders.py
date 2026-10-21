from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.Order, status_code=201)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id=order.customer_id, brand_id=order.brand_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        return crud.create_order(db=db, order=order)
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc
    except crud.ProductOrderingError as exc:
        raise _product_ordering_http_exception(exc) from exc


@router.get("/", response_model=List[schemas.Order])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    return crud.get_orders(db, skip=skip, limit=limit, brand_id=brand_id)


@router.get("/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, brand_id: int = 1, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id=order_id, brand_id=brand_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=schemas.Order)
def update_order(
    order_id: int,
    order: schemas.OrderUpdate,
    db: Session = Depends(get_db),
):
    try:
        updated_order = crud.update_order(db, order_id=order_id, order=order)
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order


@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int,
    status: schemas.OrderStatus,
    db: Session = Depends(get_db),
):
    try:
        updated_order = crud.update_order_status(db, order_id=order_id, status=status)
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order


@router.patch("/{order_id}/cancel", response_model=schemas.Order)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    try:
        cancelled_order = crud.cancel_order(db, order_id=order_id)
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc
    if cancelled_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return cancelled_order


@router.patch("/{order_id}/fulfill", response_model=schemas.Order)
def fulfill_order(order_id: int, db: Session = Depends(get_db)):
    try:
        fulfilled_order = crud.fulfill_order(db, order_id=order_id)
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc
    if fulfilled_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return fulfilled_order


@router.delete("/{order_id}", response_model=schemas.Order)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    deleted_order = crud.delete_order(db, order_id=order_id)
    if deleted_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return deleted_order


def _inventory_service_http_exception(exc: crud.InventoryServiceError) -> HTTPException:
    if isinstance(exc, crud.InventoryOrderNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, crud.InventoryProductNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=400, detail=str(exc))


def _product_ordering_http_exception(exc: crud.ProductOrderingError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))
