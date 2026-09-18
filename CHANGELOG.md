# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning is
[SemVer](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-09-18

### Added

- `transactions-and-consistency` skill — the transaction boundary belongs to the Action, what may not
  happen inside it (HTTP calls, job dispatch, cache flushes), the races a transaction does not fix,
  and idempotency for anything that runs unattended.
- `testing-layered-architecture` skill — one test shape per layer, criteria tests without a database,
  and the rule that keeps `RefreshDatabase` away from a restored production snapshot.
- `scripts/validate_plugin.py` — structural validation of frontmatter, name/path agreement, version
  agreement, reference cross-links, the counts quoted in the docs, and the contribution rule that
  every Bash-holding agent restates the database write restriction.
- `evals/` — 7 eval cases with `claude plugin eval`, checking that a realistic request routes to the
  intended skill and that the answer carries the kit's rules. Ablation on by default, so the report
  shows the plugin's delta rather than the model's baseline.
- `.github/workflows/validate.yml` — structural checks on every push; the eval suite on demand.
- README now states the supported stack explicitly (Laravel 11/12, PHP 8.2+, MySQL 8 / MariaDB
  10.6+), that **PostgreSQL is not supported**, and that the toolkit the skills describe is specified
  but not shipped.

### Changed

- Every skill's `metadata.version` now follows the plugin version, enforced in CI.
- `repository-criteria` marks its Prettus-specific behaviours as library behaviours rather than
  properties of the pattern.
- `domain-exceptions` and `repository-criteria` now link their own reference documents, which were
  previously only reachable from `SKILLS.md`.

### Fixed

- `be-auth` and `code-review` hold `Bash` but never restated the database write restriction, which
  CONTRIBUTING.md requires of every agent that can reach a database. Both now do.
- The 0.1.0 entry miscounted the reference documents (nine claimed, eight shipped).
- Typo in the anti-pattern catalogue (`findActiveByschool`).

## [0.1.0] — 2026-09-18

Initial release.

### Added

- 17 skills covering the layered architecture and everything that keeps it standing:
  `layered-architecture`, `http-boundary`, `domain-exceptions`, `authorization-policies`,
  `eloquent-model-conventions`, `repository-criteria`, `filterable-list-endpoints`,
  `repository-caching`, `query-performance`, `migrations-schema`, `php-standards`,
  `localization-enums`, `shared-static-helpers`, `http-integrations`, `package-extraction`,
  `production-data-safety`, `agent-delegation`.
- 8 reference documents: layer decision tree, a worked end-to-end endpoint, migrating off a service
  layer, an anti-pattern catalogue, a status-code map, a criteria catalogue, a large-table playbook,
  and a MySQL/MariaDB optimizer-trap catalogue.
- 8 subagents: `explore`, `be-feature`, `be-debug`, `be-test`, `be-auth`, `be-command`, `db`,
  `code-review`.
- 3 commands: `/new-endpoint`, `/architecture-review`, `/adopt-conventions`.
- `templates/CLAUDE.md` — a drop-in project conventions file that holds the decisions and points at
  the skills for depth.
