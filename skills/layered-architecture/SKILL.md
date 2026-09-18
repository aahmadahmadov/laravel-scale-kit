---
name: layered-architecture
description: Use when adding or restructuring a Laravel feature and deciding which class should hold the logic — controller, orchestrator, action, task, or repository. Invoke when creating an Action or Task, when a controller is growing business logic, when a service class is being split, when one flow needs to call another, or when asked where a piece of logic belongs. Also use to review whether existing code respects the layer boundaries.
license: MIT
metadata:
  version: "0.2.0"
  domain: backend
  triggers: Laravel architecture, action, task, orchestrator, service layer, where does this logic go, layer boundary, fat controller, business logic placement
  role: architect
  scope: implementation
  related-skills: http-boundary, repository-criteria, domain-exceptions
---

# Layered Architecture

One request flow, five possible layers. The point of this skill is that **each layer has exactly one
reason to exist**, so a reader who opens any class knows what it is allowed to do before reading a
line of it.

## The flow

```
Controller → (Orchestrator →) Action → Task → Repository (+ Criteria) → Eloquent → DTO → Resource → JSON
```

The orchestrator is optional. Use the shallowest chain that satisfies the use-case.

| Use-case | Entry point calls |
|---|---|
| One flow, small or large | Controller → Action |
| Trivial single operation, no branching | Controller → Task |
| Two or more independent flows in one endpoint | Controller → Orchestrator → Actions |

## The layers

| Layer | Path | Allowed to | Never |
|---|---|---|---|
| Controller | `app/Http/Controllers/` | Type-hint a Form Request, call one entry point, return a Resource | Hold a single `if` of business logic, read raw request input, catch domain exceptions |
| Orchestrator | `app/Orchestrators/` | Call two or more Actions and combine their results | Exist for a single Action, query the database, hold flow logic of its own |
| Action | `app/Actions/` | Own **one flow** end to end: get → process → calculate → persist, composing Tasks | Call another Action, read request input, authorize |
| Task | `app/Tasks/` | Perform **one narrow unit of real work**, reusable across Actions | Call another Task, hold flow-level branching, wrap a single query in a class |
| Repository | `app/Repositories/` | Declare `model()` and nothing else | Contain `findById`, `where`, `with`, or any business helper |
| Criteria | `app/Criteria/<Domain>/` | Express one composable query constraint | Hold anything model-agnostic — that belongs in a shared package |

## Decision procedure

Run this top to bottom before creating any class:

1. **Does an existing Action already own this flow?** Extend it with a step, do not start a second one.
2. **Is this one flow or two?** Two independent flows in one endpoint → Orchestrator. One flow with
   several steps → still one Action.
3. **Is the new piece reusable work, or flow logic?** Reusable work → Task. Flow logic → stays in the
   Action, even if the Action grows.
4. **Is it a single query or a single update?** Do it inline in the Action. A class that forwards one
   call adds a file, an interface to learn and a stack frame, and buys nothing.

## The two rules that keep depth flat

- **An Action never calls another Action.** Combining flows is the Orchestrator's job. Without this
  rule, flow A quietly starts depending on flow B's side effects, and neither can be changed alone.
- **A Task never calls another Task.** Composition is the Action's job. Task→Task chaining lets
  dependency depth grow without bound; a flat Task layer stays greppable and testable forever.

Both rules are structural, not stylistic. Violating them is the single fastest way to turn this
architecture back into a service layer with extra folders.

## YAGNI gate

Do not introduce a pass-through class. If an Action or Task only forwards its input to one deeper
call and returns the result unchanged, delete the layer and call the deeper thing directly. Every
class must justify its own existence with either branching, composition, or a real operation.

## Readability gate

When a branch carries a distinct business consequence — a different exception, message or status per
case — write explicit `if` blocks a reader can scan top to bottom. Never compress that decision into
a ternary nested inside a constructor call.

```php
// Good
if ($e->statusCode() === Response::HTTP_NOT_FOUND) {
    throw new EnrollmentException('exceptions.enrollment.not_found', Response::HTTP_NOT_FOUND, $e);
}

throw new EnrollmentException('exceptions.enrollment.failed', $e->statusCode(), $e);

// Bad
throw new EnrollmentException(
    $e->statusCode() === 404 ? 'exceptions.enrollment.not_found' : 'exceptions.enrollment.failed',
    $e->statusCode(),
    $e
);
```

## References

| Topic | File | Load when |
|---|---|---|
| Worked example, controller to JSON | `references/worked-example.md` | Building a new endpoint from scratch |
| Choosing between the layers | `references/decision-tree.md` | Unsure whether something is an Action, Task or inline |
| Migrating away from services | `references/migrating-from-services.md` | The codebase still has `app/Services/` |
| Known anti-patterns | `references/anti-patterns.md` | Reviewing code, or code smells appear |

## Constraints

- Eager-load every relation in the Action or Task layer. Lazy loading must be disabled outside
  production so a missed `with()` fails loudly in development.
- Actions and Tasks take explicit parameters. Never reach for `auth()->user()`, `request()` or any
  ambient global inside them — pass the user in from the controller.
- Never catch a domain exception inside a controller, action or task. Let it reach the global
  handler. See the `domain-exceptions` skill.
