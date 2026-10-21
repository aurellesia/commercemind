from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db


router = APIRouter(prefix="/inventory-items", tags=["inventory_items"])


@router.post("/", response_model=schemas.InventoryItem, status_code=201)
def create_inventory_item(
    inventory_item: schemas.InventoryItemCreate,
    db: Session = Depends(get_db),
):
    product = crud.get_product(db, product_id=inventory_item.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_inventory_item = crud.get_inventory_item_by_product_id(
        db,
        product_id=inventory_item.product_id,
    )
    if existing_inventory_item is not None:
        raise HTTPException(
            status_code=400,
            detail="Inventory item already exists for product",
        )

    return crud.create_inventory_item(db=db, inventory_item=inventory_item)


@router.get("/", response_model=List[schemas.InventoryItem])
def read_inventory_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_inventory_items(db, skip=skip, limit=limit)


@router.get("/low-stock", response_model=List[schemas.InventoryItem])
def read_low_stock_inventory_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_low_stock_inventory_items(db, skip=skip, limit=limit)


@router.get(
    "/by-product/{product_id}/movements",
    response_model=List[schemas.InventoryMovementRead],
)
def read_inventory_movements_by_product(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return crud.get_inventory_movements_by_product_id(
        db,
        product_id=product_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/by-product/{product_id}/reservations/active",
    response_model=List[schemas.InventoryReservationRead],
)
def read_active_inventory_reservations_by_product(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return crud.get_active_inventory_reservations_by_product_id(
        db,
        product_id=product_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/by-order/{order_id}/reservations/active",
    response_model=List[schemas.InventoryReservationRead],
)
def read_active_inventory_reservations_by_order(
    order_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return crud.get_active_inventory_reservations_by_order_id(
        db,
        order_id=order_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{inventory_item_id}", response_model=schemas.InventoryItem)
def read_inventory_item(inventory_item_id: int, db: Session = Depends(get_db)):
    inventory_item = crud.get_inventory_item(
        db,
        inventory_item_id=inventory_item_id,
    )
    if inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory_item


@router.get("/by-product/{product_id}", response_model=schemas.InventoryItem)
def read_inventory_item_by_product(product_id: int, db: Session = Depends(get_db)):
    inventory_item = crud.get_inventory_item_by_product_id(db, product_id=product_id)
    if inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory_item


@router.post("/actions/receive", response_model=schemas.InventoryItem)
def receive_stock(
    command: schemas.ReceiveStockCommand,
    db: Session = Depends(get_db),
):
    try:
        return crud.receive_stock(
            db,
            product_id=command.product_id,
            quantity=command.quantity,
            reason=command.notes,
            reference_type=command.reference_type,
            reference_id=command.reference_id,
        )
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc


@router.post("/actions/adjust", response_model=schemas.InventoryItem)
def adjust_stock(
    command: schemas.AdjustStockCommand,
    db: Session = Depends(get_db),
):
    try:
        return crud.adjust_stock(
            db,
            product_id=command.product_id,
            delta=command.delta,
            reason=command.notes,
            reference_type=command.reference_type,
            reference_id=command.reference_id,
        )
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc


@router.post("/actions/reserve", response_model=schemas.InventoryReservationRead)
def reserve_stock(
    command: schemas.ReserveStockCommand,
    db: Session = Depends(get_db),
):
    try:
        return crud.reserve_stock(
            db,
            product_id=command.product_id,
            order_id=command.order_id,
            order_item_id=command.order_item_id,
            quantity=command.quantity,
            expires_at=command.expires_at,
            reason=command.notes,
        )
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc


@router.post("/actions/release-reservation", response_model=schemas.InventoryReservationRead)
def release_reservation(
    command: schemas.ReleaseReservationCommand,
    db: Session = Depends(get_db),
):
    try:
        return crud.release_reservation(
            db,
            reservation_id=command.reservation_id,
            reason=command.notes,
        )
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc


@router.post("/actions/commit-reservation", response_model=schemas.InventoryReservationRead)
def commit_reservation(
    command: schemas.CommitReservationCommand,
    db: Session = Depends(get_db),
):
    try:
        return crud.commit_reservation(
            db,
            reservation_id=command.reservation_id,
            reason=command.notes,
        )
    except crud.InventoryServiceError as exc:
        raise _inventory_service_http_exception(exc) from exc


@router.put("/{inventory_item_id}", response_model=schemas.InventoryItem)
def update_inventory_item(
    inventory_item_id: int,
    inventory_item: schemas.InventoryItemUpdate,
    db: Session = Depends(get_db),
):
    updated_inventory_item = crud.update_inventory_item(
        db,
        inventory_item_id=inventory_item_id,
        inventory_item=inventory_item,
    )
    if updated_inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return updated_inventory_item


@router.delete("/{inventory_item_id}", response_model=schemas.InventoryItem)
def delete_inventory_item(inventory_item_id: int, db: Session = Depends(get_db)):
    deleted_inventory_item = crud.delete_inventory_item(
        db,
        inventory_item_id=inventory_item_id,
    )
    if deleted_inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return deleted_inventory_item


def _inventory_service_http_exception(exc: crud.InventoryServiceError) -> HTTPException:
    if isinstance(exc, crud.InventoryProductNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, crud.InventoryOrderNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, crud.InventoryItemNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, crud.InventoryReservationNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=400, detail=str(exc))
