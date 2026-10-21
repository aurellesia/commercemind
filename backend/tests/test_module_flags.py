from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models, schemas
from backend.api.payments import create_payment as api_create_payment
from backend.api.products import read_product_catalog
from backend.crud import (
    create_order,
    get_platform_settings,
    receive_stock,
    update_module_settings,
    update_system_settings,
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


def test_public_catalog_disabled_rejects_public_catalog_endpoint(db_session):
    get_platform_settings(db_session)
    db_session.add(
        models.Product(
            brand_id=1,
            name="Flagged Catalog Product",
            slug="flagged-catalog-product",
            base_price=Decimal("10000"),
            status="active",
        )
    )
    db_session.commit()
    update_system_settings(
        db_session,
        schemas.SystemSettingsUpdate(public_catalog_enabled=False),
    )

    with pytest.raises(HTTPException) as exc:
        read_product_catalog(brand_id=1, db=db_session)

    admin_preview = read_product_catalog(
        brand_id=1,
        include_non_public=True,
        db=db_session,
    )

    assert exc.value.status_code == 403
    assert len(admin_preview) == 1


def test_payments_disabled_rejects_payment_endpoint(db_session):
    get_platform_settings(db_session)
    update_module_settings(
        db_session,
        schemas.ModuleSettingsUpdate(payments_enabled=False),
    )
    product = models.Product(
        brand_id=1,
        name="Payment Flag Product",
        slug="payment-flag-product",
        base_price=Decimal("10000"),
        status="active",
    )
    customer = models.Customer(
        brand_id=1,
        name="Aurel",
        email="payment-flag@example.test",
    )
    db_session.add_all([product, customer])
    db_session.commit()
    db_session.refresh(product)
    db_session.refresh(customer)
    receive_stock(db_session, product.id, 2, reason="test stock")
    order = create_order(
        db_session,
        schemas.OrderCreate(
            brand_id=1,
            customer_id=customer.id,
            items=[schemas.OrderItemCreate(product_id=product.id, quantity=1)],
        ),
    )

    with pytest.raises(HTTPException) as exc:
        api_create_payment(
            schemas.PaymentCreate(
                brand_id=1,
                order_id=order.id,
                status=schemas.PaymentStatus.pending,
                method=schemas.PaymentMethod.manual,
                amount=Decimal("10000"),
            ),
            db=db_session,
        )

    assert exc.value.status_code == 403
