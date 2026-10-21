from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db


router = APIRouter(tags=["order_items"])


@router.post(
    "/orders/{order_id}/items",
    response_model=schemas.OrderItem,
    status_code=201,
)
def create_order_item(
    order_id: int,
    order_item: schemas.OrderItemCreate,
    db: Session = Depends(get_db),
):
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    product = crud.get_product(db, product_id=order_item.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        return crud.create_order_item(db=db, order_id=order_id, order_item=order_item)
    except crud.InventoryServiceError as exc:
        if isinstance(exc, crud.InventoryProductNotFoundError):
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except crud.ProductOrderingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/order-items", response_model=List[schemas.OrderItem])
def read_order_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_order_items(db, skip=skip, limit=limit)


@router.get("/orders/{order_id}/items", response_model=List[schemas.OrderItem])
def read_order_items_by_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return crud.get_order_items_by_order_id(db, order_id=order_id)


@router.get("/order-items/{order_item_id}", response_model=schemas.OrderItem)
def read_order_item(order_item_id: int, db: Session = Depends(get_db)):
    order_item = crud.get_order_item(db, order_item_id=order_item_id)
    if order_item is None:
        raise HTTPException(status_code=404, detail="Order item not found")
    return order_item


@router.put("/order-items/{order_item_id}", response_model=schemas.OrderItem)
def update_order_item(
    order_item_id: int,
    order_item: schemas.OrderItemUpdate,
    db: Session = Depends(get_db),
):
    updated_order_item = crud.update_order_item(
        db,
        order_item_id=order_item_id,
        order_item=order_item,
    )
    if updated_order_item is None:
        raise HTTPException(status_code=404, detail="Order item not found")
    return updated_order_item


@router.delete("/order-items/{order_item_id}", response_model=schemas.OrderItem)
def delete_order_item(order_item_id: int, db: Session = Depends(get_db)):
    deleted_order_item = crud.delete_order_item(db, order_item_id=order_item_id)
    if deleted_order_item is None:
        raise HTTPException(status_code=404, detail="Order item not found")
    return deleted_order_item
