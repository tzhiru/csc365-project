from fastapi import APIRouter, status, Depends, HTTPException
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
    availableBooks: List[AvailableBook] = []

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

        for bk in books:
            availableBooks.append(
                AvailableBook(
                    book_id=bk.id,
                    title=bk.title,
                    author_first=bk.f,
                    author_last=bk.l,
                    date_published=str(bk.date_published),
                    copies_available=bk.copies_available,
                )
            )

    return availableBooks


@router.get("/search/", response_model=List[AvailableBook])
def search_catalog(
    title: Optional[str] = None,
    author: Optional[str] = None,
) -> List[AvailableBook]:
    """
    Search the catalog by title and/or author name.
    Returns all matching books with how many active copies are currently available.
    """
    results: List[AvailableBook] = []

    with db.engine.begin() as connection:
        books = connection.execute(
            sqlalchemy.text(
                """
                SELECT books.id, books.title, authors.first_name AS f,
                authors.last_name AS l, books.date_published,
                COUNT(bi.id) FILTER (WHERE bi.active = TRUE
                   AND bi.id NOT IN (SELECT book_inventory_id FROM checkouts WHERE returned_at IS NULL)
                    ) AS copies_available
                FROM books
                JOIN authors ON books.author_id = authors.id
                LEFT JOIN book_inventory bi ON bi.book_id = books.id
                WHERE
                    (:title IS NULL OR books.title ILIKE '%' || :title || '%')
                    AND (
                        :author IS NULL
                        OR authors.first_name ILIKE '%' || :author || '%'
                        OR authors.last_name ILIKE '%' || :author || '%'
                    )
                GROUP BY books.id, books.title, authors.first_name, authors.last_name, books.date_published
                ORDER BY books.title ASC
                """
            ),
            {"title": title, "author": author},
        )

        for bk in books:
            results.append(
                AvailableBook(
                    book_id=bk.id,
                    title=bk.title,
                    author_first=bk.f,
                    author_last=bk.l,
                    date_published=str(bk.date_published),
                    copies_available=bk.copies_available,
                )
            )

    return results
