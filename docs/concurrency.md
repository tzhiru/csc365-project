# Concurrency Control

Our service needs concurrency control because more than one user can interact with the library system at the same time. For example, two users might try to check out the same book, place holds on the same title, or update the same inventory copy at nearly the same moment.

If we don't protect those transactions, each request might read the database before another request has finished updating it. That can lead to states that shouldn't happen in a library system, like one copy being checked out twice or a hold limit being passed.

For these cases, our service should use database transactions, `FOR UPDATE` locks when a specific row is being changed, `SERIALIZABLE` isolation for count-based checks, and database constraints for rules that should always be true.

## Case 1: Two Users Check Out the Same Copy

One possible issue is when two users try to check out the same book at the same time.

If there's only one available copy, both transactions might check the database and see that the copy is available. Since neither transaction has finished yet, they could both try to create a checkout for that same copy. The result would be invalid because one physical library copy should only be checked out by one user at a time.

This is similar to a lost update or write skew issue. Each transaction seems reasonable on its own, but together they create a result that shouldn't be possible.

To prevent this, the checkout transaction should run inside a database transaction. When the service selects an available inventory copy, it should lock that row using `FOR UPDATE` before inserting the checkout. This would make another checkout request wait instead of using the same copy based on old information.

We should also add a database constraint that prevents one inventory copy from having more than one active checkout.

```sql
CREATE UNIQUE INDEX one_active_checkout_per_copy
ON checkouts (inventory_id)
WHERE returned_at IS NULL;
```

This is the right protection because this is one of the main rules of the library system. Even if the application code has a bug or two requests happen at the same time, the database should still prevent the same copy from being checked out twice.

## Case 2: Two Users Place Holds at the Same Time

Another issue can happen when two users place holds on the same book at the same time.

If the service has a limit on the number of active holds for a book, two transactions could both count the current holds before either one inserts a new hold. For example, if a book already has four active holds and the limit is five, both transactions might read the count as four. Then both transactions insert a new hold, and the book ends up with six active holds.

This is a phantom read because the transaction is checking a group of rows that match a condition. While one transaction is still running, another transaction can insert a new row into that same group.

To prevent this, hold creation should use `SERIALIZABLE` isolation. This is a good fit because the issue comes from a count query over several rows, not just one row changing. With serializable isolation, the database can notice when two transactions are both making decisions from the same old count.

If one transaction fails because of a serialization conflict, the application can retry it. When it retries, it'll see the updated number of holds and can reject the request if the limit has already been reached.

We should also add a constraint to prevent the same user from placing more than one active hold on the same book.

```sql
CREATE UNIQUE INDEX one_active_hold_per_patron_book
ON holds (patron_id, book_id)
WHERE status = 'active';
```

This works because the duplicate-hold rule can be enforced directly by the database. The serializable transaction protects the hold-limit check, and the unique index protects against duplicate active holds.

## Case 3: Checkout While a Copy Is Removed From Inventory

A third issue can happen when a user is checking out a copy while an admin is removing or deactivating that same copy from inventory.

The checkout transaction might read that the copy is active and available. Before the checkout finishes, the admin transaction could mark that copy as inactive. If there's no protection, the checkout transaction could still create a checkout for a copy that should no longer be available.

This is a non-repeatable read or stale read problem because the checkout transaction makes a decision using information that changes before the transaction is finished.

To prevent this, both checkout and inventory removal should run inside transactions. The inventory copy row should be locked with `FOR UPDATE` before either transaction makes a decision about it.

For checkout, the service should only select active copies and should lock the selected row.

```sql
SELECT *
FROM inventory
WHERE book_id = :book_id
  AND is_active = true
FOR UPDATE;
```

For inventory removal, the service should also lock the inventory row before changing it. It should check whether that copy currently has an active checkout before marking it inactive.

If the copy is already checked out, the service should either reject the removal or mark the copy to be removed after it's returned. This prevents the database from ending up with an inactive copy that still has an active checkout.

This is the right approach because both transactions are trying to make decisions about the same physical copy. A row-level lock is useful here because the conflict is centered on one specific inventory row.

## Summary

The service should use transactions for checkout, hold creation, return, and inventory removal. It should use `FOR UPDATE` when a transaction is making a decision about a specific inventory copy. It should use `SERIALIZABLE` isolation for transactions that depend on counts or availability checks, especially hold creation and checkout.

These protections are needed because several parts of the service can read the same old database state and then write results that break the rules of the library system.
