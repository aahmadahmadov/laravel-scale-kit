# Criteria catalogue

The set of generic criteria a medium-to-large project ends up needing. Implement these once, in a
shared package, parameterised by column/relation — never per model.

## Field criteria

| Class | Signature | Purpose |
|---|---|---|
| `FieldEqualsCriteria` | `(string $field, mixed $value)` | `where($field, $value)` |
| `FieldInCriteria` | `(string $field, array $values)` | `whereIn` |
| `FieldNotInCriteria` | `(string $field, array $values)` | `whereNotIn` |
| `FieldNullCriteria` | `(string $field, bool $null = true)` | `whereNull` / `whereNotNull` |
| `FieldGreaterCriteria` | `(string $field, mixed $value, bool $orEqual = false)` | numeric/date lower bound |
| `FieldLessCriteria` | `(string $field, mixed $value, bool $orEqual = false)` | upper bound |
| `DateBeforeCriteria` / `DateAfterCriteria` | `(string $field, string $date)` | date comparison with an explicit format |

**Trap:** passing an array into a criteria that builds `where()` instead of `whereIn()` does not
error — the driver casts the array and you silently filter on its first element. Type the parameter.

## Relation criteria

| Class | Purpose |
|---|---|
| `WithCriteria` | eager load, `(array $relations)` |
| `WithCountCriteria` | `withCount`, accepts `['relation as alias' => closure]` pairs |
| `MultipleFieldsWhereHasCriteria` | one `whereHas` with several conditions on the relation |
| `GroupByCriteria` | `(array $columns)` |
| `WithTrashedCriteria` / `FilterTrashedStatusCriteria` | soft-delete state, driven by an enum |
| `WithoutGlobalScopeCriteria` | removes a named global scope for this query |

## Request-driven criteria

These read `request()` themselves and no-op when their key is absent. They are what lets an Action
push filters unconditionally. See the `filterable-list-endpoints` skill.

| Class | Reads |
|---|---|
| `FilterFieldCriteria` | `filter.<key>` for one declared field |
| `FilterFieldsCriteria` | every allowed filter declared on the Form Request |
| `RequestSortCriteria` | `sort` + `direction`, validated against an allowlist |

## Naming

`<Subject><Condition>Criteria`. The name must state the business rule, not the SQL:
`ClassCurrentEducationYearCriteria`, not `ClassWhereYearIdCriteria`.

## Testing

A criteria is the easiest thing in this architecture to unit-test: build a query, apply, assert on
`toSql()` and `getBindings()`. If a criteria is hard to test, it is doing two things.
