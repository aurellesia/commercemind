"""update order and payment statuses

Revision ID: 20260424_0002
Revises: 20260424_0001
Create Date: 2026-04-24
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260424_0002"
down_revision: Union[str, None] = "20260424_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE orders SET status = 'paid' WHERE status = 'confirmed'")
    op.execute("UPDATE payments SET status = 'pending' WHERE status = 'unpaid'")

    op.drop_constraint("ck_orders_status_allowed", "orders", type_="check")
    op.create_check_constraint(
        "ck_orders_status_allowed",
        "orders",
        "status IN ('pending', 'awaiting_payment', 'paid', 'processing', 'fulfilled', 'completed', 'cancelled')",
    )

    op.drop_constraint("ck_payments_status_allowed", "payments", type_="check")
    op.create_check_constraint(
        "ck_payments_status_allowed",
        "payments",
        "status IN ('pending', 'paid', 'failed', 'refunded')",
    )


def downgrade() -> None:
    op.execute("UPDATE orders SET status = 'confirmed' WHERE status = 'paid'")
    op.execute("UPDATE orders SET status = 'pending' WHERE status IN ('awaiting_payment', 'processing')")
    op.execute("UPDATE payments SET status = 'unpaid' WHERE status = 'pending'")

    op.drop_constraint("ck_payments_status_allowed", "payments", type_="check")
    op.create_check_constraint(
        "ck_payments_status_allowed",
        "payments",
        "status IN ('unpaid', 'paid', 'failed', 'refunded')",
    )

    op.drop_constraint("ck_orders_status_allowed", "orders", type_="check")
    op.create_check_constraint(
        "ck_orders_status_allowed",
        "orders",
        "status IN ('pending', 'confirmed', 'fulfilled', 'cancelled', 'completed')",
    )
