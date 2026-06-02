# API Specification

## 1. Creating a new account

### 1. `/accounts/create` (POST)

Creates an account for a new patron and returns the account id to be used for checking out books.

**Request:**

```json
{
  "first_name": "string",
  "last_name": "string",
  "address": "string",
  "phone_number": "string"
}
```

**Response:**

```json
{
  "patron_id": "number",
  "first_name": "string",
  "last_name": "string"
}
```
<<<<<<< HEAD
## 2. Checking out books  
1. Search catalog for specific items
2. Checkout book (add to user's account's list of checked out books)
### 1. `/catalog/search/` (GET)
Searches the library catalog via specific parameters. Returns a list of all matching search results.  
**Query Parameters:**  
* `title` (string, optional)
* `author` (string, optional)
* `available_only` (boolean, defaults to True)
* `search_page` (string, optional)

**Response:**  
=======

## 2. Checking out books

1. View catalog of avaliable books
2. Search catalog for specific items
3. Checkout book (add to user's account's list of checked out books)

### 1. `/catalog/available/` (GET)

Displays all books avaliable for checkout.

**Response:**

```json
[
  {
    "book_id": "number",
    "name": "string",
    "author": "string",
    "description": "string",
    "category": "string",
    "average_rating": "float", //between 0 and 10
    "quantity_avaliable": "number"
  }
]
```

### 2. `/catalog/search/` (GET)

Searches the library catalog via specific parameters. Returns a list of all matching search results.  
**Request:**

```json
[
  {
    "title": "string", //optional
    "author": "string" //optional
  }
]
```

**Response:**

>>>>>>> 78fbff9 (Adarsh code review updates)
```json
{
  "previous": "string",
  "next": "string",
  "results": [
    {
      "book_id": "number",
      "title": "string",
      "author": "string",
      "copies_available": "number",
      "total_copies": "number",
      "date_published": "string"
    }
  ]
}
```

<<<<<<< HEAD
### 2. `/catalog/{book_id}` (GET)
Retrieves detailed information for a specific book by ID.

**Response**:
```json
{
  "book_id": "number",
  "title": "string",
  "author": "string",
  "copies_available": "number",
  "total_copies": "number",
  "date_published": "string"
}
```
### 3. `/checkout/{book_id}` (POST)  
Checks out the specified copy of a book under the user's account.  
  
**Request**:  

```json
{
  "patron_id": "number"
}
=======
### 3. `/checkout/{book_id}/` (POST)

Checks out the specified copy of a book under the user's account.

**Request**:

```json
[
  {
    "patron_id": "string"
  }
]
>>>>>>> 78fbff9 (Adarsh code review updates)
```

**Response**:

```json
<<<<<<< HEAD
{
  "success": "boolean",
  "checkout_id": "number",
  "due_date": "string",
  "copy_id": "number"
}
=======
[
  {
    "success": "boolean",
    "checkout_id": "number",
    "due_date": "date",
    "copy_id": "number"
  }
]
>>>>>>> 78fbff9 (Adarsh code review updates)
```

## 3. Returning books

Marks a checked out item as returned.
<<<<<<< HEAD
### 1. `/checkout/return/{book_copy_id}` (POST) 
=======

### 1. `/checkout/return/{book_copy_id}/` (POST)

>>>>>>> 78fbff9 (Adarsh code review updates)
Returns the specified book and removes it from the user's list of checked out books
**Request**:

```json
{}
```

**Response**:

```json
{
  "success": "boolean",
  "checkout_id": "number",
  "patron_id": "number",
<<<<<<< HEAD
  "copy_id": "number"
}
```
## 4. Editing the library catalog (admin functions)  
### 1. `/inventory/add_book` (POST)
Adds a new book type to the library catalog.
=======
  "copy_id": "number
  }
]
```

### 2. `/admin/accounts/{account_id}/checkouts/` (GET)

Displays all books currently checked out under a specific account

**Response:**

```json
[
  {
    "book_id": "number",
    "name": "string",
    "author": "string",
    "due_date": "string"
  }
]
```

## 4. Editing the library catalog (admin functions)

### 1. `/catalog/add` (POST)

Adds a new item to the library catalog.
>>>>>>> 78fbff9 (Adarsh code review updates)

**Request**:

