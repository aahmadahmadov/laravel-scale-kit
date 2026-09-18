# Eval suite

These cases check the thing this plugin's value depends on and nothing else can verify: **that the
right skill fires on a realistic request, and that the advice it produces is the kit's advice.**

A skill nobody routes to is a file, not a rule. A `description` can be perfectly written and still
never trigger; the only way to know is to run the request.

## Running

```bash
claude plugin eval . --trust-plugin
```

Each case runs twice with the plugin and twice without it (the ablation arm), so the report shows
the **delta** the plugin makes rather than the model's baseline competence. `tool_used: Skill`
graders are plugin-fired indicators and do not count toward the score.

Useful flags:

```bash
claude plugin eval . --case 'silent-403*' --trust-plugin   # one case
claude plugin eval . --tag routing --trust-plugin          # one dimension
claude plugin eval . --threshold 0.8 --trust-plugin        # fail below 0.8
```

A full local run is 7 cases x 2 runs x 2 arms = 28 model runs. At the time of writing that is roughly
$7. Use `--runs 1` or `--case` while iterating.

## Why CI does not run these on every push

Every case is a real model run on your own credential. `.github/workflows/validate.yml` runs the
free structural checks on push, and the eval job is `workflow_dispatch` only. Run the suite before a
release, and whenever a skill's `description` changes — that field is the routing mechanism, so
editing it is editing behaviour.

## Adding a case

```
evals/<case-name>/
├── prompt.md          # frontmatter: name, description, tags, runs, max_turns, allowed_tools
└── graders/
    ├── skill-fired.md # type: tool_used, tool: Skill
    └── criteria.md    # type: llm — what a correct answer contains
```

Grader types: `regex`, `tool_order`, `tool_used`, `file_exists`, `llm`, `baseline`.

**Never name the skill in `prompt.md`.** The case exists to test whether the request routes on its
own; naming the skill tests nothing. Name it in the grader instead — graders are read by the judge,
not by the agent under test.
