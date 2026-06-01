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
    author: str
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
                    SELECT books.id, books.title, concat(authors.first_name, ' ', authors.last_name) as author,
                    date_published, count(*) as total_copies, (count(*) - checked.total) as copies_available
                    FROM book_inventory
                    JOIN books on book_inventory.book_id = books.id
                    JOIN authors on books.author_id = authors.id
                    JOIN checked on books.id = checked.book_id
                    WHERE active = true
                    GROUP BY books.id, authors.id, checked.total
                    ORDER BY books.title asc
                )
                SELECT id, title, author, date_published, total_copies, copies_available
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
                    author=bk.author,
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
                SELECT books.id, books.title, concat(authors.first_name, ' ', authors.last_name) as author,
                date_published, count(*) as total_copies, 
                (count(*) - SUM(CASE WHEN checkout_date IS NOT NULL AND returned_at IS NULL THEN 1 ELSE 0 END)) as copies_available
                FROM book_inventory
                JOIN books on book_inventory.book_id = books.id
                JOIN authors on books.author_id = authors.id
                LEFT JOIN checkouts on book_inventory_id = book_inventory.id
                WHERE active = TRUE
                GROUP BY books.id, authors.id
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
                    author=bk.author,
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
    order_by = db.book_log.c.title

    limit = 20
    if search_page != "":
        pageno = int(search_page)
    else:
        pageno = 1
    offset = (pageno - 1) * limit

    stmt = (
        sqlalchemy.select(
            db.book_log.c.id,
            db.book_log.c.title,
            db.book_log.c.author,
            db.book_log.c.copies_available,
            db.book_log.c.total_copies,
            db.book_log.c.date_published,
        )
        .limit(limit + 1)
        .offset(offset)
        .order_by(order_by, db.book_log.c.author)
    )

    if title != "":
        stmt = stmt.where(db.book_log.c.title.ilike(f"%{title}%"))
    if author != "":
        stmt = stmt.where(db.book_log.c.author.ilike(f"%{author}%"))

    items: List[CatalogItem] = []
    nextpage = False
    with db.engine.connect() as conn:
        books = conn.execute(stmt)
        i = 0
        for bk in books:
            if i == limit:
                nextpage = True
                break
            items.append(
                CatalogItem(
                    book_id=bk.id,
                    title=bk.title,
                    author=bk.author,
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
