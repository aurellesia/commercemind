from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models, schemas
from backend.crud import (
    InsufficientStockError,
    ProductNotOrderableError,
    adjust_stock,
    cancel_order,
    create_order,
    create_payment,
    fulfill_order,
    receive_stock,
    update_payment_status,
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


@pytest.fixture()
def product_and_customer(db_session):
    product = models.Product(
        name="Lifecycle Product",
        base_price=Decimal("10000"),
        status="active",
    )
    customer = models.Customer(
        name="Aurel",
        email="aurel@example.com",
    )
    db_session.add_all([product, customer])
    db_session.commit()
    db_session.refresh(product)
    db_session.refresh(customer)
    return product, customer


def make_order_payload(product_id: int, customer_id: int, quantity: int = 2):
    unit_price = Decimal("10000")
    subtotal = unit_price * quantity
    return schemas.OrderCreate(
        customer_id=customer_id,
        status=schemas.OrderStatus.pending,
        total_amount=subtotal,
        items=[
            schemas.OrderItemCreate(
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
            )
        ],
    )


def make_payment_payload(order_id: int, amount: Decimal = Decimal("20000")):
    return schemas.PaymentCreate(
        order_id=order_id,
        status=schemas.PaymentStatus.pending,
        method=schemas.PaymentMethod.manual,
        amount=amount,
    )


def test_create_order_with_enough_stock_reserves_inventory(
    db_session,
    product_and_customer,
):
    product, customer = product_and_customer
    receive_stock(db_session, product.id, 5, reason="initial stock")

    order = create_order(
        db_session,
        make_order_payload(product.id, customer.id, quantity=2),
    )

    inventory_item = (
        db_session.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product.id)
        .one()
    )
    reservation = (
        db_session.query(models.InventoryReservation)
        .filter(models.InventoryReservation.order_id == order.id)
        .one()
    )

    assert order.status == schemas.OrderStatus.awaiting_payment
    assert inventory_item.on_hand_quantity == 5
    assert inventory_item.reserved_quantity == 2
    assert inventory_item.available_quantity == 3
    assert reservation.status == "active"
    assert order.total_amount == Decimal("20000")
    assert order.items[0].unit_price == Decimal("10000")
    assert order.items[0].subtotal == Decimal("20000")
    assert order.items[0].product_name_snapshot == product.name
    assert order.items[0].product_slug_snapshot == product.slug
    assert order.items[0].price_source == "base_price"


def test_create_order_ignores_client_price_and_uses_price_set(
    db_session,
    product_and_customer,
):
    product, customer = product_and_customer
    receive_stock(db_session, product.id, 5, reason="initial stock")
    price_set = models.PriceSet(product_id=product.id, name="Storefront price", is_active=True)
    db_session.add(price_set)
    db_session.flush()
    db_session.add(
        models.PriceSetItem(
            price_set_id=price_set.id,
            price=Decimal("7500"),
            currency="IDR",
            priority=10,
            is_active=True,
        )
    )
    db_session.commit()

    order = create_order(
        db_session,
        schemas.OrderCreate(
            customer_id=customer.id,
            status=schemas.OrderStatus.pending,
            total_amount=Decimal("1"),
            items=[
                schemas.OrderItemCreate(
                    product_id=product.id,
                    quantity=2,
                    unit_price=Decimal("1"),
                    subtotal=Decimal("2"),
                )
            ],
        ),
    )

    assert order.total_amount == Decimal("15000")
    assert order.items[0].unit_price == Decimal("7500")
    assert order.items[0].subtotal == Decimal("15000")
    assert order.items[0].price_source == "price_set"


def test_create_order_rejects_non_active_product(db_session, product_and_customer):
    product, customer = product_and_customer
    product.status = "discontinued"
    db_session.commit()
    receive_stock(db_session, product.id, 5, reason="initial stock")

    with pytest.raises(ProductNotOrderableError):
        create_order(
            db_session,
            make_order_payload(product.id, customer.id, quantity=1),
        )

    assert db_session.query(models.Order).count() == 0


def test_create_order_with_insufficient_stock_rolls_back(
    db_session,
    product_and_customer,
):
    product, customer = product_and_customer
    receive_stock(db_session, product.id, 1, reason="initial stock")

    with pytest.raises(InsufficientStockError):
        create_order(
            db_session,
            make_order_payload(product.id, customer.id, quantity=2),
        )

    inventory_item = (
        db_session.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product.id)
        .one()
    )
    movements = db_session.query(models.InventoryMovement).all()

    assert inventory_item.on_hand_quantity == 1
    assert inventory_item.reserved_quantity == 0
    assert db_session.query(models.Order).count() == 0
    assert db_session.query(models.InventoryReservation).count() == 0
    assert [movement.movement_type for movement in movements] == ["inbound"]


