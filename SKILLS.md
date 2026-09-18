# Skills index

Skills activate automatically from the request. This page is for deciding what to read, and for
seeing how the pieces fit.

## By question

| You are asking | Skill |
|---|---|
| "I am starting a new project — what do I build first?" | `layered-architecture` → `references/greenfield-setup.md` |
| "Where does this logic go?" | `layered-architecture` |
| "Should this be an Action, a Task, or inline?" | `layered-architecture` → `references/decision-tree.md` |
| "How do I build this endpoint end to end?" | `layered-architecture` → `references/worked-example.md` |
| "We still have `app/Services/` — now what?" | `layered-architecture` → `references/migrating-from-services.md` |
| "Is this controller doing too much?" | `http-boundary` |
| "What shape should this response be?" | `http-boundary` |
| "Which exception do I throw?" | `domain-exceptions` |
| "Which status code?" | `domain-exceptions` → `references/status-code-map.md` |
| "Where does the permission check go?" | `authorization-policies` |
| "Why is everyone getting a 403?" | `authorization-policies` |
| "How do I lay out this model?" | `eloquent-model-conventions` |
| "Where do I put this query condition?" | `repository-criteria` |
| "Which generic criteria already exist?" | `repository-criteria` → `references/criteria-catalogue.md` |
| "How do I add `?filter[x]=` to this list?" | `filterable-list-endpoints` |
| "Why is this read stale?" | `repository-caching` |
| "Why is this endpoint slow?" | `query-performance` |
| "Can I add an index to this 100M-row table?" | `query-performance` → `references/large-table-playbook.md` |
| "The plan looks fine but it's slow" | `query-performance` → `references/optimizer-traps.md` |
| "Where does this new column go?" | `migrations-schema` |
| "How should this docblock look?" | `php-standards` |
| "How do I add this message?" | `localization-enums` |
| "This sort closure is copy-pasted everywhere" | `shared-static-helpers` |
| "I need to call a third-party API" | `http-integrations` |
| "Should this move into a package?" | `package-extraction` |
| "Where does the transaction go?" | `transactions-and-consistency` |
| "The job can't find a row that exists" | `transactions-and-consistency` |
| "Duplicate rows appeared under load" | `transactions-and-consistency` |
| "How do I test this Action?" | `testing-layered-architecture` |
| "Our only database is a production copy — can I run the suite?" | `testing-layered-architecture` |
| "Is it safe to run this?" | `production-data-safety` |
| "Should I delegate this?" | `agent-delegation` |

## By workflow

**New endpoint**
`layered-architecture` → `http-boundary` → `repository-criteria` → `filterable-list-endpoints` →
`authorization-policies` → `domain-exceptions`

**Writing more than one row**
`layered-architecture` → `transactions-and-consistency` → `repository-caching`

**Writing tests**
`testing-layered-architecture` → the skill for the layer under test

**Slow endpoint**
`query-performance` → `repository-caching` → `migrations-schema` (only if a plan justifies an index)

**New integration**
`http-integrations` → `domain-exceptions` → `localization-enums`

**Schema change on a live database**
`production-data-safety` → `migrations-schema` → `query-performance`

**Code review**
`/architecture-review`, then `layered-architecture` → `php-standards` → `query-performance`

**Starting a new project**
`layered-architecture/references/greenfield-setup.md` → `/adopt-conventions` → `http-boundary` →
`domain-exceptions` → `authorization-policies`

**Adopting the kit in an existing codebase**
`/adopt-conventions` → `layered-architecture/references/migrating-from-services.md` →
`package-extraction`

## Dependency map

```
layered-architecture ── the spine; everything else refines one layer of it
├── http-boundary ............ the shell (controller, request, resource, DTO)
│   └── filterable-list-endpoints
├── domain-exceptions ........ what crosses the layers upward
│   └── http-integrations .... shared managers translate into domain exceptions
├── authorization-policies ... attached at the boundary, never below
├── repository-criteria ...... the bottom layer
│   ├── repository-caching
│   └── query-performance
│       └── migrations-schema
├── transactions-and-consistency ... the boundary around a write, and what may not cross it
├── testing-layered-architecture .. one test shape per layer
├── eloquent-model-conventions
├── shared-static-helpers .... the small logic that otherwise scatters
├── localization-enums
├── php-standards ............ applies to every file
├── package-extraction ....... when a rule's implementation outgrows one project
├── production-data-safety ... gates every write, in every environment
└── agent-delegation ......... how the above is enforced across many sessions
```

## The four rules everything else hangs off

1. **An Action owns one flow and never calls another Action.**
2. **A Task is one unit of work and never calls another Task.**
3. **Nothing below the controller reads the request or authorizes.**
4. **Nothing writes to a real database without a human saying yes.**

Everything else in this kit is a consequence of one of these.
