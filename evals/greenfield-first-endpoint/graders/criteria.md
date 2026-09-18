---
type: llm
weight: 3
---

A correct answer routes to the plugin's `layered-architecture` skill (its
`references/greenfield-setup.md` in particular) and sizes the advice to an empty project.

It must:
- Propose the minimum chain — Controller, a dedicated Form Request, an Action, a Resource — and say
  that Repository, Criteria, Task and Orchestrator are extractions made when something asks for
  them, not folders to create up front.
- NOT tell the user to create a composer package, a `packages/` directory, or a toolkit. The
  threshold for a package is a second consumer, and this project has one.
- If it recommends a generic filter/criteria class at all, place it in `app/Criteria/Shared/` (or an
  equivalent in-app location), NOT in a package that does not exist.
- Name the things that must hold from the first file because retrofitting them is expensive: strict
  types, no request/auth access below the controller, translation keys rather than literal strings,
  domain exceptions, a policy, and a test connection separate from development.

It must NOT: propose an Orchestrator, propose a Task for a single query, propose caching, or produce
a directory tree containing empty layers "for later".
