# Utility catalogue

Every family the plugin emits in v1, every class within it, and the CSS custom property the class references. The canonical source-of-truth is [`assets/utilities.tokens.json`](../../../assets/utilities.tokens.json); this document mirrors it for human review.

## Family inventory

| Family | Responsive | Class count* | Token namespace |
|---|---|---|---|
| `color-bg` | no | 16 (11 roles + 4 `-subtle` + `-transparent`) | `--color-*`, `--color-*-bg` |
| `color-text` | no | 11 | `--color-*`, `--color-text-*` |
| `color-border` | no | 11 | `--color-*` |
| `spacing` | yes (sm/md/lg/xl) | 210 base + 210 × 4 bps = 1050 | none — literal rem values |
| `display` | yes (sm/md/lg/xl/print) | 3 responsive base (`hide`/`show`/`invisible`) + 3 × 4 bps + `print-hide` + sr-only ×2 = 18 | none |
| `flex` | yes (sm/md/lg/xl) | 21 base × 5 = 105 | none |
| `grid` | yes (sm/md/lg/xl) | 20 base × 5 = 100 | none |
| `type` | no | 19 | none — literal values from `tokens.type` |
| `radius` | no | 7 (incl. bare `.rounded`) | none |
| `shadow` | no | 6 (incl. bare `.shadow`) | none |
| `position` | no | 5 | none |
| `z-index` | no | 7 | none |

\* Approximate; exact counts depend on `utilities.tokens.json#families.<f>.enabled` and `responsive`.

## color-bg

Every class sets `background-color`. Roles map to `tokens.colorRoles[<name>]`; `-subtle` variants map to `tokens.stateBg[<name>]`.

| Class | Sets | Reads |
|---|---|---|
| `.bg-primary` | background-color | `var(--color-primary, transparent)` |
| `.bg-primary-light` | background-color | `var(--color-primary-light, transparent)` |
| `.bg-secondary` | background-color | `var(--color-secondary, transparent)` |
| `.bg-success` | background-color | `var(--color-success, transparent)` |
| `.bg-error` | background-color | `var(--color-error, transparent)` |
| `.bg-warning` | background-color | `var(--color-warning, transparent)` |
| `.bg-info` | background-color | `var(--color-info, transparent)` |
| `.bg-text` | background-color | `var(--color-text, transparent)` |
| `.bg-muted` | background-color | `var(--color-text-muted, transparent)` |
| `.bg-surface` | background-color | `var(--color-surface, transparent)` |
| `.bg-surface-secondary` | background-color | `var(--color-surface-secondary, transparent)` |
| `.bg-success-subtle` | background-color | `var(--color-success-bg, transparent)` |
| `.bg-error-subtle` | background-color | `var(--color-error-bg, transparent)` |
| `.bg-warning-subtle` | background-color | `var(--color-warning-bg, transparent)` |
| `.bg-info-subtle` | background-color | `var(--color-info-bg, transparent)` |
| `.bg-transparent` | background-color | literal `transparent` |

`--color-error`, `--color-error-bg`, `--color-primary-light`, etc. are not present in acss-kit's role catalogue. The plugin's [`token-bridge.css`](../../../assets/token-bridge.css) aliases them to acss-kit's `--color-danger`, `--color-primary`, etc. — see [`token-bridge.md`](token-bridge.md).

## color-text

Every class sets `color`. Same role list as `color-bg` (without `-subtle` variants).

| Class | Reads |
|---|---|
| `.text-primary` … `.text-surface-secondary` | `var(--color-{role}, currentColor)` |

## color-border

Every class sets `border-color`. Same role list.

| Class | Reads |
|---|---|
| `.border-primary` … `.border-surface-secondary` | `var(--color-{role}, currentColor)` |

## spacing

Generated from `tokens.spacing.{baseline, scale, properties}`. Each (property, scale-step) pair becomes a class.

- **Properties**: `m`, `mt`, `mb`, `ml`, `mr`, `mx`, `my`, `p`, `pt`, `pb`, `pl`, `pr`, `px`, `py`, `gap`
- **Scale**: `[0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32]`
- **Baseline**: `0.25rem` (so `.m-4 = 1rem`, `.p-8 = 2rem`)
- **Responsive**: yes — every class has `.sm-`, `.md-`, `.lg-`, `.xl-` variants

Directional utilities emit **CSS logical properties** so spacing follows the document's writing mode (LTR/RTL, vertical scripts). Class names are unchanged from earlier releases — the `t`/`b`/`l`/`r`/`x`/`y` prefixes are kept for familiarity. In the default LTR top-to-bottom mode they map 1:1 to the physical sides, so most consumers see no rendering difference. **In RTL or vertical writing modes the rendered side flips** (e.g. `ml-*` resolves to `margin-inline-start`, which is the right side under `dir="rtl"`); audit any markup that previously relied on physical-side semantics in those contexts.

