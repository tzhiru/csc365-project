"""initial setup. patron accounts

Revision ID: 103454e1f1ca
Revises:
Create Date: 2026-05-04 13:31:05.941591

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "103454e1f1ca"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "patron_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=False),
    )
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
    )
    op.create_table(
        "publishers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
    )
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column(
            "author_id", sa.Integer(), sa.ForeignKey("authors.id"), nullable=False
        ),
        sa.Column(
            "publisher_id", sa.Integer(), sa.ForeignKey("publishers.id"), nullable=False
        ),
        sa.Column("date_published", sa.DATE(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("patron_accounts")
    op.drop_table("books")
    op.drop_table("publishers")
    op.drop_table("authors")
