"""no identical book type row

Revision ID: 0093f834b1ef
Revises: 2c54337e0b17
Create Date: 2026-06-02 20:20:29.851303

"""

from typing import Sequence, Union

from alembic import op
# import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0093f834b1ef"
down_revision: Union[str, None] = "2c54337e0b17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "unique_book_rows",
        "books",
        ["title", "author_id", "publisher_id", "date_published"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("unique_book_rows", "books")
