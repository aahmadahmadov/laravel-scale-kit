# Which layer does this belong to?

## Start here

```
Does the endpoint combine two or more independent flows?
├─ yes → Orchestrator, one Action per flow
└─ no  → one Action

Inside the Action, is the new piece …
├─ a decision about the flow (what happens next, which error, which branch)
│     → keep it in the Action
├─ a self-contained operation that a second Action could plausibly reuse
│     → Task
├─ a single query / single update / single lookup
│     → inline in the Action
└─ a query shape reused in 2+ places
      → Criteria class
```

## "Two flows" vs "one flow with steps"

The test is not size, it is **independent reason to change**.

- *One flow:* fetch a pupil's schedule, project the lesson hours onto it, attach attendance, return
  it. Every step exists only to produce that one response. One Action, several Tasks.
- *Two flows:* return a pupil's schedule **and** their unread notification count in one endpoint.
  Notifications change for reasons that have nothing to do with schedules. Orchestrator, two Actions.

If deleting feature A would leave step B meaningless, they are one flow.

## When a Task is justified

A Task must earn its file. It is justified when **all** of these hold:

1. It performs real work — a computation, a projection, a multi-step persist, a normalisation.
2. It is callable from more than one Action, or it is large enough that inlining it would bury the
   Action's flow.
3. It needs no knowledge of *why* it is being called.

It is **not** justified for: a bare `update()`, a single `find()`, a `->pluck()`, a one-line mapping,
or "so the Action looks tidy". A private method is not the answer either — see below.

## Private methods in an Action

A private method inside an Action is a Task that has not been extracted yet. If it is genuinely
flow-specific and used once, inline it. If it is used more than once, or it is a self-contained
operation, extract a Task. Do not keep a growing tail of single-use private helpers: they are
untestable in isolation and invisible to the rest of the codebase.

## Where authorization goes

Nowhere in this tree. Authorization is an HTTP-boundary concern: route middleware or the controller,
via a policy. An Action that checks permissions cannot be reused by a console command or a job.

## Where validation goes

Input shape → Form Request. Business rules ("this pupil is not enrolled", "this slot is taken") →
inside the Action or Task, thrown as a domain exception, never as a `ValidationException`.
