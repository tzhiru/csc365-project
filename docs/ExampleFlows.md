## 1. New Patron Account Creation and Book Checkout Workflow
A new female patron has just moved into town and wants to borrow a book from the library. Since she doesnt have a library account, 
she first creates one by calling `POST/accounts/new` and submitting her first name, last name, address, and phone number. The API 
then creates her account and returns an `account_id`. Then, the new patron wants to find a book to check out. She begins by browsing 
the library's available catalog by calling `GET /catalog/available/`. The API returns a list of books that are currently available 
for checkout. She sees that *Normal People* is availiable with a `book_id` 42. She then checks out the book by calling `POST /catalog/checkout/42/`
and passing in her accoun_id. The API verifies that her account exists and that a copy of the book is available. The checkout succeeds , and the
API returns a response that indicates success. 
