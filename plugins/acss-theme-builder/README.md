# acss-theme-builder

Claude Code plugin for generating and updating CSS themes in [@fpkit/acss](https://github.com/shawn-sandy/acss) projects.

## Install

```shell
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-theme-builder@shawn-sandy-acss-plugins
```

## Commands

### `/theme-create <hex-color> [--mode=light|dark|both]`

Generate `light.css` and `dark.css` from a seed color using OKLCH palette math. Produces WCAG AA-validated semantic role tokens.

```shell
/theme-create "#4f46e5"
/theme-create "#0f766e" --mode=light
```

### `/theme-brand <name> [--from=<hex-color>]`

Scaffold a `brand-<name>.css` file with primary/accent overrides that layer on top of `light.css` and `dark.css`.

```shell
/theme-brand forest --from="#0f766e"
/theme-brand coral
```

### `/theme-update <file> <--color-role=#hex> [...]`

Edit specific role values in an existing theme file and re-validate. Reverts any change that fails WCAG AA.

```shell
/theme-update src/styles/theme/light.css --color-primary="#2563eb"
/theme-update src/styles/theme/dark.css --color-primary="#7dd3fc" --color-focus-ring="#7dd3fc"
```

### `/theme-extract <image-path|figma-url>`

Extract brand colors from an image or Figma design and generate full theme CSS.

```shell
/theme-extract ~/Downloads/brand-moodboard.png
/theme-extract https://figma.com/design/abc123/Brand-Guide
```

## Theme structure

Generated files follow the three-layer token cascade used across all acss-plugins:

- `base.css` — primitives (spacing, typography, radii) — provided by `acss-app-builder`
- `light.css` — semantic role tokens under `:root`
- `dark.css` — semantic role tokens under `[data-theme="dark"]`
- `brand-<name>.css` — primary/accent overrides layered on top

Toggle dark mode by setting `data-theme="dark"` on the `<html>` element.

## JSON round-tripping

Export CSS to JSON:

```bash
python3 scripts/css_to_tokens.py src/styles/theme/light.css src/styles/theme/dark.css \
  > theme.tokens.json
```

Import JSON to CSS:

```bash
python3 scripts/tokens_to_css.py theme.tokens.json --out-dir src/styles/theme/
```

The JSON format is validated against `assets/theme.schema.json`.

## WCAG AA contrast

`scripts/validate_theme.py` checks 10 semantic role pairs for WCAG 2.1 AA compliance. See `skills/acss-theme-builder/references/role-catalogue.md` for the full pair list and thresholds.

## Relationship to acss-app-builder

`acss-theme-builder` handles theme generation only. `acss-app-builder` handles project scaffolding (Vite setup, component generation, layout templates). Use both together or independently.
