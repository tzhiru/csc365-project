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
  
**GET `/catalog/available/`** 1473.756 ms (Slowest endpoint)  
**GET `/catalog/full_catalog/`** 1414.518 ms  
**GET `/catalog/search/`** 368.113 ms  
  
**POST `/wishlist/request/`** 23.308 ms  
**GET `/wishlist/`**  33.760 ms  
**POST `/wishlist/{wishlist_id}/fufill/`** 35.544 ms  
    
**POST `/admin/reset/`** Ommitted from tests since it is a test endpoint that clears out the data from every single table.  
**GET `/admin/accounts/{account_id}`** 10.861 ms  
**GET `/admin/accounts/{account_id}/checkouts`** 38.865 ms  

**POST `/checkout/{book_id}/`** 82.069 ms  
**POST `/checkout/return/{book_copy_id}`** 54.217 ms  

**POST `/holds/{book_id}/`** 57.132 ms  
**GET `/holds/view_holds/{book_id}`** 31.843 ms  

**POST `/inventory/remove_book/{book_id}`**  
**POST `/inventory/remove_book_copy/{book_copy_id}`** 41.792 ms  
## Performance tuning
