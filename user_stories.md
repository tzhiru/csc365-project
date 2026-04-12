User Stories:
1. As a library user, I would like to search for items by title, author, or category, so that I can quickly find specific media that I need.
2. As a student, I want to be able to check out a book to use for class.
3. As a student, I want to return a checked-out item, so that my account stays up to date to avoid fees and the item becomes available to other students.



Exceptions: 
1. Exception: An account creation fails because the email or username is already in use. 
The system will reject the registration and show an error requesting the user to choose a different email or username.
2. Exception: A search returns no matching catalog items
The system will return a not found error and inform the user that the requested item is unavailable or invalid.
3. Exception: A user tries to check out an item that is already checked out
The system will reject the checkout request and notify the user that the item is currently unavailable.
