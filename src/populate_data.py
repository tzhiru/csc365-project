import sqlalchemy
import os
import dotenv
from faker import Faker
import random


def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"


url = "postgresql://myuser:mypassword@localhost:5432/mydatabase"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(url, use_insertmanyvalues=True)

num_users = 200000
num_books = 200000
fake = Faker()
copies = []
total_copies = 0

with engine.begin() as conn:
    print("Truncating tables...")
    conn.execute(
        sqlalchemy.text(
            """
                TRUNCATE TABLE 
                holds, checkouts, wishlist,
                book_inventory, books,
                authors, publishers,
                patron_accounts
                RESTART IDENTITY
            """
        )
    )

# create fake posters with fake names and birthdays
with engine.begin() as conn:
    print("creating fake authors and publishers...")
    for i in range(10000):
        if i % 10 == 0:
            print(f"authors --- {i}")

        first_name = fake.first_name()
        last_name = fake.last_name()
        place_name = fake.company()

        conn.execute(
            sqlalchemy.text("""
                INSERT INTO authors (first_name, last_name) 
                VALUES (:first, :last);
                INSERT INTO publishers (name)
                VALUES (:place);
                """),
            {"first": first_name, "last": last_name, "place": place_name},
        )

with engine.begin() as conn:
    print("creating fake books...")
    for i in range(num_books):
        if i % 10 == 0:
            print(f"books --- {i}")

        title = fake.catch_phrase()
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

with engine.begin() as conn:
    print("creating fake accounts...")
    for i in range(num_users):
        if i % 10 == 0:
            print(f"accounts --- {i}")

        # profile = fake.profile()
        first_name = fake.first_name()
        last_name = fake.last_name()
        number = fake.phone_number()
        address = fake.address()

        poster_id = conn.execute(
            sqlalchemy.text("""
                INSERT INTO patron_accounts (first_name, last_name, phone, address) 
                VALUES (:first, :last, :phone, :add) 
                RETURNING id;
                """),
            {"first": first_name, "last": last_name, "phone": number, "add": address},
        ).scalar_one()
