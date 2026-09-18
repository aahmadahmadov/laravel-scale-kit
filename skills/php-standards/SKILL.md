---
name: php-standards
description: Use when writing or reviewing any PHP file in this codebase — strict types, PHPDoc tags, comment policy, naming, final classes, and the small style rules that a linter cannot enforce. Invoke when creating a PHP class, when writing a docblock, when adding a comment, when a private method is being introduced, or when running a code-style pass.
license: MIT
metadata:
  version: "0.2.0"
  domain: language
  triggers: PHP style, strict types, PHPDoc, docblock, comments, naming convention, final class, pint, code style, readonly
  role: specialist
  scope: implementation
  related-skills: layered-architecture, localization-enums
---

# PHP Standards

## Every file starts the same way

```php
<?php

declare(strict_types=1);
```

No exceptions. Without it, a typed `int` parameter silently accepts `"12abc"` and the bug surfaces
three layers away.

## Classes

- Application classes are `final` by default. Inheritance is opt-in, declared deliberately, and
  almost never wanted outside a package base class.
- Constructor property promotion with `private readonly` for dependencies.
- One public entry point per Action/Task: `handle()`. Consistency here is what makes the layers
  greppable.

## PHPDoc

**Never remove a `@param`, `@return` or `@throws` tag**, even when it merely repeats the typed
signature. These tags carry the documentation contract; stripping them as "cleanup" destroys it. If
the formatter is configured to remove superfluous tags, turn that rule off in the formatter config —
do not let it run and then hand-restore.

**Tags stay bare.** The tag itself is what is mandatory, not prose around it:

```php
/**
 * @param mixed $model
 * @param RepositoryInterface $repository
 *
 * @return mixed
 */
```

not

```php
/**
 * @param mixed $model Model or builder the criteria stack is being applied to.
 */
```

A description is added **only** when it states something the type and the parameter name genuinely
cannot — a unit, a format, an accepted value space, or an invariant the caller must uphold
(`ids must already be unique`) — and then only on that one tag. Describing every parameter as a habit
is noise; it is not "more documentation".

Generic collections and arrays do earn their annotation, because the type system cannot express them:

```php
/**
 * @param array<int, int> $pupilIds
 *
 * @return Collection<int, ScheduleDataObject>
 */
```

Application code gets short docblocks. Reusable package code gets longer ones — a package consumer
cannot read the implementation as cheaply as a teammate can.

## Comments

- A comment is written when something is **genuinely non-obvious** — a workaround, a business rule
  the code cannot state, a trap. Never on every block, and never narrating what the next line says.
- **Comments are in English.** One language across the whole codebase, regardless of the team's
  spoken language, regardless of the product's locale. This is not negotiable in a codebase that
  outlives its first team.
- A commented-out block is deleted. Version control already remembers it.

## Small rules that prevent real bugs

- **No single-use private methods.** A private helper called once is either inline code or a Task
  that has not been extracted. A growing tail of private helpers is an Action that needed splitting.
- **Enum predicates over comparisons.** Write `$status->isActive()`, not `$status === Status::ACTIVE`.
  When the value space grows, the predicate is one edit; the comparison is a sweep through call sites.
- **Enum over boolean for mode parameters.** A parameter that answers "which way?" is an enum.
  `handle($pupil, true)` at the call site tells the reader nothing.
- **`isset()` over `!== null`** for a value that may be absent entirely — it handles both cases and
  does not fatal on an undefined key.
- **`?? ` does not catch `''`.** On any column populated by an external sync, blank strings and
  `NULL` coexist. Check for both or normalise on write.
- **Trust the data.** Do not write guards against states the schema and the flow make impossible.
  Defensive checks for impossible states hide the real invariants and double the paths a reader has
  to hold in their head. Validate at the boundary; trust it afterwards.

## Static analysis

- Run the analyser and the formatter **on the files you changed**, not across the repository. A
  whole-repo pass buries the real diff and produces an unreviewable commit.
- A stale path in an analyser baseline aborts every run. If the baseline is broken, use an override
  config and filter by file rather than regenerating a baseline nobody reviews.
- **Lint with the PHP version production runs.** A dev box on 8.5 will happily accept syntax that
  fatals on the 8.2 the servers run. Pin the linter to the deployed version.

## Verify by booting, not by linting

`php -l` and `class_exists()` both pass on a file whose trait aliases conflict, whose service
provider binding is wrong, or whose constructor cannot be resolved. The cheapest real check is
booting the framework — run an artisan command that touches the class.
