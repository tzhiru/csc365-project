from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    dependencies=[Depends(auth.get_api_key)],
)


class PatronAccount(BaseModel):
    patron_id: int
    first_name: str
    last_name: str
    phone_number: str
    address: str


class PatronAccountInfo(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    address: str


@router.get("/list/", tags=["accounts"], response_model=List[PatronAccount])
def get_accounts() -> List[PatronAccount]:
    """
    Retrieves the list of all patron accounts.
    """
    accountsList: List[PatronAccount] = []

    with db.engine.begin() as connection:
        res = connection.execute(
            sqlalchemy.text(
                """
                SELECT *
                FROM patron_accounts
                ORDER BY last_name DESC
                """
            )
        )
        for row in res:
            accountsList.append(
                PatronAccount(
                    patron_id=row.id,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    phone_number=row.phone,
                    address=row.address,
                )
            )

    # Put in pages later
    return accountsList


class CreateAccountResponse(BaseModel):
    patron_id: int


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

        patron_id = acct_connect.id

        print(f"new account created: {acct} id: {patron_id}")
        return CreateAccountResponse(patron_id=patron_id)