```json
{
<<<<<<< HEAD
  "title": "string",
  "author_id": "number",
  "publisher_id": "number",
  "date_published": "string"
}
```
**Response**:  
=======
  "name": "number",
  "author": "string",
  "description": "string",
  "category": "string",
  "quantity_available": "number"
}
```

**Response**:

>>>>>>> 78fbff9 (Adarsh code review updates)
```json
{
  "book_id": "number",
  "success": "boolean"
}
```

<<<<<<< HEAD
### 2. `/inventory/add_copy` (POST)
Adds a physical copy of an existing book to the inventory.
=======
### 2. `/inventory/remove_book/{book_id}/` (DELETE)

Removes a book from the library catalog.

**Response**:
>>>>>>> 78fbff9 (Adarsh code review updates)

**Request**:
```json
{
<<<<<<< HEAD
  "book_id": "number",
  "barcode": "number"
=======
  "success": "boolean"
>>>>>>> 78fbff9 (Adarsh code review updates)
}
```
**Response**:  
```json
{
  "copy_id": "number",
  "success": "boolean"
}
```

### 3. `/inventory/remove_book/{book_id}` (POST)
Removes a book from the library catalog by marking all active copies as inactive. Fails if there are copies of the book currently checked out.

**Response**:  
(HTTP 204 No Content)

### 4. `/inventory/remove_copy/{book_copy_id}` (POST)
Marks a book copy from inventory as inactive/unavailable.

**Response**:  
(HTTP 204 No Content)


## 5. Viewing user account information/checked out books (admin functions)

Allows library administrators to view patron account details and the books currently checked out under a patron’s account.
<<<<<<< HEAD
### 1. `/accounts/` (GET)
=======

### 1. `/admin/accounts/list` (GET)

>>>>>>> 78fbff9 (Adarsh code review updates)
Displays a list of all library patron accounts.

**Response**:

```json
<<<<<<< HEAD
{
  "previous": "string",
  "next": "string",
  "results": [
    {
      "patron_id": "number",
      "first_name": "string",
      "last_name": "string",
      "phone_number": "string",
      "address": "string"
    }
  ]
}
```
### 2. `/accounts/{account_id}` (GET)
Displays detailed information for a specific patron account.
 
**Response**:
 
 ```json
 {
    "patron_id" : "number",
    "first_name" : "string",
    "last_name" : "string",
    "address" : "string",
    "phone_number": "string"
 }
