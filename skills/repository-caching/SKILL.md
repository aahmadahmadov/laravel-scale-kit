---
name: repository-caching
description: Use when adding or debugging caching in a Laravel data layer — cacheable repositories, tag-based invalidation, cached projections, stale reads, and cache keys. Invoke when a read returns stale data after a write, when deciding what to cache, when a cache flush does not seem to work, or when a sync process must bypass the cache.
license: MIT
metadata:
  version: "0.2.0"
  domain: backend
  triggers: cache, caching, stale data, flushCache, cache tags, Redis, invalidation, cached repository, TTL, cache key
  role: specialist
  scope: implementation
  related-skills: repository-criteria, query-performance
---

# Repository Caching

Caching in a repository layer is the highest-leverage and highest-risk change in this architecture.
Every rule below exists because of a stale-read bug that was hard to find.

## What gets cached

Only the read wrappers, under a **per-repository tag**, with an explicit TTL:

`all`, `paginate`/`simplePaginate`, `find`, `findByField`, `findWhere`, `getByCriteria`.

Consequence worth internalising: `find()` is cached but `first()` and `count()` are **not**. Two
lines that look equivalent behave completely differently after a write.

## The cache key is the query

The key is a hash of the compiled SQL plus its bindings. Two implications:

- Identical SQL from two different call sites shares one entry. Usually fine.
- **A closure inside a criteria does not appear in the SQL used for the key.** Two calls that differ
  only by a closure parameter collide and return each other's data. Any criteria carrying a closure
  must contribute something to the key, or must not be cached.

## Invalidation only covers repository writes

Anything written outside the repository leaves the cache stale:

- `$model->update(...)`
- `$model->relation()->sync(...)` / `attach()` / `detach()`
- raw builder statements
- another process writing to the same table

After any of these, call `flushCache()` on the affected repository yourself. There is no framework
mechanism that will do it for you.

**Put every write behind one trait.** A single `PerformsCacheSafeWrites` (or equivalent) that holds
every write method and always calls the flush is the only design that survives contact with a growing
team. Several partial traits, each flushing sometimes, is how half the writes end up stale.

## Pivot writes need special handling

A model fetched through a caching repository and then used for `->sync()` writes to the pivot without
the repository ever knowing. Route pivot writes through a dedicated helper that performs the write
**and** flushes — never through a bare `find()` + `sync()`.

## Payload size is a real cost

A cached collection is serialized. If the model declares `protected $with = ['user']`, every entry
carries the related rows too — even when the read asked for `all(['id'])`. A GET that got slower after
caching was added is almost always payload size, not query time. Check `$with` first.

Related: **a cached model freezes its `$casts`**. Changing a cast does not change what is already in
the cache; the change is invisible until the tag is flushed. After any cast or accessor change on a
cached model, flush the tag as part of the deploy.

## Sync processes must never read the cache

An importer that reads through the cache will compare upstream data against a stale snapshot and
"fix" rows that were already correct — or miss rows that changed. Every sync, backfill or reconcile
process reads with caching disabled (`withoutReadCache()` or equivalent) and flushes what it wrote.

## Cached projections

For an expensive aggregate reused across requests, cache the **projection**, not the models: a small
array keyed by id, with an explicit TTL and a name that says what it holds. Rules:

- TTL only. Do not attempt event-based invalidation for a projection derived from several tables —
  you will miss a path.
- The TTL is a business decision (how stale may this number be?), written down next to the code.
- Never cache a projection whose key depends on the acting user unless the user id is in the key.

## Locks

When a cached computation is expensive enough to need a lock against a stampede, keep the lock key,
TTL and wait time in **one registry**, never as class constants scattered across callers. "Wait
seconds" must mean one thing project-wide.

## Debug checklist for a stale read

1. Was the write made through the repository? If not, that is the bug.
2. Is the read one of the cached methods? (`first()` and `count()` are not.)
3. Does the criteria carry a closure that the key cannot see?
4. Is `$with` inflating the payload and hiding the real cost?
5. Is the cache driver tag-capable? A database or file driver will crash or silently no-op on
   `Cache::tags()` — verify the configured driver in every environment, not just production.
