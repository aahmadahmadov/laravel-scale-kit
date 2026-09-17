---
name: eloquent-model-conventions
description: Use when creating or editing an Eloquent model — member ordering, relations, scopes, accessors, casts, computed aliases, and where helper methods belong. Invoke when a model is getting long, when adding a relation or scope, when a query alias or computed flag needs declaring, or when reviewing a model for layout and conventions.
license: MIT
metadata:
  version: "0.1.0"
  domain: backend
  triggers: Eloquent model, model layout, relations, scopes, casts, accessor, mutator, property-read, model conventions, alias column
  role: specialist
  scope: implementation
  related-skills: layered-architecture, query-performance, shared-static-helpers
---

# Eloquent Model Conventions

A model is the one file every developer opens first. It must be scannable in five seconds: where the
attributes end and the behaviour starts, and what this table actually carries.

## Section layout

Every model groups its members into labelled sections. Markers are plain `//` comments at member
indentation, with a blank line after the opening marker and before the closing one.

```php
final class Schedule extends Model
{
    use HasFactory;
    use SoftDeletes;

    // Attributes start

    protected $table = 'schedules';

    /** @var array<int, string> */
    protected $fillable = ['class_id', 'subject_id', 'teacher_id', 'date'];

    /** @var array<int, string> */
    protected array $aliases = ['full_week_lesson_count', 'substitute_count'];

    /** @return array<string, string> */
    protected function casts(): array
    {
        return ['date' => 'date'];
    }

    // Attributes end

    protected static function booted(): void
    {
        static::addGlobalScope(new CurrentEducationYearScope());
    }

    // Relations start

    /** @return BelongsTo<Classm, $this> */
    public function class(): BelongsTo
    {
        return $this->belongsTo(Classm::class, 'class_id', 'id');
    }

    // Relations end

    // Scopes start

    /** @return Builder<$this> */
    public function scopeActive(Builder $query): Builder
    {
        return $query->whereNull('cancelled_at');
    }

    // Scopes end

    // Helpers start

    /** @return string */
    public function classSubjectCompositeKey(): string
    {
        return CompositeKeyGenerator::classSubject($this->class_id, $this->subject_id);
    }

    // Helpers end
}
```

**Order:** `use` statements → Attributes → `boot()`/`booted()` → Relations → Scopes → Helpers.

| Section | Holds |
|---|---|
| Attributes | class constants, every config property (`$table`, `$casts`, `$fillable`, `$hidden`, `$appends`, `$with`, `$aliases`), accessors/mutators, `casts()` |
| Relations | every method returning a relation type |
| Scopes | `scopeXxx()` methods |
| Helpers | business predicates, composite-key methods, static factories, `newFactory()`, `newEloquentBuilder()` |

- `boot()`/`booted()` sits **outside** every section — it is a framework hook, not a helper.
- **Omit a section that would be empty.** Never emit empty markers.
- Grouping is the only reordering allowed; preserve relative order inside a section.

## Declaring invented identifiers

Any identifier the application invents — a SQL alias, a computed flag key, a filter key — that is
read back somewhere else must be declared on the model that owns it, in `protected array $aliases`
next to `$fillable`, and documented with `@property-read` in the class docblock when it materialises
as an attribute.

```php
/**
 * @property-read int $full_week_lesson_count
 * @property-read bool $has_substitute
 */
```

- **Never a `const`, never an enum.** These are independent identifiers, and the model already
  carries the declaration+PHPDoc contract that real columns get.
- **Call sites use the plain string**, exactly like a real column:
  `$schedule->full_week_lesson_count`, `->selectRaw('COUNT(*) as substitute_count')`,
  `['staff as active_staff_count' => $constraint]`. No `Model::SOME_CONST` indirection.
- Relation-name strings stay plain strings — they are Laravel's API surface and a typo fails loudly.

## Traps that cost real debugging hours

**Global scopes make relations return `null`.** If `Classm` carries a current-year global scope, then
`$schedule->class` is `null` for any schedule outside that year — and `$schedule->class->name` is a
500 in production for old data. Never dereference such a relation bare; either drop the scope for
that read or null-check.

**`protected $with` multiplies cache payloads.** A model with `$with = ['user']` eager-loads that
relation even on `all(['id'])`, and if the repository caches the result the whole related row is
serialized into every cache entry. Check `$with` before blaming the query.

**Cached models freeze their casts.** A serialized model in cache carries the cast behaviour it had
when it was written. Changing `$casts` does not change what is already cached — the change is
invisible until the tag is flushed.

**Soft deletes void unique indexes.** A `UNIQUE (school_id, code)` index does not stop a second row
when the first has `deleted_at` set, because the pair is no longer unique in the eyes of the
constraint — and a `NULL` in any indexed column voids uniqueness entirely in MySQL/MariaDB. Enforce
such invariants in the Action as well as the schema.

## Enum over raw values

Stable finite value spaces (status, type, token name, direction) are PHP enums, never raw strings or
integers. Compare with predicate methods (`$status->isActive()`), not `=== Status::ACTIVE`, so the
value space can grow without a sweep through call sites.

When an enum is constructed from external data, use `tryFrom()` — an upstream system adding a value
you do not know must not throw a `ValueError` and turn a read endpoint into a 500.
