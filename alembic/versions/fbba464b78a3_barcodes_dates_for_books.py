"""barcodes, dates for books

Revision ID: fbba464b78a3
Revises: a1b2c3d4e5f6
Create Date: 2026-05-10 13:22:27.641970

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision: str = "fbba464b78a3"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("unique_barcode", "book_inventory", ["barcode"])
    op.drop_column("book_inventory", "added_at")
    op.add_column(
        "book_inventory",
        sa.Column(
            "added_at", sa.DATE(), nullable=False, server_default=func.current_date()
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("unique_barcode", "book_inventory")
    op.drop_column("book_inventory", "added_at")
    op.add_column("book_inventory", sa.Column("added_at", sa.DATE(), nullable=False))
