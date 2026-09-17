---
description: Create or update this project's CLAUDE.md from the laravel-scale-kit template
argument-hint: [project type hint, e.g. "new Laravel 12 API" or "existing codebase with services"]
---

Set up this project's conventions file. Context: **$ARGUMENTS**

## 1. Survey the project

Do not guess. Establish and report:

- Laravel and PHP versions (`composer.json`), and the **PHP version production runs** if it differs.
- Whether `app/Actions`, `app/Tasks`, `app/Orchestrators`, `app/Services` exist, and how many classes
  are in each.
- The repository layer in use, if any, and whether it caches.
- Database engine and version. Any table over ~10M rows — get the estimate from
  `information_schema.tables`, never a `COUNT(*)`.
- Configured locales, and whether user-facing strings are already keyed.
- Whether the database is a production snapshot, whether it is shared with another application, and
  whether binary logging is on.
- Existing `CLAUDE.md` / `AGENTS.md` content — it must be preserved, not overwritten.

## 2. Draft

Start from `templates/CLAUDE.md` in this plugin. Fill in every `<…>` placeholder from the survey.
Delete whole sections that do not apply — a rule about a layer the project does not have is noise
that teaches an agent to ignore the file.

If the project still has a service layer, keep the migration note: *new code follows the new
architecture, existing services move only when touched*, and record how many remain.

## 3. Confirm before writing

Show the diff against any existing conventions file and wait for approval. Never silently replace
rules someone wrote deliberately.

## 4. After writing

- Point out which rules the current codebase already violates, with counts — that list is the backlog.
- Note whether `CLAUDE.md` is gitignored. If it is, CI agents and teammates will never see it, and
  that is worth fixing before anything else here matters.
