"""add_invoices_tables

Revision ID: 17ab84ac99cc
Revises: 511b87626f27
Create Date: 2025-11-26 17:55:28.565722

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '17ab84ac99cc'
down_revision: Union[str, None] = '511b87626f27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "invoices"):
        op.create_table(
            "invoices",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("state", mysql.TINYINT(display_width=1), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                server_onupdate=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("ticket_id", sa.Integer(), nullable=False),
            sa.Column("client_id", sa.Integer(), nullable=False),
            sa.Column("invoice_number", sa.String(length=40), nullable=False),
            sa.Column("issue_date", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("due_date", sa.DateTime(), nullable=True),
            sa.Column("parts_cost", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("labor_cost", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("tax_percentage", sa.Numeric(5, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("total", sa.Numeric(12, 2), nullable=False, server_default=sa.text("0")),
            sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'PENDING'")),
            sa.Column("created_by_id", sa.Integer(), nullable=True),
            sa.Column("paid_at", sa.DateTime(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], onupdate="CASCADE", ondelete="RESTRICT"),
            sa.ForeignKeyConstraint(["client_id"], ["users.id"], onupdate="CASCADE", ondelete="RESTRICT"),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], onupdate="CASCADE", ondelete="SET NULL"),
            sa.UniqueConstraint("invoice_number"),
        )
        op.create_index("ix_invoices_ticket_id", "invoices", ["ticket_id"])
        op.create_index("ix_invoices_client_id", "invoices", ["client_id"])
        op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"])

    if not _table_exists(bind, "invoice_payments"):
        op.create_table(
            "invoice_payments",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("state", mysql.TINYINT(display_width=1), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
                server_onupdate=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("invoice_id", sa.Integer(), nullable=False),
            sa.Column("amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("payment_method", sa.String(length=30), nullable=False),
            sa.Column("reference", sa.String(length=100), nullable=True),
            sa.Column("paid_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("created_by_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], onupdate="CASCADE", ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], onupdate="CASCADE", ondelete="SET NULL"),
        )
        op.create_index("ix_invoice_payments_invoice_id", "invoice_payments", ["invoice_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "invoice_payments" in inspector.get_table_names():
        op.drop_index("ix_invoice_payments_invoice_id", table_name="invoice_payments")
        op.drop_table("invoice_payments")

    if "invoices" in inspector.get_table_names():
        op.drop_index("ix_invoices_invoice_number", table_name="invoices")
        op.drop_index("ix_invoices_client_id", table_name="invoices")
        op.drop_index("ix_invoices_ticket_id", table_name="invoices")
        op.drop_table("invoices")
