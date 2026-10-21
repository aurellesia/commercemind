from __future__ import annotations

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .. import models, schemas


def get_customer(db: Session, customer_id: int, brand_id: int | None = None):
    query = db.query(models.Customer).filter(models.Customer.id == customer_id)
    if brand_id is not None:
        query = query.filter(models.Customer.brand_id == brand_id)
    return query.first()


def get_customer_by_email(db: Session, email: str | None, brand_id: int = 1):
    if email is None:
        return None
    return (
        db.query(models.Customer)
        .filter(models.Customer.brand_id == brand_id, models.Customer.email == email)
        .first()
    )


def get_customer_by_phone(db: Session, phone: str | None, brand_id: int = 1):
    if phone is None:
        return None
    return (
        db.query(models.Customer)
        .filter(models.Customer.brand_id == brand_id, models.Customer.phone == phone)
        .first()
    )


def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    search: str | None = None,
    customer_type: str | None = None,
):
    query = _customer_base_query(db, brand_id=brand_id, search=search, customer_type=customer_type)
    return query.order_by(models.Customer.id.asc()).offset(skip).limit(limit).all()


def get_customer_summaries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    search: str | None = None,
    customer_type: str | None = None,
):
    customer_query = _customer_base_query(
        db,
        brand_id=brand_id,
        search=search,
        customer_type=customer_type,
    ).subquery()
    rows = (
        db.query(
            models.Customer,
            func.count(models.Order.id).label("total_orders"),
            func.max(models.Order.created_at).label("last_order_date"),
            func.coalesce(func.sum(models.Order.total_amount), 0).label("total_spent"),
        )
        .join(customer_query, models.Customer.id == customer_query.c.id)
        .outerjoin(
            models.Order,
            (models.Order.customer_id == models.Customer.id)
            & (models.Order.brand_id == models.Customer.brand_id),
        )
        .group_by(models.Customer.id)
        .order_by(models.Customer.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        schemas.CustomerSummary(
            **schemas.Customer.model_validate(customer).model_dump(),
            total_orders=total_orders,
            last_order_date=last_order_date,
            total_spent=total_spent,
        )
        for customer, total_orders, last_order_date, total_spent in rows
    ]


def get_customer_detail(
    db: Session,
    customer_id: int,
    brand_id: int = 1,
    recent_order_limit: int = 10,
):
    customer = get_customer(db, customer_id=customer_id, brand_id=brand_id)
    if customer is None:
        return None

    addresses = get_customer_addresses(db, customer_id=customer_id, brand_id=brand_id)
    recent_orders = (
        db.query(models.Order)
        .filter(models.Order.brand_id == brand_id, models.Order.customer_id == customer_id)
        .order_by(models.Order.created_at.desc(), models.Order.id.desc())
        .limit(recent_order_limit)
        .all()
    )
    return schemas.CustomerDetail(
        **schemas.Customer.model_validate(customer).model_dump(),
        addresses=[schemas.CustomerAddress.model_validate(address) for address in addresses],
        recent_orders=[
            schemas.CustomerOrderSummary(
                id=order.id,
                status=order.status,
                total_amount=order.total_amount,
                created_at=order.created_at,
            )
            for order in recent_orders
        ],
    )


def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def resolve_checkout_customer(
    db: Session,
    brand_id: int,
    customer_data: schemas.CheckoutCustomerData,
):
    phone = _clean_required(customer_data.phone)
    name = _clean_required(customer_data.name)
    email = _clean_optional(customer_data.email)

    db_customer = get_customer_by_phone(db, phone=phone, brand_id=brand_id)
    if db_customer is None:
        return create_customer(
            db,
            schemas.CustomerCreate(
                brand_id=brand_id,
                name=name,
                phone=phone,
                email=email,
                customer_type="guest",
            ),
        )

    changed = False
    if _is_more_complete_name(name, db_customer.name):
        db_customer.name = name
        changed = True
    if db_customer.email is None and email is not None and _email_available_for_customer(
        db,
        brand_id=brand_id,
        email=email,
        customer_id=db_customer.id,
    ):
        db_customer.email = email
        changed = True
    if changed:
        db.commit()
        db.refresh(db_customer)
    return db_customer


def resolve_checkout_address(
    db: Session,
    brand_id: int,
    customer_id: int,
    address: schemas.CustomerAddressCreate,
):
    db_customer = get_customer(db, customer_id=customer_id, brand_id=brand_id)
    if db_customer is None:
        return None

    address_data = address.model_dump()
    for key, value in address_data.items():
        if isinstance(value, str):
            address_data[key] = value.strip()

    existing_address = _find_matching_customer_address(
        db,
        brand_id=brand_id,
        customer_id=customer_id,
        address_data=address_data,
    )
    if existing_address is not None:
        if address_data.get("is_default") and not existing_address.is_default:
            _clear_default_customer_addresses(
                db,
                customer_id=customer_id,
                brand_id=brand_id,
                exclude_address_id=existing_address.id,
            )
            existing_address.is_default = True
            db.commit()
            db.refresh(existing_address)
        return existing_address

    has_addresses = (
        db.query(models.CustomerAddress)
        .filter(
            models.CustomerAddress.brand_id == brand_id,
            models.CustomerAddress.customer_id == customer_id,
        )
        .first()
        is not None
    )
    address_data["is_default"] = bool(address_data.get("is_default") or not has_addresses)
    return create_customer_address(
        db,
        customer_id=customer_id,
        brand_id=brand_id,
        address=schemas.CustomerAddressCreate(**address_data),
    )


def _customer_base_query(
    db: Session,
    brand_id: int = 1,
    search: str | None = None,
    customer_type: str | None = None,
):
    query = db.query(models.Customer).filter(models.Customer.brand_id == brand_id)
    if customer_type is not None:
        query = query.filter(models.Customer.customer_type == customer_type)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Customer.name.ilike(pattern),
                models.Customer.phone.ilike(pattern),
                models.Customer.email.ilike(pattern),
            )
        )
    return query


