---
name: package-extraction
description: Use when deciding whether code should move out of app/ into a local composer package, or when working inside one — path repositories, package boundaries, namespaced translations, and avoiding App coupling. Invoke when a class is needed by a second project, when generic infrastructure is accumulating in app/, or when editing a packages/ directory.
license: MIT
metadata:
  version: "0.1.0"
  domain: backend
  triggers: composer package, local package, path repository, extract package, monorepo, shared library, package boundary, vendor symlink
  role: architect
  scope: implementation
  related-skills: repository-criteria, localization-enums, http-integrations
---

# Package Extraction

First-party packages live under `packages/`, registered as `path` repositories in the root
`composer.json` and symlinked into `vendor/<vendor>/`. They are how generic infrastructure stops
being copy-pasted between projects.

## The threshold

Extract when the code is needed in **2 or more** places — a second project, or a second bounded
context in this one. Not before. A package built for one consumer is a folder move that adds a
release step and buys nothing.

What typically earns extraction in a Laravel codebase of this shape:

| Package | Holds |
|---|---|
| `*-toolkit` for the repository layer | generic criteria, repository traits, the filterable-list request stack, shared enums |
| `*-toolkit` for enums | the structured-enum contract and serialization trait |
| `*-toolkit` for integrations | the adapter base, HTTP concern, manager base, exception translation |

## The boundary rule

**A package must never reference the `App\` namespace.** Not in a type hint, not in a config lookup,
not in a translation key. The moment it does, it is application code in a subdirectory.

Two techniques cover almost every case where a package seems to need the app:

1. **Push the app-specific value behind an abstract method.** A package base class that needs the
   host's log channel declares `abstract protected function logChannel(): string;` — the host adapter
   returns its own enum's `->value`. The package never sees the enum.
2. **Widen the return type and let the host narrow it.** A package method declared to return
   `\Throwable` lets every host manager narrow it to its own domain exception base, because PHP
   return types are covariant.

## Translations

Package-owned strings ship in the package's own `lang/` under a package namespace
(`my-toolkit::messages.key`), overridable by the host application. **Never** add a package's strings
to the app's `lang/az/` or `lang/en/` — the next project that installs the package would get a
missing key.

## Documentation

Each package carries its own `README.md`, and it is the contract:

- What each class does and when to use it.
- Every gotcha, especially caching and invalidation semantics.
- A changelog entry per behaviour change.

Read the package README before touching the package. Update it in the same commit as the change —
package docs that lag are worse than none, because they are trusted.

## Working inside a package

- **Longer docblocks than app code.** A consumer cannot read the implementation as cheaply as a
  teammate can.
- No framework facades that assume the host's configuration; accept configuration through the
  constructor or a published config file.
- Version it. Even a path repository benefits from a version number in the changelog, because the
  question "does the deployed app have the fix?" must be answerable.

## Reverting an extraction is allowed

If a package turns out to have one consumer and a fiddly boundary, fold it back into `app/` and say
why in the changelog. A reverted extraction is a cheap lesson; a package nobody can change is not.

## Checklist

- [ ] 2+ consumers, or a concrete second one is imminent
- [ ] Zero `App\` references in the package
- [ ] Translations namespaced to the package
- [ ] README written, gotchas documented
- [ ] Host-specific values injected through abstract methods or constructor, not looked up
