"""add customer addresses

Revision ID: 20260501_0013
Revises: 20260501_0012
Create Date: 2026-05-01
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "20260501_0013"
down_revision: Union[str, None] = "20260501_0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tables() -> set[str]:
    return set(inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    if "customer_addresses" in _tables():
        return

    op.create_table(
        "customer_addresses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("brand_id", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("recipient_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=False),
        sa.Column("address_line", sa.Text(), nullable=False),
        sa.Column("district", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=255), nullable=False),
        sa.Column("province", sa.String(length=255), nullable=False),
        sa.Column("postal_code", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
    )
    op.create_index("ix_customer_addresses_id", "customer_addresses", ["id"])
    op.create_index("ix_customer_addresses_brand_id", "customer_addresses", ["brand_id"])
    op.create_index("ix_customer_addresses_customer_id", "customer_addresses", ["customer_id"])
    op.create_index(
        "ix_customer_addresses_brand_customer",
        "customer_addresses",
        ["brand_id", "customer_id"],
    )


def downgrade() -> None:
    if "customer_addresses" not in _tables():
        return

    op.drop_index("ix_customer_addresses_brand_customer", table_name="customer_addresses")
    op.drop_index("ix_customer_addresses_customer_id", table_name="customer_addresses")
    op.drop_index("ix_customer_addresses_brand_id", table_name="customer_addresses")
    op.drop_index("ix_customer_addresses_id", table_name="customer_addresses")
    op.drop_table("customer_addresses")
