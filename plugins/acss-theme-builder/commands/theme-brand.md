---
description: Scaffold a brand-<name>.css preset that layers over light/dark
argument-hint: <name> [--from=<hex-color>]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Scaffold `src/styles/theme/brand-<name>.css` with light and dark overrides for primary/accent tokens.

Follow the `/theme-brand` section of `.claude/plugins/acss-theme-builder/skills/acss-theme-builder/SKILL.md`.

**Arguments:**

- `<name>` — brand name slug (e.g. `forest`, `coral`). Written as `brand-<name>.css`.
- `--from=<hex>` — optional seed color; if omitted, copies `assets/brand-template.css` with placeholder values.

**Quick steps:**

1. If `--from` is provided, run `scripts/generate_palette.py <hex> --mode=brand` to get only primary/accent values.
2. Write `src/styles/theme/brand-<name>.css` with `:root` (light overrides) and `[data-theme="dark"]` blocks.
3. Run `scripts/validate_theme.py` against the output file layered on the project's existing `light.css`.
4. Print the file path and instruct the developer to add an import after `light.css` and `dark.css`.
