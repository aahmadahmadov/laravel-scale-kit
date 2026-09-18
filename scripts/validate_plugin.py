#!/usr/bin/env python3
"""Structural validation for the laravel-scale-kit plugin.

Checks everything about this repo that can be checked without a model:
frontmatter shape, name/path agreement, version agreement, cross-references,
the counts quoted in the docs, and the kit's own contribution rules.

Usage: python3 scripts/validate_plugin.py [--root <path>]
Exit code 0 = clean, 1 = at least one error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

ALLOWED_DOMAINS = {
    "backend",
    "infrastructure",
    "security",
    "language",
    "workflow",
    "operations",
    "testing",
}
ALLOWED_ROLES = {"specialist", "architect", "guardian"}
ALLOWED_SCOPES = {"implementation", "analysis", "workflow"}

# CONTRIBUTING.md: "Keep SKILL.md under ~150 lines." Hard-fail with a little slack.
SKILL_MAX_LINES = 160

# CONTRIBUTING.md: "Every agent that can touch a database must restate the write
# restriction in its own prompt." Any agent holding Bash can reach a database.
DB_RESTRICTION_MARKERS = (
    "never run",
    "forbidden without",
    "never write to",
    "do not run any command that writes",
)

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def split_frontmatter(path: Path) -> tuple[dict, str]:
    """Return (frontmatter, body) for a markdown file with YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        error(f"{path}: missing YAML frontmatter")
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        error(f"{path}: frontmatter is not terminated")
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        error(f"{path}: frontmatter is not valid YAML — {exc}")
        return {}, body
    if not isinstance(data, dict):
        error(f"{path}: frontmatter must be a mapping")
        return {}, body
    return data, body


def check_manifests(root: Path) -> str:
    plugin_path = root / ".claude-plugin" / "plugin.json"
    market_path = root / ".claude-plugin" / "marketplace.json"

    plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
    market = json.loads(market_path.read_text(encoding="utf-8"))

    version = plugin.get("version")
    if not version:
        error("plugin.json: missing version")
        return ""

    if market.get("metadata", {}).get("version") != version:
        error(
            f"marketplace.json: metadata.version "
            f"{market.get('metadata', {}).get('version')!r} != plugin.json {version!r}"
        )

    entries = market.get("plugins", [])
    if len(entries) != 1:
        error(f"marketplace.json: expected exactly 1 plugin entry, found {len(entries)}")
    else:
        entry = entries[0]
        if entry.get("version") != version:
            error(
                f"marketplace.json: plugins[0].version {entry.get('version')!r} "
                f"!= plugin.json {version!r}"
            )
        if entry.get("name") != plugin.get("name"):
            error("marketplace.json: plugins[0].name != plugin.json name")

    for field in ("name", "description", "author", "license"):
        if not plugin.get(field):
            error(f"plugin.json: missing {field}")

    return version


