---
type: llm
weight: 3
---

A correct answer routes to the plugin's `query-performance` skill (and may also use
`filterable-list-endpoints`).

It must:
- Identify `whereHas` against a very large table as the primary problem, explaining that it compiles
  to a correlated EXISTS the optimizer re-plans per row.
- Replace it with the ids-first pattern: resolve pupil ids with a cheap query, then a flat `whereIn`.
- Identify `paginate()` as a second problem because of the `COUNT(*)`, and recommend
  `simplePaginate()` on a table this size.
- Recommend measuring with EXPLAIN on the exact statement rather than with a stopwatch.

It is also correct to warn that adding an index is not the first move and must be justified by a
plan. It must NOT simply suggest "add an index" as the fix, and must NOT claim a timing improvement
it did not measure.
