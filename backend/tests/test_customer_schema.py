import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models, schemas
from backend.crud import (
    create_brand,
    create_customer,
    get_customer_by_email,
    get_customers,
    get_platform_settings,
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


def test_guest_customer_can_be_created_without_email(db_session):
    customer = create_customer(
        db_session,
        schemas.CustomerCreate(
            name="Guest Buyer",
            phone="6281234567890",
            customer_type="guest",
        ),
    )

    assert customer.email is None
    assert customer.phone == "6281234567890"
    assert customer.customer_type == "guest"
    assert get_customer_by_email(db_session, None, brand_id=customer.brand_id) is None


def test_registered_customer_can_have_email(db_session):
    customer = create_customer(
        db_session,
        schemas.CustomerCreate(
            name="Registered Buyer",
            email="registered@example.test",
            phone="628222333444",
            customer_type="registered",
        ),
    )

    assert customer.email == "registered@example.test"
    assert customer.customer_type == "registered"
    assert get_customer_by_email(db_session, "registered@example.test", brand_id=1).id == customer.id


def test_customer_brand_scope_isolated(db_session):
    get_platform_settings(db_session)
    other_brand = create_brand(
        db_session,
        schemas.BrandCreate(name="Second Brand", slug="second-brand"),
    )
    default_customer = create_customer(
        db_session,
        schemas.CustomerCreate(
            brand_id=1,
            name="Same Phone Default",
            phone="628999000111",
        ),
    )
    other_customer = create_customer(
        db_session,
        schemas.CustomerCreate(
            brand_id=other_brand.id,
            name="Same Phone Other",
            phone="628999000111",
        ),
    )

    default_customers = get_customers(db_session, brand_id=1)
    other_customers = get_customers(db_session, brand_id=other_brand.id)

    assert [customer.id for customer in default_customers] == [default_customer.id]
    assert [customer.id for customer in other_customers] == [other_customer.id]


def test_customer_type_validation():
    with pytest.raises(ValidationError):
        schemas.CustomerCreate(name="Invalid Type", customer_type="vip")


def test_password_hash_is_not_exposed_in_customer_schema(db_session):
    customer = models.Customer(
        name="Hidden Password",
        email="hidden@example.test",
        customer_type="registered",
        password_hash="secret-hash",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    payload = schemas.Customer.model_validate(customer).model_dump()

    assert "password_hash" not in payload
