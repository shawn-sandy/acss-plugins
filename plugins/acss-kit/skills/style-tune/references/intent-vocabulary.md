# Intent vocabulary

Modifier → token-family mapping for the `style-tune` skill. Every
modifier listed here is a trigger phrase; bare adjectives in prose
contexts must NOT trigger the skill (front-matter description is
component- and role-anchored).

`{c}` in token names stands for the resolved component prefix
(`btn`, `card`, `alert`, `dialog`, `input`, `nav`).

## v1 component coverage

| Family | Button | Card | Alert | Dialog | Input | Nav |
|---|---|---|---|---|---|---|
| Color | yes | yes | yes | yes | yes | yes |
| Radius | yes | yes | yes | yes | yes | — |
| Spacing | yes | yes | yes | yes | yes | yes |
| Elevation | — | yes | yes | yes | — | — |
| Size (font) | yes | — | — | — | — | — |
| Size (width) | — | — | — | yes | yes | — |
| Height | — | — | — | yes | — | — |

Components outside the v1 list (`field`, `checkbox`, `icon`, `link`,
`list`, `popover`, `table`, `tag`, `badge`, `img`) halt with a v2
hint.

## Clamp ranges

Applied after every delta:

- `--{c}-radius`: `[0.125rem, 1rem]`
- OKLCH lightness: `[0.15, 0.95]`
- OKLCH chroma: clipped at sRGB gamut by `oklch_to_hex`
- `--{c}-padding-*` / `--{c}-gap`: `[0.125rem, 4rem]`
- `--{c}-max-height`: `[20vh, 95vh]`

## Single-axis modifiers

### Radius

| Modifiers | Layer | Family | Delta | var-only fallback |
|---|---|---|---|---|
| softer, friendlier, rounded, smoother | component | `--{c}-radius` | × 1.5 (clamp ≤ 1rem) | none — radius is always scalar |
| sharper, crisper, harder, geometric | component | `--{c}-radius` | × 0.5 (clamp ≥ 0.125rem) | none |

Worked example: `--btn-radius: 0.375rem` + "softer" → `0.5625rem`.

### Color (theme-layer hue / chroma / lightness)

| Modifiers | Layer | Family | Delta | var-only fallback |
|---|---|---|---|---|
| warmer, cozier, sunnier | theme | `--color-primary` (and `-hover`) | OKLCH `hue` += +8° toward 60° | n/a (theme role) |
| cooler, icier | theme | `--color-primary` (and `-hover`) | OKLCH `hue` += −8° toward 240° | n/a |
| calmer, muted, gentler, restrained | theme | named role (default `--color-primary`) | OKLCH `chroma` × 0.75 | n/a |
| bolder, punchier, more vibrant, livelier | theme | named role | OKLCH `chroma` × 1.25 (gamut clamp) | n/a |
| deeper, richer, darker accent | theme | `--color-primary` (and `-hover`) | OKLCH `lightness` += −0.06 | n/a |
| lighter, paler, washed-out | theme | `--color-primary` (and `-hover`) | OKLCH `lightness` += +0.06 | n/a |
| tone down | theme | named role | OKLCH `chroma` × 0.75 (alias of "calmer") | n/a |

Worked example: `--color-primary: #2563eb` + "warmer" → call
`oklch_shift.py "#2563eb" --hue=8` → `#475ceb`. Apply the same
delta to `--color-primary-hover` (paired-role rule).

Hue blend rules:
- "warmer" rotates toward hue 60° (yellow-orange) with a +8° step. If
  the current hue is already within ±10° of 60°, skip with "already
  warm".
- "cooler" rotates toward hue 240° (blue) with a −8° step. Same
  threshold.

### Spacing

| Modifiers | Layer | Family | Delta | var-only fallback |
|---|---|---|---|---|
| spacious, roomier, airier, breathing | component | `--{c}-padding`, `--{c}-padding-inline`, `--{c}-padding-block`, `--{c}-content-padding`, `--{c}-content-gap`, `--{c}-gap` | × 1.5 | none |
| tighter, denser, compact | component | same as above | × 0.66 | none |

