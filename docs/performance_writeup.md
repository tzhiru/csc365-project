# Performance Tuning
## Fake Data Modeling  
[populate_data.py](https://github.com/tzhiru/csc365-project/blob/main/populate_data.py)  
  
This script creates:
- 200,000 patron accounts
- 200,000 books
- 800,000 copies in inventory (4 per book type)
- 10,000 authors
- 10,000 publishers

This ended up being more than a million (whoops). This ratio seemed realistic enough, as there should be much more book types than patrons who have an account, and in a library there is usually multiple copies of different books.
## Performance results  
**GET `/accounts/list/`** 782.484 ms  
**POST `/accounts/create/`** 12.399 ms  
  
**GET `/catalog/available/`**  
**GET `/catalog/full_catalog/`**  
**GET `/catalog/search/`**  
  
**POST `/wishlist/request/`**  
**GET `/wishlist/`**  
**POST `/wishlist/{wishlist_id}/fufill/`**  
  
**POST `/admin/reset/`**  
**GET `/admin/accounts/{account_id}`**  
**GET `/admin/accounts/{account_id}/checkouts`**  

**POST `/checkout/{book_id}/`**  
**POST `/checkout/return/{book_copy_id}`**  

**POST `/holds/{book_id}/`**  
**GET `/holds/view_holds/{book_id}`**  

**POST `/inventory/remove_book/{book_id}`**  
**POST `/inventory/remove_book_copy/{book_copy_id}`**  
## Performance tuning
