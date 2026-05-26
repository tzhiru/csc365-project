""" add wishlist table
Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-24 12:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "wishlist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patron_id", sa.Integer(), sa.ForeignKey("patron_accounts.id"), nullable=False,),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("requested_at", sa.DATE(), nullable=False),
        sa.Column("fulfilled", sa.Boolean(), nullable=False, server_default="false"),
    )       

def downgrade() -> None:
    op.drop_table("wishlist")