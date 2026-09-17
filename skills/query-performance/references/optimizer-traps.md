# Optimizer traps (MySQL / MariaDB)

Failure modes that look like application bugs.

## `EXPLAIN` on a `SELECT` does not describe the `UPDATE`

MariaDB does not apply semijoin optimization inside `UPDATE`. A subquery that plans as a materialized
semijoin in a `SELECT` degrades to a per-row scan as an `UPDATE`. Always run `EXPLAIN` on the exact
statement, including the `UPDATE` keyword.

## Semijoin splitting kills grouped aggregates

When the optimizer splits a materialized subquery into a split-materialized plan, a `GROUP BY` over
the result can go from milliseconds to minutes. Symptoms: the plan shows a materialized derived table
with a huge `r_loops`. Fix: rewrite as a `LATERAL`-style derived join, or force materialization once
and join against it.

## Cold buffer pool looks exactly like a missing index

A correctly indexed query against a table that does not fit in the InnoDB buffer pool spends its time
in I/O. Adding an index does not help; it makes writes slower and the next query still cold. Check
`innodb_buffer_pool_size` against the working set before touching the schema.

## Stale statistics

`rows` estimates far from reality make the optimizer choose the wrong index entirely. `ANALYZE TABLE`
before drawing any conclusion from a plan on a table that was recently bulk-loaded.

## `NULL` voids a unique index

`UNIQUE (school_id, code)` does not prevent duplicates when `school_id` is `NULL` — `NULL` is never
equal to `NULL`. Combined with soft deletes (`UNIQUE (…, deleted_at)`), the constraint effectively
disappears. Every invariant that matters must also be enforced in the Action.

## Non-strict connections truncate silently

A `tinyint` column receiving `300` stores `127` with a warning, not an error, on a non-strict
connection. A `varchar(30)` receiving 40 characters stores 30. Both look like application bugs months
later. Set strict mode, and check the column type before assuming a value round-trips.

## Blank strings are not `NULL`

`$value ?? $default` does not catch `''`. On identity columns populated by an upstream sync, blank
strings and `NULL` coexist, and every `whereNull` check misses half the bad rows. Normalise on write
and check both on read.

## `json` reports as `longtext`

MariaDB implements `json` as a `longtext` with a check constraint. Schema dumps and introspection
tools report `longtext`; a migration written from the dump will drop the constraint. Read the actual
`SHOW CREATE TABLE`.

## Schema dumps go stale

A committed `schema/mysql-schema.sql` reflects the last time someone regenerated it, not the
database. When they disagree, `information_schema` is the truth.
