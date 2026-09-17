---
name: domain-exceptions
description: Use when throwing, catching, designing or translating errors in a Laravel application — business rule failures, HTTP status mapping, exception class layout, and the global handler. Invoke when creating an exception class, when a try/catch is being added to an action or task, when mapping a third-party HTTP error onto a domain error, or when deciding which error message the API should return.
license: MIT
metadata:
  version: "0.1.0"
  domain: backend
  triggers: exception, error handling, try catch, throw, business rule, status code, error message, exception handler, rethrow
  role: specialist
  scope: implementation
  related-skills: layered-architecture, http-integrations, localization-enums
---

# Domain Exceptions

Every business-rule failure in the system is one exception class per **flow domain**, carrying a
translation key and an HTTP status. Nothing below the global handler formats an error response.

## The base class

```php
class BusinessRuleException extends Exception implements ShouldntReport
{
    /**
     * @param string $message translation key, never a translated string
     * @param int $statusCode
     * @param Throwable|null $previous
     */
    public function __construct(
        string $message,
        private readonly int $statusCode = Response::HTTP_BAD_REQUEST,
        ?Throwable $previous = null,
    ) {
        parent::__construct(__($message), $this->statusCode, $previous);
    }

    /** @return int */
    public function statusCode(): int
    {
        return $this->statusCode;
    }
}
```

`ShouldntReport` keeps expected business failures out of the logs. A user hitting a rule they were
always going to hit is not an incident.

## One class per flow domain

`app/Exceptions/<Domain>/`, every class `final`, every class extending `BusinessRuleException`.

- A **flow domain** is one endpoint or a closely related group of endpoints:
  `PupilScheduleException`, `PupilAbsenceException`, `AuthException`.
- The constructor's **default** message is the generic failure key for that domain
  (`exceptions.pupil.schedule_failed`). Deeper layers throw the same class with a specific key
  (`exceptions.pupil.not_enrolled`).
- Callers always pass the **key**. `__()` is called once, inside the exception.

```php
final class PupilScheduleException extends BusinessRuleException
{
    public function __construct(
        string $message = 'exceptions.pupil.schedule_failed',
        int $statusCode = Response::HTTP_BAD_REQUEST,
        ?Throwable $previous = null,
    ) {
        parent::__construct($message, $statusCode, $previous);
    }
}
```

## The global handler

One place renders the envelope:

```php
if ($e instanceof BusinessRuleException) {
    return response()->json(['message' => $e->getMessage()], $e->statusCode());
}
```

Controllers, actions and tasks **never** catch their own domain exceptions. Every per-controller
catch is another envelope shape the frontend has to special-case.

Two traps worth checking in any existing handler:

1. **Policy denials must survive it.** A catch-all branch that turns every `Throwable` into a generic
   500 will swallow `AuthorizationException` and hide every 403. Order the branches so framework
   exceptions keep their own rendering.
2. **Browser-facing routes need an HTML path.** A handler that only ever returns JSON will emit raw
   JSON into a redirect-based web flow. Branch on `$request->expectsJson()`.

## Shared managers throw their own generic exception

A component used by several unrelated flows — a shared HTTP manager, a shared importer — must throw
**its own** generic exception (`MidApiException`), never the exception class of whichever flow was
built first. Each caller then translates:

```php
try {
    $items = $this->midApiManager->fetchMovements($pupil);
} catch (MidApiException $e) {
    if ($e->statusCode() === Response::HTTP_NOT_FOUND) {
        throw new PupilMovementException('exceptions.movements.not_found', Response::HTTP_NOT_FOUND, $e);
    }

    throw new PupilMovementException('exceptions.movements.failed', $e->statusCode(), $e);
}
```

Explicit `if` + fallthrough `throw`. Never a ternary inside the constructor call — the two branches
have different business meanings and a reader must see both.

## When a try/catch is allowed below the controller

Exactly two cases:

1. **The process must continue** after a non-fatal failure — a batch where one row failing must not
   abort the other 999. Log it, continue.
2. **Translating a shared component's generic exception** into this flow's own exception, as above.

In both cases the caught exception is re-thrown, translated, or logged. Never silently swallowed.
An empty `catch` block is a bug report you will receive in six months with no stack trace attached.

## Messages

- Never a hardcoded user-facing string. Every message is a translation key that exists in **all**
  configured locales.
- Never leak an upstream provider's message to your client. Map the status, use your own key.
- `Log::` calls are the carve-out: log lines stay in English and are not translated.

## Checklist

- [ ] Exception class is `final`, in `app/Exceptions/<Domain>/`, extends `BusinessRuleException`
- [ ] Constructor signature is `(string $message = '<generic key>', int $statusCode, ?Throwable $previous)`
- [ ] Every throw site passes a key that exists in every lang file
- [ ] No catch of your own domain exception anywhere in controllers/actions/tasks
- [ ] Shared managers throw their own generic exception, callers translate it
- [ ] Status codes are meaningful: 404 not found, 409 conflict, 422 unprocessable, 400 generic rule
