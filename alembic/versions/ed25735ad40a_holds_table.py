"""holds table

Revision ID: ed25735ad40a
Revises: 9c9fb3dc8b22
Create Date: 2026-05-25 23:24:05.174547

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision: str = "ed25735ad40a"
down_revision: Union[str, None] = "9c9fb3dc8b22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "holds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "patron_id",
            sa.Integer(),
            sa.ForeignKey("patron_accounts.id"),
            nullable=False,
        ),
        sa.Column(
            "book_id",
            sa.Integer(),
            sa.ForeignKey("books.id"),
            nullable=False,
        ),
        sa.Column(
            "creation_date", sa.DATE(), nullable=False, server_default=func.now()
        ),
        sa.Column("expected_date", sa.DATE(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="yes"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("holds")
