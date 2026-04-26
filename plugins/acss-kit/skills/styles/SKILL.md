---
name: styles
description: Generate and update CSS themes for fpkit/acss projects. Creates full light/dark palettes from seed colors using OKLCH, scaffolds brand presets, edits theme roles in place with WCAG re-validation, and extracts tokens from images or Figma designs. Use when the developer wants to create a theme, customize brand colors, or update specific role values in an existing theme.
allowed-tools: AskUserQuestion, Bash, Edit, Glob, Grep, Read, Write
metadata:
  version: "0.3.0"
---

# styles

Theme generation and management for **fpkit/acss** projects. Routes between four flows depending on which slash command was invoked.

**Token and role conventions:** see `references/role-catalogue.md` and the CSS Token Convention below.
**OKLCH palette algorithm:** see `references/palette-algorithm.md`.
**JSON Schema and round-tripping:** see `references/theme-schema.md`. The JSON schema is internal to the round-trip scripts (`tokens_to_css.py` / `css_to_tokens.py`); the CSS Token Convention below is the user-facing authoring format.

---

## CSS Token Convention

The authoring format for theme tokens is **CSS custom properties** — not JSON. Users edit `light.css` / `dark.css` / `brand-*.css` files directly; the JSON schema at `${CLAUDE_PLUGIN_ROOT}/assets/theme.schema.json` is internal to the round-trip scripts and is not a user-facing contract. Existing CSS theme files remain byte-compatible with this convention.

### Semantic role names

`assets/theme.schema.json` `$defs/palette` declares **18 defined `--color-*` properties** total: **15 required roles** plus 3 optional roles (`--color-surface-subtle`, `--color-text-subtle`, `--color-brand-accent`). Names stay byte-compatible with the bundled CSS theme files — no renames, no removals, ever. Group them by purpose, matching `ROLE_GROUPS` in `${CLAUDE_PLUGIN_ROOT}/scripts/tokens_to_css.py`:

**Backgrounds**
- `--color-background` *(required)* — page background
- `--color-surface` *(required)* — card / panel surface
- `--color-surface-raised` *(required)* — elevated surface (modals, popovers)
- `--color-surface-subtle` *(optional)* — table-stripe / hover surface

**Text**
- `--color-text` *(required)* — body text
- `--color-text-muted` *(required)* — secondary text
- `--color-text-inverse` *(required)* — text on primary background
- `--color-text-subtle` *(optional)* — tertiary text (timestamps, footnotes)

**Borders**
- `--color-border` *(required)* — default border
- `--color-border-strong` *(required)* — emphasized border (form-field focus)

**Brand & semantic**
- `--color-primary` *(required)* — brand primary
- `--color-primary-hover` *(required)* — primary hover state
- `--color-success` *(required)* — success / valid state
- `--color-warning` *(required)* — caution state
- `--color-danger` *(required)* — destructive / error state
- `--color-info` *(required)* — informational state
- `--color-brand-accent` *(optional)* — secondary brand color

**Focus**
- `--color-focus-ring` *(required)* — focus indicator color (inputs, buttons)

Full role catalog with contrast pairings is in [`references/role-catalogue.md`](references/role-catalogue.md).

### Required Contrast Pairings (WCAG 2.2 AA)

Every theme must pass these pairings — the validator at `${CLAUDE_PLUGIN_ROOT}/scripts/validate_theme.py` checks them automatically on every `/theme-create`, `/theme-brand`, `/theme-update`, and `/theme-extract`:

| Foreground | Background | Min ratio | Why |
|---|---|---|---|
| `--color-text` | `--color-background` | 4.5:1 | Body text on page (WCAG 1.4.3) |
| `--color-text-muted` | `--color-background` | 4.5:1 | Secondary text on page (WCAG 1.4.3) |
| `--color-text` | `--color-surface` | 4.5:1 | Body text on cards/panels |
| `--color-text-inverse` | `--color-primary` | 4.5:1 | Label text on primary buttons |
| `--color-text-inverse` | `--color-success` | 4.5:1 | Success state buttons / badges |
| `--color-text-inverse` | `--color-danger` | 4.5:1 | Destructive buttons / error chips |
| `--color-text-inverse` | `--color-warning` | 4.5:1 | Warning chips / banners |
| `--color-text-inverse` | `--color-info` | 4.5:1 | Info chips / banners |
| `--color-focus-ring` | `--color-background` | 3:1 | Focus indicator on page (WCAG 1.4.11) |
| `--color-border-strong` | `--color-surface` | 3:1 | Form-field focus border (WCAG 1.4.11) |

The validator's full pair list (10 pairs at default thresholds) is in `scripts/validate_theme.py:PAIRS`. Any theme that fails one of these pairings should be revised — usually by adjusting the seed color or manually tuning the OKLCH lightness on the failing role.

### Authoring flow

1. **Generate or edit a CSS theme file directly.** `/theme-create` and `/theme-brand` write `light.css` / `dark.css` / `brand-*.css` using the convention above. `/theme-update` edits role values in place.
2. **The user never authors JSON.** No `theme.tokens.json` to write or maintain.
3. **Round-trip scripts (`tokens_to_css.py`, `css_to_tokens.py`) remain internal.** They use the JSON schema to translate between the OKLCH palette generator's output and CSS, but the JSON shape is not a user-facing contract.
4. **Validation runs automatically** at the end of every theme command (no separate step). Failures are surfaced inline.

---

## `/theme-create <hex-color> [--mode=light|dark|both]`

