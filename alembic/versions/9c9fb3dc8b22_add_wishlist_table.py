"""add wishlist table

Revision ID: 9c9fb3dc8b22
Revises: fbba464b78a3
Create Date: 2026-05-25 23:18:04.766955

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c9fb3dc8b22"
down_revision: Union[str, None] = "fbba464b78a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wishlist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "patron_id",
            sa.Integer(),
            sa.ForeignKey("patron_accounts.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("requested_at", sa.DATE(), nullable=False),
        sa.Column("fulfilled", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_table("wishlist")
