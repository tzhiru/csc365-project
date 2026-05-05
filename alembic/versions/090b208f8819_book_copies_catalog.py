"""book copies, catalog

Revision ID: 090b208f8819
Revises: 103454e1f1ca
Create Date: 2026-05-04 22:09:50.129721

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "090b208f8819"
down_revision: Union[str, None] = "103454e1f1ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "book_inventory",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id"), nullable=False),
        sa.Column("barcode", sa.Integer(), nullable=False),
        sa.Column("added_at", sa.DATE(), nullable=False),
    )
    # this is for individual copies of books
    # no need for status since we can look at the table of checkouts in the future


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("book_inventory")
