---
name: query-performance
description: Use when a Laravel/MySQL/MariaDB query is slow, when writing a query against a very large table, when reading EXPLAIN output, or when deciding between whereHas, joins and subqueries. Invoke for slow endpoint, N+1, missing index, EXPLAIN ANALYZE, pagination cost, aggregate over millions of rows, or before adding an index to a big table.
license: MIT
metadata:
  version: "0.2.0"
  domain: infrastructure
  triggers: slow query, EXPLAIN, index, N+1, whereHas, join, aggregate, large table, pagination, optimizer, query plan, MariaDB, MySQL
  role: specialist
  scope: analysis
  related-skills: repository-criteria, repository-caching, migrations-schema
---

# Query Performance

This skill is about queries over tables where the row count has consequences — tens of millions and
up. At that size the optimizer's choices matter more than the SQL's elegance, and most "obvious"
Eloquent is wrong.

## Declare the large tables

Put a table in the project's conventions file the moment it passes ~10M rows, with the rule that
applies to it:

| Table | Rows | Rule |
|---|---|---|
| `exam_scores` | ~136M | `simplePaginate` only; `JOIN`/`whereIn`, never `whereHas` |
| `schedules` | ~116M | same |

An agent that cannot see the row count will write the `whereHas` every time.

## The five rules

1. **Never `whereHas` on a large table.** It compiles to a correlated `EXISTS` subquery the optimizer
   re-plans per row. Resolve the ids first with a cheap query, then a flat `whereIn`.
2. **Never `COUNT(*)` for pagination** on a large table. `simplePaginate()` fetches `per_page + 1`
   rows and asks nothing else.
3. **Nested `whereHas` destroys the plan entirely.** Two levels of relation constraint on a big table
   will table-scan. Flatten it: ids first, then one `whereIn`.
4. **Measure with `EXPLAIN`, not with a stopwatch.** A second run hits a warm buffer pool and lies to
   you. Read `rows`, `filtered`, `key`, and `Extra` — that is what stays true tomorrow.
5. **A cold query is not a missing index.** Before adding an index to a 100M-row table, confirm the
   plan actually lacks one. An undersized InnoDB buffer pool makes every well-indexed query look
   slow, and the fix is a config change, not a schema change.

## The ids-first pattern

```php
// Bad — correlated subquery over 116M rows
$schedules = Schedule::whereHas('class', fn ($q) => $q->where('school_id', $schoolId))->get();

// Good — two flat queries, both index-driven
$classIds = Classm::where('school_id', $schoolId)->pluck('id');
$schedules = Schedule::whereIn('class_id', $classIds)->get();
```

The second form is more lines and orders of magnitude faster. When the id set is large, materialise
it once and reuse it rather than re-deriving it per call.

## Aggregates

- `withCount()` on a large relation is a correlated subquery per parent row. For more than a handful
  of parents, compute the counts in one grouped query and map them in PHP.
- `withExists()` does **not** fan out the way `withCount()` does — but confirm it on your data by
  reading `r_loops` in `ANALYZE FORMAT=JSON`, not by assuming.
- Deduplicate composite records with **explicit PHP keys**, not SQL `GROUP BY`, when the grouping key
  is composite. It is faster, and the dedup rule stays visible.

## Latest-per-key

`MAX(id)` is **not** chronology. Rows inserted out of order, backfilled, or restored from a soft
delete break that assumption, and the bug shows up as one user seeing stale data forever. Order by
the actual business timestamp, and if there are ties, add a deterministic tiebreaker. The correct
shape is usually a union of per-key latest rows, not a window function scan of the whole table.

## Reading the plan

| Signal | Means |
|---|---|
| `type: ALL` on a large table | full scan — stop and fix |
| `rows` wildly above reality | stale statistics; `ANALYZE TABLE` before concluding anything |
| `Using temporary; Using filesort` | the sort cannot use an index; usually an `ORDER BY created_at` with no matching composite index |
| `Using where; Using index` | covering index — the good case |
| `r_loops` > 1 in `ANALYZE FORMAT=JSON` | the subquery is being re-executed per row |

## Two traps specific to MariaDB

- **`EXPLAIN` on the `SELECT` lies about the `UPDATE`.** MariaDB does not apply semijoin optimization
  inside `UPDATE`. A subquery that plans beautifully as a `SELECT` can scan the table as an `UPDATE`.
  Always `EXPLAIN` the actual statement you will run.
- **Semijoin splitting can kill an aggregate.** When the optimizer splits a materialized subquery, a
  grouped aggregate can degrade by orders of magnitude. Rewriting as a `LATERAL`-style derived join
  is usually the fix.

See `references/large-table-playbook.md` for the full procedure and
`references/optimizer-traps.md` for the failure catalogue.

## Before you finish

- [ ] `EXPLAIN` run on the **exact** statement, not a simplified version
- [ ] No `whereHas` against a declared large table
- [ ] Pagination is `simplePaginate` where the table is large
- [ ] Any new index justified by a plan, not a hunch, and its write cost considered
- [ ] Timings taken cold, or not quoted at all
