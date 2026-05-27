# Concurrency Control

Our service needs concurrency control because more than one user can interact with the library system at the same time. For example, two users might try to check out the same book, place holds on the same title, or submit acquisition requests at nearly the same moment.

If we don't protect those transactions, each request might read the database before another request has finished updating it. That can lead to states that shouldn't happen in a library system, like one copy being checked out twice, a hold limit being passed, or duplicate acquisition requests being created.

For these cases, our service should use database transactions, `FOR UPDATE` locks when a specific row is being changed, `SERIALIZABLE` isolation for count-based or existence-based checks, and database constraints for rules that should always be true.

## Case 1: Two Users Check Out the Same Copy

One possible issue is when two users try to check out the same book at the same time.

If there's only one available copy, both transactions might check the database and see that the copy is available. Since neither transaction has finished yet, they could both try to create a checkout for that same copy. The result would be invalid because one physical library copy should only be checked out by one user at a time.

This is similar to a lost update or write skew issue. Each transaction seems reasonable on its own, but together they create a result that shouldn't be possible.

To prevent this, the checkout transaction should run inside a database transaction. When the service selects an available inventory copy, it should lock that row using `FOR UPDATE` before inserting the checkout. This would make another checkout request wait instead of using the same copy based on old information.

We should also add a database constraint that prevents one inventory copy from having more than one active checkout.

```sql
CREATE UNIQUE INDEX one_active_checkout_per_copy
ON checkouts (book_inventory_id)
WHERE returned_at IS NULL;
```

This is the right protection because this is one of the main rules of the library system. Even if the application code has a bug or two requests happen at the same time, the database should still prevent the same copy from being checked out twice.

## Case 2: Two Users Place Holds at the Same Time

Another issue can happen when two users place holds on the same book at the same time.

The holds endpoint checks whether the patron exists, checks whether the book can be placed on hold, checks how many active holds the patron has, checks how many active holds the book has, and then inserts the new hold. If two transactions run at the same time, both can read the same old counts before either one inserts a new hold.

For example, if a book already has four active holds and the limit is five, both transactions might read the count as four. Then both transactions insert a new hold, and the book ends up with six active holds.

This is a phantom read because the transaction is checking a group of rows that match a condition. While one transaction is still running, another transaction can insert a new row into that same group.

To prevent this, hold creation should use `SERIALIZABLE` isolation. This is a good fit because the issue comes from a count query over several rows, not just one row changing. With serializable isolation, the database can notice when two transactions are both making decisions from the same old count.

If one transaction fails because of a serialization conflict, the application can retry it. When it retries, it'll see the updated number of holds and can reject the request if the limit has already been reached.

We should also add a constraint to prevent the same user from placing more than one active hold on the same book.

```sql
CREATE UNIQUE INDEX one_active_hold_per_patron_book
ON holds (patron_id, book_id)
WHERE active = TRUE;
```

This works because the duplicate-hold rule can be enforced directly by the database. The serializable transaction protects the hold-limit check, and the unique index protects against duplicate active holds.

## Case 3: Two Users Submit the Same Acquisition Request

A third issue can happen when acquisition or wishlist requests are submitted at the same time.

The wishlist endpoint checks whether the patron exists and whether the requested book already exists in the catalog. It also checks for duplicate wishlist requests before inserting the new acquisition request into the wishlist table.

Without concurrency control, two transactions could both check the catalog and wishlist table before either one commits. Both transactions could see that the book doesn't exist in the catalog and that there isn't already a duplicate unfulfilled request. Then both transactions could insert the same acquisition request into the wishlist table.

This is a phantom read because each transaction checks for rows matching the requested title and `fulfilled = FALSE`, but another transaction can insert a matching row before the first transaction finishes.

To prevent this, the wishlist request transaction should use `SERIALIZABLE` isolation. This is appropriate because the endpoint makes decisions based on whether matching rows already exist in the catalog and wishlist tables. If two requests for the same title happen at the same time, serializable isolation lets the database detect that the transactions conflict.

We should also add a database constraint to prevent duplicate unfulfilled acquisition requests for the same title.

```sql
CREATE UNIQUE INDEX one_unfulfilled_wishlist_request_per_title
ON wishlist (title)
WHERE fulfilled = FALSE;
```

This is the right protection if the service only wants one active acquisition request per title. It matches the issue shown in the sequence diagram because the problem is that duplicate requests are not detected while the transactions are running concurrently.

If the service instead wants to allow multiple patrons to request the same title but prevent the same patron from submitting the same request twice, then the constraint should include `patron_id` too.

```sql
CREATE UNIQUE INDEX one_unfulfilled_wishlist_request_per_patron_title
ON wishlist (patron_id, title)
WHERE fulfilled = FALSE;
```

Either way, wishlist requests need protection because they use a check-then-insert pattern. The application checks whether something exists, then inserts if it doesn't. Without isolation or a constraint, two transactions can both pass the check and insert duplicate rows.

## Summary

The service should use transactions for checkout, hold creation, return, and wishlist requests. It should use `FOR UPDATE` when a transaction is making a decision about a specific inventory copy. It should use `SERIALIZABLE` isolation for transactions that depend on counts or existence checks, especially hold creation and wishlist requests.

These protections are needed because several parts of the service can read the same old database state and then write results that break the rules of the library system.
