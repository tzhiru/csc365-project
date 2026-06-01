# Peer Review Response

## Peer Review Feedback (Diego Melgoza)

**Feedback 1:** In `accounts.py`, line #92 (the print statement) in the function `post_new_account()` could be removed for cleanliness, since its output is not visible to the service users. If you wanted to, you could update the `CreateAccountResponse` class to hold the print statement’s information for user visibility.

**Response:** This feedback was addressed. We removed the print statement and updated `CreateAccountResponse` to return `patron_id`, `first_name`, and `last_name` so the user gets confirmation of what account was created.

**Feedback 2:** In `accounts.py`, the for-loop in the function `get_accounts()` on lines #47-54 could be replaced with a list comprehension. This fix would allow you to remove line #35 and place the list comprehension directly in the return statement where it is needed, such as `return [PatronAccount(...) for row in res]`.

**Response:** This feedback was addressed. We replaced the for-loop and `accountsList` variable with a list comprehension returned directly from the function.

**Feedback 3:** In `catalog.py`, the two functions `get_available_books()` and `get_books()` are quite similar. To fuse the two functions together, you could create a new version of `get_books()` that uses a conditional statement and an input value to determine if you get available books or all books.

**Response:** This feedback was not addressed. While the two functions are similar, they have distinct purposes and return different response models. `get_available_books()` returns all books with at least one copy currently available for checkout, while `get_books()` returns all books with both total and available copy counts. We chose to keep them separate to maintain clean separation of concerns.

**Feedback 5:** In `inventory.py`, `remove_book()` will need to use the `CASCADE` keyword to ensure book copies that reference the book are also deleted.

**Response:** This feedback was addressed. Our Alembic migration already defines `book_inventory` with a foreign key to `books` using `ON DELETE CASCADE`, so deleting a book automatically removes its inventory rows.

**Feedback 8:** In `admin.py`, `reset()` truncates the `books`, `authors`, and `publishers` tables, which could be inconvenient if they grow large, since that data would need to be re-added manually.

**Response:** This feedback was not addressed. The `reset()` endpoint is intended solely as a development and testing tool to restore the database to a clean state. It is not meant to be used in production. Keeping it as a full reset is intentional so that developers can reliably test from a known baseline. We have noted this in the endpoint's docstring.

## Peer Review Feedback (David Talavera-Dean)
### Code review
1. Where every you have a object named "row" or "results", I would change this to be more specific, that way its more readable and its just a better coding practice to give them meaningful names  
  
All "result" variable names have been changed. However, not every instance of "row" has been changed, as where they show up in the code it is still understandable.  
  
2. in account.py, I do not see the reason to have both PatronAccount and PatronAccountInfo. I see the difference, but I would just pick one or the other. I would drop the one that includes patron_id: int, just like the database handles the id key.  
  
Two different base models are required: One is without the account id, so that a user can submit their information in order to create an account (they would not know their id number before they make their account). The second contains the account id, so that the information can be returned with the new id (and for when the admins look through user account information).  
  
3. You guys seem to use repeat PartonAccount class in adim.py, I would just imported instead writing the class again
  
This has been added.  
  
4. The quarry at line 53 in adim.py is hard to read with the new name you gave to the tables. I see the idea of making it easier to write, but as an outsider read, it makes it hard to understand. Anywhere else where thats is done I would also change it  
  
This has not been added since the abbreviated table names are straightforward.   
  
5. Its seems like in the adim.py file, you have some quarries where you call all the attributes. I would use the * instead, much cleaner that way  
  
This has not been added. It is better to specifically select the attributes you want. One situation this would make sense for is if we ended up adding more columns to the affected tables in the future, but still only needed the specific attributes in the admin calls.   
  
6. In catalog.py, some of your quarries where you guys do an AS to give the attributes simpler names. However, I would give it a more meaningful name than "f" or "l", that is too simple and could confuse a reader  
  
The queries in catalog.py have been updated and no longer have attributes with vague nicknames.  
  
