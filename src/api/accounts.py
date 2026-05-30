from fastapi import APIRouter, Depends
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


@router.get("/list/", tags=["accounts"], response_model=AcctResponse)
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
                ORDER BY last_name DESC
                OFFSET :offset
                """
            ),
            [{"offset": offset}],
        )
        for row in account_results:
            if i == limit:
                nextpage = True
                break
            items.append(
                AccountItem(
                    patron_id=row.id,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    phone_number=row.phone,
                    address=row.address,
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


class CreateAccountResponse(BaseModel):
    patron_id: int
    first_name: str
    last_name: str


@router.post("/create", response_model=CreateAccountResponse)
def post_new_account(acct: PatronAccountInfo):
    """
    Create a new account.
    """
    with db.engine.begin() as connection:
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