```
### 3. `/accounts/{account_id}/checkouts` (GET)
 
**Response**:
 
 ```json
 [
  {
     "checkout_id" : "number",
     "book_id" : "number",
     "title" : "string",
     "author_first" : "string",
     "author_last" : "string",
     "copy_id" : "number",
     "checkout_date" : "string",
     "due_date": "string"
=======
[
  {
    "account_id": "string",
    "first_name": "string",
    "last_name": "string",
    "address": "string",
    "phone_number": "string"
  }
]
```

### 2. `/admin/accounts/{account_id}/` (GET)

Displays detailed information for a specific patron account.

**Response**:

```json
{
  "account_id": "string",
  "first_name": "string",
  "last_name": "string",
  "address": "string",
  "phone_number": "string"
}
```

### 3. `/admin/accounts/{account_id}/checkouts/` (GET)

**Response**:

```json
[
  {
    "book_id": "number",
    "name": "string",
    "author": "string",
    "checkout_date": "string",
    "due_date": "string"
  }
]
```

## 6. Viewing and leaving reviews on books

Allows patrons to view ratings and reviews left by other users, and submit their own ratings for books they have previously checked out.

### 1. `/catalog/{book_id}/reviews/` (GET)

Retrieves all ratings and written reviews for a specific book.

**Response:**

```json
[
  {
    "review_id": "string",
    "account_id": "string",
    "rating": "number",
    "review_text": "string",
    "date_posted": "string"
>>>>>>> 78fbff9 (Adarsh code review updates)
  }
 ]
```
<<<<<<< HEAD
## 6. Acquisition Request / Wishlist (Complex Endpoint)
=======

### 2. `/catalog/{book_id}/reviews/` (POST)

Allows a patron to leave a 1-5 star rating and an optional text review for a book they have borrowed. The API will check to ensure the user has actually checked out this book before and hasn't already reviewed it.

**Request:**

```json
{
  "account_id": "string",
  "rating": "number",
  "review_text": "string"
}
```

**Response:**

```json
{
  "success": "boolean",
  "review_id": "string",
  "message": "string"
}
```

## 7. Acquisition Request / Wishlist (Complex Endpoint)

>>>>>>> 78fbff9 (Adarsh code review updates)
Allows a patron to submit a request for a book that is not currently in the library catalog. This endpoint is complex because it performs multiple reads before writing as it verifies the patron exists, checks whether the book already exists in the catalog, checks whether the patron has already submitted a request for this title, and checks whether other patrons have also requested it. Also, the response message adapts based on existing demand for the title.

### 1. `/wishlist/request/` (POST)

Submit a request for a book not currently in the catalog.

**Request:**

<<<<<<< HEAD
 ```json
 {
   "patron_id": "number",
   "title": "string",
   "author": "string"
 }
=======
```json
[
  {
    "patron_id": "number",
    "title": "string",
    "author": "string"
  }
]
>>>>>>> 78fbff9 (Adarsh code review updates)
```

**Response:**

<<<<<<< HEAD
 ```json
 {
   "success": "boolean",
   "message": "string",
   "wishlist_id": "number" 
 }
=======
```json
[
  {
    "success": "boolean",
    "message": "string",
    "wishlist_id": "number"
  }
]
>>>>>>> 78fbff9 (Adarsh code review updates)
```

### 2. `/wishlist/` (GET)

Admin view of all acquisition requests, ordered alphabetically by title.

**Response:**

<<<<<<< HEAD
 ```json
 [
   {
     "wishlist_id": "number",
     "patron_id": "number",
     "title": "string",
     "author": "string",
     "requested_at": "string",
     "fulfilled": "boolean"
   }
 ]
=======
```json
[
  {
    "wishlist_id": "number",
    "patron_id": "number",
    "title": "string",
    "author": "string",
    "requested_at": "string",
    "fulfilled": "boolean"
  }
]
>>>>>>> 78fbff9 (Adarsh code review updates)
```

### 2. `/wishlist/{wishlist_id}/fulfill/` (POST)

Admin endpoint to mark an acquisition request as fulfilled. Automatically marks all other pending requests for the same title as fulfilled as well.

**Response:**

<<<<<<< HEAD
 ```json
 {
   "success": "boolean",
   "message": "string",
   "wishlist_id": "number"
 }
```
## 7. Placing a hold (Complex Endpoint)
=======
```json
[
  {
    "success": "boolean",
    "message": "string",
    "wishlist_id": "number"
  }
]
```

## 8. Placing a hold (Complex Endpoint)

>>>>>>> 78fbff9 (Adarsh code review updates)
### 1. `/holds/{book_id}` (POST)

Place a hold on a book that currently has all copies checked out.  
A single book type can only have 5 active holds at a time. A single user can only have 10 active holds at a time. The hold request will fail if these conditions are not met, or if the targeted book is already avaliable.
**Request:**

<<<<<<< HEAD
 ```json
 {
   "patron_id": "number"
 }
=======
```json
[
  {
    "patron_id": "number"
  }
]
>>>>>>> 78fbff9 (Adarsh code review updates)
```

**Response:**

<<<<<<< HEAD
 ```json
 {
   "success": "boolean",
   "hold_id": "number",
   "book_id": "number",
   "expected_date": "string" //the estimated date the book will be avaliable.
 }
=======
```json
[
  {
    "success": "boolean",
    "hold_id": "number",
    "book_id": "number",
    "expected_date": "date" //the estimated date the book will be avaliable.
  }
]
>>>>>>> 78fbff9 (Adarsh code review updates)
```

### 2. `/checkout/{book_id}` (POST)

Checkout the book once it is avaliable. If you are the patron who made the hold, the checkout will succeed.
<<<<<<< HEAD
**Request**:  

```json
{ 
  "patron_id": "number"
}
```

**Response**:  

```json
{
  "success": "boolean",
  "checkout_id": "number",
  "due_date": "string",
  "copy_id": "number"
}
```
=======
**Request**:

```json
[
  {
    "patron_id": "int"
  }
]
```

**Response**:

```json
[
  {
    "success": "boolean",
    "checkout_id": "number",
    "due_date": "date",
    "copy_id": "number"
  }
]
```
>>>>>>> 78fbff9 (Adarsh code review updates)