7. For the quarry at line 84 in catalog.py, you guys seem to have some Null checks which could be better remove with a LEFT JOIN where the database takes care of it rather then you deal with it  
  
The null checks are for checking if a book checkout is active or not (if there is no return date, then the book has not been returned yet and the checkout is active). Keeping track of these and aggregating the sums are needed so that we can sum up the amount of avaliable books vs books total for a specific book type.  
  
8. In checkout.py, the classes CheckoutResponse and ReturnResponse are really similar, I would recommend turning them into one class  
  
This has not been added. CheckoutResponse contains the due date so that the user is told when their book is due to return. ReturnResponse does not, since there is no due date needed for a return.  
  
9. In checkout.py, instead of an Upadate stament at the end, maybe just do an insert into, that way you guys can use SUM or COUNT in which the data will handles summations for you guys instead of you guys do it  
  
This has not been added, since determining the status of a checkout is based on the presence or non-existence of a returned date.    
  
10. Something good in invetory.py is you guys got a print statement that give you database info which is super helpful to have when looking at logs and stuff.
  
11. In catalog.py, make sure to be putting parentheses in the quarries when adding or subtracting things, that way its clear what is going on

This has been added.  
  
12. I would added comments throughout the code that explains in full detail what ever file does so that its very clear what is suppose to happen

### Schema/API design
1. I would add a DELETE call for the account sections, it might be useful for any user who stops using your service or something like that
  
We don't want to remove an already existing user, because the library keeps records of past checkouts and those records need to refer back to the users that completed those checkouts.  
  
2. For the GET api call for the account section, I recommend also making phone number unique and checking to see no person has the same number because that might get confusing  
  

  
3. For catalog API, I would add an API that allows you to see which books are checkout, so you guys can keep track of that

4. For catalog API, I would also add a POST call to allow you to put puts into the catalog, this is separate from the inventory, so you can choose which books to offer to certain people. Like in the potion shop where certain customers have different taste

5. catalog API for scearch should also call on an specific id, in case there are multiple books with the same title and author  
  
When there are multiple books with the same attributes, they will both be returned by the search.
  
6. For catalog API, I would also add a DELETE call to allow you to delete any books that you no longer want the catalog  
  
The inventory functions allow us to delete book types and book copies from the catalog.  
  
7. For admin API, I would recommend leaving as just admin rest and move the other API calls to other sections that way admin only deals with rest and it not conflicting with other databases

8. For inventory API, you can also add a section to find a certain book or sections of books. This can help you get specifics on books to potentially help the customer better

9. I am not sure what the point of remove book copy is for, if you have multiple of the same book, just add a qty column to your book section and update that rather than create another whole entry  
  
There are seperate tables for books and their individual copies (instead of just a quantity value), because we have to keep track of individual copies. It's a library, so we have to know what copies are with which users. If a specific copy is damaged, then you remove that specific copy and not the entire type of book.  
  
10. For inventory API, I would add a POST function to add books to your inventory, it might be easier this way

11. For inventory API,I would add a Get function to get either certain books from your inventory or all books, it might be easier this way4. Over all, everything seems good expect there is not much API calls for the books, I recommend you add some because it might help simplify the project and not have a bunch of for loops everywhere to try to find books

12. Not sure the purpose of default API call, I would remove it if I where you
      
This is the default call of the app and shows that the app is online. There is no need to remove it. 

## Peer Review Feedback (Adarsh Murugesan)
### Code review

1. In catalog.py, the search query uses exact matching (=) instead of substring matching (ILIKE). If both filters are omitted, the search returns nothing instead of the full catalog.  

This feedback was addressed. The search query has been updated to use ILIKE with % wildcards for partial, case-insensitive matching on both title and author. The NULL parameter issue has also been fixed by building the WHERE clause dynamically in Python so that NULL is never passed to Postgres.

2. In admin.py, /admin/reset will throw a runtime error because checkouts is not included in the TRUNCATE list, causing a foreign key constraint violation.

Response: This feedback was addressed. The checkouts table has been added to the TRUNCATE statement in the reset endpoint, and CASCADE has been added to handle any remaining foreign key dependencies.

