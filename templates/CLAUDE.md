# CLAUDE.md

Guidance for Claude Code in <project-name>.

> Generated from [laravel-scale-kit](https://github.com/aahmadahmadov/laravel-scale-kit).
> This file holds the **decisions**. The depth lives in the plugin's skills, which load on demand —
> keep this file short enough that it is actually read.

## Stack

Laravel <11>, PHP <8.2>, <MySQL 8 / MariaDB 10.6>. <State the PHP version production runs if it
differs from local — lint against that one.>

## Project Overview

<Laravel 11 REST API for …. One sentence on the domain, one on who the consumers are, one on whether
the database is shared with another application.>

## Commands

```bash
composer install
composer dev              # server + queue + logs + vite
php artisan test
php artisan pint          # changed files only
```

**NEVER run:**

```
php artisan migrate:fresh
php artisan migrate:refresh
php artisan migrate:reset
php artisan db:seed
```

<State why: e.g. "the local environment connects to a production data snapshot.">

## Database Safety

**The database holds real data. Never run a statement that changes data or schema without asking
first and getting an explicit yes.** Forbidden without permission: `UPDATE`, `DELETE`, `INSERT`,
`REPLACE`, `TRUNCATE`, all DDL including adding an index, `migrate`, `db:seed`, and any writing
tinker snippet — through artisan, a raw client, a script, or an MCP tool.

Allowed: `SELECT`, `EXPLAIN`, `SHOW CREATE TABLE`, `SHOW INDEX`, `information_schema` reads — kept
bounded on the large tables.

**Repeat this restriction in every brief given to a subagent.** It is not inherited.

Full procedure: the `production-data-safety` skill.

## Architecture

**Request flow:** `Controller → (Orchestrator →) Action → Task → Repository (Criteria) → Eloquent →
DTO → Resource → JSON`

| Layer | Location | Rule |
|---|---|---|
| Controller | `app/Http/Controllers/` | HTTP in/out only. Dedicated Form Request, one call, a Resource. Zero business logic |
| Orchestrator | `app/Orchestrators/` | Combines **two or more** flows by calling their Actions. Never for a single flow |
| Action | `app/Actions/` | Business logic for **exactly one** flow. **Never calls another Action** |
| Task | `app/Tasks/` | One narrow, reusable unit of real work. **Never calls another Task** |
| Repository | `app/Repositories/` | Declares `model()`. Nothing else |
| Criteria | `app/Criteria/<Domain>/` | Domain-specific query filters. Generic ones live in <package> |
| DTO | `app/DTO/` | `spatie/laravel-data`. Named `*DataObject` |
| Resource | `app/Http/Resources/` | Serialization only |

**YAGNI:** no pass-through classes. If an Action or Task only forwards one call, skip the layer.

**Readability:** a branch with a distinct business consequence is written as explicit `if` blocks,
not a ternary inside a constructor call.

<If migrating: "New code follows the architecture above. `app/Services/` is legacy — N classes
remain — and moves only when touched.">

Depth: the `layered-architecture` skill.

## Transactions

The transaction boundary is the **Action**, opened once, around database work only. Tasks and
Orchestrators never open one — a nested `DB::transaction()` is a savepoint, so an inner rollback
leaves the outer work committed.

Nothing that is not a database write goes inside: no HTTP call, no cache flush, no queue dispatch, no
file write. **Dispatch jobs and flush caches after commit** — a job dispatched inside the transaction
is visible to a worker before the row exists, and that failure only appears under load.

Uniqueness that matters is backed by an index; `firstOrCreate`/`updateOrCreate` are not atomic.
Anything that runs unattended states what a second run does.

Depth: the `transactions-and-consistency` skill.

## Testing

<State the test connection here, and that it is NOT the development database.> Never use
`RefreshDatabase`, `DatabaseMigrations` or `migrate:fresh` against a database that holds real data —
they rebuild the schema of whatever connection resolves.

Criteria are tested without a database (`toSql()` + bindings). Actions are tested with the repository
faked, asserting which criteria were pushed. Every endpoint test asserts one allowed caller **and**
one denied caller — a broken `can:` binding denies everyone and passes a happy-path suite.

Depth: the `testing-layered-architecture` skill.

## API surface

- `routes/api/v1.php` — <consumers>, `<guard>` guard
- `routes/api/v2.php` — <consumers>, `<guard>` guard

## PHP Standard

Every new PHP file starts with `<?php` + `declare(strict_types=1);`. No exceptions.

**Never remove a `@param`, `@return` or `@throws` tag** from any docblock, even when it repeats the
signature. Configure the formatter so it cannot strip them. Tags stay **bare** — a description only
when it states something the type and name cannot (a unit, a format, an invariant the caller must
uphold).

Comments in English, only where something is genuinely non-obvious.

Depth: the `php-standards` skill.

## Engineering Principles

`SOLID`, `DRY`, `KISS`, `YAGNI`, `OOP`, applied by default. Every class must have a clear
responsibility and justification.

## Exception Rules

- Domain exceptions: `app/Exceptions/<Domain>/`, `final`, extending `BusinessRuleException`.
- Constructor: `(string $message = '<generic domain key>', int $statusCode, ?Throwable $previous)`.
  The parent calls `__()`, so callers always pass a **translation key**.
- One exception class per flow domain. Existing domains: <list>.
- Shared managers throw their **own** generic exception; each caller translates it with explicit
  `if` per status.
- Controllers, actions and tasks **never catch** their own domain exceptions — the global handler
  renders `{"message": "…"}`.
- A `try/catch` below the controller is allowed only to (1) continue after a non-fatal failure, or
  (2) translate a shared manager's exception. Never a silent swallow.

Depth: the `domain-exceptions` skill.

## Authorization

Policies in `app/Policies/`, invoked by `can:` route middleware for grouped access, or
`$this->authorize()` for a single endpoint. Never an `if` in an action, task or repository. Policy
methods are allow-conditions ending in one `Response::deny(__('…'))`; the real checks are predicates
on the user model.

**`can:ability,model` resolves by route parameter name** — a mismatch denies everyone, silently.
**Route-scoped authorization does not scope the request body** — re-resolve payload ids.

Depth: the `authorization-policies` skill.

## Localization

Primary locale `<az>`; `APP_LOCALE` set in `.env`. No hardcoded user-facing strings — every message
is a key, present in **every** lang file. `Log::` lines stay English. Stable finite value spaces are
enums; external values parsed with `tryFrom()`.

Depth: the `localization-enums` skill.

## Repository Rules

- Repositories define `model()` only. No `findById`, no `create`, no business helpers.
- Never call Eloquent (`where`, `with`, `whereHas`) on a repository outside a Criteria.
- Eager-load through `WithCriteria`, never `->with([...])`.
- A dedicated Criteria class is earned by **2+ reuses**. A single-column check uses the generic
  package criteria.
- **Never use the `DB` facade** unless explicitly asked — it bypasses events, observers, caching and
  soft deletes.
- Pushing criteria in a loop: wrap in the fresh-criteria helper, and confirm it re-applies boot
  criteria.
- Caching: <which trait>, <TTL>, per-repository tag. Writes made outside the repository leave the
  cache stale — flush explicitly.

Depth: the `repository-criteria` and `repository-caching` skills.

## Filter & Sort Rules

List endpoints use the shared filterable-list stack from <package>. The Form Request declares
allowed filters and sorts; the Action pushes `FilterFieldsCriteria`, `FilterTrashedStatusCriteria`
and `RequestSortCriteria` **unconditionally**.

**An Action or Task never reads request input.** No `request()`, no `$request` parameter, no
`filled()` gate around a push. The criteria reads the request and no-ops when the value is blank.

New filter shapes are written **in the package** as generic classes, not as one-offs in `app/`.

Depth: the `filterable-list-endpoints` skill.

## Model Layout

Section markers, in order: `use` statements → `// Attributes start/end` → `boot()`/`booted()` →
`// Relations start/end` → `// Scopes start/end` → `// Helpers start/end`. Omit an empty section.

Invented identifiers (SQL aliases, computed flag keys) are declared in `protected array $aliases`
next to `$fillable`, documented with `@property-read`, and used as **plain strings** at call sites —
never a `const`, never an enum.

Depth: the `eloquent-model-conventions` skill.

## Sorting & Query Constraints

- In-memory sorting goes through `app/Support/Comparators/<Entity>Comparator::by<Criteria>()` —
  never an inline closure. Always include a deterministic tiebreaker.
- Reusable `with()`/`withCount()`/`whereHas()` closures live in
  `app/Support/QueryConstraints/<Entity>Constraint`, returning the `['relation as alias' => callable]`
  pair.
- Composite keys are built only in `App\Support\CompositeKeyGenerator`.
- Non-retroactive: migrate an inline closure when you touch it, do not sweep the codebase.

Depth: the `shared-static-helpers` skill.

## Migration Conventions

**Every new column declares `->after()`** naming its real neighbour; chain them in multi-column
blocks; timestamps stay last. Additive only on a live database. Guard with `hasColumn`/`hasIndex` —
environments drift.

Depth: the `migrations-schema` skill.

## Large Tables

| Table | Approx rows | Rule |
|---|---|---|
| `<table>` | ~<N>M | `simplePaginate` only; `JOIN`/`whereIn`, never `whereHas` |

Depth: the `query-performance` skill.

## Integrations

Third-party HTTP APIs: an **Adapter** (transport, thin one-liners, explicit timeout) paired with a
**Manager** (normalises response shapes, maps upstream errors to a domain exception with your own
translation key, never returns success on failure). Both log to a dedicated per-integration channel.

Depth: the `http-integrations` skill.

## Local Packages

<Name each package, its composer name, namespace, and what it holds. State the boundary rule: a
package must never depend on the `App\` namespace, and its translations ship under its own
namespace.>

Depth: the `package-extraction` skill.

## Key Conventions

- Eager-load every relation in the action/task layer — lazy loading is disabled outside production.
- Domain exception subclasses, not `ValidationException`, for business rule failures.
- Deduplicate composite records with explicit PHP keys, not SQL `GROUP BY`.
- Resources use `whenLoaded()` for optional relations.
- DTOs named `*DataObject`, constructed with `new`, never `::from()`.
- Every controller method taking input type-hints a dedicated `final` Form Request from
  `app/Http/Requests/<Domain>/`. Never read raw input in a controller.
- `DB::transaction()` is opened in the Action and nowhere else; jobs dispatch and caches flush after
  it commits.

## Agent Team

The active session is the **manager**: understand, delegate, verify. <Keep or delete this section
depending on whether the project uses subagents.>

| Agent | When |
|---|---|
| `explore` | Any file read or "where is X". Before any other agent |
| `be-feature` | New actions, tasks, orchestrators, repositories, criteria, DTOs, resources, controllers, requests |
| `be-debug` | Any bug, stack trace, or unexpected behaviour |
| `be-test` | Tests |
| `be-auth` | Guards, tokens, SSO, policies |
| `be-command` | Console commands, sync jobs, data migration scripts |
| `db` | Migrations, schema, query optimisation |
| `code-review` | Quality gate before done |

Rules: `explore` first; pass **paths, not contents**; run independent agents in parallel; restate the
database and architecture constraints in every brief; **verify results yourself** — `git status`,
read the new files, boot artisan. Untracked files do not appear in a diff.

Depth: the `agent-delegation` skill.
