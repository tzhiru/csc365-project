from http.client import HTTPException
from unittest import result

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

class PatronAccount(BaseModel):
    account_id: int
    first_name: str
    last_name: str
    phone_number: str
    address: str

@router.get("/accounts/{account_id}", response_model=PatronAccount)
def get_patron_account(account_id: int) -> PatronAccount:
    """
    Retrieve a specific patron account by ID.
    """
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, first_name, last_name, phone, address
                FROM patron_accounts
                WHERE id = :account_id
                """
            ),
            {"account_id": account_id},
            
        ).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Patron account not found.")
        
        return PatronAccount(
            account_id=row.id,
            first_name=row.first_name,
            last_name=row.last_name,
            phone_number=row.phone,
            address=row.address,
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
