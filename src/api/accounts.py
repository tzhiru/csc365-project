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
        return [
            PatronAccount(
                patron_id=row.id,
                first_name=row.first_name,
                last_name=row.last_name,
                phone_number=row.phone,
                address=row.address,
            )
            for row in res
        ]


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

        return CreateAccountResponse(
            patron_id=acct_connect.id,
            first_name=acct.first_name,
            last_name=acct.last_name,
        )
