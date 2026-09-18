---
name: testing-layered-architecture
description: Use when writing or reviewing tests for a Laravel codebase built on the Controller/Orchestrator/Action/Task/Repository layering — what to test at each layer, testing criteria and policies, faking the repository, and keeping a test suite off a shared or production-snapshot database. Invoke when adding a test for an Action, Task, Criteria or endpoint, when a test needs a database, when deciding what a test should assert, or when an existing suite passes while the feature is broken.
license: MIT
metadata:
  version: "0.2.0"
  domain: testing
  triggers: test, PHPUnit, Pest, feature test, unit test, RefreshDatabase, factory, mock repository, assert, test database, coverage
  role: specialist
  scope: implementation
  related-skills: layered-architecture, repository-criteria, authorization-policies
---

# Testing a Layered Architecture

The layering exists so that each layer can be tested for one thing. A suite that only feature-tests
endpoints re-tests the framework on every run and still misses the bugs this architecture is shaped
to prevent.

## What each layer owes the suite

| Layer | Test | Needs a database? |
|---|---|---|
| Criteria | Build a query, apply, assert on `toSql()` and `getBindings()` | No |
| Task | The operation, with its repository faked | No |
| Action | The flow: which Tasks ran, which exception on which bad state | No |
| Policy | One test per allow-condition, plus the deny | Usually |
| Controller | Status code, envelope shape, authorization **both ways** | Yes |

Criteria tests are the cheapest and catch the most, because a criteria is the one place a wrong
`where` is invisible in review and fatal in production.

```php
public function test_it_scopes_to_the_education_year(): void
{
    $query = Schedule::query();

    $sql = (new ActiveInEducationYearCriteria(7))
        ->apply($query, $this->repository)
        ->toSql();

    $this->assertStringContainsString('"education_year_id" = ?', $sql);
    $this->assertSame([7], $query->getBindings());
}
```

If a criteria is awkward to test, it is doing two things. Split it.

## Never let the suite reach a shared database

**`RefreshDatabase`, `DatabaseMigrations` and `migrate:fresh` rebuild the schema of whatever
connection the test run resolves.** Pointed at a restored production snapshot or a database shared
with a legacy application, that is not a failing test — it is data loss, from a command that looks
routine in CI.

- Give tests their own connection, declared in `phpunit.xml`, and assert on it in a base test case:
  fail loudly if the resolved database name is not the test one.
- If a separate database genuinely is not available, use `DatabaseTransactions`, say so in the
  conventions file, and never use a trait that migrates.
- Factories over fixtures. A test that depends on a row someone inserted by hand will rot, and it
  will rot on someone else's branch.

## Testing an Action

An Action's contract is the flow, so fake the repository and assert on what it was told to do — not
on rows.

- **Assert which criteria were pushed**, by class. A fluent mock that returns `$this` from
  `pushCriteria()` and is never asserted on tests nothing at all; that is the most common empty test
  in this architecture.
- **Test the failure paths.** One test per domain exception the Action can throw, named after the
  rule: `test_it_rejects_a_pupil_who_is_not_enrolled()`.
- Actions take explicit parameters and never read `request()` or `auth()`, so an Action test needs
  no HTTP context at all. If yours does, the Action is violating the architecture — fix the Action,
  do not fake a request.

## Testing the HTTP boundary

- **Assert the denied direction.** A policy broken by a `can:` middleware parameter mismatch denies
  *everyone*, and a suite that only asserts the 200 for an allowed user passes happily. Every
  endpoint test asserts one allowed caller and one denied caller.
- Assert the envelope the global handler produces (`{"message": …}`) for a business failure, not just
  the status. That envelope is the frontend's contract.
- Assert the **shape** of the payload, not every value. A test that pins all 40 fields fails on every
  additive change and teaches the team to update tests without reading them.

## Traps

**Criteria leak between assertions.** Criteria accumulate on a repository instance. Two assertions in
one test against a container-bound repository silently AND the first one's filters into the second.
Resolve a fresh repository per case, or wrap in the project's fresh-criteria helper.

**Global scopes make tests pass in one calendar year and fail in the next.** A model scoped to the
current education year needs the factory to create rows inside that window. Freeze time
(`$this->travelTo(...)`) rather than seeding whatever "now" happens to be.

**`Http::fake()` tests the adapter, not the manager.** What matters is the mapping: fake each upstream
status the manager claims to handle and assert the domain exception and status it produces. A manager
tested only on 200 is untested.

**Cache state survives between tests** when the driver is shared. Flush tags in `setUp()`, or use the
array driver for tests and accept that tag behaviour then differs from production.

**Do not assert query counts** unless the count is the requirement. `assertQueryCount(3)` fails on
every unrelated eager load and gets deleted rather than fixed. Assert the absence of the thing you
care about — a lazy-load exception, for example, which a disabled lazy-loading setting already
raises.

## Checklist

- [ ] The test connection is asserted, not assumed — no migrating trait against a shared database
- [ ] Every new Criteria has a `toSql()` + bindings test
- [ ] Every domain exception an Action throws has a test named after its rule
- [ ] Every endpoint test asserts one allowed and one denied caller
- [ ] Repository fakes are asserted on, not just satisfied
- [ ] Integration managers tested per upstream status, not only on success
