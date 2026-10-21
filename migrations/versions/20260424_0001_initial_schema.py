"""initial schema

Revision ID: 20260424_0001
Revises:
Create Date: 2026-04-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260424_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_channels_code"), "channels", ["code"], unique=True)
    op.create_index(op.f("ix_channels_id"), "channels", ["id"], unique=False)

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customers_email"), "customers", ["email"], unique=True)
    op.create_index(op.f("ix_customers_id"), "customers", ["id"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("base_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("base_price >= 0", name="ck_products_base_price_non_negative"),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'archived', 'discontinued')",
            name="ck_products_status_allowed",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
    op.create_index(op.f("ix_products_status"), "products", ["status"], unique=False)

    op.create_table(
        "regions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_regions_code"), "regions", ["code"], unique=True)
    op.create_index(op.f("ix_regions_id"), "regions", ["id"], unique=False)

    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("on_hand_quantity", sa.Integer(), nullable=False),
        sa.Column("reserved_quantity", sa.Integer(), nullable=False),
        sa.Column("low_stock_threshold", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "low_stock_threshold >= 0",
            name="ck_inventory_items_low_stock_threshold_non_negative",
        ),
        sa.CheckConstraint(
            "on_hand_quantity >= 0",
            name="ck_inventory_items_on_hand_quantity_non_negative",
        ),
        sa.CheckConstraint(
            "reserved_quantity >= 0",
            name="ck_inventory_items_reserved_quantity_non_negative",
        ),
        sa.CheckConstraint(
            "reserved_quantity <= on_hand_quantity",
            name="ck_inventory_items_reserved_not_greater_than_on_hand_quantity",
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id"),
    )
    op.create_index(op.f("ix_inventory_items_id"), "inventory_items", ["id"], unique=False)

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
        sa.CheckConstraint("quantity > 0", name="ck_inventory_movements_quantity_positive"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_movements_id"), "inventory_movements", ["id"], unique=False)
    op.create_index(
        op.f("ix_inventory_movements_movement_type"),
        "inventory_movements",
        ["movement_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_movements_product_id"),
        "inventory_movements",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_movements_reference_id"),
        "inventory_movements",
        ["reference_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_movements_reference_type"),
        "inventory_movements",
        ["reference_type"],
        unique=False,
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'awaiting_payment', 'paid', 'processing', 'fulfilled', 'completed', 'cancelled')",
            name="ck_orders_status_allowed",
        ),
        sa.CheckConstraint("total_amount >= 0", name="ck_orders_total_amount_non_negative"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_orders_id"), "orders", ["id"], unique=False)
    op.create_index(op.f("ix_orders_status"), "orders", ["status"], unique=False)

    op.create_table(
        "price_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=True),
        sa.Column("ends_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "ends_at IS NULL OR starts_at IS NULL OR ends_at >= starts_at",
            name="ck_price_sets_ends_at_after_starts_at",
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_sets_id"), "price_sets", ["id"], unique=False)
    op.create_index(op.f("ix_price_sets_product_id"), "price_sets", ["product_id"], unique=False)

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        sa.CheckConstraint("subtotal >= 0", name="ck_order_items_subtotal_non_negative"),
        sa.CheckConstraint("unit_price >= 0", name="ck_order_items_unit_price_non_negative"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_items_id"), "order_items", ["id"], unique=False)

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("amount >= 0", name="ck_payments_amount_non_negative"),
        sa.CheckConstraint(
            "method IN ('manual', 'bank_transfer', 'cash')",
            name="ck_payments_method_allowed",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'paid', 'failed', 'refunded')",
            name="ck_payments_status_allowed",
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id"),
    )
    op.create_index(op.f("ix_payments_id"), "payments", ["id"], unique=False)
    op.create_index(op.f("ix_payments_status"), "payments", ["status"], unique=False)

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
        sa.CheckConstraint("quantity > 0", name="ck_inventory_reservations_quantity_positive"),
        sa.CheckConstraint(
            "status IN ('active', 'released', 'committed', 'expired')",
            name="ck_inventory_reservations_status_allowed",
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["order_item_id"], ["order_items.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_reservations_id"), "inventory_reservations", ["id"], unique=False)
    op.create_index(
        op.f("ix_inventory_reservations_order_id"),
        "inventory_reservations",
        ["order_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_reservations_order_item_id"),
        "inventory_reservations",
        ["order_item_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_reservations_product_id"),
        "inventory_reservations",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_reservations_status"),
        "inventory_reservations",
        ["status"],
        unique=False,
    )

    op.create_table(
        "price_set_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("price_set_id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=True),
        sa.Column("region_id", sa.Integer(), nullable=True),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_price_set_items_price_non_negative"),
        sa.CheckConstraint("priority >= 0", name="ck_price_set_items_priority_non_negative"),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"]),
        sa.ForeignKeyConstraint(["price_set_id"], ["price_sets.id"]),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_set_items_channel_id"), "price_set_items", ["channel_id"], unique=False)
    op.create_index(op.f("ix_price_set_items_id"), "price_set_items", ["id"], unique=False)
    op.create_index(op.f("ix_price_set_items_price_set_id"), "price_set_items", ["price_set_id"], unique=False)
    op.create_index(op.f("ix_price_set_items_region_id"), "price_set_items", ["region_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_price_set_items_region_id"), table_name="price_set_items")
    op.drop_index(op.f("ix_price_set_items_price_set_id"), table_name="price_set_items")
    op.drop_index(op.f("ix_price_set_items_id"), table_name="price_set_items")
    op.drop_index(op.f("ix_price_set_items_channel_id"), table_name="price_set_items")
    op.drop_table("price_set_items")

    op.drop_index(op.f("ix_inventory_reservations_status"), table_name="inventory_reservations")
    op.drop_index(op.f("ix_inventory_reservations_product_id"), table_name="inventory_reservations")
    op.drop_index(op.f("ix_inventory_reservations_order_item_id"), table_name="inventory_reservations")
    op.drop_index(op.f("ix_inventory_reservations_order_id"), table_name="inventory_reservations")
    op.drop_index(op.f("ix_inventory_reservations_id"), table_name="inventory_reservations")
    op.drop_table("inventory_reservations")

    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_id"), table_name="payments")
    op.drop_table("payments")

    op.drop_index(op.f("ix_order_items_id"), table_name="order_items")
    op.drop_table("order_items")

    op.drop_index(op.f("ix_price_sets_product_id"), table_name="price_sets")
    op.drop_index(op.f("ix_price_sets_id"), table_name="price_sets")
    op.drop_table("price_sets")

    op.drop_index(op.f("ix_orders_status"), table_name="orders")
    op.drop_index(op.f("ix_orders_id"), table_name="orders")
    op.drop_table("orders")

    op.drop_index(op.f("ix_inventory_movements_reference_type"), table_name="inventory_movements")
    op.drop_index(op.f("ix_inventory_movements_reference_id"), table_name="inventory_movements")
    op.drop_index(op.f("ix_inventory_movements_product_id"), table_name="inventory_movements")
    op.drop_index(op.f("ix_inventory_movements_movement_type"), table_name="inventory_movements")
    op.drop_index(op.f("ix_inventory_movements_id"), table_name="inventory_movements")
    op.drop_table("inventory_movements")

    op.drop_index(op.f("ix_inventory_items_id"), table_name="inventory_items")
    op.drop_table("inventory_items")

    op.drop_index(op.f("ix_regions_id"), table_name="regions")
    op.drop_index(op.f("ix_regions_code"), table_name="regions")
    op.drop_table("regions")

    op.drop_index(op.f("ix_products_status"), table_name="products")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")

    op.drop_index(op.f("ix_customers_id"), table_name="customers")
    op.drop_index(op.f("ix_customers_email"), table_name="customers")
    op.drop_table("customers")

    op.drop_index(op.f("ix_channels_id"), table_name="channels")
    op.drop_index(op.f("ix_channels_code"), table_name="channels")
    op.drop_table("channels")
