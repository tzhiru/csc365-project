"""book copies have status

Revision ID: f456fe3ccf2a
Revises: 090b208f8819
Create Date: 2026-05-09 17:31:01.324781

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f456fe3ccf2a"
down_revision: Union[str, None] = "090b208f8819"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "book_inventory",
        sa.Column("active", sa.Boolean(), nullable=False, server_default="yes"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("book_inventory", "active")
