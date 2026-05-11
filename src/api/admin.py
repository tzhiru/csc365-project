from fastapi import APIRouter, Depends, HTTPException, status
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


class CheckedOutBook(BaseModel):
    checkout_id: int
    book_id: int
    title: str
    author_first: str
    author_last: str
    copy_id: int
    checkout_date: str
    due_date: str


@router.get("/accounts/{account_id}/checkouts", response_model=List[CheckedOutBook])
def get_patron_checkouts(account_id: int) -> List[CheckedOutBook]:
    """
    Retrieve all books currently checked out by a specific patron.
    """
    checkouts: List[CheckedOutBook] = []

    with db.engine.begin() as connection:
        # Check if patron exists
        patron = connection.execute(
            sqlalchemy.text("SELECT id FROM patron_accounts WHERE id = :account_id"),
            {"account_id": account_id},
        ).fetchone()

        if not patron:
            raise HTTPException(status_code=404, detail="Patron account not found.")

        # Get checkouts
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT c.id as checkout_id, b.id as book_id, b.title, a.first_name as author_first, a.last_name as author_last,
                       c.book_inventory_id as copy_id, c.checkout_date, c.due_date
                FROM checkouts c
                JOIN book_inventory bi ON c.book_inventory_id = bi.id
                JOIN books b ON bi.book_id = b.id
                JOIN authors a ON b.author_id = a.id
                WHERE c.patron_id = :account_id AND c.returned_at IS NULL
                ORDER BY c.due_date ASC
                """
            ),
            {"account_id": account_id},
        )

        for row in results:
            checkouts.append(
                CheckedOutBook(
                    checkout_id=row.checkout_id,
                    book_id=row.book_id,
                    title=row.title,
                    author_first=row.author_first,
                    author_last=row.author_last,
                    copy_id=row.copy_id,
                    checkout_date=str(row.checkout_date),
                    due_date=str(row.due_date),
                )
            )

    return checkouts


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
