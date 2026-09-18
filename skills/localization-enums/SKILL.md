---
name: localization-enums
description: Use when adding user-facing text, translation keys, or enums to a Laravel application — lang files, message keys, structured enums serialized to the frontend, and the rule that no string is hardcoded. Invoke when writing an error message, adding a lang key, creating an enum, or exposing a status value in an API response.
license: MIT
metadata:
  version: "0.2.0"
  domain: backend
  triggers: translation, localization, lang file, i18n, message key, enum, status enum, label, JsonSerializable enum
  role: specialist
  scope: implementation
  related-skills: domain-exceptions, eloquent-model-conventions, package-extraction
---

# Localization & Enums

## No hardcoded user-facing text

Every string a human may read is a translation key. Including technical-sounding ones — "Invalid
token", "Import failed" — because the day the product adds a locale, a grep for quotes is not a
migration plan.

- Keys live in `lang/<locale>/`, and **every key exists in every configured locale**. A missing key
  renders as the key itself in production.
- Exception messages: `exceptions.<domain>.<key>`.
- Callers pass the **key**; `__()` is called once, at the boundary that owns the message (usually the
  exception constructor or the Resource).
- **`Log::` calls are the carve-out.** Log lines stay in English, untranslated. They are read by
  engineers, and a translated log is unsearchable.

## Set the primary locale explicitly

`APP_LOCALE` is the product's language, not English-by-default. Set it in `.env`, keep an English
fallback file complete, and make a missing-key check part of CI if the project ships more than two
locales.

## Structured enums

Frontend-facing enums serialize as an object, not a bare value, so the client never maintains its own
label map:

```php
enum ScheduleStatusEnum: int implements StructuredEnum
{
    use HasStructuredEnumSerialization;

    case DRAFT = 1;
    case PUBLISHED = 2;
    case CANCELLED = 3;
}
```

```json
{ "name": "PUBLISHED", "value": 2, "label": "Dərc olunub" }
```

- The contract (`StructuredEnum`) and the trait (`HasStructuredEnumSerialization`) belong in a shared
  package, not in `app/`. See `package-extraction`.
- **`label()` does a dynamic translation lookup**, built from the enum's own name — never a `match`
  block. A `match` is one more place to edit for every new case, and it will be forgotten.
- Add predicate methods (`isPublished()`) and use those at call sites instead of `===`.

## Constructing an enum from external data

Always `tryFrom()`, never `from()`, for any value that arrives from outside the application — an
upstream sync, a webhook, a legacy column. An unknown value must become `null` you handle, not a
`ValueError` that turns a read endpoint into a 500. This failure mode is invisible in testing,
because the unknown value only appears once the third party adds it.

Decide and document what `null` means for each such enum: unknown-but-acceptable, or reject.

## Reuse enums across domains

One `OrgTypeEnum` for the whole codebase, not one per module that happens to need it. When two
domains genuinely mean different things by the same word, the names are what should differ, not the
value space.

## Where enum values live

Stable finite value spaces are **always** enums: status, type, direction, token name, role. Never raw
strings or magic integers in a column, a config, or a comparison.

The exception is an **invented identifier** — a SQL alias, a computed flag key — which is declared on
the model in `$aliases` and used as a plain string. See `eloquent-model-conventions`. Turning those
into enums adds indirection to something that is not a value space at all.

## Checklist

- [ ] No literal user-facing string in PHP
- [ ] Key exists in every locale file
- [ ] Enum implements the structured contract if the frontend consumes it
- [ ] `label()` is a dynamic lookup, not a `match`
- [ ] External values parsed with `tryFrom()`
- [ ] Predicate methods used instead of `===` comparisons
