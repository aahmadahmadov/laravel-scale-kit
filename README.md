# laravel-scale-kit

**Claude Code skills for Laravel codebases that outgrew controllers and services.**

17 skills · 8 subagents · 3 commands · 1 drop-in `CLAUDE.md` template

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

Everything else in this kit — exceptions, policies, model layout, caching, migrations, query
performance — exists to keep that shape true under pressure.

## Install

```bash
/plugin marketplace add YOUR-GITHUB-USERNAME/laravel-scale-kit
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
The rules are about the pattern. Swap the base class and every rule still holds.

## Credits

Extracted from a production Laravel API serving schools nationally — the rules are the ones that
survived contact with 130M-row tables, a shared legacy database and an eight-server fleet.

MIT licensed. Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
