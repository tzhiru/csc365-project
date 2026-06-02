from fastapi import FastAPI
from src.api import catalog, admin, checkout, accounts, inventory, wishlist, holds
from starlette.middleware.cors import CORSMiddleware

description = """
Library project for CSC 365
"""
tags_metadata = [
    {"name": "catalog", "description": "View the library catalog."},
    {"name": "checkout", "description": "Check out or return a book."},
    {"name": "accounts", "description": "Make or manage patron accounts."},
    {"name": "holds", "description": "Request a hold on a book."},
    {"name": "wishlist", "description": "Request new library books."},
    {"name": "inventory", "description": "Manage library catalog."},
    {"name": "admin", "description": "Admin tools for reseting the library system."},
]

app = FastAPI(
    title="library365",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata,
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(accounts.router)
app.include_router(catalog.router)
app.include_router(checkout.router)
app.include_router(holds.router)
app.include_router(wishlist.router)
app.include_router(inventory.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "App is open."}
