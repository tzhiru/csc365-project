## New Patron Account Creation and Book Checkout Workflow
A new patron has just moved into town and wants to borrow a book from the library. Since she doesnt have a library account, 
she first creates one by calling `POST /accounts/create` and submitting her first name, last name, address, and phone number. The API 
then creates her account and returns an `account_id`. Then, the patron wants to find a book to check out. She begins by browsing 
the library's available catalog by calling `GET /catalog/available/`. The API returns a list of books that are currently available 
for checkout. She sees that a book she wants to read is available and has id 4. She then checks out the book by calling `POST /checkout/4/`
and passing in her `account_id`. The API verifies that her account exists and that a copy of the book is available. The checkout succeeds, and the
API returns a response that indicates success and gives her the id of the book copy she has, 5.
Later, she wishes to return the book. She calls `POST /checkout/return/5/` with the id of the book copy she has, and gets a response that indicates success.
### Test results
**Creating a new account:**  
Request:  
```
curl -X 'POST' \
  'https://library-365.onrender.com/accounts/create' \
  -H 'accept: application/json' \
  -H 'access_token: barcode' \
  -H 'Content-Type: application/json' \
  -d '{
  "first_name": "First",
  "last_name": "Last",
  "phone_number": "000-000-000",
  "address": "123 Street Ct"
}'
```
Response:  
```
{
  "patron_id": 3
}
```
Her account id number is 3.  
  
**Getting available books:**  
Request:  
```
curl -X 'GET' \
  'https://library-365.onrender.com/catalog/available/' \
  -H 'accept: application/json' \
  -H 'access_token: barcode'
```
Response:  
```
[
  {
    "book_id": 1,
    "title": "awesome book",
    "author_first": "test 1",
    "author_last": "test 1 last",
    "copies_available": 3,
    "date_published": "2000-01-01"
  },
  {
    "book_id": 2,
    "title": "evil book",
    "author_first": "test first 2",
    "author_last": "test last 2",
    "copies_available": 1,
    "date_published": "2002-02-02"
  },
  {
    "book_id": 4,
    "title": "plant books",
    "author_first": "test first 2",
    "author_last": "test last 2",
    "copies_available": 2,
    "date_published": "1112-01-01"
  }
]
```
She sees that the book she wants has id 4, and 2 copies available.  
  
**Checking out a book:**  
Request:  
```
curl -X 'POST' \
  'https://library-365.onrender.com/checkout/4' \
  -H 'accept: application/json' \
  -H 'access_token: barcode' \
  -H 'Content-Type: application/json' \
  -d '{
  "patron_id": 3
}'
```
Response:  
```
{
  "success": true,
  "checkout_id": 5,
  "due_date": "2026-05-25",
  "copy_id": 5
}
```
She sees that the copy of book she has checked out has id number 5.
  
**Returning a book:**  
Request:  
```
curl -X 'POST' \
  'https://library-365.onrender.com/checkout/return/5' \
  -H 'accept: application/json' \
  -H 'access_token: barcode' \
  -d ''
```
Response:  
```
{
  "success": true,
  "checkout_id": 5,
  "patron_id": 3,
  "copy_id": 5
}
```
She uses the book copy id to return the book.  

## Catalog Search and Alternative Checkout Workflow 
A student has a research paper due and wants to find sources on database design. 
Since he doesn't know exact titles, he first searches the library catalog by calling `GET /catalog/search/?title=database`. 
The API then searches the catalog and returns a list of matching books. He sees that Database Management is listed with a `book_id` 102 but has `copies_available` of 0. 
Then, the student wants to find a different book to check out. He browses the returned list again and sees SQL for Beginners is available with a `book_id` 105. 
He then checks out the book by calling `POST /checkout/105` and passing in his `patron_id`. The API verifies that his account exists and that a copy of the book is available. The checkout succeeds, and the API returns a response that indicates success along with a `copy_id` of 342. After 2 weeks, the student is ready to return the book. He calls `POST /checkout/return/342`. The API records the return date for that specific checkout record.

### Test results
**Searching the catalog:**  
Request:  
```
curl -X 'GET' \
  'https://library-365.onrender.com/catalog/search/?title=database' \
  -H 'accept: application/json' \
  -H 'access_token: barcode'
```
Response:  
```
[
  {
    "book_id": 102,
    "title": "Database Management",
    "author_first": "Alice",
    "author_last": "Smith",
    "copies_available": 0,
    "total_copies": 2,
    "date_published": "2018-05-12"
  },
  {
    "book_id": 105,
    "title": "SQL for Beginners",
    "author_first": "Bob",
    "author_last": "Jones",
    "copies_available": 1,
    "total_copies": 3,
    "date_published": "2020-01-01"
  }
]
```
He sees that "Database Management" has 0 copies, but "SQL for Beginners" has 1 copy available.  
  
**Checking out a book:**  
Request:  
```
curl -X 'POST' \
  'https://library-365.onrender.com/checkout/105' \
  -H 'accept: application/json' \
  -H 'access_token: barcode' \
  -H 'Content-Type: application/json' \
  -d '{
  "patron_id": 12
}'
```
Response:  
```
{
  "success": true,
  "checkout_id": 89,
  "due_date": "2026-05-25",
  "copy_id": 342
}
```
He sees that the copy of book he has checked out has id number 342.  
  
**Returning a book:**  
Request:  
```
curl -X 'POST' \
  'https://library-365.onrender.com/checkout/return/342' \
  -H 'accept: application/json' \
  -H 'access_token: barcode' \
  -d ''
```
Response:  
```
{
  "success": true,
  "checkout_id": 89,
  "patron_id": 12,
  "copy_id": 342
}
```
He uses the book copy id to return the book.