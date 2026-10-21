from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models, schemas
from backend.crud import (
    create_order,
    fulfill_order,
    get_discontinued_products_with_remaining_stock,
    get_gross_revenue_per_product,
    get_low_stock_active_products,
    get_product_reporting_summary,
    get_slow_moving_products,
    receive_stock,
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


def create_product(db, name, status="active", base_price="10000", cost_price="4000"):
    product = models.Product(
        name=name,
        base_price=Decimal(base_price),
        cost_price=Decimal(cost_price),
        status=status,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def create_customer(db):
    customer = models.Customer(name="Aurel", email="aurel-report@example.com")
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def order_payload(product_id, customer_id, quantity):
    return schemas.OrderCreate(
        customer_id=customer_id,
        status=schemas.OrderStatus.pending,
        items=[schemas.OrderItemCreate(product_id=product_id, quantity=quantity)],
    )


def test_product_revenue_and_margin_reports_use_snapshots(db_session):
    customer = create_customer(db_session)
    product = create_product(db_session, "Margin Serum", base_price="12000", cost_price="5000")
    receive_stock(db_session, product.id, 10, reason="initial stock")
    order = create_order(db_session, order_payload(product.id, customer.id, quantity=3))
    fulfill_order(db_session, order.id)

    revenue = get_gross_revenue_per_product(db_session)
    summary = get_product_reporting_summary(db_session)

    assert len(revenue) == 1
    assert revenue[0].product_id == product.id
    assert revenue[0].quantity_sold == 3
    assert revenue[0].gross_revenue == Decimal("36000")
    assert revenue[0].estimated_cost == Decimal("15000")
    assert revenue[0].estimated_gross_margin == Decimal("21000")
    assert summary.gross_revenue == Decimal("36000")
    assert summary.estimated_gross_margin == Decimal("21000")


def test_stock_reports_find_low_stock_slow_moving_and_discontinued(db_session):
    fast = create_product(db_session, "Fast Product", base_price="10000", cost_price="3000")
    slow = create_product(db_session, "Slow Product", base_price="10000", cost_price="3000")
    low = create_product(db_session, "Low Product", base_price="10000", cost_price="3000")
    discontinued = create_product(
        db_session,
        "Discontinued Product",
        status="discontinued",
        base_price="10000",
        cost_price="3000",
    )
    customer = create_customer(db_session)

    receive_stock(db_session, fast.id, 10, reason="initial stock")
    receive_stock(db_session, slow.id, 8, reason="initial stock")
    receive_stock(db_session, low.id, 2, reason="initial stock")
    receive_stock(db_session, discontinued.id, 4, reason="remaining stock")
    low_inventory = db_session.query(models.InventoryItem).filter_by(product_id=low.id).one()
    low_inventory.low_stock_threshold = 2
    db_session.commit()

    fulfill_order(db_session, create_order(db_session, order_payload(fast.id, customer.id, quantity=5)).id)

    low_stock = get_low_stock_active_products(db_session)
    discontinued_stock = get_discontinued_products_with_remaining_stock(db_session)
    slow_moving = get_slow_moving_products(db_session, limit=2)

    assert [item.product_id for item in low_stock] == [low.id]
    assert [item.product_id for item in discontinued_stock] == [discontinued.id]
    assert slow.id in [item.product_id for item in slow_moving]
