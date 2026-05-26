# API Specification  
## 1. Creating a new account  
### 1. `/accounts/create` (POST)  
Creates an account for a new patron and returns the account id to be used for checking out books.  
  
**Request:**  
```json
[
  {
    "first_name": "string",
    "last_name": "string",
    "address": "string",
    "phone_number": "string"
  }
]
```
**Response:**  
```json
[
  {
    "account_id": "string"
  }
]
```
## 2. Checking out books  
1. View catalog of avaliable books
2. Search catalog for specific items
3. Checkout book (add to user's account's list of checked out books)
### 1. `/catalog/avaliable/` (GET)
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
    "quantity_avaliable": "number",
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
    "author": "string", //optional
  }
]
```
**Response:**  
```json
[
  {
    "book_id": "number",
    "title": "string",
    "author_first": "string",
    "author_last": "string",
    "copies_available": "number",
    "total_copies": "number",
    "date_published": "string"
  }
]
```
### 3. `/checkout/{book_id}/` (POST)  
Checks out the specified copy of a book under the user's account.  
  
**Request**:  

```json
{
  "account_id": "string"
}
```

**Response**:  

```json
{
    "success": "boolean"
}
```
## 3. Returning books  
Marks a checked out item as returned.
### 1. `/checkout/return/{book_copy_id}/` (POST) 
Returns the specified book and removes it from the user's list of checked out books

### 2. `/admin/accounts/{account_id}/checkouts/` (GET) 
Displays all books currently checked out under a specific account

**Response:**  
```json
[
  {
    "book_id": "number",
    "name": "string",
    "author": "string",
    "due_date": "string",
  }
]
```
## 4. Editing the library catalog (admin functions)  
### 1. `/catalog/add` (POST)
Adds a new item to the library catalog.

**Request**:
```json
  {
    "name": "number",
    "author": "string",
    "description": "string",
    "category": "string",
    "quantity_available": "number",
  }
```
**Response**:  

```json
{
    "book_id" : "number"
    "success": "boolean"
}
```

### 2. `/inventory/remove_book/{book_id}/` (DELETE)
Removes a book from the library catalog.

**Response**:  

```json
{
    "success": "boolean"
}
```

## 5. Viewing user account information/checked out books (admin functions) 
Allows library administrators to view patron account details and the books currently checked out under a patron’s account.
### 1. `/admin/accounts/list` (GET)
Displays a list of all library patron accounts.

**Response**:  

```json
[
 {
    "account_id" : "string",
    "first_name" : "string",
    "last_name" : "string",
    "address" : "string",
    "phone_number": "string"
 }
]
```
### 2. `/admin/accounts/{account_id}/` (GET)
Displays detailed information for a specific patron account.
 
**Response**:
 
 ```json
 {
    "account_id" : "string",
    "first_name" : "string",
    "last_name" : "string",
    "address" : "string",
    "phone_number": "string"
 }
```
### 3. `/admin/accounts/{account_id}/checkouts/` (GET)
 
**Response**:
 
 ```json
[
 {
    "book_id" : "number",
    "name" : "string",
    "author" : "string",
    "checkout_date" : "string",
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
  }
]
```
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
Allows a patron to submit a request for a book that is not currently in the library catalog. This endpoint is complex because it performs multiple reads before writing as it verifies the patron exists, checks whether the book already exists in the catalog, checks whether the patron has already submitted a request for this title, and checks whether other patrons have also requested it. Also, the response message adapts based on existing demand for the title.

### 1. `/wishlist/request/` (POST)
Submit a request for a book not currently in the catalog.

**Request:**

 ```json
[
  {
    "patron_id": "number",
    "title": "string",
    "author": "string"
  }
]
```
**Response:**

 ```json
[
  {
    "success": "boolean",
    "message": "string",
    "wishlist_id": "number" 
  }
]
```
### 2. `/wishlist/` (GET)
Admin view of all acquisition requests, ordered alphabetically by title.

**Response:**

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

```
### 2. `/wishlist/{wishlist_id}/fulfill/` (POST)
Admin endpoint to mark an acquisition request as fulfilled. Automatically marks all other pending requests for the same title as fulfilled as well.

**Response:**

 ```json
[
  {
    "success": "boolean",
    "message": "string",
    "wishlist_id": "number"
  }
]
