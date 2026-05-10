from fastapi import APIRouter, status, Depends, HTTPException
import sqlalchemy
from src.api import auth
from src import database as db
# from pydantic import BaseModel

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

# inventory management


@router.post(
    "/remove_book/{book_id}",
    tags=["inventory"],
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
