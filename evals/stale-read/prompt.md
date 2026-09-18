---
name: "Stale read after a pivot write"
description: "A stale read after a pivot write; must land on the real invalidation cause, not the TTL."
tags: [routing, caching]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

We have a caching repository layer. After this runs, a `GET` on the same data keeps returning the
old subject list for several minutes:

```php
$class = $this->classRepository->find($classId);
$class->subjects()->sync($subjectIds);
```

Why, and what is the fix?
