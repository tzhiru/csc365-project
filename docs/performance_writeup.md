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
**GET `/accounts/list/`** 26.302 ms  
**POST `/accounts/create/`** 12.399 ms  
  
**GET `/catalog/available/`** 702.569 ms  
**GET `/catalog/full_catalog/`** 748.483 ms (Longest endpoint)  
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

**POST `/inventory/remove_book/{book_id}`** 135.799 ms  
**POST `/inventory/remove_book_copy/{book_copy_id}`** 41.792 ms  
## Performance tuning
`/catalog/full_catalog/` runs this query, where the limit is set to 21 and the offset determines what page of results to look at. 
```
WITH checked (book_id, total) AS (
                    SELECT book_id, 
                    SUM(CASE WHEN checkout_date IS NOT NULL AND returned_at IS NULL THEN 1 ELSE 0 END) as total
                    FROM book_inventory
                    LEFT JOIN checkouts on book_inventory_id = book_inventory.id
                    GROUP BY book_id
                    ORDER BY book_id
)
SELECT books.id, books.title,
  authors.first_name as first, authors.last_name as last, date_published,
  count(*) as total_copies, (count(*) - checked.total) as copies_available
FROM book_inventory
JOIN books on book_inventory.book_id = books.id
JOIN authors on books.author_id = authors.id
JOIN checked on books.id = checked.book_id
WHERE active = TRUE
GROUP BY books.id, authors.id, checked.total
ORDER BY books.title ASC
LIMIT :limit
OFFSET :offset
```
Results of running EXPLAIN on this query:
```
Limit  (cost=267215.12..267215.18 rows=21 width=84)
  ->  Sort  (cost=267215.12..268717.99 rows=601147 width=84)
        Sort Key: books.title
        ->  GroupAggregate  (cost=189482.41..251007.25 rows=601147 width=84)
              Group Key: books.id, authors.id, (sum(CASE WHEN ((checkouts.checkout_date IS NOT NULL) AND (checkouts.returned_at IS NULL)) THEN 1 ELSE 0 END))
              ->  Incremental Sort  (cost=189482.41..237481.44 rows=601147 width=68)
                    Sort Key: books.id, authors.id, (sum(CASE WHEN ((checkouts.checkout_date IS NOT NULL) AND (checkouts.returned_at IS NULL)) THEN 1 ELSE 0 END))
                    Presorted Key: books.id
                    ->  Merge Join  (cost=189482.23..221198.07 rows=601147 width=68)
                          Merge Cond: (books.id = book_inventory.book_id)
                          ->  Merge Join  (cost=110462.25..131244.55 rows=200000 width=72)
                                Merge Cond: (books.id = book_inventory_1.book_id)
                                ->  Nested Loop  (cost=0.72..15239.58 rows=200000 width=60)
                                      ->  Index Scan using books_pkey on books  (cost=0.42..7225.74 rows=200000 width=46)
                                      ->  Memoize  (cost=0.30..0.31 rows=1 width=18)
                                            Cache Key: books.author_id
                                            Cache Mode: logical
                                            ->  Index Scan using authors_pkey on authors  (cost=0.29..0.30 rows=1 width=18)
                                                  Index Cond: (id = books.author_id)
                                ->  Sort  (cost=110461.54..110968.78 rows=202895 width=12)
                                      Sort Key: book_inventory_1.book_id
                                      ->  HashAggregate  (cost=79266.01..89107.46 rows=202895 width=12)
                                            Group Key: book_inventory_1.book_id
                                            Planned Partitions: 4
                                            ->  Merge Left Join  (cost=109.46..28016.01 rows=800000 width=12)
                                                  Merge Cond: (book_inventory_1.id = checkouts.book_inventory_id)
                                                  ->  Index Scan using book_inventory_pkey on book_inventory book_inventory_1  (cost=0.42..25883.42 rows=800000 width=8)
                                                  ->  Sort  (cost=109.04..112.96 rows=1570 width=12)
                                                        Sort Key: checkouts.book_inventory_id
                                                        ->  Seq Scan on checkouts  (cost=0.00..25.70 rows=1570 width=12)
                          ->  Materialize  (cost=79019.67..82025.41 rows=601147 width=4)
                                ->  Sort  (cost=79019.67..80522.54 rows=601147 width=4)
                                      Sort Key: book_inventory.book_id
                                      ->  Seq Scan on book_inventory  (cost=0.00..13096.00 rows=601147 width=4)
                                            Filter: active
JIT:
  Functions: 39
  Options: Inlining false, Optimization false, Expressions true, Deforming true
```
