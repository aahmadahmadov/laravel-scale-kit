---
name: shared-static-helpers
description: Use when an inline closure or string-built key appears in application code — in-memory sorting, query constraint closures passed to with/withCount/whereHas, and composite keys used to group or join collections. Invoke when writing a sortBy closure, a reusable eager-load constraint, or any interpolated key used to match two collections in PHP.
license: MIT
metadata:
  version: "0.1.0"
  domain: backend
  triggers: sortBy, comparator, sorting, closure, withCount constraint, query constraint, composite key, grouping key, collection join
  role: specialist
  scope: implementation
  related-skills: layered-architecture, eloquent-model-conventions, query-performance
---

# Shared Static Helpers

Three kinds of small logic spread through a codebase as copy-pasted closures and interpolated
strings, and each one drifts silently: sort orders, query constraints, and composite keys. Each gets
one home, as `final` classes of pure static factories. **No shared interface, no contract** — plain
static methods returning bare callables match the framework's own signatures directly.

## 1. Comparators — `app/Support/Comparators/`

In-memory collection sorting goes through a Comparator, never an inline closure.

```php
final class ClassComparator
{
    /** @return callable */
    public static function byGradeAndIndex(): callable
    {
        return static fn (Classm $class): array => [$class->grade, $class->index, $class->id];
    }
}
```

```php
$classes->sortBy(ClassComparator::byGradeAndIndex());
```

- Applies to **fixed, business-meaningful orderings** — "classes sort by grade then index", "teachers
  by last name". Request-driven sorting (`?sort=name`) is a separate mechanism at the query layer and
  is unaffected by this rule.
- Naming: `<Entity>Comparator::by<Criteria>()`.
- One class per entity. Add a method to the existing class before creating a new one.
- **Always include a deterministic tiebreaker** (usually `id`). Without it, two rows with equal keys
  swap order between requests and the UI flickers, or a paginated list repeats a row.
- Locale collation bites here: in some alphabets `c` and `ç` collate together, so a sort that looks
  wrong may be correct. Decide whether you want DB collation or PHP comparison, and be consistent.

## 2. Query constraints — `app/Support/QueryConstraints/`

The closures passed to `with()`, `withCount()`, `withExists()`, `whereHas()`.

```php
final class StaffConstraint
{
    /** @return array<string, callable> */
    public static function activeCount(): array
    {
        return ['schoolStaffs as active_school_staff' => static fn (Builder $q) => $q->whereNull('left_at')];
    }
}
```

- Aggregate helpers return the `['<relation> as <alias>' => callable]` **pair**, so the alias is
  produced in exactly one place — the alias string and the closure can never drift apart.
- The alias itself is declared on the model in `$aliases` with a `@property-read` line, and read back
  as a plain string. See `eloquent-model-conventions`.
- Same shape as Comparators: `final`, static, returns a callable, no interface.

## 3. Composite keys — `app/Support/CompositeKeyGenerator`

Composite string keys used to group or join collections in memory are formatted in **exactly one
place**. Never interpolated at a call site.

```php
final class CompositeKeyGenerator
{
    /** @return string */
    public static function classSubject(int $classId, int $subjectId): string
    {
        return $classId.'-'.$subjectId;
    }
}
```

Two call patterns:

- **Key derived purely from one model's own columns**, used more than once → expose a method on that
  model that delegates to the generator, named after the columns plus a `CompositeKey` suffix:
  `ScheduleRecord::schedulePupilCompositeKey()`. It lives in the model's Helpers section.
- **Key built from several models, from a relation, or from raw scalars** → call the generator
  directly. Moving such a key onto one model hides the cross-model contract that makes both sides
  match, and a relation dereference hidden inside a model method also hides its eager-load
  requirement.

**Do not create a trait for this.** Each model's key uses different columns and a different generator
method, so a trait would share no implementation, and a generic `compositeKey('name')` trades
compile-time safety for a stringly-typed lookup. If several models ever need the identical key shape,
extract then.

## Migration policy

Non-retroactive. When you touch an inline closure for another reason, migrate it at the same time.
There is no mandate to sweep the whole codebase — a sweep produces a huge unreviewable diff and no
behaviour change. If you do run a mechanical sweep, verify it with a multiset diff of before/after
results, not by reading the diff.
