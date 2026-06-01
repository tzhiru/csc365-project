"""revised search view

Revision ID: 219c3ba26e66
Revises: 2c54337e0b17
Create Date: 2026-06-01 15:33:34.916907

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "219c3ba26e66"
down_revision: Union[str, None] = "2c54337e0b17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text("DROP VIEW book_log"))
    op.execute(
        sa.text(
            """
            CREATE VIEW book_log
            AS (
                SELECT books.id, books.title, concat(authors.first_name, ' ', authors.last_name) as author,
                date_published, count(*) as total_copies, 
                (count(*) - SUM(CASE WHEN checkout_date IS NOT NULL AND returned_at IS NULL THEN 1 ELSE 0 END)) as copies_available
                FROM book_inventory
                JOIN books on book_inventory.book_id = books.id
                JOIN authors on books.author_id = authors.id
                LEFT JOIN checkouts on book_inventory_id = book_inventory.id
                WHERE active = TRUE
                GROUP BY books.id, authors.id
                )
            """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text("DROP VIEW book_log"))
    op.execute(
        sa.text(
            """
            CREATE VIEW book_log
            AS (
                WITH checked AS (
                    SELECT book_id, 
                    SUM(CASE WHEN checkout_date IS NOT NULL AND returned_at IS NULL THEN 1 ELSE 0 END) as total
                    FROM book_inventory
                    LEFT JOIN checkouts on book_inventory_id = book_inventory.id
                    GROUP BY book_id
                )
                SELECT books.id, books.title, concat(authors.first_name, ' ', authors.last_name) as author,
                date_published, count(*) as total_copies, (count(*) - checked.total) as copies_available
                FROM book_inventory
                JOIN books on book_inventory.book_id = books.id
                JOIN authors on books.author_id = authors.id
                JOIN checked on books.id = checked.book_id
                WHERE active = TRUE
                GROUP BY books.id, authors.id, checked.total
                )
            """
        )
    )