Worked example: `--card-padding: 1rem; --card-content-gap: 1rem` +
"spacious" → both become `1.5rem`.

### Elevation (border + shadow)

| Modifiers | Layer | Family | Delta | var-only fallback |
|---|---|---|---|---|
| elevated, lifted, floating | component | `--{c}-shadow`, `--{c}-radius` | shadow → `stronger` preset; radius += `+0.125rem` | none |
| grounded, planted, weighted | component | `--{c}-shadow`, `--{c}-border-bottom` | shadow → `inset` preset; emphasize border-bottom | none |
| quieter, subtler | component | `--{c}-border`, `--{c}-shadow` | border thinner; shadow → `none` | none |
| louder, prominent, attention-grabbing | component | `--{c}-border`, `--{c}-shadow` | border × 2; shadow → `stronger` preset | none |
| minimal, flat, clean | component | `--{c}-shadow`, `--{c}-border` | shadow → `none`; border → `1px solid` | none |

Shadow preset enumeration (canonical values used by deltas above):

| Preset | Value |
|---|---|
| `none` | `none` |
| `flat` | `0 1px 2px rgba(0,0,0,0.06)` |
| `default` | `0 1px 3px rgba(0,0,0,0.10)` |
| `stronger` | `0 8px 16px rgba(0,0,0,0.12), 0 4px 6px rgba(0,0,0,0.08)` |
| `inset` | `inset 0 1px 2px rgba(0,0,0,0.08)` |

When a modifier maps to a preset, replace the existing
`--{c}-shadow` declaration's RHS with the preset value verbatim. Do
not attempt to interpolate between presets.

### Size — font scale

| Modifiers | Layer | Family | Delta | var-only fallback |
|---|---|---|---|---|
| smaller, tinier | component (button) | `--btn-fs` | swap to next-smaller `--btn-size-*` step | none |
| bigger, larger | component (button) | `--btn-fs` | swap to next-larger `--btn-size-*` step | none |

The button scale ladder is xs → sm → md → lg → xl. Default is `md`.
"Smaller" from `md` → `sm`; from `xs` → halt with "already at
smallest". "Bigger" from `xl` → halt with "already at largest".

Worked example: `--btn-fs: var(--btn-size-md, 0.9375rem)` + "smaller"
→ `--btn-fs: var(--btn-size-sm, 0.8125rem)`. Both the variable
reference and the fallback move together to keep the component
self-contained without a global tokens file.

### Size — width

| Modifiers | Layer | Family | Delta | var-only fallback |
|---|---|---|---|---|
| narrower | component (dialog/input) | `--{c}-width`, `--{c}-max-width` | × 0.75 | none |
| wider | component (dialog/input) | `--{c}-width`, `--{c}-max-width` | × 1.25 | none |

Worked example: `--dialog-width: 32rem` + "narrower" → `24rem`.

### Height

| Modifiers | Layer | Family | Delta | var-only fallback |
|---|---|---|---|---|
| shorter | component (dialog) | `--{c}-max-height` | × 0.75 (clamp ≥ 20vh) | none |
| taller | component (dialog) | `--{c}-max-height` | × 1.25 (clamp ≤ 95vh) | none |

Worked example: `--dialog-max-height: 85vh` + "shorter" → `64vh` (× 0.75 rounded).

## Compound presets

These rows are flagged `preset: true`. Each maps one modifier to
multiple token families. Apply each family delta independently as a
single batch.

| Modifier | Layer | Token-family deltas |
|---|---|---|
| inviting, welcoming | component (button) | `--btn-radius` × 1.5; `--btn-padding-inline` × 1.25 |
| businesslike, formal, conservative | component | `--{c}-radius` × 0.5; `--{c}-shadow` → `flat` preset |
| playful, fun | component | `--{c}-radius` × 2 (clamp ≤ 1rem); `--{c}-padding` × 1.25 |

