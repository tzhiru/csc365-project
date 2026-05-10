from fastapi import APIRouter, Depends, status

# from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post(
    "/{copy_id}",
    tags=["checkout"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_book(copy_id: int):
    """
    Checkout a book.
    """
    pass
    # placeholder.
