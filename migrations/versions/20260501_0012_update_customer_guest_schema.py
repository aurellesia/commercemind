"""update customer schema for guest checkout

Revision ID: 20260501_0012
Revises: 20260430_0011
Create Date: 2026-05-01
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "20260501_0012"
down_revision: Union[str, None] = "20260430_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
    if "customers" not in _tables():
        return

    columns = _columns("customers")
    with op.batch_alter_table("customers") as batch_op:
        if "email" in columns:
            batch_op.alter_column(
                "email",
                existing_type=sa.String(length=255),
                nullable=True,
            )
        if "customer_type" not in columns:
            batch_op.add_column(
                sa.Column(
                    "customer_type",
                    sa.String(length=50),
                    nullable=False,
                    server_default="guest",
                )
            )
        if "password_hash" not in columns:
            batch_op.add_column(sa.Column("password_hash", sa.String(length=255), nullable=True))

    indexes = _indexes("customers")
    if "ix_customers_customer_type" not in indexes:
        op.create_index("ix_customers_customer_type", "customers", ["customer_type"])
    if "ix_customers_brand_phone" not in indexes:
        op.create_index("ix_customers_brand_phone", "customers", ["brand_id", "phone"])

    if op.get_bind().dialect.name != "sqlite":
        op.create_check_constraint(
            "ck_customers_customer_type_allowed",
            "customers",
            "customer_type IN ('guest', 'registered')",
        )


def downgrade() -> None:
    if "customers" not in _tables():
        return

    indexes = _indexes("customers")
    if "ix_customers_brand_phone" in indexes:
        op.drop_index("ix_customers_brand_phone", table_name="customers")
    if "ix_customers_customer_type" in indexes:
        op.drop_index("ix_customers_customer_type", table_name="customers")

    if op.get_bind().dialect.name != "sqlite":
        op.drop_constraint("ck_customers_customer_type_allowed", "customers", type_="check")

    columns = _columns("customers")
    with op.batch_alter_table("customers") as batch_op:
        if "password_hash" in columns:
            batch_op.drop_column("password_hash")
        if "customer_type" in columns:
            batch_op.drop_column("customer_type")
        if "email" in columns:
            batch_op.alter_column(
                "email",
                existing_type=sa.String(length=255),
                nullable=False,
            )
