---
name: transactions-and-consistency
description: Use when a flow writes more than one row, dispatches a job, flushes a cache or calls an external service around a write in a Laravel application — deciding where the transaction boundary goes, what may not happen inside it, and how retries stay safe. Invoke when adding DB::transaction, when a queued job cannot find a model that exists, when duplicate rows appear under load, when a deadlock is reported, or when a command must be safe to re-run.
license: MIT
metadata:
  version: "0.2.0"
  domain: backend
  triggers: transaction, DB::transaction, rollback, deadlock, race condition, idempotent, afterCommit, dispatch job, duplicate rows, lockForUpdate, upsert, retry
  role: specialist
  scope: implementation
  related-skills: layered-architecture, repository-caching, production-data-safety
---

# Transactions & Consistency

The transaction boundary is a **flow** decision, so it belongs to the layer that owns the flow: the
Action. Everything in this skill follows from putting it there and keeping it small.

## The boundary is the Action

```php
public function handle(Classm $class, StoreSubjectsDataObject $data): void
{
    DB::transaction(function () use ($class, $data): void {
        $this->replaceSubjects->handle($class, $data->subjectIds);
        $this->recalculateHours->handle($class);
    });

    $this->scheduleRepository->flushCache();
    ClassSubjectsChangedJob::dispatch($class->id);
}
```

- **A Task never opens a transaction.** It does not know whether it is one step of five.
- **An Orchestrator never opens one either.** Two independent flows that must commit together are
  not two flows — they are one Action.
- One `DB::transaction()` per flow, at most. A nested call is **not** a transaction: Laravel opens a
  savepoint, and the inner block commits nothing of its own — everything still hangs on the outer
  commit. Two consequences. Code that assumes "the inner part is safely committed by now" is wrong.
  And if anything between the inner throw and the outer closure **catches** the exception, the inner
  work rolls back to the savepoint while the outer work commits, leaving exactly the partial state the
  transaction was supposed to prevent.

## Nothing that is not a database write goes inside

Inside a transaction, rows are locked and the undo log grows for as long as it is open. A third-party
call inside one holds those locks for the length of *their* timeout, which you do not control.

Keep out of the transaction: HTTP calls, queue dispatches, cache reads and writes, file and storage
writes, mail, and anything that sleeps or retries.

**Dispatch after commit.** A job dispatched inside a transaction is visible to a worker before the
transaction commits, and the worker fails to find a row that "obviously exists". The failure is load
dependent, so it never reproduces locally. Dispatch outside the closure as above, or declare the
intent on the job — `->afterCommit()` on the dispatch, `public bool $afterCommit = true;` on the
class, or `after_commit => true` on the queue connection so it is the default.

**Flush the cache after commit too.** A flush inside the transaction lets a concurrent request
repopulate the cache from pre-commit state, and the stale entry then outlives the write that was
supposed to clear it. See `repository-caching`.

## Let domain exceptions roll back

A domain exception thrown inside the closure propagates, the transaction rolls back, and the global
handler renders it. That is the designed path — and it is another reason nothing below the controller
catches its own exception. A `catch` inside the closure that logs and continues **commits the partial
write**.

The one legitimate catch is the batch case: one row of a thousand failing must not abort the rest.
Then each row gets its own transaction, not one transaction around the loop.

## Races that a transaction does not fix

A transaction gives you atomicity, not mutual exclusion. These need something more:

- **`firstOrCreate` / `updateOrCreate` are not atomic.** Two concurrent requests both miss, both
  insert. The fix is a real `UNIQUE` index that makes the second insert fail — and remember a
  nullable column or a soft-delete column in that index voids it. See `migrations-schema`.
- **Read-modify-write on a counter loses updates.** Use an atomic `increment()`, or
  `lockForUpdate()` on the row you are about to change, inside the transaction.
- **Lock in a consistent order.** Two flows that lock parent-then-child and child-then-parent will
  deadlock under load and nowhere else. Pick an order per aggregate and write it down.
- **Deadlocks are normal, not exceptional.** InnoDB kills one transaction and returns an error.
  Retry the whole transaction a bounded number of times; never retry a partial one.

## Idempotency for commands and jobs

Anything that runs unattended runs twice eventually — a retry, a redeploy, an operator.

- State, in the class docblock, what a second run does. If the answer is "double-writes", it is not
  finished.
- Prefer an `upsert()` on a unique key over select-then-insert.
- A job's retry is a re-run of the **whole** handler. A handler that writes, then calls an API, then
  writes again will repeat the first write on every retry. Split it, or make each step idempotent.
- Overlap protection (`WithoutOverlapping`) is not re-run protection. Decide which one you need; they
  solve different problems.

## Long transactions are an operational cost

On InnoDB, an open transaction holds MVCC history for every reader. A transaction kept open across a
long loop inflates the undo log, slows every other query on the instance, and shows up as replication
lag rather than as a slow endpoint. Chunk the work into many short transactions instead of wrapping
the loop.

## Checklist

- [ ] The transaction is opened in the Action, once, and closed around database work only
- [ ] No HTTP call, cache write, file write or dispatch inside the closure
- [ ] Jobs dispatched after commit; cache flushed after commit
- [ ] No `catch` inside the closure that swallows and continues
- [ ] Uniqueness that matters is backed by an index, not by `firstOrCreate`
- [ ] Concurrent counters use an atomic update or a row lock
- [ ] Commands and jobs state what a second run does
