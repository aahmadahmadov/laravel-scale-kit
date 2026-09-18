---
type: llm
weight: 3
---

A correct answer routes to the plugin's `authorization-policies` skill and identifies the exact
cause: `can:view,pupil` resolves the model by ROUTE PARAMETER NAME, the route binds `{student}`, so
Laravel cannot resolve the model, passes null or the string, and the policy denies everyone silently.

The fix must be to make the parameter name and the middleware argument match character-for-character.

It should also say to verify afterwards by calling the endpoint once as a user who should pass AND
once as a user who should be denied.

It must NOT blame the policy's conditions, the guard, or a missing policy registration as the primary
cause without first identifying the parameter-name mismatch.
