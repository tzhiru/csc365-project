# API Specification  
## 1. Creating a new account  
### `/accounts/new` (POST)  
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
    "quantity_avaliable": "number",
  }
]
```
### 2. `/catalog/search/` (GET)
Searches the library catalog via specific parameters.  
### 3. `/catalog/checkout/{book_id}/` (POST)  
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
### 1. `/catalog/return/{book_id}/` (POST) 
Returns the specified book and removes it from the user's list of checked out books

### 2. `/accounts/{account_id}/checkedout/` (GET) 
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
### 1. `/catalog/add/` (POST)
Adds a new item to the library catalog.

**Request**:
```json
  {
    "name": "number",
    "author": "string",
    "description": "string",
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

### 2. `/catalog/remove/{book_id}/` (DELETE)
Removes a book from the library catalog.

**Response**:  

```json
{
    "success": "boolean"
}
```

## 5. Viewing user account information/checked out books (admin functions) 
Allows library administrators to view patron account details and the books currently checked out under a patron’s account.
### 1. `/admin/accounts/` (GET)
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
### 3. `/admin/accounts/{account_id}/checkedout/` (GET)
 
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
