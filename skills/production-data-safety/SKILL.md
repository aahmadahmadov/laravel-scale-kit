---
name: production-data-safety
description: Use before running any database statement, artisan command, or script in an environment that holds real or production-snapshot data. Invoke when about to run migrate, seed, tinker, an UPDATE/DELETE/DDL statement, a backfill, or any command whose blast radius is unclear. Also use when writing a brief for another agent that will touch a database.
license: MIT
metadata:
  version: "0.1.0"
  domain: operations
  triggers: migrate, db:seed, migrate fresh, tinker, UPDATE, DELETE, TRUNCATE, DROP, backfill, production data, database safety, destructive command
  role: guardian
  scope: analysis
  related-skills: migrations-schema, query-performance, agent-delegation
---

# Production Data Safety

Many teams develop against a **restored production snapshot**. That database looks local and is not:
the rows are real, and on a shared or staging box other people are looking at them. This skill exists
to make the blast radius of a command explicit *before* it runs.

## Forbidden without an explicit human yes

No exceptions, no "just this once", no matter how small:

- `UPDATE`, `DELETE`, `INSERT`, `REPLACE`, `TRUNCATE`
- **All DDL**: `CREATE`, `ALTER`, `DROP` — *including adding an index*
- Any artisan command that writes: `migrate`, `db:seed`, `tinker` snippets calling
  `save()`/`update()`/`delete()`
- The same statements issued through a raw client, a script, a queue job, or an MCP tool

Absolutely never, in any environment holding real data:

```
php artisan migrate:fresh
php artisan migrate:refresh
php artisan migrate:reset
php artisan db:seed
```

## Allowed without asking

`SELECT`, `EXPLAIN`, `EXPLAIN ANALYZE`, `SHOW CREATE TABLE`, `SHOW INDEX`, `information_schema`
reads — **as long as they stay bounded on the large tables**. An unbounded `SELECT *` or a bare
`COUNT(*)` on a 100M-row table is its own kind of incident.

## The procedure

1. **State the statement** you intend to run, in full.
2. **State what it changes** — which table, how many rows (get the number with a `SELECT COUNT` on a
   bounded predicate first), and whether it is reversible.
3. **Wait for an explicit yes.** Silence is not approval, and approval for one statement is not
   approval for the next.
4. **Run it once**, then verify with a read.

For a multi-row write, do a **dry run first**: the same `WHERE` as a `SELECT`, count the rows, show a
sample, and only then run the write.

## Know which environment you are in

- **`APP_ENV` picks the env file.** A local `.env` can be pointing at staging or production without
  anything on screen saying so. Before any write, print the resolved database host and name, and read
  it — do not assume.
- Keep production credentials in a separate file that requires a deliberate act to activate.
- If a deploy pipeline overwrites `.env` on the servers, know that before debugging a config problem.

## There may be no undo

- Binary logging is often **off** on these databases. That means **no point-in-time recovery and no
  audit trail**: an `UPDATE` with a wrong `WHERE` is unrecoverable except from the last backup.
- Confirm the backup's age before any destructive operation. "There's a backup" is not a fact until
  someone has said when it was taken.
- Application-level soft deletes do not protect against a raw `DELETE`.

## Shared databases

If a second, older application still reads the same database:

- A migration that renames or drops a column is an **outage for that application**, not a refactor.
- Additive only. Two-release deprecations. Coordinate the deploy.
- Check what else writes to a table before assuming your application owns it.

## Delegation

**Repeat this restriction in every brief you give another agent or contractor**, and name which
statement types are allowed. An agent with database access and no constraint in its prompt will
happily run a "quick fix" `UPDATE`. The rule is not inherited; it must be restated.

## Checklist before any write

- [ ] Resolved DB host/name printed and read
- [ ] Statement written out in full
- [ ] Row count measured with a bounded `SELECT`
- [ ] Reversibility stated; backup age confirmed if not reversible
- [ ] Explicit human approval for this specific statement
- [ ] Verified afterwards with a read