**Purpose:** Generate `light.css` and/or `dark.css` under `src/styles/theme/` from a seed color.

### Workflow

1. Validate the seed is a 3- or 6-digit hex color. If invalid, halt with usage hint.
2. Run `${CLAUDE_PLUGIN_ROOT}/scripts/generate_palette.py <hex-color> --mode=<mode>` (default `both`). Capture JSON stdout.
   - If exit code 1 (`"reasons"` non-empty), print the reasons and halt.
3. Determine output directory. If `src/styles/theme/` exists in the project, use it. Otherwise ask the developer where to write theme files.
4. Run `${CLAUDE_PLUGIN_ROOT}/scripts/tokens_to_css.py --stdin --out-dir=<dir>` piping the palette JSON. This writes `light.css` and/or `dark.css` with mandatory `var(--x, <fallback>)` syntax.
5. Run `${CLAUDE_PLUGIN_ROOT}/scripts/validate_theme.py <dir>`. If contrast failures are found, print them as warnings and continue — generation is complete but the developer should adjust the seed or manually tune values.
6. Print a summary: files written, primary color, top contrast ratios.

### References to load

- `references/palette-algorithm.md` — OKLCH lightness targets and state-color hue offsets.
- `references/role-catalogue.md` — full role list and contrast targets.

---

## `/theme-brand <name> [--from=<hex-color>]`

**Purpose:** Scaffold `brand-<name>.css` with light and dark primary/accent overrides.

### Workflow

1. Validate `<name>` is a lowercase slug (alphanumeric + hyphens). If not, suggest a corrected slug.
2. Determine output directory (same as `/theme-create`).
3. If `--from` is provided:
   - Run `${CLAUDE_PLUGIN_ROOT}/scripts/generate_palette.py <hex> --mode=brand`. Capture brand overrides JSON.
   - Write `brand-<name>.css` using the `:root` (light) and `[data-theme="dark"]` overrides.
4. If `--from` is not provided:
   - Copy `${CLAUDE_PLUGIN_ROOT}/assets/brand-template.css` to `brand-<name>.css`. Instruct the developer to replace the placeholder values.
5. Run `${CLAUDE_PLUGIN_ROOT}/scripts/validate_theme.py <brand-file>`. Report contrast results. Failures are warnings only (the brand file's primary is validated in context of the project's existing `light.css` background, which may not be present here).
6. Print the file path and instruct the developer to add an import **after** `light.css` and `dark.css` in their entry file.

### References to load

- `references/palette-algorithm.md` — brand mode generation.
- `references/role-catalogue.md` — which roles are allowed in brand files.

---

## `/theme-update <file> <--color-role=#hex> [...]`

**Purpose:** Edit specific role values in an existing theme file and re-validate.

### Workflow

1. Confirm `<file>` exists and its name matches `light.css`, `dark.css`, or `brand-*.css`. Halt if not.
2. Parse the developer's role=value arguments. Each must be of the form `--color-<role>=#<hex>`.
3. For each update:
   a. Use Edit to replace the existing hex value for that role in-place, preserving comments and file structure.
   b. After each edit, run `${CLAUDE_PLUGIN_ROOT}/scripts/validate_theme.py <file>`.
   c. If any contrast pair fails: print the failure, revert the edit for that role (restore original value), and continue with remaining roles.
4. Print a final table: role / old value / new value / accepted|reverted.

### References to load

- `references/role-catalogue.md` — contrast thresholds per pair.

---

## `/theme-extract <image-path|figma-url>`

**Purpose:** Extract brand colors from an image or Figma design and generate theme CSS.

### Workflow

1. Detect input type:
   - `figma.com` URL → delegate to user-level `figma-design-tokens` skill.
   - File path (png/jpg/webp/gif) → delegate to user-level `design-token-extractor` skill.
   - Neither → halt with usage hint.
2. Both extractors return at minimum a `primary` hex color (and optionally `secondary`, `accent`, `background`). Map the `primary` value to the seed color.
3. Run `${CLAUDE_PLUGIN_ROOT}/scripts/generate_palette.py <primary-hex> --mode=both`. Capture JSON.
4. If the extractor also returned `secondary` or `accent` colors, AskUserQuestion: "Should I also scaffold a brand preset using the secondary color?" If yes, run the brand flow inline.
5. Write theme CSS via `${CLAUDE_PLUGIN_ROOT}/scripts/tokens_to_css.py`. Validate with `${CLAUDE_PLUGIN_ROOT}/scripts/validate_theme.py`.
6. Optionally write `theme.tokens.json` alongside the CSS files:
   - Run `${CLAUDE_PLUGIN_ROOT}/scripts/css_to_tokens.py` on the written files and save the result.
7. Print files written and a note about round-tripping via `scripts/css_to_tokens.py`.

### References to load

- `references/palette-algorithm.md`
- `references/theme-schema.md` — JSON output format and round-trip contract.
- `references/role-catalogue.md`

---

## Error handling (all flows)

| Situation | Action |
|---|---|
| Seed hex invalid | Halt with: `"<value>" is not a valid hex color. Use #rrggbb or #rgb.` |
| `generate_palette.py` exits 1 | Print each reason from `"reasons"` array. Halt. |
| Output file already exists | Halt with list of conflicts. Proceed only with `--force`. |
| Contrast failure during update | Revert that specific role. Continue with remaining roles. |
| Extractor skill unavailable | Halt with: `"/theme-extract requires the design-token-extractor or figma-design-tokens skill. Run: /find-skills design-token"` |
