---
name: http-boundary
description: Use when writing or reviewing a Laravel controller, Form Request, API Resource, or DTO — the classes that sit between HTTP and the domain. Invoke when a controller reads raw request input, when validation is written inline, when deciding what a Resource should expose, when naming a data object, or when shaping an endpoint's JSON payload.
license: MIT
metadata:
  version: "0.1.0"
  domain: backend
  triggers: controller, form request, validation, api resource, JsonResource, DTO, data object, response shape, payload, whenLoaded
  role: specialist
  scope: implementation
  related-skills: layered-architecture, filterable-list-endpoints, localization-enums
---

# HTTP Boundary

Controllers, Form Requests, Resources and DTOs form the shell of the application. Everything in this
shell is about *transport*: parsing input, shaping output. None of it decides anything.

## Controller

A controller method is four lines or fewer: type-hint, call, return.

```php
final class PupilScheduleController extends Controller
{
    public function __construct(private readonly GetPupilScheduleAction $action) {}

    /**
     * @param GetPupilScheduleRequest $request
     * @param Pupil $pupil
     *
     * @return PupilScheduleResource
     */
    public function show(GetPupilScheduleRequest $request, Pupil $pupil): PupilScheduleResource
    {
        return PupilScheduleResource::make($this->action->handle($pupil, $request->user()));
    }
}
```

Rules:

- **Every method that accepts input type-hints a dedicated Form Request.** Never `Request $request`
  with inline `validate()`, never `$request->input('x')` read directly in the controller.
- One controller method calls **one** entry point. If it calls two Actions, it wants an Orchestrator.
- No `try`/`catch` around domain exceptions.
- No `if`. A branch in a controller is business logic in the wrong place.
- Resolve the acting user here and pass it down as a parameter; Actions must not call `auth()`.

## Form Request

One Request class per controller method, `final`, named after the action:
`ListSchoolProfilesRequest`, `StoreClassSubjectRequest`, `GetPupilScheduleRequest`. Live under
`app/Http/Requests/<Domain>/`.

- `authorize()` returns `true`. Access control belongs to policies, not requests — keeping both in
  play means two places to look when a 403 is wrong.
- Requests own **input shape** only: types, presence, ranges, enum membership.
- Business uniqueness (`this name already exists for this school`) is **not** a `Rule::unique`. It is
  a check in the Action throwing a domain exception, because it usually needs scoping the validator
  does not have and a message the domain owns.
- List endpoints extend the shared filterable-list base request instead of redeclaring filter rules.
  See `filterable-list-endpoints`.

## Payload shape is the Action's decision

When an endpoint returns a composite payload — several entities, plus computed totals — the shape is
decided in the Action, which returns **one wrapper DTO**, and serialized by **one** Resource.

Do not let the Resource assemble the payload out of three loose variables, and do not return an
array from the Action. A typed wrapper makes the contract visible and greppable.

```php
final class PupilScheduleDataObject extends Data
{
    /**
     * @param Collection<int, ScheduleDataObject> $lessons
     * @param int $totalHours
     * @param bool $isEditable
     */
    public function __construct(
        public readonly Collection $lessons,
        public readonly int $totalHours,
        public readonly bool $isEditable,
    ) {}
}
```

## DTO conventions

- Named `*DataObject`, never `*Dto`.
- Construct with `new XDataObject(...)`, not `XDataObject::from($array)`. `from()` resolves types at
  runtime, swallows shape mistakes, and costs reflection on every call. An explicit constructor call
  fails at compile/static-analysis time when the shape drifts.
- Add **named constructors** for the ways a DTO is really built: `fromModel(Pupil $pupil)`,
  `empty()`. They document the valid entry points and keep mapping out of the Action.
- A DTO carries **computed** values. Raw model fields are passed by holding a reference to the model
  and letting the Resource read it — copying 20 columns into a DTO to hand them to a Resource is
  duplication that drifts the moment a column is added.

## Resource

- Serialization only. No queries, no `load()`, no conditionals about permissions.
- Optional relations always through `whenLoaded()`.
- **Tier resources by field breadth, not by caller.** `PupilResource` (full), `PupilListResource`
  (list rows), `PupilMinimalResource` (id + name for pickers). A resource named after the endpoint
  that consumes it becomes a lie the moment a second endpoint reuses it.
- Extra top-level keys go through `additional()`; a shared private helper that injects the same
  envelope keys must take the **model**, not the resource, so subclasses can reuse it.
- Nested resource collections: prefer `ResourceClass::collection($this->whenLoaded('relation'))`.

## Checklist before finishing an endpoint

- [ ] Controller method has a dedicated `final` Form Request
- [ ] No `request()` access below the controller
- [ ] Every relation the Resource touches was eager-loaded in the Action
- [ ] Composite payload goes through one wrapper DTO and one Resource
- [ ] Resource exposes no field the caller is not allowed to see
- [ ] Response shape documented (OpenAPI annotation or equivalent) if the project publishes a spec