def _clean_required(value: str) -> str:
    return value.strip()


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _is_more_complete_name(new_name: str, existing_name: str) -> bool:
    return len(new_name.split()) > len((existing_name or "").split()) or len(new_name) > len(
        existing_name or ""
    )


def _email_available_for_customer(
    db: Session,
    brand_id: int,
    email: str,
    customer_id: int,
) -> bool:
    existing_owner = get_customer_by_email(db, email=email, brand_id=brand_id)
    return existing_owner is None or existing_owner.id == customer_id


def _find_matching_customer_address(
    db: Session,
    brand_id: int,
    customer_id: int,
    address_data: dict,
):
    return (
        db.query(models.CustomerAddress)
        .filter(
            models.CustomerAddress.brand_id == brand_id,
            models.CustomerAddress.customer_id == customer_id,
            models.CustomerAddress.recipient_name == address_data["recipient_name"],
            models.CustomerAddress.phone == address_data["phone"],
            models.CustomerAddress.address_line == address_data["address_line"],
            models.CustomerAddress.district == address_data["district"],
            models.CustomerAddress.city == address_data["city"],
            models.CustomerAddress.province == address_data["province"],
            models.CustomerAddress.postal_code == address_data["postal_code"],
        )
        .first()
    )


def update_customer(
    db: Session,
    customer_id: int,
    customer: schemas.CustomerUpdate,
    brand_id: int | None = None,
):
    brand_id = brand_id if brand_id is not None else customer.brand_id
    db_customer = get_customer(db, customer_id, brand_id=brand_id)
    if db_customer is None:
        return None

    update_data = customer.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int, brand_id: int | None = None):
    db_customer = get_customer(db, customer_id, brand_id=brand_id)
    if db_customer is None:
        return None

    db.delete(db_customer)
    db.commit()
    return db_customer


def get_customer_address(db: Session, address_id: int, brand_id: int | None = None):
    query = db.query(models.CustomerAddress).filter(models.CustomerAddress.id == address_id)
    if brand_id is not None:
        query = query.filter(models.CustomerAddress.brand_id == brand_id)
    return query.first()


def get_customer_addresses(
    db: Session,
    customer_id: int,
    brand_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(models.CustomerAddress).filter(models.CustomerAddress.customer_id == customer_id)
    if brand_id is not None:
        query = query.filter(models.CustomerAddress.brand_id == brand_id)
    return query.order_by(models.CustomerAddress.is_default.desc(), models.CustomerAddress.id.asc()).offset(skip).limit(limit).all()


def create_customer_address(
    db: Session,
    customer_id: int,
    address: schemas.CustomerAddressCreate,
    brand_id: int = 1,
):
    db_customer = get_customer(db, customer_id=customer_id, brand_id=brand_id)
    if db_customer is None:
        return None

    address_data = address.model_dump()
    if address_data.get("is_default"):
        _clear_default_customer_addresses(db, customer_id=customer_id, brand_id=brand_id)
    db_address = models.CustomerAddress(
        **address_data,
        brand_id=brand_id,
        customer_id=customer_id,
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def update_customer_address(
    db: Session,
    address_id: int,
    address: schemas.CustomerAddressUpdate,
    brand_id: int | None = None,
):
    db_address = get_customer_address(db, address_id=address_id, brand_id=brand_id)
    if db_address is None:
        return None

    update_data = address.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_address, field, value)
    if update_data.get("is_default") is True:
        _clear_default_customer_addresses(
            db,
            customer_id=db_address.customer_id,
            brand_id=db_address.brand_id,
            exclude_address_id=db_address.id,
        )
    db.commit()
    db.refresh(db_address)
    return db_address


def delete_customer_address(db: Session, address_id: int, brand_id: int | None = None):
    db_address = get_customer_address(db, address_id=address_id, brand_id=brand_id)
    if db_address is None:
        return None

    db.delete(db_address)
    db.commit()
    return db_address


def _clear_default_customer_addresses(
    db: Session,
    customer_id: int,
    brand_id: int,
    exclude_address_id: int | None = None,
):
    query = db.query(models.CustomerAddress).filter(
        models.CustomerAddress.brand_id == brand_id,
        models.CustomerAddress.customer_id == customer_id,
    )
    if exclude_address_id is not None:
        query = query.filter(models.CustomerAddress.id != exclude_address_id)
    query.update({models.CustomerAddress.is_default: False}, synchronize_session=False)