Worked example: `inviting` button →
`--btn-radius: 0.375rem` becomes `0.5625rem` AND
`--btn-padding-inline: calc(var(--btn-fs, 0.9375rem) * 1.5)` becomes
`calc(var(--btn-fs, 0.9375rem) * 1.875)`. Both edits batch into one
`Edit` pass per the SKILL's D3 rule.

## Var-only fallback table

Some component tokens are pure `var(--color-*, …)` references — they
have no scalar to multiply. When a color-targeting modifier hits one,
the skill auto-routes to the underlying theme role per this table:

| Component token | Routes to theme role |
|---|---|
| `--alert-bg` | `--color-surface` |
| `--alert-color` | `--color-text` |
| `--alert-border` | `--color-border` |
| `--card-bg` | `--color-surface` |
| `--card-color` | `--color-text` |
| `--card-border` | `--color-border` (in border declaration) |
| `--card-footer-bg` | `--color-surface-subtle` |
| `--card-footer-border-top` | `--color-border` |
| `--dialog-bg` | `--color-surface` |
| `--dialog-color` | `--color-text` |
| `--dialog-header-border-bottom` | `--color-border` |
| `--dialog-footer-bg` | `--color-surface-subtle` |
| `--dialog-footer-border-top` | `--color-border` |
| `--input-bg` | `--color-surface` |
| `--input-color` | `--color-text` |
| `--input-border` | `--color-border` (in border declaration) |
| `--input-outline` | `--color-primary` |
| `--input-focus-border` | `--color-primary` |
| `--input-disabled-bg` | `--color-surface-subtle` |
| `--input-placeholder-color` | `--color-text-subtle` |
| `--btn-primary-bg` | `--color-primary` |
| `--btn-primary-color` | `--color-text-inverse` |
| `--btn-hover-bg` | `--color-primary-hover` |
| `--nav-link-color` | `--color-text` |
| `--nav-link-hover-color` | `--color-primary` |
| `--nav-link-active-color` | `--color-primary` |

When auto-routing fires, Step F appends a note: "Tuning
`<component-token>` requires changing `<theme-role>`, which affects
every component using it." This makes the cascade impact explicit so
users can opt out (re-run with explicit `--scope` once that flag
ships in v2).

## Alert severity variants

By default, "calmer alert" / "warmer alert" / etc. tune only the base
alert tokens (`--alert-bg`, `--alert-border`, `--alert-color`,
`--alert-fs`, `--alert-padding`, `--alert-radius`).

The four severity variants — `--alert-info-{bg,border,color}`,
`--alert-success-{bg,border,color}`, `--alert-warning-{bg,border,color}`,
`--alert-error-{bg,border,color}` — stay locked unless the user names
them explicitly. Trigger phrases for variants:

- "calmer success alert" / "warmer error alert" / "bolder warning
  alert" → tune the named single variant.
- "calmer alert variants" / "tune all alert states" → tune all four.

This avoids meaning-loss: a "calm" danger state still needs to read
as urgent.

## Brand-*.css edits

Theme-layer modifiers ("warmer primary", "tone down primary") edit
`light.css` + `dark.css` only by default. Any `brand-*.css` files in
the same directory are **not** touched.

To tune a brand file, the user must name it explicitly:

- "warmer acme brand" → tune `brand-acme.css`
- "tone down acme primary" → tune `brand-acme.css` only
- "deeper accent for acme" → tune `brand-acme.css` only

When brand files are present and the user did not name them, Step F
appends: "Brand `acme` is present and unchanged. To tune it, say
'tune the acme brand'."

## Hue blend constants

The hue rotation modifiers reference these target hues (CSS Color 4
OKLCH degrees):

| Direction | Target hue | Rationale |
|---|---|---|
| warmer | 60° | yellow-orange (sun, fire) |
| cooler | 240° | blue (sky, ice) |

The +8° / −8° step is calibrated to feel perceptually distinct
without overshooting. Three to four "warmer" tunes saturate the move
to the target hue.

## Idempotency tolerance

Step E3 reports "already at target" when the computed value equals
the current value within:

- Hex equality for color values (case-insensitive).
- `±0.0001rem` for rem values.
- `±0.5px` for vh / vw / px values (after rounding to one decimal).
