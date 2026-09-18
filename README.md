# laravel-scale-kit

**Claude Code skills for Laravel codebases that outgrew controllers and services.**

19 skills · 8 subagents · 3 commands · 1 drop-in `CLAUDE.md` template

---

## What this is

Most Laravel guidance assumes a small app. This plugin encodes one opinionated architecture for the
other case: a codebase with hundreds of endpoints, tables with a hundred million rows, several
people and several agents working in it at once, and a database that holds real data.

The architecture:

```
Controller → (Orchestrator →) Action → Task → Repository (+ Criteria) → Eloquent → DTO → Resource → JSON
```

with two structural rules that keep it from collapsing back into a service layer:

- **An Action never calls another Action.** Combining flows is the Orchestrator's job.
- **A Task never calls another Task.** Composition is the Action's job.

Everything else in this kit — exceptions, policies, model layout, caching, transactions, migrations,
query performance — exists to keep that shape true under pressure.

## What it assumes

| | |
|---|---|
| Framework | Laravel 11 or 12 |
| PHP | 8.2+ |
| Database | **MySQL 8 or MariaDB 10.6+** |
| Application shape | A JSON API with its own controllers, Form Requests and Resources |

**PostgreSQL is not supported.** Several rules are engine-specific and wrong elsewhere — column
placement with `->after()` does not exist in PostgreSQL, and the optimizer, index and `NULL`-in-unique
traps are written against InnoDB. The architecture rules still hold; the database skills do not.

The kit is written for an API. A Livewire, Inertia or Filament-first application shares the layering
but not the `http-boundary` and Resource rules.

## Install

```bash
/plugin marketplace add aahmadahmadov/laravel-scale-kit
/plugin install laravel-scale-kit@laravel-scale-kit
```

Then, in a project you want it to govern:

```
/adopt-conventions existing Laravel 11 API with a service layer
```

That surveys the codebase and writes a `CLAUDE.md` from `templates/CLAUDE.md`, filled in with what it
actually found — versions, existing layers, real table sizes, locales — and shows you the diff before
writing anything.

## The two files that matter

| File | Role |
|---|---|
| `templates/CLAUDE.md` | **Decisions.** Always in context. Short on purpose |
| `skills/*/SKILL.md` | **Depth.** Loaded only when the task touches that area |

Keeping them separate is the point. A 900-line conventions file is a file agents skim; a 90-line one
that points at skills is a file they follow.

## Skills

| Skill | Use when |
|---|---|
| `layered-architecture` | Deciding which class holds the logic |
| `http-boundary` | Controllers, Form Requests, Resources, DTOs |
| `domain-exceptions` | Throwing, translating and rendering errors |
| `authorization-policies` | Policies, `can:` middleware, access predicates |
| `eloquent-model-conventions` | Model layout, relations, aliases, casts |
| `repository-criteria` | Repositories and composable query criteria |
| `filterable-list-endpoints` | `?filter[…]`, `?sort=`, pagination |
| `repository-caching` | Tagged caching, invalidation, stale reads |
| `query-performance` | Slow queries, `EXPLAIN`, very large tables |
| `migrations-schema` | Migrations, column placement, indexes |
| `php-standards` | Strict types, PHPDoc, comments, style |
| `localization-enums` | Translation keys and structured enums |
| `shared-static-helpers` | Comparators, query constraints, composite keys |
| `http-integrations` | Third-party APIs: Adapter + Manager |
| `package-extraction` | Moving generic code into local packages |
| `production-data-safety` | Before any statement that writes |
| `transactions-and-consistency` | Transaction boundaries, job dispatch, races, idempotency |
| `testing-layered-architecture` | Testing actions, tasks, criteria, policies and endpoints |
| `agent-delegation` | Coordinating and **verifying** subagents |

Full index with decision trees: [SKILLS.md](SKILLS.md).

## Agents

`explore`, `be-feature`, `be-debug`, `be-test`, `be-auth`, `be-command`, `db`, `code-review`.

Each carries the constraints in its own prompt, because **an agent does not inherit your rules** —
the database restriction in particular has to be restated in every brief or it does not exist.

## Commands

| Command | Does |
|---|---|
| `/new-endpoint GET /classes/{class}/subjects — list taught subjects` | Locates what exists, decides the layers, confirms, then implements |
| `/architecture-review` | Reviews the diff against the rules, ranked by severity |
| `/adopt-conventions` | Surveys the project and writes its `CLAUDE.md` |

## What this kit is opinionated about

It will tell you to:

- Delete classes that only forward one call.
- Keep repositories empty and put query shapes in Criteria objects.
- Never read `request()` below the controller.
- Never catch your own domain exception.
- Never `whereHas` against a hundred-million-row table.
- Never run a write against a production snapshot without asking a human first.

If you disagree with a rule, delete that skill. A rule nobody follows teaches agents that the
conventions file is optional, and that is more expensive than not having the rule.

## What it deliberately leaves open

The repository layer's base class, the DTO library and the toolkit packages are named as a
**reference implementation** (`prettus/l5-repository`, `spatie/laravel-data`), not as requirements.
The architecture rules are about the pattern: swap the base class and they still hold.

Be aware of the split, though. `repository-criteria` carries a **Prettus-specific** section — criteria
that write methods ignore, `pluck()` not resetting the stack — and those are that library's
behaviours, not properties of the pattern. They are marked as such. If you use a different base
class, verify the equivalents rather than assuming.

The kit also **does not ship the toolkit it describes**. `FilterableListRequest`, the generic
criteria, `BusinessRuleException`, the structured-enum trait and the Adapter/Manager bases are
specified here and built by you. That is deliberate for now — the specification generalises, a
package would pin you to one implementation — but it is real adoption cost, so budget for it.

## Verifying the kit

```bash
python3 scripts/validate_plugin.py     # structure, frontmatter, versions, cross-references, counts
claude plugin eval . --trust-plugin    # does the right skill actually fire, and is its advice ours
```

The first is free and runs in CI on every push. The second costs real model runs and is
`workflow_dispatch` only — run it before a release and whenever a skill's `description` changes,
because that field *is* the routing mechanism. See [evals/README.md](evals/README.md).

## Credits

Extracted from a production Laravel API serving schools nationally — the rules are the ones that
survived contact with 130M-row tables, a shared legacy database and an eight-server fleet.

MIT licensed. Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
