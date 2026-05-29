import sqlalchemy
import os
import dotenv
from faker import Faker

# import numpy as np
import random


def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"


# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

num_users = 200000
num_books = 200000
fake = Faker()
copies = []
total_copies = 0

# create fake posters with fake names and birthdays
with engine.begin() as conn:
    print("creating fake accounts...")
    for i in range(num_users):
        if i % 10 == 0:
            print(i)

        # profile = fake.profile()
        first_name = fake.unique.first_name()
        last_name = fake.unique.last_name()
        number = fake.unique.phone_number()
        address = fake.unique.address()

        poster_id = conn.execute(
            sqlalchemy.text("""
                INSERT INTO patron_accounts (first_name, last_name, phone, address) 
                VALUES (:first, :last, :phone, :add) 
                RETURNING id;
                """),
            {"first": first_name, "last": last_name, "phone": number, "add": address},
        ).scalar_one()

    print("creating fake authors and publishers...")
    for i in range(10000):
        if i % 10 == 0:
            print(i)

        first_name = fake.unique.first_name()
        last_name = fake.unique.last_name()
        place_name = fake.book.publisher()

        conn.execute(
            sqlalchemy.text("""
                INSERT INTO authors (first_name, last_name) 
                VALUES (:first, :last);
                INSERT INTO publishers (name)
                VALUES (:place);
                """),
            {"first": first_name, "last": last_name, "place": place_name},
        )

    print("creating fake books...")
    for i in range(num_books):
        if i % 10 == 0:
            print(i)

        title = fake.book.title()
        day = fake.date_between(start_date="-100y")
        author = random.randint(1, 10000)
        pub = random.randint(1, 10000)

        book_id = conn.execute(
            sqlalchemy.text("""
                INSERT INTO books (title, author_id, publisher_id, date_published) 
                VALUES (:title, :author, :publisher, :date_published)
                RETURNING id;
                """),
            {"title": title, "author": author, "publisher": pub, "date_published": day},
        ).scalar_one()

        for j in range(4):
            total_copies += 1
            copies.append(
                {
                    "book_id": book_id,
                    "barcode": fake.unique.ean(length=8),
                    "added_at": fake.date_between(start_date="-5y"),
                    "active": fake.boolean(chance_of_getting_true=75),
                }
            )
    if copies:
        conn.execute(
            sqlalchemy.text("""
        INSERT INTO book_inventory (book_id, barcode, added_at, active) 
        VALUES (:book_id, :barcode, :added_at, :active);
        """),
            copies,
        )

print(f"total copies: {total_copies}")
