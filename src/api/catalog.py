from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
    dependencies=[Depends(auth.get_api_key)],
)


class CatalogItem(BaseModel):
    book_id: int
    title: str
    author_first: str
    author_last: str
    copies_available: int
    total_copies: int
    date_published: str


class AvailableBook(BaseModel):
    book_id: int
    title: str
    author_first: str
    author_last: str
    copies_available: int
    date_published: str


@router.get("/available/", response_model=List[AvailableBook])
def get_available_books() -> List[AvailableBook]:
    """
    Retrieves a list of available book copies in the inventory.
    """
    with db.engine.begin() as connection:
        books = connection.execute(
            sqlalchemy.text(
                """
                SELECT books.id, books.title, authors.first_name as f, authors.last_name as l,
                books.date_published, COUNT(bi.id) AS copies_available
                FROM books
                JOIN authors ON books.author_id = authors.id
                JOIN book_inventory bi ON bi.book_id = books.id
                WHERE bi.active = TRUE AND bi.id NOT IN (
                    SELECT book_inventory_id
                    FROM checkouts
                    WHERE returned_at IS NULL)
                GROUP BY books.id, books.title, authors.first_name, authors.last_name, books.date_published
                HAVING COUNT(bi.id) > 0
                ORDER BY books.title ASC
                """
            )
        )

        return [
            AvailableBook(
                book_id=bk.id,
                title=bk.title,
                author_first=bk.f,
                author_last=bk.l,
                date_published=str(bk.date_published),
                copies_available=bk.copies_available,
            )
            for bk in books
        ]


@router.get("/full_catalog/", tags=["catalog"], response_model=List[CatalogItem])
def get_books() -> List[CatalogItem]:
    """
    Show all books, total copies, and currently avaliable copies.
    """

    with db.engine.begin() as connection:
        books = connection.execute(
            sqlalchemy.text(
                """
                WITH checked (book_id, total) AS (
                    SELECT book_id, 
                    SUM(CASE WHEN checkout_date IS NOT NULL AND returned_at IS NULL THEN 1 ELSE 0 END) as total
                    FROM book_inventory
                    LEFT JOIN checkouts on book_inventory_id = book_inventory.id
                    GROUP BY book_id
                    ORDER BY book_id
                )
                SELECT books.id, books.title, authors.first_name as f, authors.last_name as l,
                date_published, count(*) as total_copies, count(*) - checked.total as copies_available
                FROM book_inventory
                JOIN books on book_inventory.book_id = books.id
                JOIN authors on books.author_id = authors.id
                JOIN checked on books.id = checked.book_id
                WHERE active = TRUE
                GROUP BY books.id, authors.id, checked.total
                ORDER BY books.title ASC
                """
            )
        )
        return [
            CatalogItem(
                book_id=bk.id,
                title=bk.title,
                author_first=bk.f,
                author_last=bk.l,
                copies_available=bk.copies_available,
                total_copies=bk.total_copies,
                date_published=str(bk.date_published),
            )
            for bk in books
        ]

@router.get("/search/", response_model=List[CatalogItem])
def search_catalog(
    title: Optional[str] = None,
    author: Optional[str] = None,
) -> List[CatalogItem]:
    """
    Search the catalog by title and/or author name.
    Returns all matching books with how many active copies are currently available.
    """
    results: List[CatalogItem] = []

    with db.engine.begin() as connection:
        books = connection.execute(
            sqlalchemy.text(
                """
                WITH checked (book_id, total) AS (
                    SELECT book_id, 
                    SUM(CASE WHEN checkout_date IS NOT NULL AND returned_at IS NULL THEN 1 ELSE 0 END) as total
                    FROM book_inventory
                    LEFT JOIN checkouts on book_inventory_id = book_inventory.id
                    GROUP BY book_id
                    ORDER BY book_id
                )
                SELECT books.id, books.title, authors.first_name as f, authors.last_name as l,
                date_published, count(*) as total_copies, count(*) - checked.total as copies_available
                FROM book_inventory
                JOIN books on book_inventory.book_id = books.id
                JOIN authors on books.author_id = authors.id
                JOIN checked on books.id = checked.book_id
                WHERE active = TRUE
                AND (books.title = :title OR (authors.first_name = :author OR authors.last_name = :author))
                GROUP BY books.id, authors.id, checked.total
                ORDER BY books.title ASC
                """
            ),
            {"title": title, "author": author},
        )

        for bk in books:
            results.append(
                CatalogItem(
                    book_id=bk.id,
                    title=bk.title,
                    author_first=bk.f,
                    author_last=bk.l,
                    date_published=str(bk.date_published),
                    copies_available=bk.copies_available,
                    total_copies=bk.total_copies,
                )
            )

    return results
