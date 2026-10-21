from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models


class InventoryServiceError(Exception):
    """Base exception for inventory domain workflow failures."""


class InventoryProductNotFoundError(InventoryServiceError):
    pass


class InventoryItemNotFoundError(InventoryServiceError):
    pass


class InventoryOrderNotFoundError(InventoryServiceError):
    pass


class InventoryReservationNotFoundError(InventoryServiceError):
    pass


class InsufficientStockError(InventoryServiceError):
    pass


class InvalidInventoryOperationError(InventoryServiceError):
    pass


def receive_stock(
    db: Session,
    product_id: int,
    quantity: int,
    reason: Optional[str] = None,
    reference_type: Optional[str] = None,
    reference_id: Optional[int] = None,
) -> models.InventoryItem:
    _ensure_positive_quantity(quantity)

    try:
        product = _get_product(db, product_id)
        if product is None:
            raise InventoryProductNotFoundError(f"Product {product_id} not found")

        inventory_item = _get_inventory_item_for_update(db, product_id)
        if inventory_item is None:
            inventory_item = models.InventoryItem(
                brand_id=product.brand_id,
                product_id=product_id,
                on_hand_quantity=0,
                reserved_quantity=0,
                low_stock_threshold=0,
            )
            db.add(inventory_item)
            db.flush()

        inventory_item.on_hand_quantity += quantity
        _ensure_inventory_invariants(inventory_item)
        _add_movement(
            db,
            brand_id=product.brand_id,
            product_id=product_id,
            quantity=quantity,
            movement_type="inbound",
            reference_type=reference_type,
            reference_id=reference_id,
            notes=reason,
        )

        db.commit()
        db.refresh(inventory_item)
        return inventory_item
    except Exception:
        db.rollback()
        raise


def adjust_stock(
    db: Session,
    product_id: int,
    delta: int,
    reason: Optional[str] = None,
    reference_type: Optional[str] = None,
    reference_id: Optional[int] = None,
) -> models.InventoryItem:
    if delta == 0:
        raise InvalidInventoryOperationError("delta must not be zero")

    try:
        inventory_item = _require_inventory_item_for_update(db, product_id)
        next_on_hand_quantity = inventory_item.on_hand_quantity + delta
        if next_on_hand_quantity < 0:
            raise InsufficientStockError("on_hand_quantity cannot become negative")
        if next_on_hand_quantity < inventory_item.reserved_quantity:
            raise InsufficientStockError(
                "on_hand_quantity cannot be lower than reserved_quantity"
            )

        inventory_item.on_hand_quantity = next_on_hand_quantity
        _ensure_inventory_invariants(inventory_item)
        _add_movement(
            db,
            brand_id=inventory_item.brand_id,
            product_id=product_id,
            quantity=abs(delta),
            movement_type="adjustment",
            reference_type=reference_type,
            reference_id=reference_id,
            notes=reason,
        )

        db.commit()
        db.refresh(inventory_item)
        return inventory_item
    except Exception:
        db.rollback()
        raise


def reserve_stock(
    db: Session,
    product_id: int,
    order_id: int,
    quantity: int,
    order_item_id: Optional[int] = None,
    expires_at: Optional[datetime] = None,
    reason: Optional[str] = None,
) -> models.InventoryReservation:
    _ensure_positive_quantity(quantity)

    try:
        product = _get_product(db, product_id)
        if product is None:
            raise InventoryProductNotFoundError(f"Product {product_id} not found")

        order = _get_order(db, order_id)
        if order is None:
            raise InventoryOrderNotFoundError(f"Order {order_id} not found")

        inventory_item = _require_inventory_item_for_update(db, product_id)
        if inventory_item.available_quantity < quantity:
            raise InsufficientStockError(f"Product {product_id} has insufficient stock")

        inventory_item.reserved_quantity += quantity
        _ensure_inventory_invariants(inventory_item)

        reservation = models.InventoryReservation(
            brand_id=order.brand_id,
            product_id=product_id,
            order_id=order_id,
            order_item_id=order_item_id,
            quantity=quantity,
            status="active",
            expires_at=expires_at,
        )
        db.add(reservation)
        _add_movement(
            db,
            brand_id=order.brand_id,
            product_id=product_id,
            quantity=quantity,
            movement_type="reservation",
            reference_type="order",
            reference_id=order_id,
            notes=reason,
        )

        db.commit()
        db.refresh(reservation)
        return reservation
    except Exception:
        db.rollback()
        raise


