# Quick start

## 1. Install the plugin

```bash
/plugin marketplace add YOUR-GITHUB-USERNAME/laravel-scale-kit
/plugin install laravel-scale-kit@laravel-scale-kit
```

Verify: `/plugin` should list `laravel-scale-kit`, and the skills appear in the available-skills list.

### Local development

Clone it and add the local path instead:

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/laravel-scale-kit.git ~/projects/laravel-scale-kit
```

```bash
/plugin marketplace add ~/projects/laravel-scale-kit
/plugin install laravel-scale-kit@laravel-scale-kit
```

Edits to `skills/*/SKILL.md` take effect on the next session.

## 2. Give a project its conventions file

In the project directory:

```
/adopt-conventions new Laravel 12 API, own MySQL database
```

or, for an existing codebase:

```
/adopt-conventions existing Laravel 11 API, still has app/Services, shared MariaDB with a legacy app
```

It surveys the project first — versions, existing layers, real table sizes, locales, whether the
database is shared — then fills in `templates/CLAUDE.md` and **shows you the diff before writing**.

Review it. Delete the sections that do not apply to this project. A conventions file containing rules
about a layer that does not exist trains agents to skim it.

## 3. Check `CLAUDE.md` is not gitignored

If it is, teammates and CI agents never see it, and every rule in it applies only to you. This is a
surprisingly common and completely invisible failure.

```bash
git check-ignore -v CLAUDE.md
```

## 4. Build something

```
/new-endpoint GET /classes/{class}/subjects — subjects taught in a class with weekly scheduled hours
```

It locates what already exists, proposes the layer breakdown, waits for your approval, then
implements and verifies.

## 5. Review before merging

```
/architecture-review
```

Findings ranked by severity, each with the concrete consequence. Clean diff → one line, no padding.

## Using the agents

The agents ship with the plugin: `explore`, `be-feature`, `be-debug`, `be-test`, `be-auth`,
`be-command`, `db`, `code-review`.

The habit that matters: **`explore` first, then a brief with paths, then verify the result
yourself** — `git status`, read the new files, boot artisan. Untracked files never show up in a diff,
so a report of "created 6 files" is not evidence that 6 files exist.

## Adopting it in an existing codebase

Do not sweep. In order:

1. Write the conventions file.
2. List what already violates it, with counts. That list is the backlog, not a task.
3. Apply the rules to **new** code from today.
4. Migrate a legacy class only when you are touching it anyway, and never in the same commit as a
   behaviour change.

A migration with a visible denominator finishes. One without does not.
