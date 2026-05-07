---
description: Generate a 10-step OKLCH color scale from a hex value, CSS named color, or theme role
argument-hint: <color> [--name=<name>] [--format=css|json|both]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Generate a 10-step color scale (steps 50–900) from a seed color in OKLCH space.

Follow the `/color-scale` section of `${CLAUDE_PLUGIN_ROOT}/skills/styles/SKILL.md`.

**Arguments:**

- `<color>` — seed color as `#rrggbb`, CSS named color (`red`, `cornflowerblue`), or theme role name (`background`, `primary`, `surface`)
- `--name=<name>` — CSS variable prefix used in output (e.g. `--color-<name>-50`). Defaults to the role/color name or `scale`.
- `--format=css|json|both` — output format (default: `both`)

**Quick steps:**

1. Resolve `<color>` to a hex value — look up theme role in `light.css` if needed; convert CSS named color to hex.
2. Run `scripts/generate_color_scale.py <hex> --name=<name> --format=both`.
3. Display the CSS block and a visual swatch summary of the 10 steps.
