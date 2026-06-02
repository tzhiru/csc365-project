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


@router.get("/search/", response_model=PageResponse, tags=["catalog"])
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
