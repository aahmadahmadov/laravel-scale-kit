# Migrating an existing `app/Services/` layer

Most codebases arrive here with a fat service layer. Do not rewrite it in one pass — that is how a
migration stalls halfway and leaves two architectures live at once.

## The rule while migrating

**New code follows the new architecture. Existing services are legacy and move only when touched.**
Write this sentence into the project's `CLAUDE.md` so every agent and every new developer reads it.

## Per-service procedure

1. **Find the flows.** A service class usually holds several unrelated flows, one per public method.
   List the public methods; each one is a candidate Action.
2. **Take one public method.** Create the Action named after the use-case (`ListClassSubjectsAction`),
   not after the entity (`ClassSubjectAction`).
3. **Move the body verbatim first.** Do not refactor and relocate in the same commit — you lose the
   ability to tell a behaviour change from a move.
4. **Then split.** Private helpers used more than once become Tasks. Private helpers used once get
   inlined. Repeated query shapes become Criteria.
5. **Repoint the controller** at the Action and delete the service method.
6. **Delete the service class** when its last method is gone. A half-empty service is worse than a
   full one — it hides where the remaining logic lives.

## What usually goes wrong

| Symptom | Cause | Fix |
|---|---|---|
| The new Action calls the old service | The flow was split across two services | Migrate both together, or wrap in an Orchestrator only if they are genuinely two flows |
| Every method became a Task | Mistaking "small" for "reusable" | Only extract what a second Action would call |
| The Action grew to 400 lines | Flow steps were never extracted as Tasks | Extract the self-contained steps; the branching stays |
| Two Actions share 90% of their body | They are one flow with a parameter | Merge them; pass an enum for the variant, not a boolean |

## Keep a scoreboard

Track how many services remain in the project's conventions file. A migration with a visible
denominator finishes; one without a denominator does not.
