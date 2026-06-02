"""
API router for managing book checkouts and returns.
Includes endpoints for checking out books (with hold/priority validation)
and returning books, plus viewing currently active checkouts.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/checkout",
    tags=["checkout"],
    dependencies=[Depends(auth.get_api_key)],
)


class CheckoutRequest(BaseModel):
    patron_id: int


class CheckoutResponse(BaseModel):
    success: bool
    checkout_id: int
    due_date: str
    copy_id: int


class ReturnResponse(BaseModel):
    success: bool
    checkout_id: int
    patron_id: int
    copy_id: int


class ActiveCheckoutItem(BaseModel):
    checkout_id: int
    book_id: int
    title: str
    author: str
    patron_id: int
    patron_name: str
    copy_id: int
    due_date: str


@router.post("/{book_id}", response_model=CheckoutResponse)
def checkout_book(book_id: int, request: CheckoutRequest):
    """
    checks out an available copy for a patron. Verifies the patron account
    exists and that a copy is available. The due date is set to 2 weeks from checkout date.
    """

    with db.engine.begin() as connection:
        # check if patron exists
        patron = connection.execute(
            sqlalchemy.text("SELECT id FROM patron_accounts WHERE id = :patron_id"),
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
                FOR UPDATE SKIP LOCKED
                """
            ),
            {"book_id": book_id},
        )

        copies = available_copy.rowcount

        if copies == 0:
            raise HTTPException(
                status_code=409,
                detail="No copies of this book are available currently.",
            )

        i = 0
        for row in available_copy:
            loan = row.id
            i += 1
            if i > 0:
                break

        hold_check = connection.execute(
            sqlalchemy.text(
                """
                SELECT patron_id
                FROM holds
                WHERE active = TRUE AND book_id = :book_id
                ORDER BY creation_date ASC
                LIMIT :limit
                """
            ),
            {"book_id": book_id, "limit": copies},
        )

        if hold_check.rowcount != 0:
            holding_users = []
            for row in hold_check:
                holding_users.append(row.patron_id)

            if request.patron_id not in holding_users:
                print(" --- Checkout failed bc hold priority")
                raise HTTPException(
                    status_code=403,
                    detail="This book copy is being held for another user.",
                )
            else:
                # fulfill hold.
                print(f" --- Fulfill hold by user {request.patron_id} book {book_id}")
                connection.execute(
                    sqlalchemy.text(
                        """
                        UPDATE holds
                        SET active = FALSE
                        WHERE book_id = :book_id AND patron_id = :patron_id AND active = TRUE
                        """
                    ),
                    {"book_id": book_id, "patron_id": request.patron_id},
                )

        # create the checkout record with due date 2 weeks from now
        checkout = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO checkouts (patron_id, book_inventory_id, checkout_date, due_date)
                VALUES (:patron_id, :copy_id, CURRENT_DATE, CURRENT_DATE + INTERVAL '14 days')
                RETURNING id, due_date
                """
            ),
            {"patron_id": request.patron_id, "copy_id": loan},
        ).one()

    return CheckoutResponse(
        success=True,
        checkout_id=checkout.id,
        due_date=str(checkout.due_date),
        copy_id=loan,
    )


@router.post("/return/{book_copy_id}", response_model=ReturnResponse)
def return_book(book_copy_id: int):
    """
    Returns a checked out book (via copy id).
    """

    with db.engine.begin() as connection:
        find_checkout = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, patron_id
                FROM checkouts
                WHERE book_inventory_id = :copy AND returned_at IS NULL
                LIMIT 1
                """
            ),
            {"copy": book_copy_id},
        ).fetchone()

        if not find_checkout:
            raise HTTPException(
                status_code=409,
                detail="This book copy is not currently checked out.",
            )

        connection.execute(
            sqlalchemy.text(
                """
                UPDATE checkouts
                SET returned_at = CURRENT_DATE
                WHERE id = :checkout_id
                """
            ),
            {"checkout_id": find_checkout.id},
        )

    return ReturnResponse(
        success=True,
        checkout_id=find_checkout.id,
        patron_id=find_checkout.patron_id,
        copy_id=book_copy_id,
    )


@router.get("/active", response_model=List[ActiveCheckoutItem])
def get_active_checkouts():
    """
    Retrieves a list of all active checkouts in the library system.
    """
    items = []
    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT c.id AS checkout_id,
                       b.id AS book_id,
                       b.title,
                       concat(a.first_name, ' ', a.last_name) AS author,
                       pa.id AS patron_id,
                       concat(pa.first_name, ' ', pa.last_name) AS patron_name,
                       bi.id AS copy_id,
                       c.due_date
                FROM checkouts c
                JOIN book_inventory bi ON c.book_inventory_id = bi.id
                JOIN books b ON bi.book_id = b.id
                JOIN authors a ON b.author_id = a.id
                JOIN patron_accounts pa ON c.patron_id = pa.id
                WHERE c.returned_at IS NULL
                ORDER BY c.due_date ASC
                """
            )
        )
        for row in results:
            items.append(
                ActiveCheckoutItem(
                    checkout_id=row.checkout_id,
                    book_id=row.book_id,
                    title=row.title,
                    author=row.author,
                    patron_id=row.patron_id,
                    patron_name=row.patron_name,
                    copy_id=row.copy_id,
                    due_date=str(row.due_date),
                )
            )
    return items
