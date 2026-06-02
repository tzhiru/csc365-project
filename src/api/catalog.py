from fastapi import APIRouter, Depends, HTTPException
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


<<<<<<< HEAD
@router.get("/search/", response_model=PageResponse, tags=["catalog"])
=======
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
                date_published, count(*) as total_copies, GREATEST((count(*) - checked.total as copies_available), 0)
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
>>>>>>> 78fbff9 (Adarsh code review updates)
def search_catalog(
    title: str = "",
    author: str = "",
    available_only: bool = True,
    search_page: str = "",
):
    """
    Search the catalog by title and/or author name.
    Searching by title is by prefix.
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
        .where(db.book_log.c.total_copies > 0)
        .limit(limit + 1)
        .offset(offset)
        .order_by(order_by, db.book_log.c.author)
    )

    if title != "":
        stmt = stmt.where(db.book_log.c.title.ilike(f"{title}%"))
    if author != "":
        stmt = stmt.where(db.book_log.c.author.ilike(f"%{author}%"))
    if available_only:
        stmt = stmt.where(db.book_log.c.copies_available > 0)

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


@router.get("/{book_id}", response_model=CatalogItem, tags=["catalog"])
def get_book_details(book_id: int):
    """
    Retrieve detailed information for a specific book by ID.
    """
    with db.engine.connect() as conn:
        book = conn.execute(
            sqlalchemy.select(
                db.book_log.c.id,
                db.book_log.c.title,
                db.book_log.c.author,
                db.book_log.c.copies_available,
                db.book_log.c.total_copies,
                db.book_log.c.date_published,
            ).where(db.book_log.c.id == book_id)
        ).fetchone()

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        return CatalogItem(
            book_id=book.id,
            title=book.title,
            author=book.author,
            copies_available=book.copies_available,
            total_copies=book.total_copies,
            date_published=str(book.date_published),
        )
