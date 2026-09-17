# Anti-patterns

Each entry is a real failure mode this architecture exists to prevent. When reviewing code, scan for
these by name.

## 1. The pass-through class

```php
final class GetPupilTask
{
    public function handle(int $id): Pupil
    {
        return $this->repository->find($id);   // and nothing else
    }
}
```

One call in, same value out. Delete it and call the repository from the Action. A class earns its
file with branching, composition, or real work.

## 2. Action calling Action

```php
$schedule = $this->getScheduleAction->handle($class);   // inside another Action
```

Now the two flows share a lifetime. Changing the schedule flow's return shape silently breaks a
feature nobody was looking at. Use an Orchestrator, or move the shared piece down into a Task both
Actions call.

## 3. Task calling Task

The Task layer stops being flat. Depth grows one call at a time until nobody can answer "what runs
when I call this?" without a debugger. Compose Tasks in the Action.

## 4. Request input inside an Action

```php
if (request()->filled('filter.name')) {                 // inside an Action
    $this->repository->pushCriteria(new NameFilterCriteria());
}
```

The Action is now unusable from a command, a job or a test without faking a request. Push the
criteria unconditionally and let the criteria read the request and no-op when the key is absent.

## 5. Authorization inside an Action

```php
if ($user->school_id !== $class->school_id) {
    throw new AccessDeniedException();
}
```

Scattered checks drift apart. Centralise in a policy, attach it on the route group or with
`$this->authorize()` in the controller. See the `authorization-policies` skill.

## 6. Catching your own domain exception

```php
try {
    $this->action->handle($class);
} catch (ClassException $e) {
    return response()->json(['message' => $e->getMessage()], 400);
}
```

That is the global handler's job, and doing it per-controller guarantees inconsistent envelopes.
The only legitimate catches are: continue-after-non-fatal-failure, and translating a shared
manager's generic exception into this flow's own exception.

## 7. The orchestrator with one action

An Orchestrator that calls a single Action is a rename with extra indirection. Delete it.

## 8. Repository with business methods

```php
public function findActiveByschool(int $schoolId): Collection
```

Every such method is a query shape frozen into the wrong layer, and it will grow parameters forever.
Repositories declare `model()`. Query shapes are Criteria.

## 9. The god Action

An Action that handles list, create, update and delete. Four flows, four Actions. The controller
method names tell you where the split is.

## 10. Eloquent leaking upward

A Resource or a controller calling `$model->load(...)` because a relation was missing. Eager-load in
the Action or Task. A missing relation must fail loudly in development, not be patched at the edge.
