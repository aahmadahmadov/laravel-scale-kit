---
name: authorization-policies
description: Use when adding or reviewing access control in a Laravel application — policies, the can middleware, route-group authorization, controller authorize calls, and model-level access predicates. Invoke when an endpoint needs permission checks, when a 403 is wrong or missing, when scattered if-checks guard data, or when deciding where an ownership check belongs.
license: MIT
metadata:
  version: "0.1.0"
  domain: security
  triggers: authorization, policy, can middleware, authorize, 403, permission, access control, ownership check, gate
  role: specialist
  scope: implementation
  related-skills: http-boundary, layered-architecture, domain-exceptions
---

# Authorization & Policies

Authorization lives at the HTTP boundary, expressed as policies, and nowhere else. An `if` that
guards data inside an Action is an access rule that no audit will ever find.

## Where the check is attached

| Scope | Mechanism |
|---|---|
| One ability guards a **group** of endpoints on a route-bound model | Route middleware: `Route::prefix('{pupil:utis_id}')->middleware(['can:view,pupil'])` |
| One ability applies to exactly **one** endpoint (`delete`, `approve`) | `$this->authorize('delete', $model)` inside that controller method |
| No role may ever perform it (`create` on a read-only resource) | Policy method returns a bare `Response::deny()` |

The route-group form is the default; it removes the possibility of forgetting the check on the
fourteenth endpoint added to the group.

### The silent-403 trap

`can:view,pupil` resolves `pupil` **by the route parameter name**. If the route binds `{student}`
and the middleware says `pupil`, Laravel cannot resolve the model, passes `null`/the string, and the
policy denies **everyone** — with no error, no log, and a perfectly plausible 403. Whenever you add
`can:` middleware, confirm the parameter name character-for-character against the route definition,
then hit the endpoint once as a user who *should* pass.

### Route-scoped ≠ body-scoped

`can:update,class` proves the caller may edit **that** class. It proves nothing about the ids inside
the request body. If the payload carries `subject_ids`, `pupil_ids` or a parent id, re-resolve those
against the authorized scope inside the Action before writing. This is the most common real
authorization hole in an otherwise policy-driven codebase.

## Policies stay thin

A policy method is a top-to-bottom list of allow-conditions ending in a single deny.

```php
final class PupilPolicy
{
    /**
     * @param User $user
     * @param Pupil $pupil
     *
     * @return Response
     */
    public function view(User $user, Pupil $pupil): Response
    {
        if ($user->teachesPupil($pupil)) {
            return Response::allow();
        }

        if ($user->directsPupilSchool($pupil)) {
            return Response::allow();
        }

        return Response::deny(__('exceptions.pupil.access_denied'));
    }
}
```

- **No queries inline.** The real checks are predicates on the user model, bundled through access
  traits (`app/Traits/Model/`), e.g. `teachesPupil()`, `directsSchool()`, `regionCoversSchool()`.
  The policy only composes booleans.
- Deny messages are **translation keys**.
- Prefer passing an already-resolved parent (the school, the class) into the predicate so the check
  costs zero extra queries on a hot path.

## Access predicates on the model

```php
/**
 * @param Pupil $pupil
 *
 * @return bool
 */
public function teachesPupil(Pupil $pupil): bool
{
    return $this->taughtClassIds()->contains($pupil->class_id);
}
```

Two traps worth a guard clause:

- **Null-safe negation.** `belongsToDifferentSchool()` returning `true` when one side is `null` will
  deny a legitimate user or, worse, allow a stranger depending on which way the negation runs. Decide
  explicitly what `null` means and write it down.
- **Scoped relations.** If the membership relation carries a global scope (current year, not
  deleted), an authorization check running outside that window silently fails. For auth checks,
  query without the convenience scope.

## Never authorize in

- Actions, Tasks, Repositories — they must be callable from a console command or a queued job where
  there is no authenticated user at all.
- Form Requests — `authorize()` returns `true`; keeping a second mechanism alive means two places to
  look when a 403 is wrong.
- Resources — hiding a field in the serializer is not access control, it is cosmetics. If the caller
  must not see it, they must not receive it.

## Checklist

- [ ] Policy registered in the auth service provider
- [ ] `can:` middleware parameter name matches the route binding exactly
- [ ] Verified once as an allowed user, once as a denied user
- [ ] Ids inside the request body re-resolved against the authorized scope
- [ ] Deny messages are translation keys
- [ ] No permission `if` outside a policy
