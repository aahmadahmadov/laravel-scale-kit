# Contributing

## What belongs here

A rule earns a place in this kit when it meets all three:

1. **It was learned the hard way.** A bug, an outage, a review that kept repeating. Not a preference.
2. **It generalises.** It holds in a second Laravel codebase of similar size, not just in the one it
   came from.
3. **It is checkable.** Someone reading a diff can tell whether the rule was followed.

Guidance that is true but unfalsifiable — "keep classes small", "write clean code" — makes the kit
longer without making any diff better. It gets rejected.

## Writing a skill

```
skills/<kebab-name>/
├── SKILL.md
└── references/          # optional, for depth that is not needed every time
```

`SKILL.md` frontmatter:

```yaml
---
name: kebab-name              # must match the directory
description: Use when …       # third person, trigger-rich — this is what routes to the skill
license: MIT
metadata:
  version: "0.1.0"
  domain: backend | infrastructure | security | language | workflow | operations
  triggers: comma, separated, phrases
  role: specialist | architect | guardian
  scope: implementation | analysis | workflow
  related-skills: other-skill, another-skill
---
```

Body conventions:

- **Lead with the rule, then the reason.** A rule whose reason is missing gets argued with; a reason
  without a rule gets skimmed.
- Short code examples, in PHP, showing the wrong way and the right way when the difference is subtle.
- A trap section. The traps are the most valuable part of every skill in this repo.
- A checklist at the end when the skill governs something with a clear "done".
- Keep `SKILL.md` under ~150 lines. Overflow goes into `references/`.

## Writing a reference

A reference is loaded only when the task needs it, so it can be long — but it must be *lookup*
material: tables, catalogues, procedures. Not prose.

## Writing an agent

`agents/<name>.md`, frontmatter with `name`, `description`, `tools`, optional `model`.

**Every agent that can touch a database must restate the write restriction in its own prompt.**
Agents do not inherit the conventions file of whoever spawned them.

## Pull requests

- One rule or one skill per PR.
- Say in the description what went wrong that made the rule necessary. That sentence usually belongs
  in the skill too.
- If you are changing an existing rule, say what it breaks for anyone already following it.
