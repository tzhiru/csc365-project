## 1. New Patron Account Creation and Book Checkout Workflow
A new female patron has just moved into town and wants to borrow a book from the library. Since she doesnt have a library account, 
she first creates one by calling `POST/accounts/new` and submitting her first name, last name, address, and phone number. The API 
then creates her account and returns an `account_id`. Then, the new patron wants to find a book to check out. She begins by browsing 
the library's available catalog by calling `GET /catalog/available/`. The API returns a list of books that are currently available 
for checkout. She sees that *Normal People* is availiable with a `book_id` 42. She then checks out the book by calling `POST /catalog/checkout/42/`
and passing in her `account_id`. The API verifies that her account exists and that a copy of the book is available. The checkout succeeds , and the
API returns a response that indicates success. 

## 2: Catalog Search and Alternative Checkout Workflow 
A student has a research paper due and wants to find sources on database design. 
Since he doesn't know exact titles, he first searches the library catalog by calling `GET /catalog/search/?category=databases`. 
The API then searches the catalog and returns a list of matching books. He sees that Database Management is listed with a `book_id` 102 but has a `quantity_available` of 0. 
Then, the student wants to find a different book to check out. He browses the returned list again and sees SQL for Beginners is available with a `book_id` 105. 
He then checks out the book by calling `POST /catalog/checkout/105/` and passing in his `account_id`. The API verifies that his account exists and that a copy of the book is available. 
The checkout succeeds, and the API returns a response that indicates success. After 2 weeks, the student is ready to return the book. He calls `POST /catalog/return/105/. The API removes the book from the student’s list of checked out books from their account.



## 3: Librarian Removing Damaged Inventory Workflow 
A library worker is doing inventory and wants to remove an old, damaged book from the system. 
Since the book is no longer readable, she first removes it from the catalog by calling `DELETE /catalog/remove/55/`. 
The API then deletes the book's record and returns a response that indicates success. Then, the library worker wants to verify the book is actually gone. 
She begins by browsing the library's available catalog by calling `GET /catalog/available/`. The API returns a list of books that are currently available for checkout. 
She sees that the damaged book is no longer listed in the catalog. She then wants to make sure no patron accounts still have it listed as checked out. 
She checks the system by calling `GET /admin/accounts/` to review active accounts. The API verifies her admin access and returns the account lists. 
The audit succeeds, and the API returns a response that indicates no active checkouts for that item.
