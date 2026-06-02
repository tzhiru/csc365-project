from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(auth.get_api_key)],
)


class PatronAccountInfo(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    address: str


class AccountItem(BaseModel):
    patron_id: int
    first_name: str
    last_name: str
    phone_number: str
    address: str


class AcctResponse(BaseModel):
    previous: Optional[str] = None
    next: Optional[str] = None
    results: List[AccountItem]


class CreateAccountResponse(BaseModel):
    patron_id: int
    first_name: str
    last_name: str


class CheckedOutBook(BaseModel):
    checkout_id: int
    book_id: int
    title: str
    author_first: str
    author_last: str
    copy_id: int
    checkout_date: str
    due_date: str


@router.post("/create", response_model=CreateAccountResponse)
def post_new_account(acct: PatronAccountInfo):
    """
    Create a new account.
    """
    with db.engine.begin() as connection:
        phone_exists = connection.execute(
            sqlalchemy.text("SELECT 1 FROM patron_accounts WHERE phone = :phone"),
            {"phone": acct.phone_number},
        ).scalar()
        if phone_exists:
            raise HTTPException(status_code=400, detail="Phone number is already registered.")

        acct_connect = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO patron_accounts (first_name, last_name, phone, address)
                VALUES (:first, :last, :phone, :address)
                RETURNING id
                """
            ),
            [
                {
                    "first": acct.first_name,
                    "last": acct.last_name,
                    "phone": acct.phone_number,
                    "address": acct.address,
                }
            ],
        ).one()

        return AccountItem(
            patron_id=acct_connect.id,
            first_name=acct.first_name,
            last_name=acct.last_name,
            phone_number=acct.phone_number,
            address=acct.address,
        )


@router.get("/", tags=["accounts"], response_model=AcctResponse)
def get_accounts(search_page: str = "") -> AcctResponse:
    """
    Retrieves the list of all patron accounts.
    """
    items: List[AccountItem] = []
    nextpage = False
    limit = 20  # amount of results per page
    if search_page != "":
        pageno = int(search_page)
    else:
        pageno = 1
    offset = (pageno - 1) * limit
    with db.engine.begin() as connection:
        i = 0
        account_results = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM patron_accounts
                ORDER BY last_name ASC
                LIMIT :limit
                OFFSET :offset
                """
            ),
            [{"offset": offset, "limit": limit + 1}],
        )
        for account_row in account_results:
            if i == limit:
                nextpage = True
                break
            items.append(
                AccountItem(
                    patron_id=account_row.id,
                    first_name=account_row.first_name,
                    last_name=account_row.last_name,
                    phone_number=account_row.phone,
                    address=account_row.address,
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

    return AcctResponse(previous=previous, next=next, results=items)


@router.get("/{account_id}/checkouts", response_model=List[CheckedOutBook])
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
        checkout_results = connection.execute(
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

        for checkout_row in checkout_results:
            checkouts.append(
                CheckedOutBook(
                    checkout_id=checkout_row.checkout_id,
                    book_id=checkout_row.book_id,
                    title=checkout_row.title,
                    author_first=checkout_row.author_first,
                    author_last=checkout_row.author_last,
                    copy_id=checkout_row.copy_id,
                    checkout_date=str(checkout_row.checkout_date),
                    due_date=str(checkout_row.due_date),
                )
            )

    return checkouts


@router.get("/{account_id}", response_model=AccountItem)
def get_patron_account(account_id: int) -> AccountItem:
    """
    Retrieve a specific patron account by ID.
    """
    with db.engine.begin() as connection:
        patron_row = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, first_name, last_name, phone, address
                FROM patron_accounts
                WHERE id = :account_id
                """
            ),
            {"account_id": account_id},
        ).fetchone()

        if not patron_row:
            raise HTTPException(status_code=404, detail="Patron account not found.")

        return AccountItem(
            patron_id=patron_row.id,
            first_name=patron_row.first_name,
            last_name=patron_row.last_name,
            phone_number=patron_row.phone,
            address=patron_row.address,
        )
