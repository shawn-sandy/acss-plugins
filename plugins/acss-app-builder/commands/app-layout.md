---
description: Generate an app shell (AppShell.tsx + .scss) with grid-area layout
argument-hint: <holy-grail|sidebar|centered> [--force]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

Generate `src/app/AppShell.tsx` + `src/app/AppShell.scss` from one of three layout templates.

Follow the `/app-layout` section of `.claude/plugins/acss-app-builder/skills/acss-app-builder/SKILL.md`.

**Shells:**

- `holy-grail` — header + nav + main + aside + footer (three-column responsive grid)
- `sidebar` — fixed sidebar + content + footer
- `centered` — single centered column for auth / error pages

**Quick steps:**

1. Shared preflight (Vite detection, component source detection, theme base check).
2. Read `assets/layouts/app-shell-<shell>.tsx` and resolve `{{IMPORT_SOURCE:...}}` tokens via `scripts/detect_component_source.py`.
3. Compute relative paths from `src/app/AppShell.tsx` depth.
4. Write the shell + its SCSS (refuse on conflict without `--force`).
5. Print import snippet for `src/App.tsx`.
