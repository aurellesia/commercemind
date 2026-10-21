from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models, schemas
from backend.api.customers import read_customer_detail, read_customer_summaries, read_customers, update_customer
from backend.crud import create_brand, create_customer, create_customer_address, get_platform_settings
from backend.database import Base


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


def create_order(db, customer_id: int, brand_id: int, total: str = "10000", status: str = "paid"):
    order = models.Order(
        brand_id=brand_id,
        customer_id=customer_id,
        status=status,
        total_amount=Decimal(total),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def test_customer_list_search_and_type_filter_are_brand_scoped(db_session):
    get_platform_settings(db_session)
    other_brand = create_brand(
        db_session,
        schemas.BrandCreate(name="Other Customer Brand", slug="other-customer-brand"),
    )
    create_customer(
        db_session,
        schemas.CustomerCreate(
            brand_id=1,
            name="Aurel Guest",
            phone="628111",
            customer_type="guest",
        ),
    )
    create_customer(
        db_session,
        schemas.CustomerCreate(
            brand_id=1,
            name="Registered Buyer",
            email="registered-buyer@example.test",
            phone="628222",
            customer_type="registered",
        ),
    )
    create_customer(
        db_session,
        schemas.CustomerCreate(
            brand_id=other_brand.id,
            name="Aurel Other",
            phone="628111",
            customer_type="guest",
        ),
    )

    guests = read_customers(
        brand_id=1,
        search="aurel",
        customer_type="guest",
        db=db_session,
    )
    registered = read_customers(
        brand_id=1,
        search="registered-buyer@example.test",
        customer_type="registered",
        db=db_session,
    )

    assert [customer.name for customer in guests] == ["Aurel Guest"]
    assert [customer.name for customer in registered] == ["Registered Buyer"]


def test_customer_summary_includes_order_metrics(db_session):
    customer = create_customer(
        db_session,
        schemas.CustomerCreate(name="Metric Buyer", phone="628333"),
    )
    create_order(db_session, customer_id=customer.id, brand_id=customer.brand_id, total="15000")
    create_order(db_session, customer_id=customer.id, brand_id=customer.brand_id, total="25000")

    summaries = read_customer_summaries(brand_id=customer.brand_id, db=db_session)

    assert len(summaries) == 1
    assert summaries[0].id == customer.id
    assert summaries[0].total_orders == 2
    assert summaries[0].total_spent == Decimal("40000.00")
    assert summaries[0].last_order_date is not None


def test_customer_detail_includes_addresses_and_recent_orders(db_session):
    customer = create_customer(
        db_session,
        schemas.CustomerCreate(name="Detail Buyer", phone="628444"),
    )
    create_customer_address(
        db_session,
        customer_id=customer.id,
        brand_id=customer.brand_id,
        address=schemas.CustomerAddressCreate(
            recipient_name="Detail Buyer",
            phone="628444",
            address_line="Jl. Detail No. 1",
            district="Setiabudi",
            city="Jakarta Selatan",
            province="DKI Jakarta",
            postal_code="12910",
            is_default=True,
        ),
    )
    order = create_order(
        db_session,
        customer_id=customer.id,
        brand_id=customer.brand_id,
        total="99000",
        status="awaiting_payment",
    )

    detail = read_customer_detail(customer.id, brand_id=customer.brand_id, db=db_session)

    assert detail.id == customer.id
    assert detail.addresses[0].is_default is True
    assert detail.recent_orders[0].id == order.id
    assert detail.recent_orders[0].status == "awaiting_payment"
    assert "password_hash" not in detail.model_dump()


def test_customer_detail_rejects_other_brand(db_session):
    get_platform_settings(db_session)
    other_brand = create_brand(
        db_session,
        schemas.BrandCreate(name="Detail Other Brand", slug="detail-other-brand"),
    )
    customer = create_customer(
        db_session,
        schemas.CustomerCreate(
            brand_id=other_brand.id,
            name="Other Detail Buyer",
            phone="628555",
        ),
    )

    with pytest.raises(HTTPException) as exc:
        read_customer_detail(customer.id, brand_id=1, db=db_session)

    assert exc.value.status_code == 404


def test_customer_update_is_brand_scoped(db_session):
    get_platform_settings(db_session)
    other_brand = create_brand(
        db_session,
        schemas.BrandCreate(name="Update Other Brand", slug="update-other-brand"),
    )
    customer = create_customer(
        db_session,
        schemas.CustomerCreate(
            brand_id=other_brand.id,
            name="Other Update Buyer",
            phone="628666",
        ),
    )

    with pytest.raises(HTTPException) as exc:
        update_customer(
            customer.id,
            schemas.CustomerUpdate(name="Wrong Brand Update"),
            brand_id=1,
            db=db_session,
        )

    assert exc.value.status_code == 404