def reserve_stock_for_order(
    db: Session,
    order_id: int,
    expires_at: Optional[datetime] = None,
    reason: Optional[str] = None,
    commit: bool = True,
) -> List[models.InventoryReservation]:
    try:
        order = _get_order(db, order_id)
        if order is None:
            raise InventoryOrderNotFoundError(f"Order {order_id} not found")
        if not order.items:
            raise InvalidInventoryOperationError("order has no items to reserve")

        existing_active_reservation = (
            db.query(models.InventoryReservation)
            .filter(
                models.InventoryReservation.order_id == order_id,
                models.InventoryReservation.status == "active",
            )
            .first()
        )
        if existing_active_reservation is not None:
            raise InvalidInventoryOperationError(
                f"Order {order_id} already has active inventory reservations"
            )

        reservations: List[models.InventoryReservation] = []
        for order_item in order.items:
            inventory_item = _require_inventory_item_for_update(
                db,
                order_item.product_id,
            )
            if inventory_item.available_quantity < order_item.quantity:
                raise InsufficientStockError(
                    f"Product {order_item.product_id} has insufficient stock"
                )

            inventory_item.reserved_quantity += order_item.quantity
            _ensure_inventory_invariants(inventory_item)

            reservation = models.InventoryReservation(
                brand_id=order.brand_id,
                product_id=order_item.product_id,
                order_id=order_id,
                order_item_id=order_item.id,
                quantity=order_item.quantity,
                status="active",
                expires_at=expires_at,
            )
            db.add(reservation)
            reservations.append(reservation)

            _add_movement(
                db,
                brand_id=order.brand_id,
                product_id=order_item.product_id,
                quantity=order_item.quantity,
                movement_type="reservation",
                reference_type="order",
                reference_id=order_id,
                notes=reason,
            )

        if commit:
            db.commit()
            for reservation in reservations:
                db.refresh(reservation)
        else:
            db.flush()
        return reservations
    except Exception:
        db.rollback()
        raise


def release_reservation(
    db: Session,
    reservation_id: int,
    reason: Optional[str] = None,
) -> models.InventoryReservation:
    try:
        reservation = _require_reservation_for_update(db, reservation_id)
        if reservation.status != "active":
            raise InvalidInventoryOperationError(
                f"Reservation {reservation_id} is not active"
            )

        inventory_item = _require_inventory_item_for_update(db, reservation.product_id)
        if inventory_item.reserved_quantity < reservation.quantity:
            raise InvalidInventoryOperationError(
                "reserved_quantity is lower than reservation quantity"
            )

        inventory_item.reserved_quantity -= reservation.quantity
        reservation.status = "released"
        _ensure_inventory_invariants(inventory_item)
        _add_movement(
            db,
            brand_id=reservation.brand_id,
            product_id=reservation.product_id,
            quantity=reservation.quantity,
            movement_type="release",
            reference_type="reservation",
            reference_id=reservation.id,
            notes=reason,
        )

        db.commit()
        db.refresh(reservation)
        return reservation
    except Exception:
        db.rollback()
        raise


def release_stock_for_order(
    db: Session,
    order_id: int,
    reason: Optional[str] = None,
    commit: bool = True,
) -> List[models.InventoryReservation]:
    try:
        order = _get_order(db, order_id)
        if order is None:
            raise InventoryOrderNotFoundError(f"Order {order_id} not found")

        reservations = _get_active_reservations_for_order(db, order_id)
        for reservation in reservations:
            inventory_item = _require_inventory_item_for_update(
                db,
                reservation.product_id,
            )
            if inventory_item.reserved_quantity < reservation.quantity:
                raise InvalidInventoryOperationError(
                    "reserved_quantity is lower than reservation quantity"
                )

            inventory_item.reserved_quantity -= reservation.quantity
            reservation.status = "released"
            _ensure_inventory_invariants(inventory_item)

            _add_movement(
                db,
                brand_id=order.brand_id,
                product_id=reservation.product_id,
                quantity=reservation.quantity,
                movement_type="release",
                reference_type="order",
                reference_id=order_id,
                notes=reason,
            )

        if commit:
            db.commit()
            for reservation in reservations:
                db.refresh(reservation)
        else:
            db.flush()
        return reservations
    except Exception:
        db.rollback()
        raise


def commit_reservation(
    db: Session,
    reservation_id: int,
    reason: Optional[str] = None,
) -> models.InventoryReservation:
    try:
        reservation = _require_reservation_for_update(db, reservation_id)
        if reservation.status != "active":
            raise InvalidInventoryOperationError(
                f"Reservation {reservation_id} is not active"
            )

        inventory_item = _require_inventory_item_for_update(db, reservation.product_id)
        if inventory_item.reserved_quantity < reservation.quantity:
            raise InvalidInventoryOperationError(
                "reserved_quantity is lower than reservation quantity"
            )
        if inventory_item.on_hand_quantity < reservation.quantity:
            raise InsufficientStockError(
                "on_hand_quantity is lower than reservation quantity"
            )

        inventory_item.reserved_quantity -= reservation.quantity
        inventory_item.on_hand_quantity -= reservation.quantity
        reservation.status = "committed"
        _ensure_inventory_invariants(inventory_item)
        _add_movement(
            db,
            brand_id=reservation.brand_id,
            product_id=reservation.product_id,
            quantity=reservation.quantity,
            movement_type="deduction",
            reference_type="reservation",
            reference_id=reservation.id,
            notes=reason,
        )

        db.commit()
        db.refresh(reservation)
        return reservation
    except Exception:
        db.rollback()
        raise


