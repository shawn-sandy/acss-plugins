---
description: Stamp a page template (dashboard, auth, settings, list-detail, landing, error) into src/pages
argument-hint: <template> [name] [--force]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Stamp a page template into `src/pages/<Name>.tsx`.

**Templates:** `dashboard`, `auth-login`, `auth-signup`, `settings`, `list-detail`, `landing`, `error-404`, `error-500`.

Follow the `/app-page` section of `.claude/plugins/acss-app-builder/skills/acss-app-builder/SKILL.md`.

**Quick steps:**

1. Shared preflight.
2. If `name` is omitted, derive PascalCase from the template (e.g. `auth-login` → `AuthLogin`).
3. Read `assets/pages/<template>.tsx`.
4. For each fpkit component the template imports, verify against the active source. If `generated` and the component is missing locally, halt and print a `/kit-add <component>` hint.
5. Substitute `{{IMPORT_SOURCE:...}}` and `{{NAME}}` tokens.
6. Write to `src/pages/<Name>.tsx` (refuse non-empty without `--force`).
7. Print a wiring snippet for `src/App.tsx`.

**Reference:** `references/pages.md` — includes the tab-pattern clarification for the `settings` template (it uses `role="tablist"`, NOT the `Details` disclosure widget).
