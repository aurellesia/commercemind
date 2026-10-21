"""add order item cost snapshot

Revision ID: 20260425_0007
Revises: 20260425_0006
Create Date: 2026-04-25
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "20260425_0007"
down_revision: Union[str, None] = "20260425_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(table_name: str) -> set[str]:
    inspector = inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    columns = _columns("order_items")
    if not columns or "product_cost_price_snapshot" in columns:
        return

    op.add_column(
        "order_items",
        sa.Column(
            "product_cost_price_snapshot",
            sa.Numeric(12, 2),
            nullable=False,
            server_default="0",
        ),
    )
    op.get_bind().execute(
        text(
            """
            UPDATE order_items
            SET product_cost_price_snapshot = COALESCE(
                (SELECT products.cost_price FROM products WHERE products.id = order_items.product_id),
                0
            )
            """
        )
    )
    if op.get_bind().dialect.name != "sqlite":
        op.alter_column("order_items", "product_cost_price_snapshot", server_default=None)


def downgrade() -> None:
    columns = _columns("order_items")
    if "product_cost_price_snapshot" in columns:
        op.drop_column("order_items", "product_cost_price_snapshot")
