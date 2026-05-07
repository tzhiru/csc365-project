from fastapi import APIRouter, Depends, status

import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset():
    """
    Full reset: clears all tables and restarts PKs.
    """
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                TRUNCATE TABLE 
                books, book_inventory,
                authors, publishers,
                patron_accounts
                RESTART IDENTITY
                """
            )
        )
