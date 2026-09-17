# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning is
[SemVer](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-09-18

Initial release.

### Added

- 17 skills covering the layered architecture and everything that keeps it standing:
  `layered-architecture`, `http-boundary`, `domain-exceptions`, `authorization-policies`,
  `eloquent-model-conventions`, `repository-criteria`, `filterable-list-endpoints`,
  `repository-caching`, `query-performance`, `migrations-schema`, `php-standards`,
  `localization-enums`, `shared-static-helpers`, `http-integrations`, `package-extraction`,
  `production-data-safety`, `agent-delegation`.
- 9 reference documents: layer decision tree, a worked end-to-end endpoint, migrating off a service
  layer, an anti-pattern catalogue, a status-code map, a criteria catalogue, a large-table playbook,
  and a MySQL/MariaDB optimizer-trap catalogue.
- 8 subagents: `explore`, `be-feature`, `be-debug`, `be-test`, `be-auth`, `be-command`, `db`,
  `code-review`.
- 3 commands: `/new-endpoint`, `/architecture-review`, `/adopt-conventions`.
- `templates/CLAUDE.md` — a drop-in project conventions file that holds the decisions and points at
  the skills for depth.
