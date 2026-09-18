---
name: "Layer placement for a new flow"
description: "Where the logic for a two-step write endpoint belongs; must produce the layer split, not a service class."
tags: [routing, architecture]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

I am adding an endpoint to our Laravel API: `POST /classes/{class}/subjects` assigns a set of
subjects to a class, recalculates that class's weekly scheduled hours, and returns the updated list.

Where should each piece of logic live? Give me the class list before any code.
