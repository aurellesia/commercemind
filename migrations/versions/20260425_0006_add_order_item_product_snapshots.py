"""add order item product snapshots

Revision ID: 20260425_0006
Revises: 20260425_0005
Create Date: 2026-04-25
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "20260425_0006"
down_revision: Union[str, None] = "20260425_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table_name: str) -> set[str]:
    inspector = inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    columns = _columns("order_items")
    if not columns:
        return

    if "product_name_snapshot" not in columns:
        op.add_column(
            "order_items",
            sa.Column("product_name_snapshot", sa.String(length=255), nullable=True),
        )
    if "product_sku_snapshot" not in columns:
        op.add_column(
            "order_items",
            sa.Column("product_sku_snapshot", sa.String(length=100), nullable=True),
        )
    if "product_slug_snapshot" not in columns:
        op.add_column(
            "order_items",
            sa.Column("product_slug_snapshot", sa.String(length=255), nullable=True),
        )
    if "price_source" not in columns:
        op.add_column(
            "order_items",
            sa.Column(
                "price_source",
                sa.String(length=50),
                nullable=False,
                server_default="base_price",
            ),
        )

    op.get_bind().execute(
        text(
            """
            UPDATE order_items
            SET
                product_name_snapshot = COALESCE(
                    product_name_snapshot,
                    (SELECT products.name FROM products WHERE products.id = order_items.product_id)
                ),
                product_sku_snapshot = COALESCE(
                    product_sku_snapshot,
                    (SELECT products.sku FROM products WHERE products.id = order_items.product_id)
                ),
                product_slug_snapshot = COALESCE(
                    product_slug_snapshot,
                    (SELECT products.slug FROM products WHERE products.id = order_items.product_id)
                )
            """
        )
    )
    op.get_bind().execute(
        text(
            """
            UPDATE order_items
            SET
                product_name_snapshot = COALESCE(product_name_snapshot, 'Unknown product'),
                product_slug_snapshot = COALESCE(product_slug_snapshot, 'unknown-product'),
                price_source = COALESCE(price_source, 'base_price')
            """
        )
    )

    # SQLite cannot alter nullability without table rebuild; application model enforces it for new rows.
    bind_name = op.get_bind().dialect.name
    if bind_name != "sqlite":
        op.alter_column("order_items", "product_name_snapshot", nullable=False)
        op.alter_column("order_items", "product_slug_snapshot", nullable=False)
        op.alter_column("order_items", "price_source", server_default=None)


def downgrade() -> None:
    columns = _columns("order_items")
    if "price_source" in columns:
        op.drop_column("order_items", "price_source")
    if "product_slug_snapshot" in columns:
        op.drop_column("order_items", "product_slug_snapshot")
    if "product_sku_snapshot" in columns:
        op.drop_column("order_items", "product_sku_snapshot")
    if "product_name_snapshot" in columns:
        op.drop_column("order_items", "product_name_snapshot")
