---
description: Plan and scaffold a new API endpoint through the full layered architecture
argument-hint: <METHOD> <path> — <one-line description of what it returns or does>
---

Plan a new endpoint: **$ARGUMENTS**

Work in this order. Do not write any file until step 3 is answered.

## 1. Locate

Find, and report paths for:

- An existing controller that owns this resource — reuse it rather than creating a sibling.
- An existing Action covering this or an adjacent flow.
- The repository and model involved, and any global scopes on that model.
- Existing Criteria that already express the filtering this endpoint needs.
- The Resource tier that fits the field breadth this endpoint returns.

Report what exists before proposing anything new.

## 2. Decide the layers

State explicitly:

- One flow or two? (Two ⇒ Orchestrator, one Action each. One ⇒ Controller → Action.)
- Which steps are Tasks, and why each one is reusable or large enough to extract.
- Which steps stay inline in the Action.
- Whether a wrapper DTO is needed (composite payload) or the Resource can serialize the model.
- Whether the endpoint writes more than one row. If it does, where the transaction opens, and what
  must happen after it commits.
- Which policy ability guards this, and whether it attaches on the route group or in the method.

## 3. Confirm

Present the plan as a file list with one line each — path, layer, responsibility. Wait for approval.

## 4. Implement

Follow `layered-architecture`, `http-boundary`, `repository-criteria` and, if the endpoint takes
filters, `filterable-list-endpoints`. Every new file starts with `declare(strict_types=1);`.

## 5. Verify

- Formatter and static analyser on the changed files only.
- Boot the framework against the new code — `route:list` plus one real call.
- Confirm the authorization denies the user it should deny, not just that it allows the one it should
  allow.
- Report exactly what was created, by path, and what you verified.