| Prefix | CSS property emitted | LTR equivalent |
|---|---|---|
| `mt` / `pt` | `margin-block-start` / `padding-block-start` | top |
| `mb` / `pb` | `margin-block-end` / `padding-block-end` | bottom |
| `ml` / `pl` | `margin-inline-start` / `padding-inline-start` | left |
| `mr` / `pr` | `margin-inline-end` / `padding-inline-end` | right |
| `mx` / `px` | `margin-inline` / `padding-inline` | left + right |
| `my` / `py` | `margin-block` / `padding-block` | top + bottom |
| `m` / `p` / `gap` | `margin` / `padding` / `gap` (already side-agnostic) | all sides |

Examples:

| Class | Sets |
|---|---|
| `.m-0` | `margin: 0` |
| `.m-4` | `margin: 1rem` |
| `.mt-2` | `margin-block-start: 0.5rem` |
| `.px-6` | `padding-inline: 1.5rem` |
| `.gap-3` | `gap: 0.75rem` |
| `.sm-p-4` | wrapped in `@media (width >= 30rem)` |

## display

Layout / visibility primitives.

| Class | Sets | Note |
|---|---|---|
| `.hide` | `display: none !important` | wins over component styles by design |
| `.show` | `display: revert !important` | resets `.hide` |
| `.invisible` | `visibility: hidden !important` | preserves layout |
| `.sr-only` | absolute clip rect | screen-reader-only utility |
| `.sr-only-focusable` | absolute clip rect, becomes static on focus | skip-link pattern |
| `.print-hide` | `display: none !important` inside `@media print` | print-specific |
| `.sm-hide` etc. | `display: none !important` inside `@media (width >= …)` | responsive |

`.sr-only` and `.sr-only-focusable` are not responsive — they're accessibility primitives that should always be active regardless of viewport.

## flex

| Class | Sets |
|---|---|
| `.flex`, `.inline-flex` | `display: flex` / `inline-flex` |
| `.flex-row`, `.flex-row-reverse`, `.flex-col`, `.flex-col-reverse` | `flex-direction: …` |
| `.flex-wrap`, `.flex-nowrap` | `flex-wrap: …` |
| `.flex-1` | `flex: 1 1 0%` |
| `.flex-auto` | `flex: 1 1 auto` |
| `.flex-none` | `flex: none` |
| `.justify-start/end/center/between/around` | `justify-content: …` |
| `.items-start/end/center/baseline/stretch` | `align-items: …` |

All have responsive variants.

## grid

| Class | Sets |
|---|---|
| `.grid`, `.inline-grid` | `display: grid` / `inline-grid` |
| `.grid-cols-1` … `.grid-cols-12` | `grid-template-columns: repeat(N, minmax(0, 1fr))` |
| `.grid-rows-1` … `.grid-rows-6` | `grid-template-rows: repeat(N, minmax(0, 1fr))` |

All have responsive variants.

## type

| Class | Sets |
|---|---|
| `.text-xs/sm/base/lg/xl/2xl/3xl/4xl` | `font-size: <size>` |
| `.font-normal/medium/semibold/bold` | `font-weight: <400-700>` |
| `.leading-tight/normal/loose` | `line-height: <ratio>` |
| `.text-left/center/right/justify` | `text-align: …` |

Note: `.text-{role}` (color) and `.text-{size}` (size) share the `.text-` prefix but resolve different CSS properties. fpkit upstream uses the same pattern; the validator allows both since selector parsing only checks form.

## radius

| Class | Sets |
|---|---|
| `.rounded` | `border-radius: 0.375rem` (alias of `rounded-md`) |
| `.rounded-none/sm/md/lg/xl/full` | `border-radius: <value>` |

## shadow

| Class | Sets |
|---|---|
| `.shadow` | `box-shadow: <md value>` (alias of `shadow-md`) |
| `.shadow-none/sm/md/lg/xl` | `box-shadow: <value>` |

## position

| Class | Sets |
|---|---|
| `.static`, `.relative`, `.absolute`, `.fixed`, `.sticky` | `position: <value>` |

## z-index

| Class | Sets |
|---|---|
| `.z-0`, `.z-10`, `.z-20`, `.z-30`, `.z-40`, `.z-50`, `.z-auto` | `z-index: <value>` |

## Adding a family

See [`.claude/skills/utility-author/SKILL.md`](../../../../../.claude/skills/utility-author/SKILL.md) for the maintainer workflow. In short: edit `tokens.families`, register an emitter in `generate_utilities.py`, regenerate, validate.
