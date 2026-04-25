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

## CSS Token Convention (v0.2.0+)

The going-forward authoring format is **CSS custom properties**, not JSON. Users edit `light.css` / `dark.css` / `brand-*.css` files directly. The full convention — 18 defined `--color-*` properties (15 required + 3 optional), grouped by purpose, with the WCAG 2.2 AA Required Contrast Pairings table — is documented in [`skills/acss-theme-builder/SKILL.md`](skills/acss-theme-builder/SKILL.md#css-token-convention-v020).

The slash commands (`/theme-create`, `/theme-brand`, `/theme-update`, `/theme-extract`) all produce CSS theme files that conform to this convention; users never need to author JSON.

## JSON round-tripping (internal)

> **Deprecated as a user-facing contract — sunset in `acss-theme-builder@0.3.0`.** The CSS Token Convention above is the canonical authoring format.

Round-trip scripts are retained as **internal utilities** for tooling that needs to translate between OKLCH palette JSON and CSS:

```bash
# Export CSS to JSON (internal export utility)
python3 scripts/css_to_tokens.py src/styles/theme/light.css src/styles/theme/dark.css \
  > theme.tokens.json

# Import JSON to CSS (internal — used by /theme-create internally)
python3 scripts/tokens_to_css.py theme.tokens.json --out-dir src/styles/theme/
```

The JSON format is validated against `assets/theme.schema.json`, which carries `"deprecated": true` and `"x-sunset-version": "0.3.0"` markers as of v0.2.0. End users should not author JSON conforming to this schema; the schema and round-trip scripts are internal to the plugin's pipeline.

## WCAG AA contrast

`scripts/validate_theme.py` checks 10 semantic role pairs for WCAG 2.1 AA compliance. See `skills/acss-theme-builder/references/role-catalogue.md` for the full pair list and thresholds.

## Relationship to acss-app-builder

`acss-theme-builder` handles theme generation only. `acss-app-builder` handles project scaffolding (Vite setup, component generation, layout templates). Use both together or independently.
