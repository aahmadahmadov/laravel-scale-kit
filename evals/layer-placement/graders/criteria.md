---
type: llm
weight: 3
---

A correct answer routes to the plugin's `layered-architecture` skill and applies its rules.

It must:
- Place the flow in a single Action (assignment + recalculation are one flow, one reason to change),
  NOT split across two Actions and NOT behind an Orchestrator.
- Justify any Task it proposes by reuse or size, and not propose a Task that merely wraps one query
  or one update.
- Keep the controller to a Form Request, one entry-point call and a Resource, with no branching.
- Put query shapes in Criteria, and keep the repository declaring `model()` only.

It must NOT: propose a Service class, propose an Orchestrator for this single flow, propose a
pass-through Action or Task, or put authorization or request reads below the controller.
