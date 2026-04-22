---
description: Generate a theme preset (light, dark, both, or brand-*) with CSS variable validation
argument-hint: <light|dark|both|brand-neutral|brand-vibrant> [--mode=light|dark|both]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

Generate theme CSS files under `src/styles/theme/` and validate them.

Follow the `/app-theme` section of `.claude/plugins/acss-app-builder/skills/acss-app-builder/SKILL.md`.

**Presets:**

- `light` — `src/styles/theme/light.css`
- `dark` — `src/styles/theme/dark.css` (scoped under `[data-theme="dark"]`)
- `both` — writes both files above
- `brand-neutral` — accent overrides only
- `brand-vibrant` — saturated accent palette

**Quick steps:**

1. Shared preflight (this command is exempt from the theme-base check when the preset includes `light`).
2. Copy the chosen `assets/themes/*.css` file(s) to `src/styles/theme/`.
3. Update the sentinel-bounded block in the entry file to import the new theme file(s).
4. Run `scripts/validate_theme.py src/styles/theme/` for WCAG contrast checks on palette files. Report failures as warnings.

**Note:** `validate_css_vars.py` is intentionally NOT run here — it enforces the component-variable pattern (`--btn-bg`), which is a category mismatch for design-token primitives (`--fs-xs`, `--space-1`) and semantic role tokens (`--color-primary`). That validator is used by `/app-compose` on component SCSS instead.
