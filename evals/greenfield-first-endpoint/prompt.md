---
name: "First endpoint on an empty project"
description: "A brand-new Laravel app with no app/ code yet; must propose the minimum chain, not the full layer stack and a package."
tags: [routing, architecture, greenfield]
runs: 2
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

I just created a brand new Laravel 12 project. `app/` still only has the default `Models/User.php`
and the default controller. MySQL 8, one developer, maybe a dozen endpoints planned.

First endpoint: `GET /teachers` — a list of teachers with `?filter[school_id]=` and `?sort=`.

What do I build, and in what order?