def check_skills(root: Path, version: str) -> list[str]:
    skills_dir = root / "skills"
    names: list[str] = []
    seen_refs: dict[Path, set[Path]] = {}

    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            error(f"{skill_dir}: no SKILL.md")
            continue

        fm, body = split_frontmatter(skill_file)
        names.append(skill_dir.name)

        if fm.get("name") != skill_dir.name:
            error(f"{skill_file}: name {fm.get('name')!r} != directory {skill_dir.name!r}")

        description = fm.get("description", "")
        if not description:
            error(f"{skill_file}: missing description")
        elif not description.startswith("Use "):
            error(f"{skill_file}: description must start with 'Use when …' / 'Use before …'")
        elif "Invoke" not in description:
            error(f"{skill_file}: description must carry an 'Invoke …' trigger clause")
        elif len(description) < 80:
            warn(f"{skill_file}: description is short ({len(description)} chars) — weak routing")

        if fm.get("license") != "MIT":
            error(f"{skill_file}: license must be MIT")

        meta = fm.get("metadata") or {}
        if str(meta.get("version")) != version:
            error(
                f"{skill_file}: metadata.version {meta.get('version')!r} "
                f"!= plugin version {version!r}"
            )
        if meta.get("domain") not in ALLOWED_DOMAINS:
            error(f"{skill_file}: metadata.domain {meta.get('domain')!r} not allowed")
        if meta.get("role") not in ALLOWED_ROLES:
            error(f"{skill_file}: metadata.role {meta.get('role')!r} not allowed")
        if meta.get("scope") not in ALLOWED_SCOPES:
            error(f"{skill_file}: metadata.scope {meta.get('scope')!r} not allowed")
        if not meta.get("triggers"):
            error(f"{skill_file}: metadata.triggers is required")

        line_count = len(skill_file.read_text(encoding="utf-8").splitlines())
        if line_count > SKILL_MAX_LINES:
            error(f"{skill_file}: {line_count} lines, limit is {SKILL_MAX_LINES}")

        referenced = {
            (skill_dir / "references" / m.group(1)).resolve()
            for m in re.finditer(r"references/([\w.-]+\.md)", body)
        }
        for ref in referenced:
            if not ref.exists():
                error(f"{skill_file}: points at missing {ref.relative_to(root)}")
        seen_refs[skill_dir] = referenced

    for skill_dir, referenced in seen_refs.items():
        ref_dir = skill_dir / "references"
        if not ref_dir.is_dir():
            continue
        for ref in sorted(ref_dir.glob("*.md")):
            if ref.resolve() not in referenced:
                error(f"{ref.relative_to(root)}: never referenced from its SKILL.md")

    for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        fm, _ = split_frontmatter(skill_dir / "SKILL.md")
        related = (fm.get("metadata") or {}).get("related-skills", "")
        for related_name in [s.strip() for s in str(related).split(",") if s.strip()]:
            if related_name not in names:
                error(f"{skill_dir / 'SKILL.md'}: related-skills names unknown skill {related_name!r}")

    return names


def check_agents(root: Path) -> list[str]:
    names: list[str] = []
    for agent_file in sorted((root / "agents").glob("*.md")):
        fm, body = split_frontmatter(agent_file)
        names.append(agent_file.stem)

        if fm.get("name") != agent_file.stem:
            error(f"{agent_file}: name {fm.get('name')!r} != filename {agent_file.stem!r}")
        if not fm.get("description"):
            error(f"{agent_file}: missing description")

        tools = fm.get("tools", "")
        tool_list = [t.strip() for t in str(tools).split(",") if t.strip()]
        if not tool_list:
            error(f"{agent_file}: missing tools")

        if "Bash" in tool_list:
            lowered = body.lower()
            if not any(marker in lowered for marker in DB_RESTRICTION_MARKERS):
                error(
                    f"{agent_file}: holds Bash but never restates the database write "
                    f"restriction (CONTRIBUTING.md requires it — it is not inherited)"
                )
    return names


def check_commands(root: Path) -> list[str]:
    names: list[str] = []
    for command_file in sorted((root / "commands").glob("*.md")):
        fm, _ = split_frontmatter(command_file)
        names.append(command_file.stem)
        if not fm.get("description"):
            error(f"{command_file}: missing description")
    return names


def check_quoted_counts(root: Path, counts: dict[str, int]) -> None:
    """The docs quote counts. Keep them true, so the README never drifts again."""
    patterns = {
        "skills": r"(\d+)\s+skills",
        "agents": r"(\d+)\s+subagents",
        "commands": r"(\d+)\s+commands",
        "references": r"(\d+)\s+reference documents",
    }
    targets = [
        root / "README.md",
        root / "CHANGELOG.md",
        root / ".claude-plugin" / "marketplace.json",
    ]
    for target in targets:
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8")
        if target.name == "CHANGELOG.md":
            # Only the newest release section describes the current tree. Older entries
            # record what was true then and must not be rewritten to match today.
            sections = re.split(r"^## \[", text, flags=re.M)
            text = "## [" + sections[1] if len(sections) > 1 else text
        for key, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                quoted = int(match.group(1))
                if quoted != counts[key]:
                    line = text[: match.start()].count("\n") + 1
                    error(
                        f"{target.relative_to(root)}:{line}: says {quoted} {key}, "
                        f"actual is {counts[key]}"
                    )


