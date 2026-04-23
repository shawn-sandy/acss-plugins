---
description: Edit one or more role values in an existing theme file and re-validate
argument-hint: <file> <--color-role=#hex> [...]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Update specific role values in an existing `light.css`, `dark.css`, or `brand-*.css` and re-run contrast checks.

Follow the `/theme-update` section of `.claude/plugins/acss-theme-builder/skills/acss-theme-builder/SKILL.md`.

**Arguments:**

- `<file>` — path to the theme CSS file (e.g. `src/styles/theme/light.css`)
- `<--color-role=#hex>` — one or more role+value pairs (e.g. `--color-primary=#2563eb`)

**Quick steps:**

1. Read the target CSS file. Identify each named role to update.
2. For each role: use Edit to replace the value in-place, preserving surrounding comments and file structure.
3. Run `scripts/validate_theme.py <file>` for contrast checks. If a pair fails, print the failure and revert the change to the offending role(s).
4. Confirm final state: which roles were updated, which (if any) were rejected due to contrast failure.
