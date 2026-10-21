"""add brand foundation

Revision ID: 20260430_0009
Revises: 20260430_0008
Create Date: 2026-04-30
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "20260430_0009"
down_revision: Union[str, None] = "20260430_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SETTINGS_TABLES = (
    "brand_settings",
    "storefront_settings",
    "seo_settings",
    "module_settings",
    "system_settings",
)


def _tables() -> set[str]:
    return set(inspect(op.get_bind()).get_table_names())


def _columns(table_name: str) -> set[str]:
    inspector = inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    tables = _tables()

    if "brands" not in tables:
        op.create_table(
            "brands",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("slug", sa.String(length=255), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
            sa.Column("plan", sa.String(length=100), nullable=False, server_default="starter"),
            sa.Column("primary_domain", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.CheckConstraint(
                "status IN ('draft', 'active', 'suspended', 'archived')",
                name="ck_brands_status_allowed",
            ),
        )
        op.create_index("ix_brands_name", "brands", ["name"])
        op.create_index("ix_brands_status", "brands", ["status"])
        op.create_index("ix_brands_slug", "brands", ["slug"], unique=True)
        op.create_index("ix_brands_primary_domain", "brands", ["primary_domain"], unique=True)

    _seed_default_brand()

    for table_name in SETTINGS_TABLES:
        if table_name in _tables():
            _add_brand_id(table_name)


def _seed_default_brand() -> None:
    op.get_bind().execute(
        text(
            """
            INSERT INTO brands (id, name, slug, status, plan, created_at, updated_at)
            SELECT 1, 'CommerceMind', 'default', 'active', 'starter', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM brands WHERE id = 1)
            """
        )
    )


def _add_brand_id(table_name: str) -> None:
    columns = _columns(table_name)
    if "brand_id" not in columns:
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
        op.create_unique_constraint(
            f"uq_{table_name}_brand_id",
            table_name,
            ["brand_id"],
        )

    op.create_index(
        f"ix_{table_name}_brand_id",
        table_name,
        ["brand_id"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    for table_name in SETTINGS_TABLES:
        if table_name in _tables() and "brand_id" in _columns(table_name):
            if bind.dialect.name != "sqlite":
                op.drop_constraint(f"uq_{table_name}_brand_id", table_name, type_="unique")
                op.drop_constraint(
                    f"fk_{table_name}_brand_id_brands",
                    table_name,
                    type_="foreignkey",
                )
            op.drop_index(f"ix_{table_name}_brand_id", table_name=table_name)
            op.drop_column(table_name, "brand_id")

    if "brands" in _tables():
        op.drop_table("brands")
