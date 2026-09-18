---
name: "List endpoint over a very large table"
description: "A slow list endpoint over a 136M-row table; must reject the correlated subquery and the counting paginator."
tags: [routing, performance]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

This list endpoint takes about 40 seconds. `exam_scores` has roughly 136 million rows.

```php
$scores = ExamScore::whereHas('pupil', fn ($q) => $q->where('school_id', $schoolId))
    ->with('subject')
    ->paginate($perPage);
```

What is wrong and what should it be?
