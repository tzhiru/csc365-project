from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src import database as db

router = APIRouter()


class CatalogItem(BaseModel):
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
                SELECT books.title, authors.first_name as f, authors.last_name as l,
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
                    title=bk.title,
                    author_first=bk.f,
                    author_last=bk.l,
                    date_published=bk.date_published,
                )
            )


    return newCatalog

def create_catalog() -> List[CatalogItem]:
    with db.engine.begin() as connection:
        catalog = connection.execute(
            sqlalchemy.text(
                """
                SELECT * FROM books
                """
            )
    ).fetchall()

    return catalog

@router.get("/catalog/available", tags=["catalog"], response_model=List[CatalogItem])
def get_catalog() -> List[CatalogItem]:
    """
    Retrieves the catalog of items. Each unique item combination should have only a single price.
    You can have at most 6 potion SKUs offered in your catalog at one time.
    """
    return create_catalog()

@router.post("/catalog/remove/{book_id}", status_code=status.HTTP_204_NO_CONTENT)  #fix response
def delete():
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM books
                WHERE id = :book_id
                """
            ), 
            [{"book_id": book_id}]
    )