def commit_stock_for_order(
    db: Session,
    order_id: int,
    reason: Optional[str] = None,
    commit: bool = True,
) -> List[models.InventoryReservation]:
    try:
        order = _get_order(db, order_id)
        if order is None:
            raise InventoryOrderNotFoundError(f"Order {order_id} not found")

        reservations = _get_active_reservations_for_order(db, order_id)
        if not reservations:
            raise InvalidInventoryOperationError(
                f"Order {order_id} has no active inventory reservations to commit"
            )

        for reservation in reservations:
            inventory_item = _require_inventory_item_for_update(
                db,
                reservation.product_id,
            )
            if inventory_item.reserved_quantity < reservation.quantity:
                raise InvalidInventoryOperationError(
                    "reserved_quantity is lower than reservation quantity"
                )
            if inventory_item.on_hand_quantity < reservation.quantity:
                raise InsufficientStockError(
                    "on_hand_quantity is lower than reservation quantity"
                )

            inventory_item.reserved_quantity -= reservation.quantity
            inventory_item.on_hand_quantity -= reservation.quantity
            reservation.status = "committed"
            _ensure_inventory_invariants(inventory_item)

            _add_movement(
                db,
                brand_id=order.brand_id,
                product_id=reservation.product_id,
                quantity=reservation.quantity,
                movement_type="deduction",
                reference_type="order",
                reference_id=order_id,
                notes=reason,
            )

        if commit:
            db.commit()
            for reservation in reservations:
                db.refresh(reservation)
        else:
            db.flush()
        return reservations
    except Exception:
        db.rollback()
        raise


def _get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def _get_order(db: Session, order_id: int) -> Optional[models.Order]:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def _get_inventory_item_for_update(
    db: Session,
    product_id: int,
) -> Optional[models.InventoryItem]:
    return (
        db.query(models.InventoryItem)
        .filter(models.InventoryItem.product_id == product_id)
        .with_for_update()
        .first()
    )


def _require_inventory_item_for_update(
    db: Session,
    product_id: int,
) -> models.InventoryItem:
    inventory_item = _get_inventory_item_for_update(db, product_id)
    if inventory_item is None:
        raise InventoryItemNotFoundError(
            f"Inventory item for product {product_id} not found"
        )
    return inventory_item


def _get_active_reservations_for_order(
    db: Session,
    order_id: int,
) -> List[models.InventoryReservation]:
    return (
        db.query(models.InventoryReservation)
        .filter(
            models.InventoryReservation.order_id == order_id,
            models.InventoryReservation.status == "active",
        )
        .with_for_update()
        .all()
    )


def _require_reservation_for_update(
    db: Session,
    reservation_id: int,
) -> models.InventoryReservation:
    reservation = (
        db.query(models.InventoryReservation)
        .filter(models.InventoryReservation.id == reservation_id)
        .with_for_update()
        .first()
    )
    if reservation is None:
        raise InventoryReservationNotFoundError(
            f"Inventory reservation {reservation_id} not found"
        )
    return reservation


def _add_movement(
    db: Session,
    brand_id: int,
    product_id: int,
    quantity: int,
    movement_type: str,
    reference_type: Optional[str],
    reference_id: Optional[int],
    notes: Optional[str],
) -> models.InventoryMovement:
    if movement_type == "deduction" and (
        reference_type is None or reference_id is None
    ):
        raise InvalidInventoryOperationError(
            "deduction movement requires reference_type and reference_id"
        )

    movement = models.InventoryMovement(
        brand_id=brand_id,
        product_id=product_id,
        quantity=quantity,
        movement_type=movement_type,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=notes,
    )
    db.add(movement)
    return movement


def _ensure_positive_quantity(quantity: int) -> None:
    if quantity <= 0:
        raise InvalidInventoryOperationError("quantity must be greater than zero")


def _ensure_inventory_invariants(inventory_item: models.InventoryItem) -> None:
    if inventory_item.on_hand_quantity < 0:
        raise InvalidInventoryOperationError("on_hand_quantity cannot be negative")
    if inventory_item.reserved_quantity < 0:
        raise InvalidInventoryOperationError("reserved_quantity cannot be negative")
    if inventory_item.reserved_quantity > inventory_item.on_hand_quantity:
        raise InvalidInventoryOperationError(
            "reserved_quantity cannot exceed on_hand_quantity"
        )
