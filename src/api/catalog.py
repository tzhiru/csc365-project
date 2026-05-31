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


class PageResponse(BaseModel):
    previous: Optional[str] = None
    next: Optional[str] = None
    results: List[CatalogItem]


@router.get("/available/", response_model=PageResponse)
def get_available_books(search_page: str = ""):
    """
    Retrieves a list of available book copies in the inventory.
    """
    items: List[CatalogItem] = []
    nextpage = False
    limit = 20  # amount of results per page
    if search_page != "":
        pageno = int(search_page)
    else:
        pageno = 1
    offset = (pageno - 1) * limit
    with db.engine.begin() as connection:
        i = 0
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
                ),
                data as (
                    SELECT books.id, books.title, authors.first_name as first, authors.last_name as last,
                    date_published, count(*) as total_copies, (count(*) - checked.total) as copies_available
                    FROM book_inventory
                    JOIN books on book_inventory.book_id = books.id
                    JOIN authors on books.author_id = authors.id
                    JOIN checked on books.id = checked.book_id
                    WHERE active = true
                    GROUP BY books.id, authors.id, checked.total
                    ORDER BY books.title asc
                )
                SELECT id, title, first, last, date_published, total_copies, copies_available
                FROM data
                WHERE copies_available > 0
                LIMIT :limit
                OFFSET :offset
                """
            ),
            [{"offset": offset, "limit": limit + 1}],
        )
        for bk in books:
            if i == limit:
                nextpage = True
                break
            items.append(
                CatalogItem(
                    book_id=bk.id,
                    title=bk.title,
                    author_first=bk.first,
                    author_last=bk.last,
                    copies_available=bk.copies_available,
                    total_copies=bk.total_copies,
                    date_published=str(bk.date_published),
                )
            )
            i += 1

    if pageno <= 1:
        previous = None
    else:
        previous = str(pageno - 1)

    if nextpage:
        next = str(pageno + 1)
    else:
        next = None

    return PageResponse(previous=previous, next=next, results=items)


@router.get("/full_catalog/", tags=["catalog"], response_model=PageResponse)
def get_books(search_page: str = ""):
    """
    Show all books, total copies, and currently avaliable copies.
    """
    items: List[CatalogItem] = []
    nextpage = False
    limit = 20  # amount of results per page
    if search_page != "":
        pageno = int(search_page)
    else:
        pageno = 1
    offset = (pageno - 1) * limit
    with db.engine.begin() as connection:
        i = 0
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
                SELECT books.id, books.title, authors.first_name as first, authors.last_name as last,
                date_published, count(*) as total_copies, (count(*) - checked.total) as copies_available
                FROM book_inventory
                JOIN books on book_inventory.book_id = books.id
                JOIN authors on books.author_id = authors.id
                JOIN checked on books.id = checked.book_id
                WHERE active = TRUE
                GROUP BY books.id, authors.id, checked.total
                ORDER BY books.title ASC
                LIMIT :limit
                OFFSET :offset
                """
            ),
            [{"offset": offset, "limit": limit + 1}],
        )
        for bk in books:
            if i == limit:
                nextpage = True
                break
            items.append(
                CatalogItem(
                    book_id=bk.id,
                    title=bk.title,
                    author_first=bk.first,
                    author_last=bk.last,
                    copies_available=bk.copies_available,
                    total_copies=bk.total_copies,
                    date_published=str(bk.date_published),
                )
            )
            i += 1

    if pageno <= 1:
        previous = None
    else:
        previous = str(pageno - 1)

    if nextpage:
        next = str(pageno + 1)
    else:
        next = None

    return PageResponse(previous=previous, next=next, results=items)


@router.get("/search/", response_model=PageResponse, tags=["catalog"])
def search_catalog(
    title: str = "",
    author: str = "",
    search_page: str = "",
):
    """
    Search the catalog by title and/or author name.
    Returns all matching books with how many active copies are currently available.
    """

    items: List[CatalogItem] = []
    nextpage = False
    limit = 20  # amount of results per page
    if search_page != "":
        pageno = int(search_page)
    else:
        pageno = 1
    offset = (pageno - 1) * limit

    with db.engine.begin() as connection:
        i = 0
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
                SELECT books.id, books.title, authors.first_name as first, authors.last_name as last,
                date_published, count(*) as total_copies, (count(*) - checked.total) as copies_available
                FROM book_inventory
                JOIN books on book_inventory.book_id = books.id
                JOIN authors on books.author_id = authors.id
                JOIN checked on books.id = checked.book_id
                WHERE active = TRUE
                AND (books.title = :title OR (authors.first_name = :author OR authors.last_name = :author))
                GROUP BY books.id, authors.id, checked.total
                ORDER BY books.title ASC
                LIMIT :limit
                OFFSET :offset
                """
            ),
            {"title": title, "author": author, "offset": offset, "limit": limit + 1},
        )
        for bk in books:
            if i == limit:
                nextpage = True
                break
            items.append(
                CatalogItem(
                    book_id=bk.id,
                    title=bk.title,
                    author_first=bk.first,
                    author_last=bk.last,
                    copies_available=bk.copies_available,
                    total_copies=bk.total_copies,
                    date_published=str(bk.date_published),
                )
            )
            i += 1

    if pageno <= 1:
        previous = None
    else:
        previous = str(pageno - 1)

    if nextpage:
        next = str(pageno + 1)
    else:
        next = None

    return PageResponse(previous=previous, next=next, results=items)
