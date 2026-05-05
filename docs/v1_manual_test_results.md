### Example Workflow: Librarian Removing Damaged Inventory Workflow 
A library worker is doing inventory and wants to remove an old, damaged book from the system. She calls `GET /catalog/` to find the id of the book she means to remove.
Since the book is no longer readable, she first removes it from the catalog by calling `POST /catalog/remove/6/`. 
The API then deletes the book's record and returns a response that indicates success. Then, the library worker wants to verify the book is actually gone. 
She begins by browsing the library's available catalog by calling `GET /catalog/`. The API returns a list of books that are currently available for checkout. 
She sees that the damaged book is no longer listed in the catalog.

## Test results
### Calling catalog:
Request:  
```
curl -X 'GET' \
  'https://library-365.onrender.com/catalog/' \
  -H 'accept: application/json'
```
Response:  
```
[
  {
    "book_id": 3,
    "title": "awesome book",
    "author_first": "test first",
    "author_last": "test last",
    "date_published": "1222-01-01"
  },
  {
    "book_id": 5,
    "title": "book about bugs and stuff",
    "author_first": "test first",
    "author_last": "test last",
    "date_published": "2222-02-02"
  },
  {
    "book_id": 7,
    "title": "book full of whimsy and joy",
    "author_first": "test 2 first",
    "author_last": "test 2 last",
    "date_published": "2006-07-15"
  },
  {
    "book_id": 6,
    "title": "book that curses you",
    "author_first": "test first",
    "author_last": "test last",
    "date_published": "5200-05-01"
  },
  {
    "book_id": 4,
    "title": "evil book",
    "author_first": "test 2 first",
    "author_last": "test 2 last",
    "date_published": "2012-12-12"

  }
]
  ```
