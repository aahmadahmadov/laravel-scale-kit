# Large-table playbook

A procedure for touching a table with tens or hundreds of millions of rows.

## 1. Establish the facts before writing SQL

```sql
SELECT table_rows, data_length, index_length
FROM information_schema.tables
WHERE table_schema = DATABASE() AND table_name = 'schedules';

SHOW INDEX FROM schedules;
SHOW CREATE TABLE schedules;
```

`table_rows` from `information_schema` is an estimate — good enough to decide which rules apply.
Never run a bare `SELECT COUNT(*)` on such a table to "check the size".

## 2. Write the query as two flat queries

Resolve the filtering entity ids first. The id query hits a small table and an index; the big query
becomes a single `whereIn` against a covering index.

If the id set is bigger than a few thousand, do not inline it:
- chunk the `whereIn`, or
- join against a real (temporary) table, or
- push the filter into the big table directly if a suitable column exists denormalised.

## 3. EXPLAIN, then ANALYZE

```sql
EXPLAIN SELECT ...;
ANALYZE FORMAT=JSON SELECT ...;   -- MariaDB: actual loops and rows
```

Read `r_loops` and `r_rows` against `rows`. A 200x gap between estimate and reality means stale
statistics — run `ANALYZE TABLE` and re-plan before changing anything else.

## 4. Index decisions

- A new index on a 100M-row table is a **hours-long** operation and permanent write overhead on every
  insert. It must be justified by a plan.
- Column order in a composite index: equality columns first, then the range/sort column. An index
  leading with the low-selectivity column is often worse than no index, because the optimizer will
  choose it and then scan.
- A `plan_id`-leading index on a table where `plan_id` matches millions of rows will produce a full
  scan of that slice. Lead with the selective column.
- Check for an existing index that already covers the need before adding one — duplicate prefixes are
  common in tables that grew over years.

## 5. Pagination

- `simplePaginate()` always. No `COUNT(*)`.
- Deep pages still cost: `LIMIT 20 OFFSET 200000` reads 200,020 rows. If deep paging is a real use
  case, switch to keyset pagination (`WHERE id > :last_seen ORDER BY id LIMIT 20`).
- A year-scoped filter plus `ORDER BY created_at` with no matching composite index is the classic
  5-15 second list endpoint. The fix is the index, or dropping the sort.

## 6. Aggregate strategy

| Need | Do |
|---|---|
| Count per parent, few parents | one grouped query, map in PHP |
| Count per parent, many parents | a single grouped query over the id set, never `withCount` |
| Existence per parent | `withExists`, verified with `ANALYZE FORMAT=JSON` |
| Expensive aggregate reused across a request | compute once, pass it down; do not recompute per item |
| Expensive aggregate reused across requests | cached projection with an explicit TTL — see `repository-caching` |

## 7. Batch writes

- Never `$model->update()` in a loop over thousands of rows. Batch with a single `UPDATE ... WHERE
  id IN (...)` in chunks, or `upsert()`.
- A backfill over a large table runs in chunks with a sleep, ordered by primary key, resumable. Log
  the last processed id so a crash does not mean starting over.
- Soft-deleted rows are invisible to Eloquent but present to a raw builder. A backfill written with a
  raw builder will happily rewrite rows the application considers deleted. Decide explicitly.

## 8. Report honestly

Quote the plan, not a stopwatch reading from the second run. "574ms → 12ms by materialising the id
set once" is a claim you can defend; "feels faster" is not.
