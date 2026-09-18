---
name: "Testing an Action and its criteria"
description: "How to test an Action and a Criteria when the only database is a production copy."
tags: [routing, testing]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

How should I test `ListClassSubjectsAction` and the `ActiveInEducationYearCriteria` it pushes? Our
local database is a restored copy of production, and it is the only one configured.
