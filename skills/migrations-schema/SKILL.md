---
name: migrations-schema
description: Use when writing a Laravel migration or changing database schema — adding columns, placing them with after(), indexes, foreign keys, and additive-only rules on a live database. Invoke when creating a migration, when a column needs a position, when adding an index to a big table, or when deciding whether a schema change is safe to deploy.
license: MIT
metadata:
  version: "0.2.0"
  domain: infrastructure
  triggers: migration, schema, add column, after, index, foreign key, alter table, drop column, deploy schema change
  role: specialist
  scope: implementation
  related-skills: query-performance, production-data-safety, eloquent-model-conventions
---

# Migrations & Schema

## Every new column declares its position

```php
$table->string('hour_type', 30)->nullable()->after('study_hour');
```

A column added without `->after()` lands at the physical end of the table — which on any table with
`timestamps()` or `softDeletes()` means **after** `deleted_at`/`created_at`/`updated_at`. The audit
columns stop being the tail, and the schema becomes unreadable in `SHOW CREATE TABLE`, in the
committed schema dump, and in every GUI client.

Rules:

- Name the real neighbour column.
- Group the new column with what it belongs to **semantically** — a `content_*` column next to the
  other `content_*` columns, an FK next to the other FKs — not merely where it fits.
- Timestamps always stay last. Never place a business column after them, and never let one land
  there by omission.
- **Every** column in a multi-column `Schema::table()` block needs its own `->after()`. Blueprint
  does not carry position forward: chain them, the second after the first, the third after the
  second.
- `$table->softDeletes()` / `$table->timestamps()` are the only exceptions — they belong at the end.

Verify before finishing: read the migration top to bottom and confirm the column list reproduces the
intended final `SHOW CREATE TABLE` order.

On MariaDB 11.1+ with `innodb_instant_alter_column_allowed = add_drop_reorder`, placing a column with
`->after()` is still `ALGORITHM=INSTANT`. Correct placement costs nothing; getting it wrong costs a
second migration that rebuilds the table.

## Additive only, on a live database

If the database is shared with another live application, or holds production data:

- **Additive changes only.** New nullable columns, new tables, new indexes.
- **Never** drop or rename a column in the same release that stops using it. Two releases: stop
  writing, deploy, verify, then drop.
- A `NOT NULL` column added to a populated table needs a default or a backfill plan; adding one
  without either fails on deploy after the code is already out.
- Renaming is a drop+add to every other consumer of that database. If a legacy application still
  reads the table, a rename is an outage.

## Environment drift is normal

Staging and production schemas diverge — someone applied a fix by hand, a migration was run out of
order, an index exists in one place only. Guard migrations so they are idempotent:

```php
if (! Schema::hasColumn('schedules', 'hour_type')) {
    Schema::table('schedules', function (Blueprint $table): void {
        $table->string('hour_type', 30)->nullable()->after('study_hour');
    });
}

if (! $this->hasIndex('schedules', 'schedules_class_id_date_index')) {
    // …
}
```

This is not defensive clutter — it is the difference between a deploy that finishes and one that
aborts halfway across a fleet.

## Indexes on large tables

- An index on a 100M-row table is an hours-long operation and permanent write overhead. Justify it
  with a query plan, never a hunch. See `query-performance`.
- Equality columns first in a composite index, then the range/sort column.
- Check for an existing index that already covers the prefix before adding one.
- Plan the deploy window. On a live table this is a deployment decision, not just a code change.

## Unique constraints

A `UNIQUE` index containing a nullable column does not enforce what you think: `NULL` is never equal
to `NULL`, so duplicates pass. With soft deletes in the key, the constraint disappears entirely.
Enforce the real invariant in the Action **as well**, and say so in a comment on the migration.

## Foreign keys

- State the `ON DELETE` behaviour explicitly. A `CASCADE` added without thought will one day delete
  a journal history because someone removed a lookup row.
- On a big table, adding an FK requires a full validation scan. Same cost conversation as an index.

## Checklist

- [ ] Every added column has `->after()`, chained correctly
- [ ] Timestamps remain last
- [ ] Change is additive, or a two-release plan is written down
- [ ] `hasColumn`/`hasIndex` guards where environments may have drifted
- [ ] New index justified by an `EXPLAIN`, deploy cost considered
- [ ] `down()` actually reverses the change, and is safe to run
