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
