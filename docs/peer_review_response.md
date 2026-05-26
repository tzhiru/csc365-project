# Peer Review Response

## Peer Review Feedback (Diego Melgoza)

**Feedback 1:** In `accounts.py`, line #92 (the print statement) in the function `post_new_account()` could be removed for cleanliness, since its output is not visible to the service users. If you wanted to, you could update the `CreateAccountResponse` class to hold the print statement’s information for user visibility.

**Response:** This feedback was addressed. We removed the print statement and updated `CreateAccountResponse` to return `patron_id`, `first_name`, and `last_name` so the user gets confirmation of what account was created.

**Feedback 2:** In `accounts.py`, the for-loop in the function `get_accounts()` on lines #47-54 could be replaced with a list comprehension. This fix would allow you to remove line #35 and place the list comprehension directly in the return statement where it is needed, such as `return [PatronAccount(...) for row in res]`.

**Response:** This feedback was addressed. We replaced the for-loop and `accountsList` variable with a list comprehension returned directly from the function.

**Feedback 3:** In `catalog.py`, the two functions `get_available_books()` and `get_books()` are quite similar. To fuse the two functions together, you could create a new version of `get_books()` that uses a conditional statement and an input value to determine if you get available books or all books.

**Response:** This feedback was not addressed. While the two functions are similar, they have distinct purposes and return different response models. `get_available_books()` returns all books with at least one copy currently available for checkout, while `get_books()` returns all books with both total and available copy counts. We chose to keep them separate to maintain clean separation of concerns.

**Feedback 5:** In `inventory.py`, `remove_book()` will need to use the `CASCADE` keyword to ensure book copies that reference the book are also deleted.

**Response:** This feedback was addressed. Our Alembic migration already defines `book_inventory` with a foreign key to `books` using `ON DELETE CASCADE`, so deleting a book automatically removes its inventory rows.

**Feedback 8:** In `admin.py`, `reset()` truncates the `books`, `authors`, and `publishers` tables, which could be inconvenient if they grow large, since that data would need to be re-added manually.

**Response:** This feedback was not addressed. The `reset()` endpoint is intended solely as a development and testing tool to restore the database to a clean state. It is not meant to be used in production. Keeping it as a full reset is intentional so that developers can reliably test from a known baseline. We have noted this in the endpoint's docstring.
