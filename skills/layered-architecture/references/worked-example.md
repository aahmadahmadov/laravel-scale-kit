# Worked example: one endpoint, top to bottom

`GET /api/v1/classes/{class}/subjects` — list the subjects taught in a class, with the weekly hours
each one is scheduled for.

## 1. Route

```php
Route::prefix('classes/{class}')
    ->middleware(['can:view,class'])
    ->group(function (): void {
        Route::get('subjects', [ClassSubjectController::class, 'index']);
    });
```

Authorization is attached once on the group; the middleware resolves the bound model and calls
`ClassPolicy::view()`. No `if` in the controller.

## 2. Form Request

```php
final class ListClassSubjectsRequest extends FilterableListRequest
{
    /** @return array<int, AllowedFilter> */
    protected function allowedFilters(): array
    {
        return [
            AllowedFilter::exact('subject_id'),
            AllowedFilter::partial('name'),
        ];
    }

    /** @return array<int, string> */
    protected function allowedSorts(): array
    {
        return ['name', 'created_at'];
    }
}
```

## 3. Controller

```php
final class ClassSubjectController extends Controller
{
    public function __construct(private readonly ListClassSubjectsAction $action) {}

    /**
     * @param ListClassSubjectsRequest $request
     * @param Classm $class
     *
     * @return AnonymousResourceCollection
     */
    public function index(ListClassSubjectsRequest $request, Classm $class): AnonymousResourceCollection
    {
        return ClassSubjectResource::collection($this->action->handle($class));
    }
}
```

The request object is type-hinted but never read here — the filter criteria read it themselves.
The controller has no branch, no query, no `auth()`.

## 4. Action — one flow

```php
final class ListClassSubjectsAction
{
    public function __construct(
        private readonly ClassSubjectRepository $repository,
        private readonly CalculateScheduledHoursTask $calculateScheduledHours,
    ) {}

    /**
     * @param Classm $class
     *
     * @return Collection<int, ClassSubject>
     */
    public function handle(Classm $class): Collection
    {
        $subjects = $this->repository
            ->pushCriteria(new FieldEqualsCriteria('class_id', $class->id))
            ->pushCriteria(new WithCriteria(['subject', 'teacher.user']))
            ->pushCriteria(new FilterFieldsCriteria())
            ->pushCriteria(new RequestSortCriteria())
            ->all();

        $hours = $this->calculateScheduledHours->handle($class, $subjects->pluck('subject_id')->all());

        return $subjects
            ->each(fn (ClassSubject $subject) => $subject->setAttribute(
                'scheduled_hours',
                $hours[$subject->subject_id] ?? 0,
            ))
            ->sortBy(SubjectComparator::byName())
            ->values();
    }
}
```

Note what the Action does **not** do: it never reads `request()`, never authorizes, never catches.
The filter criteria are pushed unconditionally — each one no-ops when its request key is absent.

## 5. Task — one unit of work

```php
final class CalculateScheduledHoursTask
{
    public function __construct(private readonly ScheduleRepository $repository) {}

    /**
     * @param Classm $class
     * @param array<int, int> $subjectIds
     *
     * @return array<int, int> keyed by subject id
     */
    public function handle(Classm $class, array $subjectIds): array
    {
        return $this->repository
            ->pushCriteria(new FieldEqualsCriteria('class_id', $class->id))
            ->pushCriteria(new FieldInCriteria('subject_id', $subjectIds))
            ->pushCriteria(new GroupByCriteria(['subject_id']))
            ->all(['subject_id', DB::raw('COUNT(*) as lesson_count')])
            ->pluck('lesson_count', 'subject_id')
            ->all();
    }
}
```

The Task knows nothing about why the hours are wanted. A second Action can call it unchanged.

## 6. Resource

```php
final class ClassSubjectResource extends JsonResource
{
    /**
     * @param Request $request
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'scheduled_hours' => $this->scheduled_hours,
            'subject' => SubjectResource::make($this->whenLoaded('subject')),
            'teacher' => TeacherResource::make($this->whenLoaded('teacher')),
        ];
    }
}
```

## What would have been wrong

- Putting `CalculateScheduledHoursTask` logic in the controller — untestable, unreusable.
- Making `ListClassSubjectsAction` call a `GetClassAction` — Action calling Action.
- Wrapping `$this->repository->all()` in its own `GetClassSubjectsTask` — a pass-through class.
- Adding an Orchestrator — there is only one flow here.
