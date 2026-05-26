from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from typing import List


router = APIRouter(
    prefix="/holds",
    tags=["holds"],
    dependencies=[Depends(auth.get_api_key)],
)

# holds: id, copy_id, patron_id, active (y/n), expected_date


class HoldRequest(BaseModel):
    patron_id: int


class HoldResponse(BaseModel):
    success: bool
    hold_id: int
    book_id: int
    expected_date: str


@router.post("/{book_id}", response_model=HoldResponse)
def place_hold(book_id: int, request: HoldRequest):
    """
    Places a hold on a book.
    A patron can only have 10 active holds at a time and 1 hold per book listing.
    A book listing can only have 5 active holds at a time.
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

        if available_copy:
            raise HTTPException(
                status_code=403,
                detail="This book is currently avaliable, request it via checkouts.",
            )

        # check if the user already has a hold on this book.
        dupe_hold_check = connection.execute(
            sqlalchemy.text(
                """
                SELECT book_id
                FROM holds
                WHERE patron_id = :patron_id AND active = TRUE AND book_id = :book_id
                LIMIT 1
                """
            ),
            {
                "book_id": book_id,
                "patron_id": request.patron_id,
            },
        ).one()

        if dupe_hold_check:
            raise HTTPException(
                status_code=403,
                detail="This patron already has an active hold on this book.",
            )

        # check how many active holds the user currently has
        user_current_holds = connection.execute(
            sqlalchemy.text(
                """
                SELECT COUNT(*) AS total_holds
                FROM holds
                WHERE patron_id = :patron_id AND active = TRUE
                """
            ),
            {
                "patron_id": request.patron_id,
            },
        ).one()

        if user_current_holds.total_holds >= 10:
            raise HTTPException(
                status_code=403,
                detail="This patron has reached the maximum of 10 holds.",
            )

        # check how many holds the book type has (not the copy)
        book_current_holds = connection.execute(
            sqlalchemy.text(
                """
                SELECT COUNT(*) AS total_holds
                FROM holds
                WHERE book_id = :book_id AND active = TRUE
                """
            ),
            {
                "book_id": book_id,
            },
        ).one()

        if book_current_holds.total_holds >= 5:
            raise HTTPException(
                status_code=403,
                detail="This book already has 5 holds. You can create a hold on this book after preexisting holds are fufilled.",
            )

        # create the hold
        hold = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO holds (book_id, patron_id, expected_date)
                VALUES (:book_id, :patron_id, :date)
                RETURNING id, due_date
                """
            ),
            {
                "book_id": book_id,
                "patron_id": request.patron_id,
                "date": available_copy.id,
            },
        ).one()

    return HoldResponse(
        success=True,
        hold_id=hold.id,
        book_id=book_id,
        expected_date=str(hold.expected_date),
    )


class HoldData(BaseModel):
    hold_id: int
    patron_id: int
    expected_date: str


@router.get("/view_holds/{book_id}", response_model=List[HoldData])
def return_book(book_id: int):
    """
    Display all active holds for a certain book.
    """
    with db.engine.begin() as connection:
        book = connection.execute(
            sqlalchemy.text("SELECT id FROM books WHERE id = :book_id"),
            {"book_id": book_id},
        ).fetchone()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found.")

        res = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, patron_id, expected_date
                FROM holds
                WHERE book_id = :book_id AND active = TRUE
                ORDER BY id ASC
                """
            ),
            [{"book_id": book_id}],
        )
        return [
            HoldData(
                hold_id=row.id, patron_id=row.patron_id, expected_date=row.expected_date
            )
            for row in res
        ]
