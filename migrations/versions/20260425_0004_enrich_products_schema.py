"""enrich products schema

Revision ID: 20260425_0004
Revises: 20260425_0003
Create Date: 2026-04-25
"""

from __future__ import annotations

import re
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "20260425_0004"
down_revision: Union[str, None] = "20260425_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(table_name: str) -> set[str]:
    return {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def _index_names(table_name: str) -> set[str]:
    return {index["name"] for index in inspect(op.get_bind()).get_indexes(table_name)}


def _check_constraint_names(table_name: str) -> set[str]:
    return {
        constraint["name"]
        for constraint in inspect(op.get_bind()).get_check_constraints(table_name)
    }


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "product"


def upgrade() -> None:
    columns = _column_names("products")

    if "slug" not in columns:
        op.add_column("products", sa.Column("slug", sa.String(length=255), nullable=True))
    if "sku" not in columns:
        op.add_column("products", sa.Column("sku", sa.String(length=100), nullable=True))
    if "bpom_number" not in columns:
        op.add_column("products", sa.Column("bpom_number", sa.String(length=100), nullable=True))
    if "usage_instructions" not in columns:
        op.add_column("products", sa.Column("usage_instructions", sa.Text(), nullable=True))
    if "ingredients" not in columns:
        op.add_column("products", sa.Column("ingredients", sa.Text(), nullable=True))
    if "storage_instructions" not in columns:
        op.add_column("products", sa.Column("storage_instructions", sa.Text(), nullable=True))
    if "warnings" not in columns:
        op.add_column("products", sa.Column("warnings", sa.Text(), nullable=True))
    if "net_weight" not in columns:
        op.add_column("products", sa.Column("net_weight", sa.String(length=100), nullable=True))
    if "cost_price" not in columns:
        op.add_column(
            "products",
            sa.Column(
                "cost_price",
                sa.Numeric(precision=12, scale=2),
                nullable=False,
                server_default="0",
            ),
        )
        op.alter_column("products", "cost_price", server_default=None)

    bind = op.get_bind()
    rows = bind.execute(text("SELECT id, name, slug FROM products ORDER BY id")).mappings()
    used_slugs: set[str] = set()
    for row in rows:
        existing_slug = row["slug"]
        base_slug = _slugify(existing_slug or row["name"])
        slug = base_slug
        suffix = 2
        while slug in used_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        used_slugs.add(slug)
        if existing_slug != slug:
            bind.execute(
                text("UPDATE products SET slug = :slug WHERE id = :id"),
                {"slug": slug, "id": row["id"]},
            )

    op.alter_column(
        "products",
        "slug",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    indexes = _index_names("products")
    if "ix_products_slug" not in indexes:
        op.create_index("ix_products_slug", "products", ["slug"], unique=True)
    if "ix_products_sku" not in indexes:
        op.create_index("ix_products_sku", "products", ["sku"], unique=True)

    checks = _check_constraint_names("products")
    if "ck_products_cost_price_non_negative" not in checks:
        op.create_check_constraint(
            "ck_products_cost_price_non_negative",
            "products",
            "cost_price >= 0",
        )


def downgrade() -> None:
    indexes = _index_names("products")
    if "ix_products_sku" in indexes:
        op.drop_index("ix_products_sku", table_name="products")
    if "ix_products_slug" in indexes:
        op.drop_index("ix_products_slug", table_name="products")

    checks = _check_constraint_names("products")
    if "ck_products_cost_price_non_negative" in checks:
        op.drop_constraint(
            "ck_products_cost_price_non_negative",
            "products",
            type_="check",
        )

    columns = _column_names("products")
    for column_name in (
        "cost_price",
        "net_weight",
        "warnings",
        "storage_instructions",
        "ingredients",
        "usage_instructions",
        "bpom_number",
        "sku",
        "slug",
    ):
        if column_name in columns:
            op.drop_column("products", column_name)
