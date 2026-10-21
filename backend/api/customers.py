from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db


router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=schemas.Customer, status_code=201)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    if customer.email is not None:
        existing_customer = crud.get_customer_by_email(
            db,
            email=customer.email,
            brand_id=customer.brand_id,
        )
        if existing_customer is not None:
            raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_customer(db=db, customer=customer)


@router.get("/", response_model=List[schemas.Customer])
def read_customers(
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    search: Optional[str] = None,
    customer_type: Optional[Literal["guest", "registered"]] = None,
    db: Session = Depends(get_db),
):
    return crud.get_customers(
        db,
        skip=skip,
        limit=limit,
        brand_id=brand_id,
        search=search,
        customer_type=customer_type,
    )


@router.get("/summary", response_model=List[schemas.CustomerSummary])
def read_customer_summaries(
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    search: Optional[str] = None,
    customer_type: Optional[Literal["guest", "registered"]] = None,
    db: Session = Depends(get_db),
):
    return crud.get_customer_summaries(
        db,
        skip=skip,
        limit=limit,
        brand_id=brand_id,
        search=search,
        customer_type=customer_type,
    )


@router.get("/{customer_id}/detail", response_model=schemas.CustomerDetail)
def read_customer_detail(
    customer_id: int,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    detail = crud.get_customer_detail(db, customer_id=customer_id, brand_id=brand_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return detail


@router.get("/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, brand_id: int = 1, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id=customer_id, brand_id=brand_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=schemas.Customer)
def update_customer(
    customer_id: int,
    customer: schemas.CustomerUpdate,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    if customer.email is not None:
        existing_customer = crud.get_customer_by_email(
            db,
            email=customer.email,
            brand_id=brand_id,
        )
        if existing_customer is not None and existing_customer.id != customer_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    updated_customer = crud.update_customer(
        db,
        customer_id=customer_id,
        customer=customer,
        brand_id=brand_id,
    )
    if updated_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer


@router.delete("/{customer_id}", response_model=schemas.Customer)
def delete_customer(customer_id: int, brand_id: int = 1, db: Session = Depends(get_db)):
    deleted_customer = crud.delete_customer(db, customer_id=customer_id, brand_id=brand_id)
    if deleted_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return deleted_customer


@router.get("/{customer_id}/addresses", response_model=List[schemas.CustomerAddress])
def read_customer_addresses(
    customer_id: int,
    brand_id: int = 1,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    customer = crud.get_customer(db, customer_id=customer_id, brand_id=brand_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.get_customer_addresses(
        db,
        customer_id=customer_id,
        brand_id=brand_id,
        skip=skip,
        limit=limit,
    )


@router.post("/{customer_id}/addresses", response_model=schemas.CustomerAddress, status_code=201)
def create_customer_address(
    customer_id: int,
    address: schemas.CustomerAddressCreate,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    db_address = crud.create_customer_address(
        db,
        customer_id=customer_id,
        address=address,
        brand_id=brand_id,
    )
    if db_address is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_address


@router.put("/addresses/{address_id}", response_model=schemas.CustomerAddress)
def update_customer_address(
    address_id: int,
    address: schemas.CustomerAddressUpdate,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    updated_address = crud.update_customer_address(
        db,
        address_id=address_id,
        address=address,
        brand_id=brand_id,
    )
    if updated_address is None:
        raise HTTPException(status_code=404, detail="Customer address not found")
    return updated_address


@router.delete("/addresses/{address_id}", response_model=schemas.CustomerAddress)
def delete_customer_address(
    address_id: int,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    deleted_address = crud.delete_customer_address(
        db,
        address_id=address_id,
        brand_id=brand_id,
    )
    if deleted_address is None:
        raise HTTPException(status_code=404, detail="Customer address not found")
    return deleted_address

