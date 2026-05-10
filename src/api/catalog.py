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


@router.get("/avaliable/", tags=["catalog"], response_model=List[CatalogItem])
def get_catalog() -> List[CatalogItem]:
    """
    Retrieves the catalog of items. Each unique item combination should have only a single price.
    You can have at most 6 potion SKUs offered in your catalog at one time.
    """
    newCatalog: List[CatalogItem] = []

    with db.engine.begin() as connection:
        books = connection.execute(
            sqlalchemy.text(
                """
                SELECT books.id, books.title, authors.first_name as f, authors.last_name as l,
                date_published, count(*) as total_copies
                FROM book_inventory
                JOIN books on book_inventory.book_id = books.id
                JOIN authors on books.author_id = authors.id
                WHERE active = TRUE
                GROUP BY books.id, authors.id
                ORDER BY books.title ASC
                """
            )
        )

        # later actually have it based on what copies of books are actually in store, display how many copies avaliable.

        for bk in books:
            newCatalog.append(
                CatalogItem(
                    book_id=bk.id,
                    title=bk.title,
                    author_first=bk.f,
                    author_last=bk.l,
                    total_copies=bk.total_copies,
                    date_published=str(bk.date_published),
                )
            )

    return newCatalog


@router.post(
    "/remove_book/{book_id}",
    tags=["catalog"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_book(book_id: int):
    """
    Remove a book type from the catalog.
    """
    print(f"removing book from catalog. id: {book_id}")
    with db.engine.begin() as connection:
        update = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM books
                WHERE id = :book_id
                RETURNING id
            """
            ),
            [{"book_id": book_id}],
        )
        if update.rowcount == 0:
            raise HTTPException(status_code=404, detail="Book not found")
    # also put this in another file later so that you need the api key to do this


@router.post(
    "/remove_copy/{book_id}",
    tags=["catalog"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_book_copy(book_copy_id: int):
    """
    Marks book copy from inventory as inactive/unavaliable.
    """
    print(f"remove book copy. id: {book_copy_id}")
    with db.engine.begin() as connection:
        update = connection.execute(
            sqlalchemy.text(
                """
                UPDATE book_inventory
                SET active = FALSE
                WHERE id = :book_copy_id
                RETURNING id
            """
            ),
            [{"book_copy_id": book_copy_id}],
        )
        if update.rowcount == 0:
            raise HTTPException(status_code=404, detail="Book copy not found")


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


class CheckoutRequest(BaseModel):
    patron_id: int


class CheckoutResponse(BaseModel):
    success: bool
    checkout_id: int
    due_date: str

@router.post("/checkout/{book_id}", response_model=CheckoutResponse)
def checkout_book(book_id: int, request: CheckoutRequest):
    """
    checks out an available copy for a patron. Verifies the patron account
    exists and that a copy is available. The due date is set to 2 weeks from checkout date."""
    
    with db.engine.begin() as connection: 
        # check if patron exists
        patron = connection.execute(
            sqlalchemy.text(
                
                "SELECT id FROM patron_accounts WHERE id = :patron_id"
            ),
            {"patron_id": request.patron_id},
        ).fetchone()
        if not patron:
            raise HTTPException(status_code=404, detail="Patron account not found.")
        
        # find an available copy of the book
        available_copy = connection.execute(
            sqlalchemy.text(
                """
                SELECT bi.id
                FROM book_inventory bi
                WHERE bi.book_id = :book_id AND bi.active = TRUE
                    AND bi.id NOT IN (
                        SELECT book_inventory_id 
                        FROM checkouts 
                        WHERE returned_at IS NULL
                    )
                LIMIT 1
                """
            ),
            {"book_id": book_id},

        ).fetchone()

        if not available_copy:
            raise HTTPException(status_code=409, 
                                detail="No copies of this book are available currently.",)
        
        # create the checkout record with due date 2 weeks from now
        checkout = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO checkouts (patron_id, book_inventory_id, checkout_date, due_date)
                VALUES (:patron_id, :copy_id, CURRENT_DATE, CURRENT_DATE + INTERVAL '14 days')
                RETURNING id, due_date
                """
            ),
            {"patron_id": request.patron_id, "copy_id": available_copy.id},
        ).one()

    return CheckoutResponse(success=True, checkout_id=checkout.id, due_date=str(checkout.due_date))

