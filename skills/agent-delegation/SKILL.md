---
name: agent-delegation
description: Use when working on a large codebase as a coordinating session that delegates to subagents — deciding what to delegate, writing agent briefs, running agents in parallel, and verifying their output. Invoke when a task spans many files, when choosing between doing work inline or handing it off, or when an agent's report needs verifying.
license: MIT
metadata:
  version: "0.2.0"
  domain: workflow
  triggers: delegate, subagent, agent brief, parallel agents, explore first, verify agent output, manager agent, task handoff
  role: architect
  scope: workflow
  related-skills: layered-architecture, production-data-safety
---

# Agent Delegation

On a codebase large enough that no session can hold it in context, the coordinating session's job is
to **understand, delegate and verify** — not to type. This skill describes that split and, more
importantly, how not to be lied to by a subagent's summary.

## The agent roster

Ship these as plugin agents (see `agents/` in this plugin) or define them per project:

| Agent | Use for |
|---|---|
| `explore` | Any file read, symbol search, "where is X". Cheap model. Run it **first**, always |
| `be-feature` | New code: actions, tasks, orchestrators, repositories, criteria, DTOs, resources, controllers, requests |
| `be-debug` | Any bug, error, stack trace, unexpected behaviour |
| `be-test` | Tests |
| `be-auth` | Auth guards, tokens, SSO, policies — security-sensitive work |
| `be-command` | Console commands, sync jobs, report generators, data migration scripts |
| `db` | Migrations, schema analysis, query optimisation |
| `code-review` | Quality gate before a task is considered done |

## Rules

1. **`explore` first.** Before writing a brief for any other agent, locate the relevant files and
   establish current state. More than two file reads in the coordinating session means an `explore`
   was skipped.
2. **Pass paths, never contents.** A brief contains file paths and the decision; the agent reads its
   own files. Pasting file contents into a brief wastes the context you were trying to save.
3. **Run independent agents in parallel**, in one message. Two unrelated features, or a feature and
   its tests against an already-written interface, are independent.
4. **One flow per agent.** An agent asked to do four unrelated things will do the first one well.
5. **Restate the constraints in every brief.** Database restrictions, architecture rules and the
   "ask before writing" rule are **not inherited**. An agent whose prompt does not forbid a
   destructive statement may run one.
6. **Verify. Do not trust the summary.** This is the rule that matters.

## Verifying an agent's work

Agent reports are optimistic. Before accepting one:

- `git status` — did files appear where you expected, and only there? **Untracked files do not show
  in a diff**; a new file's existence is only proven by reading it.
- Read at least the entry point of every new class. "Created `FooAction`" and "created a working
  `FooAction`" are different claims.
- Boot the framework — run an artisan command that touches the new code. `php -l` and `class_exists`
  both pass on a file with a trait-alias fatal or an unresolvable constructor.
- For a mechanical sweep across many files, verify with a **multiset diff** of before/after results,
  not by reading the diff.
- When two agents report conflicting facts, neither is authoritative. Go look.

## Writing a good brief

```
Goal:        one sentence, the outcome
Files:       exact paths from explore
Constraints: architecture rules that apply + the DB rule, restated
Out of scope: what not to touch
Done when:   the observable condition
```

Vague briefs produce invented abstractions. An agent told "improve the schedule flow" will create
enums, interfaces and a cache layer nobody asked for. Scope discipline is the brief's job.

## When not to delegate

- A one-line change in a file already open and understood.
- A question the coordinating session can answer from what it already read.
- Anything where writing the brief costs more than doing the work — but be honest, because that
  estimate is where context budgets go to die.

## Keep memory outside the session

Facts worth carrying between sessions — a table's real meaning, a trap in a library, a decision and
its reason — belong in a project conventions file or a durable memory store, not in a chat log that
will be summarised away. One line per fact, with the reason attached.
