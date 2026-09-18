---
name: filterable-list-endpoints
description: Use when building or reviewing a list endpoint with request-driven filtering, sorting or pagination in Laravel — allowed filters, sort allowlists, per-page handling, and filter-options endpoints. Invoke when an endpoint accepts filter[...] or sort query parameters, when an action contains a filled() check around a filter, or when pagination behaviour needs deciding.
license: MIT
metadata:
  version: "0.2.0"
  domain: backend
  triggers: list endpoint, filter, sorting, pagination, per_page, query parameters, filter options, simplePaginate, allowed filters
  role: specialist
  scope: implementation
  related-skills: repository-criteria, http-boundary, query-performance
---

# Filterable List Endpoints

Request-driven filtering, sorting and pagination is **one mechanism**, implemented once in a shared
package and reused by every list endpoint. Hand-rolling it per endpoint is how a codebase ends up
with six different meanings for `?sort=`.

## The shape

```php
final class ListTeachersRequest extends FilterableListRequest
{
    /** @return array<int, AllowedFilter> */
    protected function allowedFilters(): array
    {
        return [
            AllowedFilter::exact('school_id'),
            AllowedFilter::exact('subject_id'),
            AllowedFilter::partial('full_name'),
            AllowedFilter::trashed(),
        ];
    }

    /** @return array<int, string> */
    protected function allowedSorts(): array
    {
        return ['last_name', 'created_at'];
    }
}
```

The base request validates the incoming `filter.*`, `sort`, `direction` and `per_page` input against
these declarations. Anything not declared is rejected, so a filter can never reach a column the
endpoint did not intend to expose.

## The rule that matters most

**An Action or Task never reads request input.** No `request()`, no `$request` parameter threaded
down from the controller, and above all no conditional push:

```php
// WRONG — the Action now cannot run outside an HTTP request
if (request()->filled('filter.school_id')) {
    $repository->pushCriteria(new FieldEqualsCriteria('school_id', request('filter.school_id')));
}

// RIGHT — one flat chain, always the same
$repository
    ->pushCriteria(new FilterFieldsCriteria())
    ->pushCriteria(new FilterTrashedStatusCriteria())
    ->pushCriteria(new RequestSortCriteria());
```

The **criteria** reads `request()->input('filter.<key>')` and returns the model untouched when the
value is blank or the wrong type. A conditional push in an Action is a bug to fix, not a style
choice: it is the seam through which request coupling spreads back into the domain.

## Enums for the finite value spaces

Trashed state and sort direction are enums (`TrashedStatusEnum`, `SortDirectionEnum`), not strings.
They are validated at the request boundary and consumed by the criteria; no string comparison of
`'asc'` anywhere.

## Pagination

- **`per_page` is opt-in.** Absent → return the full collection. Present → paginate. Never return
  both shapes from the same endpoint depending on some other flag; the client cannot branch on a
  shape it cannot predict.
- On very large tables use `simplePaginate()`. A `COUNT(*)` over a 100M-row table to render "page 3
  of 41,318" costs seconds and nobody reads the number. See `query-performance`.
- Cap `per_page`. An uncapped one is a denial-of-service parameter.

## Filter-options endpoints

A list endpoint with filters almost always needs a sibling that tells the client **what values are
selectable** — `GET /teachers/filter-options`. Rules:

- The options endpoint mirrors the list endpoint's scoping exactly. If the list is school-scoped,
  the options are too, or the UI offers filters that return nothing.
- It returns `{label, value}` pairs, built from the same enums and the same criteria.
- It is a separate Action, not a flag on the list Action.
- Role-variant endpoints: when the list changes shape per role, the options endpoint must vary with
  the same rule, in the same place.

## New filter shapes go into the package

When an endpoint needs a filter the package does not cover — LIKE search, a concatenated column,
filtering through a relation — write it **in the shared package** as a generic class parameterised by
relation/columns/request key. Not as a one-off in `app/Criteria/`. Document it in the package README
so the next developer finds it instead of writing a seventh variant.

## Checklist

- [ ] Form Request extends the shared filterable base
- [ ] Every filter and sort field is declared in an allowlist
- [ ] Action pushes criteria unconditionally, one flat chain
- [ ] No `request()` below the controller
- [ ] `per_page` opt-in and capped
- [ ] Very large table → `simplePaginate`
- [ ] Filter-options endpoint scoped identically to the list
