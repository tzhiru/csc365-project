from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/wishlist",
    tags=["wishlist"],
    dependencies=[Depends(auth.get_api_key)],
)


class AcquisitionRequest(BaseModel):
    patron_id: int
    title: str
    author: str | None = (
        None  # author can be optional since some patrons might just enter a title without knowing the author
    )


class AcquisitionResponse(BaseModel):
    success: bool
    message: str
    wishlist_id: int | None = None


class WishlistItem(BaseModel):
    wishlist_id: int
    patron_id: int
    title: str
    author: str | None
    requested_at: str
    fulfilled: bool


class PageResponse(BaseModel):
    previous: Optional[str] = None
    next: Optional[str] = None
    results: List[WishlistItem]


@router.post("/request/", response_model=AcquisitionResponse)
def request_acquisition(request: AcquisitionRequest):

    with db.engine.begin() as connection:
        # 1 verifies patron exists
        patron = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM patron_accounts
                WHERE id = :patron_id
                """
            ),
            {"patron_id": request.patron_id},
        ).fetchone()

        if not patron:
            raise HTTPException(status_code=404, detail="Patron account not found.")

        # 2 checks if the book already exists in the catalog
        existing_book = connection.execute(
            sqlalchemy.text(
                """
                SELECT books.id FROM books
                JOIN authors ON books.author_id = authors.id
                WHERE books.title = :title
                LIMIT 1 
                """
            ),
            {"title": request.title},
        ).fetchone()

        if existing_book:
            raise HTTPException(
                status_code=409,
                detail=f"'{request.title}' already exists in the catalog. You can check it out or place a hold if it's currently unavailable.",
            )

        # 3 checks if same patron already requested this title
        duplicate = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM wishlist
                WHERE patron_id = :patron_id 
                AND title = :title
                AND fulfilled = FALSE
                """
            ),
            {"patron_id": request.patron_id, "title": request.title},
        ).fetchone()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="You have already requested this book.",
            )

        # 4 checks if another patron already requested it
        other_requests = connection.execute(
            sqlalchemy.text(
                """
                SELECT COUNT(*) as total FROM wishlist
                WHERE title = :title
                AND fulfilled = FALSE
                """
            ),
            {"title": request.title},
        ).fetchone()
        assert other_requests is not None  # for type checker

        already_requested = other_requests.total > 0

        # 5 Add to wishlist
        new_request = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO wishlist (patron_id, title, author, requested_at, fulfilled)
                VALUES (:patron_id, :title, :author, CURRENT_DATE, FALSE)
                RETURNING id
                """
            ),
            {
                "patron_id": request.patron_id,
                "title": request.title,
                "author": request.author,
            },
        ).fetchone()
        assert new_request is not None  # for type checker

        if already_requested:
            message = f"'{request.title}' has been added to the wishlist. This title has already been requested by another patron."

        else:
            message = f"'{request.title}' has been added to the wishlist."

    return AcquisitionResponse(
        success=True,
        message=message,
        wishlist_id=new_request.id,
    )


@router.get("/", response_model=PageResponse)
def get_wishlist(search_page: str = ""):
    """
    Admin view of all pending acquisition requests in the wishlist ordered alpabetically by title.
    """
    items: List[WishlistItem] = []
    nextpage = False
    limit = 20  # amount of results per page
    if search_page != "":
        pageno = int(search_page)
    else:
        pageno = 1
    offset = (pageno - 1) * limit
    with db.engine.begin() as connection:
        i = 0
        wishlist_results = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, patron_id, title, author, requested_at, fulfilled
                FROM wishlist
                WHERE fulfilled = FALSE
                ORDER BY title ASC
                OFFSET :offset
                """
            ),
            [{"offset": offset}],
        )
        for row in wishlist_results:
            if i == limit:
                nextpage = True
                break
            items.append(
                WishlistItem(
                    wishlist_id=row.id,
                    patron_id=row.patron_id,
                    title=row.title,
                    author=row.author,
                    requested_at=str(row.requested_at),
                    fulfilled=row.fulfilled,
                )
            )
            i += 1
    if pageno <= 1:
        previous = None
    else:
        previous = str(pageno - 1)

    if nextpage:
        next = str(pageno + 1)
    else:
        next = None

    return PageResponse(previous=previous, next=next, results=items)


@router.post("/{wishlist_id}/fulfill/", response_model=AcquisitionResponse)
def fulfill_request(wishlist_id: int):
    """
    Admin endpoint to mark a wishlist request as fulfilled. This would typically be called after the library has acquired the requested book.
    """
    with db.engine.begin() as connection:
        # Check if the wishlist item exists and is not already fulfilled
        request = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, title 
                FROM wishlist
                WHERE id = :wishlist_id
                """
            ),
            {"wishlist_id": wishlist_id},
        ).fetchone()

        if not request:
            raise HTTPException(status_code=404, detail="Wishlist item not found.")

        # mark the request as fulfilled
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE wishlist
                SET fulfilled = TRUE
                WHERE title = :title 
                """
            ),
            {"title": request.title},
        )

    return AcquisitionResponse(
        success=True,
        message=f"'{request.title}' has been marked as fulfilled.",
        wishlist_id=wishlist_id,
    )
