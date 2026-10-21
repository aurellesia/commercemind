from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/products", response_model=schemas.ProductReportingDashboard)
def read_product_reporting_dashboard(
    limit: int = 10,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    return crud.get_product_reporting_dashboard(db, limit=limit, brand_id=brand_id)


@router.get("/products/summary", response_model=schemas.ProductReportingSummary)
def read_product_reporting_summary(brand_id: int = 1, db: Session = Depends(get_db)):
    return crud.get_product_reporting_summary(db, brand_id=brand_id)


@router.get("/products/revenue", response_model=List[schemas.ProductRevenueReport])
def read_gross_revenue_per_product(
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    return crud.get_gross_revenue_per_product(db, skip=skip, limit=limit, brand_id=brand_id)


@router.get("/products/slow-moving", response_model=List[schemas.ProductStockReport])
def read_slow_moving_products(
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    return crud.get_slow_moving_products(db, skip=skip, limit=limit, brand_id=brand_id)


@router.get("/products/low-stock-active", response_model=List[schemas.ProductStockReport])
def read_low_stock_active_products(
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    return crud.get_low_stock_active_products(db, skip=skip, limit=limit, brand_id=brand_id)


@router.get(
    "/products/discontinued-with-stock",
    response_model=List[schemas.ProductStockReport],
)
def read_discontinued_products_with_remaining_stock(
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    return crud.get_discontinued_products_with_remaining_stock(
        db,
        skip=skip,
        limit=limit,
        brand_id=brand_id,
    )
