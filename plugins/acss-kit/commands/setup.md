---
description: Bootstrap a React project for acss-kit — installs sass, copies ui.tsx, writes .acss-target.json, optionally seeds a starter theme
argument-hint: [--no-theme] [--target=<dir>]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /setup

First-run bootstrap for acss-kit. Run once after `/plugin install acss-kit` to prepare your project before generating components or themes.

## Usage

```
/setup
/setup --no-theme
/setup --target=src/ui/fpkit/
```

## Workflow

When this command is invoked, follow the full bootstrap workflow documented in the `setup` skill at `${CLAUDE_PLUGIN_ROOT}/skills/setup/SKILL.md`.

### Quick Reference

Step numbers below match the canonical sequence in [`skills/setup/SKILL.md`](../skills/setup/SKILL.md):

- **Step 1 — Verify project** — confirm React + TypeScript project is present
- **Step 2 — React version** — detect React 19+ and warn if ui.tsx adaptation may be needed
- **Step 3 — Package manager** — auto-detect from lockfile or `package.json#packageManager` field
- **Step 4 — sass check** — if missing, print the exact install command and stop (no side effects)
- **Step 5 — Target directory** — read `.acss-target.json` or prompt for target dir and write the file
- **Step 6 — ui.tsx** — copy `${CLAUDE_PLUGIN_ROOT}/assets/foundation/ui.tsx` to target dir (verbatim)
- **Step 7 — Starter theme** — seed `src/styles/theme/light.css` and `dark.css` via OKLCH pipeline (skip with `--no-theme`)
- **Step 7.5 — Wire theme imports** — detect the project's main CSS/SCSS entry (`detect_css_entry.py`), prompt when ambiguous or absent, append `@import` lines idempotently, and record the choice in `stack.cssEntryFile`
- **Step 8 — Summary** — tabulate `created` vs `kept` artifacts and print next steps

### After Setup

Once `/setup` completes:

```
/kit-add button card      # generate your first components
/theme-create "#4f46e5"   # re-generate or tune the theme
```

Generated files (`src/components/fpkit/`, `src/styles/theme/`, `.acss-target.json`) are owned by your project — commit them.
