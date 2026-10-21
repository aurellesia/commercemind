import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import schemas
from backend.api.customers import read_customer_addresses
from backend.crud import (
    create_brand,
    create_customer,
    create_customer_address,
    get_customer_addresses,
    get_platform_settings,
    update_customer_address,
)
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


def address_payload(**overrides):
    payload = {
        "recipient_name": "Aurel",
        "phone": "6281234567890",
        "address_line": "Jl. CommerceMind No. 1",
        "district": "Kebayoran Baru",
        "city": "Jakarta Selatan",
        "province": "DKI Jakarta",
        "postal_code": "12110",
        "notes": "Dekat lobby",
        "is_default": False,
    }
    payload.update(overrides)
    return schemas.CustomerAddressCreate(**payload)


def test_customer_address_can_be_created_for_brand_scoped_customer(db_session):
    customer = create_customer(
        db_session,
        schemas.CustomerCreate(name="Address Guest", phone="628111222333"),
    )

    address = create_customer_address(
        db_session,
        customer_id=customer.id,
        address=address_payload(is_default=True),
        brand_id=customer.brand_id,
    )

    assert address.customer_id == customer.id
    assert address.brand_id == customer.brand_id
    assert address.is_default is True
    assert address.city == "Jakarta Selatan"


def test_only_one_default_address_per_customer(db_session):
    customer = create_customer(
        db_session,
        schemas.CustomerCreate(name="Multi Address", phone="628111222334"),
    )
    first = create_customer_address(
        db_session,
        customer_id=customer.id,
        address=address_payload(recipient_name="First", is_default=True),
        brand_id=customer.brand_id,
    )
    second = create_customer_address(
        db_session,
        customer_id=customer.id,
        address=address_payload(recipient_name="Second", is_default=True),
        brand_id=customer.brand_id,
    )

    addresses = get_customer_addresses(db_session, customer_id=customer.id, brand_id=customer.brand_id)
    default_addresses = [address for address in addresses if address.is_default]

    assert len(default_addresses) == 1
    assert default_addresses[0].id == second.id
    assert db_session.get(type(first), first.id).is_default is False


def test_updating_default_address_clears_previous_default(db_session):
    customer = create_customer(
        db_session,
        schemas.CustomerCreate(name="Update Default", phone="628111222335"),
    )
    first = create_customer_address(
        db_session,
        customer_id=customer.id,
        address=address_payload(recipient_name="First", is_default=True),
        brand_id=customer.brand_id,
    )
    second = create_customer_address(
        db_session,
        customer_id=customer.id,
        address=address_payload(recipient_name="Second", is_default=False),
        brand_id=customer.brand_id,
    )

    update_customer_address(
        db_session,
        address_id=second.id,
        address=schemas.CustomerAddressUpdate(is_default=True),
        brand_id=customer.brand_id,
    )

    assert db_session.get(type(first), first.id).is_default is False
    assert db_session.get(type(second), second.id).is_default is True


def test_customer_addresses_are_isolated_by_brand(db_session):
    get_platform_settings(db_session)
    other_brand = create_brand(
        db_session,
        schemas.BrandCreate(name="Address Brand", slug="address-brand"),
    )
    default_customer = create_customer(
        db_session,
        schemas.CustomerCreate(brand_id=1, name="Default Customer", phone="628555000111"),
    )
    other_customer = create_customer(
        db_session,
        schemas.CustomerCreate(
            brand_id=other_brand.id,
            name="Other Customer",
            phone="628555000111",
        ),
    )
    default_address = create_customer_address(
        db_session,
        customer_id=default_customer.id,
        address=address_payload(recipient_name="Default"),
        brand_id=1,
    )
    other_address = create_customer_address(
        db_session,
        customer_id=other_customer.id,
        address=address_payload(recipient_name="Other"),
        brand_id=other_brand.id,
    )

    assert get_customer_addresses(db_session, default_customer.id, brand_id=1)[0].id == default_address.id
    assert get_customer_addresses(db_session, other_customer.id, brand_id=other_brand.id)[0].id == other_address.id

    with pytest.raises(HTTPException) as exc:
        read_customer_addresses(
            customer_id=other_customer.id,
            brand_id=1,
            db=db_session,
        )

    assert exc.value.status_code == 404


def test_customer_address_requires_checkout_fields():
    with pytest.raises(ValidationError):
        address_payload(address_line="")
