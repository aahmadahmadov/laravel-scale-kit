# Starting a new project on this architecture

The rest of this kit is written for a codebase that already has shape. On an empty one, the risk is
the opposite of drift: building all five layers and a package on day one, for an application with
four endpoints, and calling the ceremony architecture.

**The layering is what you grow into, in this order.** Nothing here is skipped later; it is deferred
until something asks for it.

## Day one — what to install

| Concern | Reference implementation | Required? |
|---|---|---|
| Repository base + criteria | `prettus/l5-repository` | No — any base class works; see `repository-criteria` |
| DTOs | `spatie/laravel-data` | No — a plain `readonly` class is fine until it is not |
| Filter/sort/pagination | `spatie/laravel-query-builder`, or your own base request | Pick one **before** the second list endpoint |

Choose the engine deliberately: this kit's database skills assume **MySQL 8 or MariaDB 10.6+**. On
PostgreSQL the architecture rules hold and the database skills do not.

## Day one — directories

Create only these, and only when the first class needs one:

```
app/Actions/<Domain>/            first endpoint with any logic
app/Http/Requests/<Domain>/      first endpoint that takes input
app/Http/Resources/              first endpoint that returns a model
app/Exceptions/<Domain>/         first business-rule failure
app/Policies/                    first endpoint that is not public
app/Repositories/                first query you want to reuse
app/Criteria/Shared/             first generic criteria
app/Criteria/<Domain>/           first criteria that names a business rule
```

Not yet: `app/Orchestrators/` (needs two flows in one endpoint), `app/Tasks/` (needs a second caller),
`packages/` (needs a second consumer — see `package-extraction`).

An empty directory committed "for later" tells the next developer the layer is expected. Do not
create one.

## The first endpoint

Build it as Controller → Action → Eloquent, with a Form Request and a Resource. That is the whole
architecture at minimum size, and it is correct — the remaining layers are extractions from it:

| You add | When |
|---|---|
| A Repository + Criteria | The same query shape appears in a second place |
| A Task | A step inside an Action is called by a second Action |
| An Orchestrator | One endpoint genuinely serves two independent flows |
| `packages/` | A second project or bounded context needs the generic code |
| Caching | A real read is measurably slow — never before, see `repository-caching` |

Extracting later is cheap because each rule is about a boundary, not a folder. Building the folders
first is what produces four-file endpoints that do one `where`.

## What to hold from the first file, because retrofitting it is expensive

These are not deferrable — they cost nothing now and a sweep later:

- `declare(strict_types=1);` in every file.
- No user-facing string in PHP. Translation keys from the first message, in every configured locale.
- No `request()` or `auth()` below the controller. This one decision is what lets every Action be
  called from a console command later.
- Business-rule failures throw a domain exception, rendered in one place by the global handler.
- Authorization in a policy, attached at the boundary — even when there is one role today.
- Generic criteria name no model, so `app/Criteria/Shared/` stays promotable.
- Stable value spaces are enums, parsed from external data with `tryFrom()`.
- `Model::preventLazyLoading()` outside production, from the first model.
- A **test connection** that is not the development database, before the first test.

## Write the conventions file on day one

Run `/adopt-conventions new Laravel 12 API, own MySQL database`. Delete every section describing
something the project does not have — large tables, a shared database, local packages, a legacy
service layer. A conventions file that describes an imaginary codebase teaches agents that the file
is decorative, and that is harder to undo than starting without one.

Add each section back the day the thing it describes exists.
