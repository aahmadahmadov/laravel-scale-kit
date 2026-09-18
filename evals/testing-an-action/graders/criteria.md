---
type: llm
weight: 3
---

A correct answer routes to the plugin's `testing-layered-architecture` skill.

It must:
- Warn explicitly that `RefreshDatabase` / `DatabaseMigrations` / `migrate:fresh` would rebuild the
  schema of that production copy, and tell the user to configure a separate test connection, or at
  minimum use transaction-wrapping and never a migrating trait.
- Test the criteria without a database, by applying it to a query and asserting on `toSql()` and the
  bindings.
- Test the Action with the repository faked, asserting on WHICH criteria were pushed, and warn that a
  fluent mock nobody asserts on tests nothing.
- Note that the Action needs no HTTP context because it does not read the request.

A strong answer also mentions freezing time because of the education-year global scope, or asserting
the denied path when the endpoint itself is tested.

It must NOT recommend running the suite against the production copy as-is.
