from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
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
                LIMIT 1
                """
            ),
            {"book_id": book_id},
        ).fetchone()

        if not available_copy:
            raise HTTPException(
                status_code=409,
                detail="No copies of this book are available currently.",
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
            {"patron_id": request.patron_id, "copy_id": available_copy.id},
        ).one()

    return CheckoutResponse(
        success=True,
        checkout_id=checkout.id,
        due_date=str(checkout.due_date),
        copy_id=available_copy.id,
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