def check_docs_cover_everything(root: Path, skills: list[str], agents: list[str]) -> None:
    readme = (root / "README.md").read_text(encoding="utf-8")
    skills_index = (root / "SKILLS.md").read_text(encoding="utf-8")
    for skill in skills:
        if f"`{skill}`" not in readme:
            error(f"README.md: skill {skill!r} is not listed")
        if f"`{skill}`" not in skills_index:
            error(f"SKILLS.md: skill {skill!r} is not listed")
    for agent in agents:
        if f"`{agent}`" not in readme:
            error(f"README.md: agent {agent!r} is not listed")


def check_evals(root: Path, skills: list[str]) -> None:
    evals_dir = root / "evals"
    if not evals_dir.is_dir():
        warn("evals/: no eval suite — skill routing is unverified")
        return

    cases = sorted(p for p in evals_dir.iterdir() if p.is_dir() and p.name != "results")
    if not cases:
        error("evals/: directory exists but holds no cases")

    valid_grader_types = {"regex", "tool_order", "tool_used", "file_exists", "llm", "baseline"}
    for case in cases:
        prompt = case / "prompt.md"
        if not prompt.exists():
            error(f"{case.relative_to(root)}: missing prompt.md")
            continue
        split_frontmatter(prompt)

        graders = sorted((case / "graders").glob("*.md"))
        if not graders:
            error(f"{case.relative_to(root)}: no graders")
        for grader in graders:
            fm, _ = split_frontmatter(grader)
            grader_type = fm.get("type")
            if grader_type not in valid_grader_types:
                error(
                    f"{grader.relative_to(root)}: type {grader_type!r} is not one of "
                    f"{sorted(valid_grader_types)}"
                )
            if grader_type == "tool_used" and not fm.get("tool"):
                error(f"{grader.relative_to(root)}: tool_used grader needs a 'tool' key")
            if grader_type == "file_exists" and not fm.get("path"):
                error(f"{grader.relative_to(root)}: file_exists grader needs a 'path' key")

    # Coverage is declared in the graders, never in prompt.md: naming the skill in
    # the prompt would bias the very routing the case exists to measure.
    covered = set()
    for case in cases:
        grader_text = "".join(
            g.read_text(encoding="utf-8") for g in sorted((case / "graders").glob("*.md"))
        )
        if (case / "prompt.md").exists():
            prompt_text = (case / "prompt.md").read_text(encoding="utf-8")
            body = prompt_text.split("\n---\n", 1)[-1]
            for skill in skills:
                if skill in body:
                    error(
                        f"{case.relative_to(root)}/prompt.md: names the skill {skill!r} — "
                        f"that biases routing; declare it in the grader instead"
                    )
        covered.update(skill for skill in skills if skill in grader_text)
    uncovered = sorted(set(skills) - covered)
    if uncovered:
        warn(f"evals/: no case names these skills — {', '.join(uncovered)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = Path(args.root).resolve()

    version = check_manifests(root)
    skills = check_skills(root, version)
    agents = check_agents(root)
    commands = check_commands(root)
    references = sorted((root / "skills").glob("*/references/*.md"))

    counts = {
        "skills": len(skills),
        "agents": len(agents),
        "commands": len(commands),
        "references": len(references),
    }
    check_quoted_counts(root, counts)
    check_docs_cover_everything(root, skills, agents)
    check_evals(root, skills)

    print(
        f"laravel-scale-kit v{version}: {counts['skills']} skills, "
        f"{counts['references']} references, {counts['agents']} agents, "
        f"{counts['commands']} commands"
    )

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")

    if errors:
        print(f"\n{len(errors)} error(s).")
        return 1
    print("\nOK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
