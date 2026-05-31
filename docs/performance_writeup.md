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
Time in ms each endpoint took to execute via curl.  
  
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
Results of running EXPLAIN ANALYZE on this query:
```
Limit  (cost=255296.37..255296.42 rows=21 width=84) (actual time=850.197..850.204 rows=21.00 loops=1)
  Buffers: shared hit=42803, temp read=2708 written=3829
  ->  Sort  (cost=255296.37..256799.24 rows=601147 width=84) (actual time=837.958..837.964 rows=21.00 loops=1)
        Sort Key: books.title
        Sort Method: top-N heapsort  Memory: 29kB
        Buffers: shared hit=42803, temp read=2708 written=3829
        ->  GroupAggregate  (cost=177563.65..239088.49 rows=601147 width=84) (actual time=329.481..801.257 rows=199194.00 loops=1)
              Group Key: books.id, authors.id, (sum(CASE WHEN ((checkouts.checkout_date IS NOT NULL) AND (checkouts.returned_at IS NULL)) THEN 1 ELSE 0 END))
              Buffers: shared hit=42803, temp read=2708 written=3829
              ->  Incremental Sort  (cost=177563.65..225562.68 rows=601147 width=68) (actual time=329.468..730.390 rows=599450.00 loops=1)
                    Sort Key: books.id, authors.id, (sum(CASE WHEN ((checkouts.checkout_date IS NOT NULL) AND (checkouts.returned_at IS NULL)) THEN 1 ELSE 0 END))
                    Presorted Key: books.id
                    Full-sort Groups: 18096  Sort Method: quicksort  Average Memory: 27kB  Peak Memory: 27kB
                    Buffers: shared hit=42803, temp read=2708 written=3829
                    ->  Merge Join  (cost=177563.47..209279.32 rows=601147 width=68) (actual time=329.390..619.674 rows=599450.00 loops=1)
                          Merge Cond: (books.id = book_inventory.book_id)
                          Buffers: shared hit=42803, temp read=2708 written=3829
                          ->  Merge Join  (cost=98543.50..119325.79 rows=200000 width=72) (actual time=260.764..397.639 rows=200000.00 loops=1)
                                Merge Cond: (books.id = book_inventory_1.book_id)
                                Buffers: shared hit=37707, temp read=1826 written=2944
                                ->  Nested Loop  (cost=0.72..15239.58 rows=200000 width=60) (actual time=0.058..90.323 rows=200000.00 loops=1)
                                      Buffers: shared hit=32610
                                      ->  Index Scan using books_pkey on books  (cost=0.42..7225.74 rows=200000 width=46) (actual time=0.019..19.423 rows=200000.00 loops=1)
                                            Index Searches: 1
                                            Buffers: shared hit=2610
                                      ->  Memoize  (cost=0.30..0.31 rows=1 width=18) (actual time=0.000..0.000 rows=1.00 loops=200000)
                                            Cache Key: books.author_id
                                            Cache Mode: logical
                                            Hits: 190000  Misses: 10000  Evictions: 0  Overflows: 0  Memory Usage: 1168kB
                                            Buffers: shared hit=30000
                                            ->  Index Scan using authors_pkey on authors  (cost=0.29..0.30 rows=1 width=18) (actual time=0.001..0.001 rows=1.00 loops=10000)
                                                  Index Cond: (id = books.author_id)
                                                  Index Searches: 10000
                                                  Buffers: shared hit=30000
                                ->  Sort  (cost=98542.78..99050.02 rows=202895 width=12) (actual time=260.667..275.463 rows=200000.00 loops=1)
                                      Sort Key: book_inventory_1.book_id
                                      Sort Method: external merge  Disk: 5096kB
                                      Buffers: shared hit=5097, temp read=1826 written=2944
                                      ->  HashAggregate  (cost=67347.26..77188.71 rows=202895 width=12) (actual time=169.096..224.919 rows=200000.00 loops=1)
                                            Group Key: book_inventory_1.book_id
                                            Planned Partitions: 4  Batches: 5  Memory Usage: 8249kB  Disk Usage: 11392kB
                                            Buffers: shared hit=5097, temp read=1189 written=2305
                                            ->  Hash Left Join  (cost=1.18..16097.26 rows=800000 width=12) (actual time=0.040..83.690 rows=800001.00 loops=1)
                                                  Hash Cond: (book_inventory_1.id = checkouts.book_inventory_id)
                                                  Buffers: shared hit=5097
                                                  ->  Seq Scan on book_inventory book_inventory_1  (cost=0.00..13096.00 rows=800000 width=8) (actual time=0.022..32.653 rows=800000.00 loops=1)
                                                        Buffers: shared hit=5096
                                                  ->  Hash  (cost=1.08..1.08 rows=8 width=12) (actual time=0.011..0.012 rows=8.00 loops=1)
                                                        Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                                        Buffers: shared hit=1
                                                        ->  Seq Scan on checkouts  (cost=0.00..1.08 rows=8 width=12) (actual time=0.005..0.007 rows=8.00 loops=1)
                                                              Buffers: shared hit=1
                          ->  Materialize  (cost=79019.67..82025.41 rows=601147 width=4) (actual time=68.593..155.388 rows=599450.00 loops=1)
                                Storage: Memory  Maximum Storage: 17kB
                                Buffers: shared hit=5096, temp read=882 written=885
                                ->  Sort  (cost=79019.67..80522.54 rows=601147 width=4) (actual time=68.588..101.407 rows=599450.00 loops=1)
                                      Sort Key: book_inventory.book_id
                                      Sort Method: external merge  Disk: 7056kB
                                      Buffers: shared hit=5096, temp read=882 written=885
                                      ->  Seq Scan on book_inventory  (cost=0.00..13096.00 rows=601147 width=4) (actual time=0.019..35.094 rows=599450.00 loops=1)
                                            Filter: active
                                            Rows Removed by Filter: 200550
                                            Buffers: shared hit=5096
Planning:
  Buffers: shared hit=15
Planning Time: 0.447 ms
JIT:
  Functions: 50
  Options: Inlining false, Optimization false, Expressions true, Deforming true
  Timing: Generation 1.437 ms (Deform 0.510 ms), Inlining 0.000 ms, Optimization 1.048 ms, Emission 13.811 ms, Total 16.296 ms
Execution Time: 854.590 ms
```
The plan uses a sequential scan once on checkouts and twice on book_inventory.
