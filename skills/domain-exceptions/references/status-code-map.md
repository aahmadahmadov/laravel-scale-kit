# Status code map

Pick the status from what the client can *do* about it, not from what went wrong internally.

| Situation | Status | Notes |
|---|---|---|
| Requested resource does not exist, or is not visible to this caller | 404 | Prefer 404 over 403 when revealing existence is itself a leak |
| Caller is authenticated but not permitted | 403 | From the policy, via the framework's `AuthorizationException` |
| Caller is not authenticated / token expired | 401 | Never from a domain exception |
| Input shape is wrong | 422 | From the Form Request, automatically |
| Input shape is fine, business rule refuses | 400 or 422 | Pick one project-wide and never mix. 422 reads better for "valid syntax, invalid state" |
| The state changed under the caller (already enrolled, already graded, row was edited) | 409 | Conflicts must be distinguishable from plain rule failures so the client can offer a retry |
| Write attempted against a closed period (finalised year, locked journal) | 423 or 409 | 423 Locked if the project uses it consistently |
| Upstream integration returned 404 | 404 | Map, with **your** translation key |
| Upstream integration returned 5xx | same 5xx | Same status, your message. Never forward their body |
| Upstream timed out / connection refused | 504 | Distinguish from 500 so monitoring can separate "us" from "them" |
| Rate limit | 429 | Include `Retry-After` |

## Anti-patterns

- Returning 200 with `{"success": false}`. Clients stop checking statuses and start parsing bodies.
- Returning 500 for a business rule. It pages someone at 03:00 for a user typo.
- Returning the upstream provider's status *and* their message. You have just made their outage look
  like your bug, in their language.
