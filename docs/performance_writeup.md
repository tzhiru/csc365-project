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
  
**GET `/catalog/search/`** 87.212 ms (Longest)  
  
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
`/catalog/search/` runs at varying speeds depending on the amount of search attributes.
Results of running EXPLAIN ANALYZE on this query (searching by title, but not author):
```
Limit  (cost=61657.93..61657.98 rows=21 width=90) (actual time=298.842..298.850 rows=21.00 loops=1)
  Buffers: shared hit=7176, temp read=1371 written=1374
  ->  Sort  (cost=61657.93..62174.07 rows=206455 width=90) (actual time=298.841..298.847 rows=21.00 loops=1)
        Sort Key: book_log.title, book_log.author
        Sort Method: top-N heapsort  Memory: 30kB
        Buffers: shared hit=7176, temp read=1371 written=1374
        ->  Subquery Scan on book_log  (cost=48349.51..56091.58 rows=206455 width=90) (actual time=252.088..291.568 rows=50704.00 loops=1)
              Buffers: shared hit=7176, temp read=1371 written=1374
              ->  GroupAggregate  (cost=48349.51..54027.03 rows=206455 width=94) (actual time=252.086..288.584 rows=50704.00 loops=1)
                    Group Key: books.id, authors.id
                    Buffers: shared hit=7176, temp read=1371 written=1374
                    ->  Sort  (cost=48349.51..48865.65 rows=206455 width=68) (actual time=252.068..261.786 rows=153021.00 loops=1)
                          Sort Key: books.id, authors.id
                          Sort Method: external merge  Disk: 10968kB
                          Buffers: shared hit=7176, temp read=1371 written=1374
                          ->  Hash Left Join  (cost=5663.77..21654.22 rows=206455 width=68) (actual time=94.973..212.821 rows=153021.00 loops=1)
                                Hash Cond: (book_inventory.id = checkouts.book_inventory_id)
                                Buffers: shared hit=7176
                                ->  Hash Join  (cost=5662.59..20878.81 rows=206455 width=64) (actual time=94.919..201.870 rows=153021.00 loops=1)
                                      Hash Cond: (books.author_id = authors.id)
                                      Buffers: shared hit=7175
                                      ->  Hash Join  (cost=5375.59..20049.63 rows=206455 width=50) (actual time=93.452..182.792 rows=153021.00 loops=1)
                                            Hash Cond: (book_inventory.book_id = books.id)
                                            Buffers: shared hit=7113
                                            ->  Seq Scan on book_inventory  (cost=0.00..13096.00 rows=601147 width=8) (actual time=0.007..41.556 rows=599450.00 loops=1)
                                                  Filter: active
                                                  Rows Removed by Filter: 200550
                                                  Buffers: shared hit=5096
                                            ->  Hash  (cost=4517.00..4517.00 rows=68687 width=46) (actual time=93.388..93.388 rows=50929.00 loops=1)
                                                  Buckets: 131072  Batches: 1  Memory Usage: 5054kB
                                                  Buffers: shared hit=2017
                                                  ->  Seq Scan on books  (cost=0.00..4517.00 rows=68687 width=46) (actual time=0.008..84.196 rows=50929.00 loops=1)
                                                        Filter: ((title)::text ~~* '%ar%'::text)
                                                        Rows Removed by Filter: 149071
                                                        Buffers: shared hit=2017
                                      ->  Hash  (cost=162.00..162.00 rows=10000 width=18) (actual time=1.458..1.458 rows=10000.00 loops=1)
                                            Buckets: 16384  Batches: 1  Memory Usage: 632kB
                                            Buffers: shared hit=62
                                            ->  Seq Scan on authors  (cost=0.00..162.00 rows=10000 width=18) (actual time=0.007..0.464 rows=10000.00 loops=1)
                                                  Buffers: shared hit=62
                                ->  Hash  (cost=1.08..1.08 rows=8 width=12) (actual time=0.020..0.020 rows=8.00 loops=1)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      Buffers: shared hit=1
                                      ->  Seq Scan on checkouts  (cost=0.00..1.08 rows=8 width=12) (actual time=0.014..0.014 rows=8.00 loops=1)
                                            Buffers: shared hit=1
Planning:
  Buffers: shared hit=25
Planning Time: 0.387 ms
Execution Time: 300.364 ms
```
The query does sequential searches on checkouts, authors, book_inventory, and books. The query has to look through active checkouts to determine the avaliable and total number of copies. However, the checkouts table is currently less than a page, so indexing on checkouts will not change anything. I created indexes on copy status, book titles and authors since that is what the search function runs through books by.
```
CREATE INDEX active_inv ON book_inventory (active);
CREATE INDEX bk_title ON books (title);
CREATE INDEX bk_authors ON books (author_id);
```
These do not affect the behavior of the query at all. I looked up indexing for ILIKE searches and found it improves performance to remove the leading % in a search attribute so the database has less possibilities to look at (which makes sense for a search function anyways). I did this for title, but not for author (since one could be searching by the first or last name of the author which are combined in the searched table).
```
Limit  (cost=17920.46..17920.52 rows=21 width=90) (actual time=82.150..82.501 rows=21.00 loops=1)
  Buffers: shared hit=7302
  ->  Sort  (cost=17920.46..17981.19 rows=24289 width=90) (actual time=82.149..82.498 rows=21.00 loops=1)
        Sort Key: book_log.title, book_log.author
        Sort Method: top-N heapsort  Memory: 30kB
        Buffers: shared hit=7302
        ->  Subquery Scan on book_log  (cost=16658.37..17265.59 rows=24289 width=90) (actual time=77.005..80.573 rows=10037.00 loops=1)
              Buffers: shared hit=7302
              ->  HashAggregate  (cost=16658.37..17022.70 rows=24289 width=94) (actual time=77.003..79.936 rows=10037.00 loops=1)
                    Group Key: books.id, authors.id
                    Batches: 1  Memory Usage: 1817kB
                    Buffers: shared hit=7302
                    ->  Gather  (cost=4835.19..16415.48 rows=24289 width=68) (actual time=42.595..71.734 rows=30184.00 loops=1)
                          Workers Planned: 2
                          Workers Launched: 2
                          Buffers: shared hit=7302
                          ->  Hash Left Join  (cost=3835.19..12986.58 rows=10120 width=68) (actual time=30.898..61.436 rows=10061.33 loops=3)
                                Hash Cond: (book_inventory.id = checkouts.book_inventory_id)
                                Buffers: shared hit=7302
                                ->  Hash Join  (cost=3834.01..12947.44 rows=10120 width=64) (actual time=30.855..60.546 rows=10061.33 loops=3)
                                      Hash Cond: (books.author_id = authors.id)
                                      Buffers: shared hit=7299
                                      ->  Parallel Hash Join  (cost=3547.01..12633.86 rows=10120 width=50) (actual time=28.760..56.640 rows=10061.33 loops=3)
                                            Hash Cond: (book_inventory.book_id = books.id)
                                            Buffers: shared hit=7113
                                            ->  Parallel Seq Scan on book_inventory  (cost=0.00..8429.33 rows=250478 width=8) (actual time=0.020..16.370 rows=199816.67 loops=3)
                                                  Filter: active
                                                  Rows Removed by Filter: 66850
                                                  Buffers: shared hit=5096
                                            ->  Parallel Hash  (cost=3487.59..3487.59 rows=4754 width=46) (actual time=28.523..28.523 rows=3360.00 loops=3)
                                                  Buckets: 16384 (originally 8192)  Batches: 1 (originally 1)  Memory Usage: 1024kB
                                                  Buffers: shared hit=2017
                                                  ->  Parallel Seq Scan on books  (cost=0.00..3487.59 rows=4754 width=46) (actual time=0.037..26.670 rows=3360.00 loops=3)
                                                        Filter: ((title)::text ~~* 'a%'::text)
                                                        Rows Removed by Filter: 63307
                                                        Buffers: shared hit=2017
                                      ->  Hash  (cost=162.00..162.00 rows=10000 width=18) (actual time=2.024..2.025 rows=10000.00 loops=3)
                                            Buckets: 16384  Batches: 1  Memory Usage: 632kB
                                            Buffers: shared hit=186
                                            ->  Seq Scan on authors  (cost=0.00..162.00 rows=10000 width=18) (actual time=0.011..0.605 rows=10000.00 loops=3)
                                                  Buffers: shared hit=186
                                ->  Hash  (cost=1.08..1.08 rows=8 width=12) (actual time=0.025..0.025 rows=8.00 loops=3)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      Buffers: shared hit=3
                                      ->  Seq Scan on checkouts  (cost=0.00..1.08 rows=8 width=12) (actual time=0.018..0.020 rows=8.00 loops=3)
                                            Buffers: shared hit=3
Planning:
  Buffers: shared hit=31
Planning Time: 0.404 ms
Execution Time: 82.574 ms
```
This removes some work for the query to do.   
I also tried using a GIN trigram index on title:  
```
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX bk_title_tgm ON books USING gin (title gin_trgm_ops);
```
```
Limit  (cost=16568.53..16568.58 rows=21 width=90) (actual time=67.162..67.537 rows=21.00 loops=1)
  Buffers: shared hit=7313
  ->  Sort  (cost=16568.53..16629.25 rows=24289 width=90) (actual time=67.161..67.534 rows=21.00 loops=1)
        Sort Key: book_log.title, book_log.author
        Sort Method: top-N heapsort  Memory: 30kB
        Buffers: shared hit=7313
        ->  Subquery Scan on book_log  (cost=15306.43..15913.66 rows=24289 width=90) (actual time=61.640..65.479 rows=10037.00 loops=1)
              Buffers: shared hit=7313
              ->  HashAggregate  (cost=15306.43..15670.77 rows=24289 width=94) (actual time=61.639..64.798 rows=10037.00 loops=1)
                    Group Key: books.id, authors.id
                    Batches: 1  Memory Usage: 1817kB
                    Buffers: shared hit=7313
                    ->  Gather  (cost=3483.26..15063.54 rows=24289 width=68) (actual time=25.982..56.166 rows=30184.00 loops=1)
                          Workers Planned: 2
                          Workers Launched: 2
                          Buffers: shared hit=7313
                          ->  Hash Left Join  (cost=2483.26..11634.64 rows=10120 width=68) (actual time=15.037..46.565 rows=10061.33 loops=3)
                                Hash Cond: (book_inventory.id = checkouts.book_inventory_id)
                                Buffers: shared hit=7313
                                ->  Hash Join  (cost=2482.08..11595.50 rows=10120 width=64) (actual time=14.988..45.626 rows=10061.33 loops=3)
                                      Hash Cond: (books.author_id = authors.id)
                                      Buffers: shared hit=7310
                                      ->  Parallel Hash Join  (cost=2195.08..11281.93 rows=10120 width=50) (actual time=12.993..41.586 rows=10061.33 loops=3)
                                            Hash Cond: (book_inventory.book_id = books.id)
                                            Buffers: shared hit=7124
                                            ->  Parallel Seq Scan on book_inventory  (cost=0.00..8429.33 rows=250478 width=8) (actual time=0.045..17.062 rows=199816.67 loops=3)
                                                  Filter: active
                                                  Rows Removed by Filter: 66850
                                                  Buffers: shared hit=5096
                                            ->  Parallel Hash  (cost=2135.65..2135.65 rows=4754 width=46) (actual time=12.723..12.724 rows=3360.00 loops=3)
                                                  Buckets: 16384 (originally 8192)  Batches: 1 (originally 1)  Memory Usage: 1024kB
                                                  Buffers: shared hit=2028
                                                  ->  Parallel Bitmap Heap Scan on books  (cost=59.23..2135.65 rows=4754 width=46) (actual time=1.182..10.650 rows=3360.00 loops=3)
                                                        Recheck Cond: ((title)::text ~~* 'a%'::text)
                                                        Rows Removed by Index Recheck: 13958
                                                        Heap Blocks: exact=1264
                                                        Buffers: shared hit=2028
                                                        Worker 0:  Heap Blocks: exact=386
                                                        Worker 1:  Heap Blocks: exact=367
                                                        ->  Bitmap Index Scan on bk_title_tgm  (cost=0.00..57.21 rows=8081 width=0) (actual time=2.934..2.934 rows=51953.00 loops=1)
                                                              Index Cond: ((title)::text ~~* 'a%'::text)
                                                              Index Searches: 1
                                                              Buffers: shared hit=11
                                      ->  Hash  (cost=162.00..162.00 rows=10000 width=18) (actual time=1.951..1.952 rows=10000.00 loops=3)
                                            Buckets: 16384  Batches: 1  Memory Usage: 632kB
                                            Buffers: shared hit=186
                                            ->  Seq Scan on authors  (cost=0.00..162.00 rows=10000 width=18) (actual time=0.012..0.643 rows=10000.00 loops=3)
                                                  Buffers: shared hit=186
                                ->  Hash  (cost=1.08..1.08 rows=8 width=12) (actual time=0.037..0.037 rows=8.00 loops=3)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      Buffers: shared hit=3
                                      ->  Seq Scan on checkouts  (cost=0.00..1.08 rows=8 width=12) (actual time=0.014..0.016 rows=8.00 loops=3)
                                            Buffers: shared hit=3
Planning:
  Buffers: shared hit=26
Planning Time: 0.392 ms
Execution Time: 67.638 ms
```
This improved the time as well. 
