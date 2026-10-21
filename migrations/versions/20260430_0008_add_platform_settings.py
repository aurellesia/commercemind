"""add platform settings

Revision ID: 20260430_0008
Revises: 20260425_0007
Create Date: 2026-04-30
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "20260430_0008"
down_revision: Union[str, None] = "20260425_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tables() -> set[str]:
    return set(inspect(op.get_bind()).get_table_names())


def _timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def upgrade() -> None:
    tables = _tables()

    if "brand_settings" not in tables:
        op.create_table(
            "brand_settings",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("brand_name", sa.String(length=255), nullable=False, server_default="CommerceMind"),
            sa.Column("tagline", sa.String(length=500), nullable=True),
            sa.Column("logo_url", sa.Text(), nullable=True),
            sa.Column("contact_whatsapp", sa.String(length=50), nullable=True),
            sa.Column("support_email", sa.String(length=255), nullable=True),
            sa.Column("business_address", sa.Text(), nullable=True),
            *_timestamps(),
        )

    if "storefront_settings" not in tables:
        op.create_table(
            "storefront_settings",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("storefront_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column(
                "homepage_headline",
                sa.String(length=500),
                nullable=False,
                server_default="Katalog produk dengan stok dan harga yang jelas.",
            ),
            sa.Column("homepage_description", sa.Text(), nullable=True),
            sa.Column("featured_product_limit", sa.Integer(), nullable=False, server_default="3"),
            sa.Column("show_out_of_stock_products", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("show_sku", sa.Boolean(), nullable=False, server_default=sa.true()),
            *_timestamps(),
            sa.CheckConstraint(
                "featured_product_limit >= 0",
                name="ck_storefront_settings_featured_product_limit_non_negative",
            ),
        )

    if "seo_settings" not in tables:
        op.create_table(
            "seo_settings",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("site_url", sa.String(length=500), nullable=False, server_default="http://localhost:5173"),
            sa.Column("default_title", sa.String(length=255), nullable=False, server_default="CommerceMind"),
            sa.Column("default_description", sa.Text(), nullable=True),
            sa.Column("social_image_url", sa.Text(), nullable=True),
            *_timestamps(),
        )

    if "module_settings" not in tables:
        op.create_table(
            "module_settings",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("products_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("inventory_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("cart_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("guest_checkout_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("customer_accounts_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("payments_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("shipping_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("reports_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            *_timestamps(),
        )

    if "system_settings" not in tables:
        op.create_table(
            "system_settings",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("maintenance_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("test_mode", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("public_catalog_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("allow_checkout", sa.Boolean(), nullable=False, server_default=sa.false()),
            *_timestamps(),
        )

    _seed_defaults()


def _seed_defaults() -> None:
    bind = op.get_bind()
    default_description = (
        "CommerceMind adalah template storefront ecommerce untuk menampilkan produk, "
        "harga, stok, dan detail katalog secara rapi."
    )
    homepage_description = (
        "Gunakan storefront ini sebagai template toko untuk skincare, fashion, "
        "aksesoris, atau brand lain."
    )

    bind.execute(
        text(
            """
            INSERT INTO brand_settings (id, brand_name, tagline, created_at, updated_at)
            SELECT 1, 'CommerceMind', 'Template toko online untuk katalog produk yang rapi.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM brand_settings WHERE id = 1)
            """
        )
    )
    bind.execute(
        text(
            """
            INSERT INTO storefront_settings (
                id, storefront_enabled, homepage_headline, homepage_description,
                featured_product_limit, show_out_of_stock_products, show_sku,
                created_at, updated_at
            )
            SELECT 1, true, 'Katalog produk dengan stok dan harga yang jelas.', :homepage_description,
                3, true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM storefront_settings WHERE id = 1)
            """
        ),
        {"homepage_description": homepage_description},
    )
    bind.execute(
        text(
            """
            INSERT INTO seo_settings (
                id, site_url, default_title, default_description, created_at, updated_at
            )
            SELECT 1, 'http://localhost:5173', 'CommerceMind', :default_description,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM seo_settings WHERE id = 1)
            """
        ),
        {"default_description": default_description},
    )
    bind.execute(
        text(
            """
            INSERT INTO module_settings (
                id, products_enabled, inventory_enabled, cart_enabled, guest_checkout_enabled,
                customer_accounts_enabled, payments_enabled, shipping_enabled, reports_enabled,
                created_at, updated_at
            )
            SELECT 1, true, true, false, false, false, true, false, true,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM module_settings WHERE id = 1)
            """
        )
    )
    bind.execute(
        text(
            """
            INSERT INTO system_settings (
                id, maintenance_mode, test_mode, public_catalog_enabled, allow_checkout,
                created_at, updated_at
            )
            SELECT 1, false, true, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            WHERE NOT EXISTS (SELECT 1 FROM system_settings WHERE id = 1)
            """
        )
    )


def downgrade() -> None:
    tables = _tables()
    for table_name in (
        "system_settings",
        "module_settings",
        "seo_settings",
        "storefront_settings",
        "brand_settings",
    ):
        if table_name in tables:
            op.drop_table(table_name)
