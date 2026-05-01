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

1. **Verify project** — confirm React + TypeScript project is present
2. **React version** — detect React 19+ and warn if ui.tsx adaptation may be needed
3. **Package manager** — auto-detect from lockfile or `package.json#packageManager` field
4. **sass check** — if missing, print the exact install command and stop (no side effects)
5. **Target directory** — read `.acss-target.json` or prompt for target dir and write the file
6. **ui.tsx** — copy `${CLAUDE_PLUGIN_ROOT}/assets/foundation/ui.tsx` to target dir (verbatim)
7. **Starter theme** — seed `src/styles/theme/light.css` and `dark.css` via OKLCH pipeline (skip with `--no-theme`)
8. **Wire theme imports** — detect the project's main CSS/SCSS entry (`detect_css_entry.py`), prompt when ambiguous or absent, append `@import` lines idempotently, and record the choice in `stack.cssEntryFile`
9. **Summary** — tabulate `created` vs `kept` artifacts and print next steps

### After Setup

Once `/setup` completes:

```
/kit-add button card      # generate your first components
/theme-create "#4f46e5"   # re-generate or tune the theme
```

Generated files (`src/components/fpkit/`, `src/styles/theme/`, `.acss-target.json`) are owned by your project — commit them.
