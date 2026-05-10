"""add checkouts table

Revision ID: a1b2c3d4e5f6
Revises: f456fe3ccf2a
Create Date: 2026-05-09 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f456fe3ccf2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "checkouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "patron_id",
            sa.Integer(),
            sa.ForeignKey("patron_accounts.id"),
            nullable=False,
        ),
        sa.Column(
            "book_inventory_id",
            sa.Integer(),
            sa.ForeignKey("book_inventory.id"),
            nullable=False,
        ),
        sa.Column("checkout_date", sa.DATE(), nullable=False),
        sa.Column("due_date", sa.DATE(), nullable=False),
        sa.Column("returned_at", sa.DATE(), nullable=True),  # NULL = still checked out
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("checkouts")
