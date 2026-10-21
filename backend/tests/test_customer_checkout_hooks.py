import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import schemas
from backend.crud import (
    create_brand,
    get_customer_addresses,
    get_platform_settings,
    resolve_checkout_address,
    resolve_checkout_customer,
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


def customer_payload(name="Guest Buyer", phone="6281234567890", email=None):
    return schemas.CheckoutCustomerData(name=name, phone=phone, email=email)


def address_payload(**overrides):
    payload = {
        "recipient_name": "Guest Buyer",
        "phone": "6281234567890",
        "address_line": "Jl. Checkout No. 1",
        "district": "Cilandak",
        "city": "Jakarta Selatan",
        "province": "DKI Jakarta",
        "postal_code": "12430",
        "notes": "Dekat pos satpam",
        "is_default": False,
    }
    payload.update(overrides)
    return schemas.CustomerAddressCreate(**payload)


def test_resolve_checkout_customer_creates_guest_without_email(db_session):
    customer = resolve_checkout_customer(
        db_session,
        brand_id=1,
        customer_data=customer_payload(email=None),
    )

    assert customer.name == "Guest Buyer"
    assert customer.phone == "6281234567890"
    assert customer.email is None
    assert customer.customer_type == "guest"


def test_resolve_checkout_customer_reuses_phone_and_updates_more_complete_data(db_session):
    first = resolve_checkout_customer(
        db_session,
        brand_id=1,
        customer_data=customer_payload(name="Aurel", phone="628111222333"),
    )
    second = resolve_checkout_customer(
        db_session,
        brand_id=1,
        customer_data=customer_payload(
            name="Aurel Putri",
            phone="628111222333",
            email="aurel@example.test",
        ),
    )

    assert second.id == first.id
    assert second.name == "Aurel Putri"
    assert second.email == "aurel@example.test"


def test_resolve_checkout_customer_does_not_attach_email_owned_by_same_brand(db_session):
    resolve_checkout_customer(
        db_session,
        brand_id=1,
        customer_data=customer_payload(
            name="Email Owner",
            phone="62810101010",
            email="taken@example.test",
        ),
    )
    checkout_customer = resolve_checkout_customer(
        db_session,
        brand_id=1,
        customer_data=customer_payload(name="Checkout Guest", phone="62820202020"),
    )

    resolved_customer = resolve_checkout_customer(
        db_session,
        brand_id=1,
        customer_data=customer_payload(
            name="Checkout Guest Full",
            phone="62820202020",
            email="taken@example.test",
        ),
    )

    assert resolved_customer.id == checkout_customer.id
    assert resolved_customer.email is None


def test_resolve_checkout_customer_does_not_mix_brands(db_session):
    get_platform_settings(db_session)
    other_brand = create_brand(
        db_session,
        schemas.BrandCreate(name="Checkout Other Brand", slug="checkout-other-brand"),
    )

    default_customer = resolve_checkout_customer(
        db_session,
        brand_id=1,
        customer_data=customer_payload(name="Default Buyer", phone="628999888777"),
    )
    other_customer = resolve_checkout_customer(
        db_session,
        brand_id=other_brand.id,
        customer_data=customer_payload(name="Other Buyer", phone="628999888777"),
    )

    assert default_customer.id != other_customer.id
    assert default_customer.brand_id == 1
    assert other_customer.brand_id == other_brand.id


def test_resolve_checkout_address_creates_default_first_address(db_session):
    customer = resolve_checkout_customer(
        db_session,
        brand_id=1,
        customer_data=customer_payload(),
    )

    address = resolve_checkout_address(
        db_session,
        brand_id=1,
        customer_id=customer.id,
        address=address_payload(),
    )

    assert address.customer_id == customer.id
    assert address.is_default is True
    assert address.city == "Jakarta Selatan"


def test_resolve_checkout_address_reuses_matching_address(db_session):
    customer = resolve_checkout_customer(
        db_session,
        brand_id=1,
        customer_data=customer_payload(),
    )
    first = resolve_checkout_address(
        db_session,
        brand_id=1,
        customer_id=customer.id,
        address=address_payload(),
    )
    second = resolve_checkout_address(
        db_session,
        brand_id=1,
        customer_id=customer.id,
        address=address_payload(is_default=True),
    )

    addresses = get_customer_addresses(db_session, customer_id=customer.id, brand_id=1)

    assert second.id == first.id
    assert len(addresses) == 1
    assert addresses[0].is_default is True


def test_resolve_checkout_address_rejects_customer_from_other_brand(db_session):
    get_platform_settings(db_session)
    other_brand = create_brand(
        db_session,
        schemas.BrandCreate(name="Address Other Brand", slug="address-other-brand"),
    )
    other_customer = resolve_checkout_customer(
        db_session,
        brand_id=other_brand.id,
        customer_data=customer_payload(phone="628000111222"),
    )

    address = resolve_checkout_address(
        db_session,
        brand_id=1,
        customer_id=other_customer.id,
        address=address_payload(),
    )

    assert address is None
