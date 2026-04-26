---
description: Generate light and/or dark theme CSS from a seed hex color
argument-hint: <hex-color> [--mode=light|dark|both]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Generate `src/styles/theme/light.css` and/or `dark.css` from a seed color using OKLCH palette math.

Follow the `/theme-create` section of `${CLAUDE_PLUGIN_ROOT}/skills/styles/SKILL.md`.

**Arguments:**

- `<hex-color>` — seed color for `--color-primary` (e.g. `"#4f46e5"`)
- `--mode=light|dark|both` — which palette file(s) to write (default: `both`)

**Quick steps:**

1. Run `scripts/generate_palette.py <hex-color> --mode=<mode>`. Capture JSON stdout.
2. Run `scripts/tokens_to_css.py` with the JSON to write theme CSS file(s) to `src/styles/theme/`.
3. Run `scripts/validate_theme.py src/styles/theme/` for WCAG AA contrast checks. Report failures; do not write files on failure.
4. Print a summary of files written and the top contrast ratios.
