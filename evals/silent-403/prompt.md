---
name: "Everyone gets a 403"
description: "A route group that denies everyone with nothing in the logs; must find the parameter-name mismatch."
tags: [routing, security]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

Every user gets a 403 on this route group, including users the policy should allow. There is nothing
in the logs.

```php
Route::prefix('pupils/{student}')
    ->middleware(['can:view,pupil'])
    ->group(function () {
        Route::get('schedule', [PupilScheduleController::class, 'show']);
    });
```

What is happening?
