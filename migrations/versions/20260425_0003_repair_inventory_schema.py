"""repair inventory schema

Revision ID: 20260425_0003
Revises: 20260424_0002
Create Date: 2026-04-25
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "20260425_0003"
down_revision: Union[str, None] = "20260424_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_names() -> set[str]:
    return set(inspect(op.get_bind()).get_table_names())


def _column_names(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def _check_constraint_names(table_name: str) -> set[str]:
    return {
        constraint["name"]
        for constraint in inspect(op.get_bind()).get_check_constraints(table_name)
    }


def upgrade() -> None:
    tables = _table_names()

    if "inventory_items" in tables:
        columns = _column_names("inventory_items")
        checks = _check_constraint_names("inventory_items")

        if "ck_inventory_items_quantity_non_negative" in checks:
            op.drop_constraint(
                "ck_inventory_items_quantity_non_negative",
                "inventory_items",
                type_="check",
            )
        if "ck_inventory_items_reserved_not_greater_than_quantity" in checks:
            op.drop_constraint(
                "ck_inventory_items_reserved_not_greater_than_quantity",
                "inventory_items",
                type_="check",
            )

        if "quantity" in columns and "on_hand_quantity" not in columns:
            op.alter_column(
                "inventory_items",
                "quantity",
                new_column_name="on_hand_quantity",
                existing_type=sa.Integer(),
                existing_nullable=False,
            )
        elif "on_hand_quantity" not in columns:
            op.add_column(
                "inventory_items",
                sa.Column(
                    "on_hand_quantity",
                    sa.Integer(),
                    nullable=False,
                    server_default="0",
                ),
            )
            op.alter_column("inventory_items", "on_hand_quantity", server_default=None)

        checks = _check_constraint_names("inventory_items")
        if "ck_inventory_items_on_hand_quantity_non_negative" not in checks:
            op.create_check_constraint(
                "ck_inventory_items_on_hand_quantity_non_negative",
                "inventory_items",
                "on_hand_quantity >= 0",
            )
        if "ck_inventory_items_reserved_not_greater_than_on_hand_quantity" not in checks:
            op.create_check_constraint(
                "ck_inventory_items_reserved_not_greater_than_on_hand_quantity",
                "inventory_items",
                "reserved_quantity <= on_hand_quantity",
            )

    tables = _table_names()

    if "inventory_movements" not in tables:
        op.create_table(
            "inventory_movements",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("movement_type", sa.String(length=50), nullable=False),
            sa.Column("reference_type", sa.String(length=100), nullable=True),
            sa.Column("reference_id", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.CheckConstraint(
                "movement_type IN ('inbound', 'reservation', 'release', 'deduction', 'adjustment', 'return')",
                name="ck_inventory_movements_type_allowed",
            ),
            sa.CheckConstraint(
                "quantity > 0",
                name="ck_inventory_movements_quantity_positive",
            ),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_inventory_movements_id"), "inventory_movements", ["id"])
        op.create_index(
            op.f("ix_inventory_movements_movement_type"),
            "inventory_movements",
            ["movement_type"],
        )
        op.create_index(
            op.f("ix_inventory_movements_product_id"),
            "inventory_movements",
            ["product_id"],
        )
        op.create_index(
            op.f("ix_inventory_movements_reference_id"),
            "inventory_movements",
            ["reference_id"],
        )
        op.create_index(
            op.f("ix_inventory_movements_reference_type"),
            "inventory_movements",
            ["reference_type"],
        )

    tables = _table_names()

    if "inventory_reservations" not in tables:
        op.create_table(
            "inventory_reservations",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("order_id", sa.Integer(), nullable=False),
            sa.Column("order_item_id", sa.Integer(), nullable=True),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.CheckConstraint(
                "status IN ('active', 'released', 'committed', 'expired')",
                name="ck_inventory_reservations_status_allowed",
            ),
            sa.CheckConstraint(
                "quantity > 0",
                name="ck_inventory_reservations_quantity_positive",
            ),
            sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
            sa.ForeignKeyConstraint(["order_item_id"], ["order_items.id"]),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_inventory_reservations_id"), "inventory_reservations", ["id"])
        op.create_index(
            op.f("ix_inventory_reservations_order_id"),
            "inventory_reservations",
            ["order_id"],
        )
        op.create_index(
            op.f("ix_inventory_reservations_order_item_id"),
            "inventory_reservations",
            ["order_item_id"],
        )
        op.create_index(
            op.f("ix_inventory_reservations_product_id"),
            "inventory_reservations",
            ["product_id"],
        )
        op.create_index(
            op.f("ix_inventory_reservations_status"),
            "inventory_reservations",
            ["status"],
        )


def downgrade() -> None:
    tables = _table_names()

    if "inventory_reservations" in tables:
        op.drop_index(op.f("ix_inventory_reservations_status"), table_name="inventory_reservations")
        op.drop_index(op.f("ix_inventory_reservations_product_id"), table_name="inventory_reservations")
        op.drop_index(op.f("ix_inventory_reservations_order_item_id"), table_name="inventory_reservations")
        op.drop_index(op.f("ix_inventory_reservations_order_id"), table_name="inventory_reservations")
        op.drop_index(op.f("ix_inventory_reservations_id"), table_name="inventory_reservations")
        op.drop_table("inventory_reservations")

    tables = _table_names()

    if "inventory_movements" in tables:
        op.drop_index(op.f("ix_inventory_movements_reference_type"), table_name="inventory_movements")
        op.drop_index(op.f("ix_inventory_movements_reference_id"), table_name="inventory_movements")
        op.drop_index(op.f("ix_inventory_movements_product_id"), table_name="inventory_movements")
        op.drop_index(op.f("ix_inventory_movements_movement_type"), table_name="inventory_movements")
        op.drop_index(op.f("ix_inventory_movements_id"), table_name="inventory_movements")
        op.drop_table("inventory_movements")

    tables = _table_names()

    if "inventory_items" in tables:
        columns = _column_names("inventory_items")
        checks = _check_constraint_names("inventory_items")

        if "ck_inventory_items_on_hand_quantity_non_negative" in checks:
            op.drop_constraint(
                "ck_inventory_items_on_hand_quantity_non_negative",
                "inventory_items",
                type_="check",
            )
        if "ck_inventory_items_reserved_not_greater_than_on_hand_quantity" in checks:
            op.drop_constraint(
                "ck_inventory_items_reserved_not_greater_than_on_hand_quantity",
                "inventory_items",
                type_="check",
            )

        if "on_hand_quantity" in columns and "quantity" not in columns:
            op.alter_column(
                "inventory_items",
                "on_hand_quantity",
                new_column_name="quantity",
                existing_type=sa.Integer(),
                existing_nullable=False,
            )

        checks = _check_constraint_names("inventory_items")
        if "ck_inventory_items_quantity_non_negative" not in checks:
            op.create_check_constraint(
                "ck_inventory_items_quantity_non_negative",
                "inventory_items",
                "quantity >= 0",
            )
        if "ck_inventory_items_reserved_not_greater_than_quantity" not in checks:
            op.create_check_constraint(
                "ck_inventory_items_reserved_not_greater_than_quantity",
                "inventory_items",
                "reserved_quantity <= quantity",
            )
