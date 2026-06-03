from fastapi import APIRouter, status, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)


class BookRequest(BaseModel):
    title: str
    author_id: int
    publisher_id: int
    date_published: str


class BookCopyRequest(BaseModel):
    book_id: int
    barcode: int


@router.post(
    "/add_book",
    tags=["inventory"],
    status_code=status.HTTP_201_CREATED,
)
def add_book(book: BookRequest):
    """
    Add a new book type to the catalog.
    """
    with db.engine.begin() as connection:
        author_exists = connection.execute(
            sqlalchemy.text("SELECT 1 FROM authors WHERE id = :author_id"),
            {"author_id": book.author_id},
        ).scalar()
        if not author_exists:
            raise HTTPException(status_code=404, detail="Author not found")

        pub_exists = connection.execute(
            sqlalchemy.text("SELECT 1 FROM publishers WHERE id = :publisher_id"),
            {"publisher_id": book.publisher_id},
        ).scalar()
        if not pub_exists:
            raise HTTPException(status_code=404, detail="Publisher not found")

        book_id = connection.execute(
            sqlalchemy.text(
                """
                WITH insert_book AS (
                    INSERT INTO books (title, author_id, publisher_id, date_published)
                    VALUES (:title, :author_id, :publisher_id, :date_published)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                )
                SELECT COALESCE(sum(id), 0) FROM insert_book
                """
            ),
            {
                "title": book.title,
                "author_id": book.author_id,
                "publisher_id": book.publisher_id,
                "date_published": book.date_published,
            },
        ).scalar_one()

        if book_id == 0:
            raise HTTPException(
                status_code=404, detail="Exact book type already exists."
            )

        return {"book_id": book_id, "success": True}


@router.post(
    "/add_copy",
    tags=["inventory"],
    status_code=status.HTTP_201_CREATED,
)
def add_book_copy(copy: BookCopyRequest):
    """
    Add a physical copy of an existing book to the inventory.
    """
    with db.engine.begin() as connection:
        book_exists = connection.execute(
            sqlalchemy.text("SELECT 1 FROM books WHERE id = :book_id"),
            {"book_id": copy.book_id},
        ).scalar()
        if not book_exists:
            raise HTTPException(status_code=404, detail="Book not found")

        barcode_exists = connection.execute(
            sqlalchemy.text("SELECT 1 FROM book_inventory WHERE barcode = :barcode"),
            {"barcode": copy.barcode},
        ).scalar()
        if barcode_exists:
            raise HTTPException(
                status_code=400, detail="Barcode already exists in inventory"
            )

        copy_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO book_inventory (book_id, barcode, active)
                VALUES (:book_id, :barcode, TRUE)
                RETURNING id
                """
            ),
            {
                "book_id": copy.book_id,
                "barcode": copy.barcode,
            },
        ).scalar_one()

        return {"copy_id": copy_id, "success": True}


@router.post(
    "/remove_book/{book_id}",
    tags=["inventory"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_book(book_id: int):
    """
    Remove a book type from the catalog by marking all active copies in the catalog as inactive.
    Fails if there are copies of the book currently checked out.
    """
    print(f"removing book from catalog. id: {book_id}")
    with db.engine.begin() as connection:
        checkouts = connection.execute(
            sqlalchemy.text(
                """
                SELECT count(*)
                FROM checkouts
                JOIN book_inventory ON book_inventory_id = book_inventory.id
                WHERE returned_at IS NULL AND book_id = :book_id
            """
            ),
            [{"book_id": book_id}],
        ).scalar_one()

        if checkouts > 0:
            raise HTTPException(
                status_code=404,
                detail="There are copies of this book currently checked out.",
            )

        copies = connection.execute(
            sqlalchemy.text(
                """
                UPDATE book_inventory
                SET active = FALSE
                WHERE book_id = :book_id AND active = TRUE
                RETURNING id
            """
            ),
            [{"book_id": book_id}],
        )

        if copies.rowcount == 0:
            raise HTTPException(
                status_code=404, detail="No copies of the book were found"
            )


@router.post(
    "/remove_copy/{book_copy_id}",
    tags=["inventory"],
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