3. In inventory.py, the route /remove_copy/{book_id} declares a path parameter book_id but the function uses book_copy_id, causing a mismatch where the path value is ignored.

Response: This feedback was addressed. The path parameter has been corrected to use book_copy_id consistently in both the route definition and the function signature.

4. In catalog.py, copies_available can go negative if a copy is checked out and then marked inactive, because the count only includes active copies but the checked CTE counts all open checkouts.

Response: This feedback was addressed. We wrapped the subtraction in GREATEST(..., 0) in both get_books() and search_catalog() to prevent copies_available from going negative in the edge case where a copy is checked out and then marked inactive.

5. In inventory.py, /inventory/remove_book does a hard DELETE which raises a foreign key error when book_inventory rows exist.

Response: This feedback was addressed. The remove_book endpoint has been updated to perform a soft delete by setting active = FALSE on all copies of the book rather than deleting the book row itself. This prevents foreign key errors and preserves checkout history.

6. In checkout.py, there is a race condition where two simultaneous checkout requests can grab the same copy.

Response: This feedback was identified and is documented in our concurrency.md file as one of the three concurrency scenarios. We describe the lost update phenomenon and the solution of using SELECT ... FOR UPDATE SKIP LOCKED to prevent double checkout.

7. In auth.py, the API key is printed to logs on every request. secrets.compare_digest() should be used instead of ==, and the 401 status code should not use "Forbidden" as the detail message.

This feedback was partially addressed. The print statement logging the API key has been removed. The secrets.compare_digest() improvement and the status code/message mismatch are noted as valid improvements for a future version.

8. default.env ships with a usable fallback API key (brat), meaning any environment without its own key silently uses the committed value.

Response: This feedback was not addressed. We acknowledge this is a security concern. For our current academic project context the risk is low, but we note that in a production setting a missing key should cause a hard startup error rather than falling back to a known default.

9. In server.py, the CORS setup only allows GET and OPTIONS, blocking POST requests from browsers. The allowed origin also points to the old potion shop project.

Response: This feedback was addressed. The CORS configuration has been updated to include POST in the allowed methods and the allowed origin has been corrected to match the library project.

10. There is leftover material from the old potions project including pyproject.toml naming, commented-out test files, and admin tag descriptions.

Response: This feedback was addressed. The pyproject.toml name and description have been updated to reflect the library project, and leftover commented-out potion test files have been cleaned up.

11. docs/APISpec.md does not match the actual implemented routes.

Response: This feedback was addressed. The APISpec.md has been updated to reflect the actual routes currently implemented in the service.

12. PatronAccount is defined separately in both accounts.py and admin.py with inconsistent field names (patron_id vs account_id).

Response: This feedback was partially addressed. The PatronAccount class from admin.py has been replaced with an import from accounts.py to avoid duplication. We acknowledge the field name inconsistency and have standardized to patron_id across both files.

13. There are no indexes on frequently filtered columns such as book_inventory_id, patron_id, and returned_at in the checkouts table.

Response: This feedback was addressed as part of our V5 performance tuning work. We ran EXPLAIN ANALYZE on our slowest endpoints and added indexes based on the results.

14. book_inventory.barcode is stored as an Integer, but barcodes and ISBNs can have leading zeros and exceed 32-bit range.

Response: This feedback was not addressed. Changing the column type would require a new migration. We acknowledge this is a valid concern and would change the barcode column to TEXT in a future version.
15. There is no validation on account creation — empty names and malformed phone numbers are accepted.

Response: This feedback was not addressed. Adding Pydantic field constraints such as minimum length and regex validation for phone numbers is a valid improvement. This is noted as a future enhancement.

16. Print statements used for logging, commented-out code blocks, and remove_book/remove_copy using POST instead of DELETE.

Response: Print statements have been removed from accounts.py and inventory.py. The large commented-out search block in catalog.py has been deleted. The POST vs DELETE issue is acknowledged as a valid RESTful design concern but was not changed at this stage to avoid breaking existing test documentation.

