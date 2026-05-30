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
  
