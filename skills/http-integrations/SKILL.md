---
name: http-integrations
description: Use when integrating a third-party HTTP API into a Laravel application — adapters, managers, response normalization, error mapping, timeouts, retries, and per-integration logging. Invoke when adding an external API call, when an upstream error must become a domain error, or when an existing integration is being changed.
license: MIT
metadata:
  version: "0.2.0"
  domain: backend
  triggers: third-party API, HTTP client, adapter, integration, external service, upstream error, timeout, retry, webhook, API client
  role: specialist
  scope: implementation
  related-skills: domain-exceptions, layered-architecture, package-extraction
---

# HTTP Integrations

Every third-party API gets exactly two classes: an **Adapter** that knows the wire, and a **Manager**
that knows what the wire means to this product. Mixing them is the reason integrations become
unmaintainable.

```
Action → Manager (business meaning, error mapping) → Adapter (transport) → third party
```

## Adapter — transport only

```php
final class PaymentsAdapter extends Adapter
{
    /** @return string */
    protected function baseUrl(): string
    {
        return config('services.payments.url');
    }

    /** @return string */
    protected function logChannel(): string
    {
        return LogChannelEnum::PAYMENTS->value;
    }

    /** @return Response */
    public function fetchInvoice(string $id, string $bearerToken): Response
    {
        return $this->get("/invoices/{$id}", bearerToken: $bearerToken);
    }
}
```

- Endpoint methods are **thin one-liners**. An adapter holds no project business logic — it abstracts
  the third party and nothing else.
- The request pipeline, header builder and verb helpers live in an abstract base plus a trait. Never
  re-implement HTTP plumbing per adapter.
- The base logs transport failures to the integration's own channel and re-throws.
- Configure an explicit `timeout()`. A default-timeout integration will one day hold every worker in
  the pool.

## Manager — meaning

The Manager is where the project's rules live:

- **Normalise response shapes.** Real APIs return `{data: {...}}` on one endpoint and `{...}` on the
  next. The rest of the application must never see that inconsistency.
- **Map upstream errors to a domain exception with a consistent status.** 404 → 404 with *your*
  translation key. 5xx → same status, *your* message. Never forward the upstream body: their outage
  should not look like your bug, in their language.
- **Never return a success status when the upstream call failed.** This is the single most common
  integration bug, and it surfaces as corrupt data days later.
- Log the mapped decision to the integration's channel.

## Shared managers throw their own exception

A manager used by several unrelated flows throws its **own generic exception**
(`PaymentsApiException`), never the exception class of whichever flow was built first. Each calling
Action translates it into that flow's domain exception with an explicit `if` per status. See
`domain-exceptions`.

## Logging

One dedicated channel per integration in `config/logging.php`: daily driver,
`storage_path('logs/integrations/<name>/…')`, bounded retention. Both the adapter (transport) and the
manager (decision) log there. When the integration misbehaves, one directory holds the whole story.

Log requests and responses with **credentials and PII redacted**. A request-log table that captures
raw bodies will contain passwords and tokens; if the project has one, treat it as a secret store and
say so in the conventions file.

## Configuration and hosts

- Base URLs, keys and secrets come from config/env — never a literal in the adapter.
- If an integration's host is resolved through `/etc/hosts` rather than DNS, that fact must be in the
  deployment docs. Half a fleet missing the entry produces "cURL error 6" on some servers only, and
  it will be blamed on the code for a week.
- Commit no key. If one is committed, rotating it is the fix; deleting the file is not.

## Batch and streaming

- Provide a `pool()`-style batch executor on the adapter base for fan-out calls, and use it instead
  of a loop of sequential requests.
- Provide a streaming download path for large payloads so a 200MB export does not become a memory
  limit crash.

## Checklist

- [ ] Adapter methods are one-liners, no business logic
- [ ] Explicit timeout configured
- [ ] Manager normalises shapes and maps every error status
- [ ] Domain exception thrown with your own translation key
- [ ] Never returns success on upstream failure
- [ ] Dedicated log channel with retention, secrets redacted
- [ ] Credentials from config, nothing committed
