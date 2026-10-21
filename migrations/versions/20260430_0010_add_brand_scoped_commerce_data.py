"""add brand scoped commerce data

Revision ID: 20260430_0010
Revises: 20260430_0009
Create Date: 2026-04-30
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "20260430_0010"
down_revision: Union[str, None] = "20260430_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


BRAND_SCOPED_TABLES = (
    "products",
    "inventory_items",
    "inventory_reservations",
    "inventory_movements",
    "customers",
    "orders",
    "order_items",
    "payments",
    "price_sets",
    "channels",
    "regions",
)


def _tables() -> set[str]:
    return set(inspect(op.get_bind()).get_table_names())


def _columns(table_name: str) -> set[str]:
    inspector = inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    inspector = inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    for table_name in BRAND_SCOPED_TABLES:
        if table_name in _tables():
            _add_brand_id(table_name)

    _replace_global_unique_indexes()
    _add_brand_unique_constraints()


def downgrade() -> None:
    bind = op.get_bind()

    if bind.dialect.name != "sqlite":
        for constraint_name, table_name in (
            ("uq_products_brand_slug", "products"),
            ("uq_products_brand_sku", "products"),
            ("uq_customers_brand_email", "customers"),
            ("uq_channels_brand_code", "channels"),
            ("uq_regions_brand_code", "regions"),
        ):
            if table_name in _tables():
                op.drop_constraint(constraint_name, table_name, type_="unique")

    _restore_global_unique_indexes()

    for table_name in reversed(BRAND_SCOPED_TABLES):
        if table_name in _tables() and "brand_id" in _columns(table_name):
            if bind.dialect.name != "sqlite":
                op.drop_constraint(
                    f"fk_{table_name}_brand_id_brands",
                    table_name,
                    type_="foreignkey",
                )
            if f"ix_{table_name}_brand_id" in _indexes(table_name):
                op.drop_index(f"ix_{table_name}_brand_id", table_name=table_name)
            op.drop_column(table_name, "brand_id")


def _add_brand_id(table_name: str) -> None:
    if "brand_id" not in _columns(table_name):
        op.add_column(table_name, sa.Column("brand_id", sa.Integer(), nullable=True))

    op.get_bind().execute(
        text(f"UPDATE {table_name} SET brand_id = 1 WHERE brand_id IS NULL")
    )

    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.alter_column(table_name, "brand_id", nullable=False)
        op.create_foreign_key(
            f"fk_{table_name}_brand_id_brands",
            table_name,
            "brands",
            ["brand_id"],
            ["id"],
        )

    if f"ix_{table_name}_brand_id" not in _indexes(table_name):
        op.create_index(f"ix_{table_name}_brand_id", table_name, ["brand_id"])


def _replace_global_unique_indexes() -> None:
    for table_name, index_name, column_name in (
        ("products", "ix_products_slug", "slug"),
        ("products", "ix_products_sku", "sku"),
        ("customers", "ix_customers_email", "email"),
        ("channels", "ix_channels_code", "code"),
        ("regions", "ix_regions_code", "code"),
    ):
        if table_name not in _tables():
            continue
        indexes = _indexes(table_name)
        if index_name in indexes:
            op.drop_index(index_name, table_name=table_name)
        op.create_index(index_name, table_name, [column_name], unique=False)


def _restore_global_unique_indexes() -> None:
    for table_name, index_name, column_name in (
        ("products", "ix_products_slug", "slug"),
        ("products", "ix_products_sku", "sku"),
        ("customers", "ix_customers_email", "email"),
        ("channels", "ix_channels_code", "code"),
        ("regions", "ix_regions_code", "code"),
    ):
        if table_name not in _tables():
            continue
        indexes = _indexes(table_name)
        if index_name in indexes:
            op.drop_index(index_name, table_name=table_name)
        op.create_index(index_name, table_name, [column_name], unique=True)


def _add_brand_unique_constraints() -> None:
    if op.get_bind().dialect.name == "sqlite":
        return

    for constraint_name, table_name, columns in (
        ("uq_products_brand_slug", "products", ["brand_id", "slug"]),
        ("uq_products_brand_sku", "products", ["brand_id", "sku"]),
        ("uq_customers_brand_email", "customers", ["brand_id", "email"]),
        ("uq_channels_brand_code", "channels", ["brand_id", "code"]),
        ("uq_regions_brand_code", "regions", ["brand_id", "code"]),
    ):
        if table_name in _tables():
            op.create_unique_constraint(constraint_name, table_name, columns)
