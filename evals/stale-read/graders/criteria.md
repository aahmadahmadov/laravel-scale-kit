---
type: llm
weight: 3
---

A correct answer routes to the plugin's `repository-caching` skill.

It must identify that `sync()` writes to the pivot without the repository knowing, so nothing
invalidates the cache, and that invalidation only covers writes made through the repository.

The fix it gives must include flushing the affected repository's cache explicitly, and it should
recommend routing pivot writes through one shared write helper/trait that always flushes, rather
than remembering to flush at each call site.

A strong answer also mentions at least one of: `first()`/`count()` not being cached while `find()`
is; a closure inside a criteria not appearing in the cache key; `$with` inflating the cached payload;
the cache driver needing to be tag-capable.

It must NOT suggest simply lowering the TTL or disabling caching as the primary fix.
