### Example Workflow: Librarian Removing Damaged Inventory Workflow 
A library worker is doing inventory and wants to remove an old, damaged book from the system. 
Since the book is no longer readable, she first removes it from the catalog by calling `DELETE /catalog/remove/55/`. 
The API then deletes the book's record and returns a response that indicates success. Then, the library worker wants to verify the book is actually gone. 
She begins by browsing the library's available catalog by calling `GET /catalog/available/`. The API returns a list of books that are currently available for checkout. 
She sees that the damaged book is no longer listed in the catalog.
