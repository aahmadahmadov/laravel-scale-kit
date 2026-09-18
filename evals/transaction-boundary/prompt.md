---
name: "Transaction boundary and job dispatch"
description: "A job that cannot find its own row under load; must move the dispatch and the flush out of the transaction."
tags: [routing, consistency]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

This job intermittently fails in production with "No query results for model Enrollment", but only
under load, and never locally. Review it.

```php
DB::transaction(function () use ($data) {
    $enrollment = $this->enrollmentRepository->create($data);
    $this->notifyUpstream->handle($enrollment);      // HTTP call to the ministry API
    SendEnrollmentEmailJob::dispatch($enrollment->id);
    $this->enrollmentRepository->flushCache();
});
