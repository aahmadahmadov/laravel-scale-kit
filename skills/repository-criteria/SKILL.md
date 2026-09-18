---
name: repository-criteria
description: Use when writing database access in a Laravel project that uses a repository layer with composable criteria — creating a repository, adding a query filter, deciding whether a query shape deserves its own class, or reviewing where an Eloquent call belongs. Invoke on repository, criteria, pushCriteria, query scoping, or when a repository is growing business methods.
license: MIT
metadata:
  version: "0.2.0"
  domain: backend
  triggers: repository, criteria, pushCriteria, prettus, query object, data access layer, where clause, query builder, DB facade
  role: specialist
  scope: implementation
  related-skills: layered-architecture, filterable-list-endpoints, repository-caching, query-performance
---

# Repository & Criteria

All database access goes through a repository; every query condition is a composable **Criteria**
object. The reference implementation here is `prettus/l5-repository`, but the rules are about the
pattern — swap the base class and they still hold.

## The repository is empty

```php
final class ScheduleRepository extends BaseRepository
{
    /** @return string */
    public function model(): string
    {
        return Schedule::class;
    }
}
```

That is the whole class. Specifically:

- **No business helper methods.** No `findActiveBySchool()`, no `createWithLessons()`. Every such
  method freezes one query shape into the wrong layer and grows parameters forever.
- **No Eloquent calls on the repository from outside.** `->where()`, `->with()`, `->whereHas()`
  called on the repository in an Action defeats the entire point — the condition is now invisible to
  every other caller and untestable on its own. Use criteria.
- Eager loading goes through a `WithCriteria`, never `->with([...])` on the repository.

## Criteria

```php
final class ActiveInEducationYearCriteria implements CriteriaInterface
{
    public function __construct(private readonly int $educationYearId) {}

    /**
     * @param mixed $model
     * @param RepositoryInterface $repository
     *
     * @return mixed
     */
    public function apply($model, RepositoryInterface $repository)
    {
        return $model
            ->where('education_year_id', $this->educationYearId)
            ->whereNull('cancelled_at');
    }
}
```

**When a Criteria class is justified:** a group of conditions reused in **2 or more** places. That
repetition is what earns a file.

**When it is not:** a single-column equality. Use the generic `FieldEqualsCriteria` /
`FieldInCriteria` from the shared toolkit. A one-off class wrapping one `where` is noise.

## Generic vs domain-specific

| Kind | Lives in | Example |
|---|---|---|
| Model-agnostic, parameterised by column/relation | a shared package (`packages/…-toolkit`) | `FieldEqualsCriteria`, `FilterFieldsCriteria`, `RequestSortCriteria`, `WithCriteria`, `GroupByCriteria` |
| Encodes a business rule about one domain | `app/Criteria/<Domain>/` | `ClassCurrentEducationYearCriteria`, `VisibleToParentCriteria` |

Before writing a criteria, **check the package first**. Never copy a package class into `app/`. See
the `package-extraction` skill for when a criteria has earned promotion into the package.

## Never use the `DB` facade

`DB::table()` / `DB::select()` bypass model events, observers, repository caching, soft-delete scopes
and global scopes. The result is a write nobody's observer sees and a read that returns deleted rows.
Use Eloquent relations — `whereHas('school', …)`, not `->from('schools')`. The only acceptable raw
usage is `DB::raw()` inside a select for an aggregate expression, and `DB::transaction()`.

## Criteria stacking in loops

Criteria accumulate on the repository instance. Pushing inside a loop silently ANDs iteration 1's
filters into iteration 2:

```php
foreach ($classes as $class) {
    $rows = $this->repository->withFreshCriteria(
        fn () => $this->repository
            ->pushCriteria(new FieldEqualsCriteria('class_id', $class->id))
            ->all()
    );
}
```

Two things to verify in whatever `withFreshCriteria` helper the project has:

1. It resets accumulated criteria **before and after** each iteration.
2. It re-applies **boot criteria** — the ones the repository registers in `boot()`. A naive reset
   drops those too, and a query that was always school-scoped silently goes global.

## Sharp edges of the base class, not of the pattern

Everything above is a rule about the pattern and holds whatever base class you use. **This section is
different: these are behaviours of `prettus/l5-repository`.** On another base class the equivalents
may differ or not exist — verify them rather than assuming, and correct this section for your project.

- **Write methods ignore criteria.** `deleteWhere()` and `update()` do not call `applyCriteria()`, so
  a criteria pushed to scope a write is silently ineffective — including one whose whole job was to
  remove a global scope. Prefer performing writes on a model instance obtained by a scoped read.
- **`pluck()` may not reset the criteria stack.** Some base-repository methods reset after running,
  some do not. Whichever ones do not, leak their conditions into the next call on the same instance
  within a request. Know which ones, and never "fix" it by calling `resetModel()` by hand.
- **`find()` on a repository with leaked criteria returns `null`** and looks exactly like a missing
  row. When a lookup mysteriously fails, dump the applied criteria first.

One edge is not library-specific: pivot writes (`sync`, `attach`) performed on a model fetched through
a caching repository will not invalidate the cache. See `repository-caching`.

## References

| Topic | File | Load when |
|---|---|---|
| The generic criteria a project ends up needing | `references/criteria-catalogue.md` | Before writing a new criteria, or when building the shared package |

## Checklist

- [ ] Repository declares only `model()`
- [ ] No `where`/`with`/`whereHas` called on the repository outside a Criteria
- [ ] New criteria checked against the shared package before writing
- [ ] Criteria reused in 2+ places, or it is a generic one from the package
- [ ] Loops wrapped in a fresh-criteria helper that preserves boot criteria
- [ ] No `DB::table()` anywhere
