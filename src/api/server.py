from fastapi import FastAPI
from src.api import catalog, admin, checkout, accounts
from starlette.middleware.cors import CORSMiddleware

description = """
Library project for CSC 365
"""
tags_metadata = [
    {"name": "accounts", "description": "Manage patron accounts."},
    {"name": "catalog", "description": "View the available potions."},
    {"name": "admin", "description": "Where you reset the game state."},
    {"name": "checkout", "description": "Check out or return a book"},
]

app = FastAPI(
    title="library365",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata,
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(accounts.router)
app.include_router(catalog.router)
app.include_router(admin.router)
app.include_router(checkout.router)


@app.get("/")
async def root():
    return {"message": "App is open."}
