## User Stories
1. As a library user, I would like to search for items by title, author, or category, so that I can quickly find specific media that I need.
2. As a student, I want to be able to check out a book to use for class.
3. As a student, I want to return a checked-out item, so that my account stays up to date to avoid fees and the item becomes available to other students.
4. As a library patron, I want to be able to make an account, so that I can check out books.
5. As a library worker, I want to be able to add and remove book listings in the library catalog, to keep the catalog up to date with what the library actually has.
6. As a library worker, I want to be able to see what accounts have checked out what books, so that I can keep track of where books are going.
7. As a library user, I want to view my currently checked-out items, so that I can keep track of what I need to return.
8. As a library worker, I want to update item information (title, author, category), so that incorrect or outdated catalog data can be fixed.
9. As a library user, I want to see whether an item is available or checked out, so that I know if I can borrow it.
10. As a library user, I want to be able to view the ratings of a book, so that I may make an informed decision on whether or not to check out a book.
11. As a student, I want to be able to leave ratings on books I have checked out, so that other users can evaluate the quality of a book before borrowing it and I can share my opinion on a book.
12. As a library worker, I want to be able to restrict users with overdue books from checking out other books, so that a user may not continue borrowing books without returning overdue ones.

## Exceptions
1. Exception: An account creation fails because the email or username is already in use.   
The system will reject the registration and show an error requesting the user to choose a different email or username.
2. Exception: A search returns no matching catalog items.  
The system will return a not found error and inform the user that the requested item is unavailable or invalid.  
3. Exception: A user tries to check out an item that is already checked out.  
The system will reject the checkout request and notify the user that the item is currently unavailable.
4. Exception: A user tries to check out an item that doesn’t exist in the library catalog.  
The system will reject the checkout with a notice that the item ID does not match anything in the catalog.
5. Exception: A user tries to delete their account while still having items checked out.  
The request will fail, and the system will inform the user that they must return all checked out items before closing their account.
6. Exception: A librarian tries to remove the catalog listing of a book that is currently checked out.  
The request will fail, and the system will inform the user that the book must be returned first.
7. Exception: A user attempts to return an item they did not check out.
The system will reject the return and notify the user that the item is not associated with their account.
8. Exception: A librarian attempts to update or delete an item that does not exist.
The system will return an error indicating the item was not found.
9. Exception: A user attempts to check out more items than the allowed limit.
The system will reject the checkout and notify the user that they have reached the maximum number of borrowed items.
10. Exception: A user wants to view the ratings of a book that has no ratings.  
The system notifies the user that no ratings are available for that specific book.
11. Exception: A user tries to leave a rating on a book they have already rated.  
The system keeps track of a user’s ratings and updates ratings so that the user may not leave duplicate ratings.
12. Exception: A user with one or more overdue books attempts to checkout another book.  
The system notifies they must return the book(s) before checking out another one and rejects the checkout request.

