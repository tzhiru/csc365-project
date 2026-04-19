# API Specification  
## 1. Creating a new account  
### `/accounts/new` (POST)  
Creates an account for a new patron.  
  
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
2. Checkout book (add to user's account's list of checked out books)  
## 3. Returning books  
## 4. Editing the library catalog (admin functions)  
## 5. Viewing user account information/checked out books (admin functions)  
## 6. Viewing and leaving reviews on books