def test_cancel_order_releases_reservation(db_session, product_and_customer):
    product, customer = product_and_customer
    receive_stock(db_session, product.id, 5, reason="initial stock")
    order = create_order(
        db_session,
        make_order_payload(product.id, customer.id, quantity=2),
    )

    cancelled_order = cancel_order(db_session, order.id)

    inventory_item = (
        db_session.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product.id)
        .one()
    )
    reservation = (
        db_session.query(models.InventoryReservation)
        .filter(models.InventoryReservation.order_id == order.id)
        .one()
    )

    assert cancelled_order.status == schemas.OrderStatus.cancelled
    assert inventory_item.on_hand_quantity == 5
    assert inventory_item.reserved_quantity == 0
    assert reservation.status == "released"


def test_payment_failed_releases_reservation(db_session, product_and_customer):
    product, customer = product_and_customer
    receive_stock(db_session, product.id, 5, reason="initial stock")
    order = create_order(
        db_session,
        make_order_payload(product.id, customer.id, quantity=2),
    )
    payment = create_payment(db_session, make_payment_payload(order.id))

    update_payment_status(db_session, payment.id, schemas.PaymentStatus.failed)

    inventory_item = (
        db_session.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product.id)
        .one()
    )
    reservation = (
        db_session.query(models.InventoryReservation)
        .filter(models.InventoryReservation.order_id == order.id)
        .one()
    )
    refreshed_order = (
        db_session.query(models.Order).filter(models.Order.id == order.id).one()
    )

    assert refreshed_order.status == schemas.OrderStatus.cancelled
    assert inventory_item.on_hand_quantity == 5
    assert inventory_item.reserved_quantity == 0
    assert reservation.status == "released"


def test_fulfillment_deducts_on_hand_quantity(db_session, product_and_customer):
    product, customer = product_and_customer
    receive_stock(db_session, product.id, 5, reason="initial stock")
    order = create_order(
        db_session,
        make_order_payload(product.id, customer.id, quantity=2),
    )
    payment = create_payment(db_session, make_payment_payload(order.id))
    update_payment_status(db_session, payment.id, schemas.PaymentStatus.paid)

    fulfilled_order = fulfill_order(db_session, order.id)

    inventory_item = (
        db_session.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product.id)
        .one()
    )
    reservation = (
        db_session.query(models.InventoryReservation)
        .filter(models.InventoryReservation.order_id == order.id)
        .one()
    )

    assert fulfilled_order.status == schemas.OrderStatus.fulfilled
    assert inventory_item.on_hand_quantity == 3
    assert inventory_item.reserved_quantity == 0
    assert reservation.status == "committed"
    assert (
        db_session.query(models.InventoryMovement)
        .filter(models.InventoryMovement.movement_type == "deduction")
        .count()
        == 1
    )


def test_refund_does_not_automatically_restock(db_session, product_and_customer):
    product, customer = product_and_customer
    receive_stock(db_session, product.id, 5, reason="initial stock")
    order = create_order(
        db_session,
        make_order_payload(product.id, customer.id, quantity=2),
    )
    payment = create_payment(db_session, make_payment_payload(order.id))
    update_payment_status(db_session, payment.id, schemas.PaymentStatus.paid)
    fulfill_order(db_session, order.id)

    update_payment_status(db_session, payment.id, schemas.PaymentStatus.refunded)

    inventory_item = (
        db_session.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product.id)
        .one()
    )

    assert inventory_item.on_hand_quantity == 3
    assert inventory_item.reserved_quantity == 0
    assert (
        db_session.query(models.InventoryMovement)
        .filter(models.InventoryMovement.movement_type == "return")
        .count()
        == 0
    )


def test_return_receive_stock_adds_stock_back(db_session, product_and_customer):
    product, customer = product_and_customer
    receive_stock(db_session, product.id, 5, reason="initial stock")
    order = create_order(
        db_session,
        make_order_payload(product.id, customer.id, quantity=2),
    )
    payment = create_payment(db_session, make_payment_payload(order.id))
    update_payment_status(db_session, payment.id, schemas.PaymentStatus.paid)
    fulfill_order(db_session, order.id)

    receive_stock(
        db_session,
        product.id,
        1,
        reason="return received",
        reference_type="return",
        reference_id=order.id,
    )

    inventory_item = (
        db_session.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product.id)
        .one()
    )

    assert inventory_item.on_hand_quantity == 4
    assert inventory_item.reserved_quantity == 0


def test_inventory_aggregate_invariant_blocks_invalid_adjustment(
    db_session,
    product_and_customer,
):
    product, customer = product_and_customer
    receive_stock(db_session, product.id, 5, reason="initial stock")
    create_order(
        db_session,
        make_order_payload(product.id, customer.id, quantity=3),
    )

    with pytest.raises(InsufficientStockError):
        adjust_stock(db_session, product.id, -3, reason="invalid adjustment")

    inventory_item = (
        db_session.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product.id)
        .one()
    )
    assert inventory_item.on_hand_quantity == 5
    assert inventory_item.reserved_quantity == 3
    assert inventory_item.available_quantity == 2
