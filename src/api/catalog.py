from fastapi import APIRouter, status, Depends
from pydantic import BaseModel
from typing import List
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
    date_published: str


@router.get("/catalog/", tags=["catalog"], response_model=List[CatalogItem])
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
                date_published
                FROM books
                JOIN authors on books.author_id = authors.id
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
                    date_published=str(bk.date_published),
                )
            )

    return newCatalog


@router.post(
    "/catalog/remove/{book_id}",
    tags=["catalog"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_book(book_id: int):
    print(f"removing book. id: {book_id}")
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM books
                WHERE id = :book_id
            """
            ),
            [{"book_id": book_id}],
        )
    # to do: make this be for copies in inventory not the actual book info entries
    # also put this in another file later so that you need the api key to do this
