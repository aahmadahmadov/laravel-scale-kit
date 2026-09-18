---
description: Review the current diff against the layered-architecture rules
argument-hint: [branch or path to review — defaults to the working tree diff]
---

Review **$ARGUMENTS** (default: the uncommitted working tree diff plus untracked files) against this
project's architecture rules.

Read the diff first. Then check, in this order, and report only what actually fails:

## Blockers

1. An Action calling another Action, or a Task calling another Task.
2. A class that only forwards a single call (pass-through Action/Task).
3. Request input read below the controller, or a conditional criteria push.
4. Authorization outside a policy.
5. Eloquent called on a repository outside a Criteria, or any `DB::table()`.
6. A business helper method added to a repository.
7. `whereHas` or `COUNT(*)` pagination against a table the conventions file declares as large.
8. A write outside the repository with no cache flush.
9. A removed `@param`/`@return`/`@throws` tag.
10. A hardcoded user-facing string.
11. A queue dispatch, HTTP call or cache flush inside a `DB::transaction()` closure.
12. A transaction opened in a Task or an Orchestrator, or nested inside another one.
13. A test using `RefreshDatabase`/`DatabaseMigrations`/`migrate:fresh` against a connection that is
    not a dedicated test database.

## Warnings

- Missing eager load for a relation the Resource touches.
- New migration column without `->after()`, or a business column after the timestamps.
- Model sections out of order, or a new alias not declared in `$aliases`.
- An inline sort closure or interpolated composite key that should have moved to a shared helper.
- A `catch` that neither re-throws nor logs.
- A new index with no `EXPLAIN` justifying it.
- `firstOrCreate`/`updateOrCreate` guarding an invariant that no unique index backs.
- An endpoint test that asserts only the allowed caller, never the denied one.
- A new Criteria with no `toSql()` test.

## Output

For each finding: `path:line`, the rule, and the concrete consequence — what input or state produces
the wrong result. Rank by severity. Do not list style preferences the conventions file does not
state. If the diff is clean, say so in one line and stop.

Untracked files are not in the diff — list them and read them before concluding.
