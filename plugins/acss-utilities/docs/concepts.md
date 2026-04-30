# acss-utilities — Core Concepts

This page covers the mental model you need before running `/utility-add`. Understanding these ideas will help you reason about what gets shipped into your project, why the bundle looks the way it does, and what to do when a class does not resolve the way you expect.

## Why a committed bundle instead of a build step

The plugin ships a hand-tested `utilities.css` (the full atomic suite) plus per-family partials under `assets/utilities/`. There is **no JIT scanner, no purge step, and no JS runtime**. `/utility-add` copies pre-built CSS into your project; you ship that file as-is. The trade-off: the bundle is ~58 KB unminified out of the box. If you only need a subset, pass `--families=color-bg,spacing,display` to filter at copy-time.

The committed bundle is regeneratable from `assets/utilities.tokens.json` via `scripts/generate_utilities.py`, and `tests/run.sh` enforces byte-for-byte idempotency between the two. Edits to tokens always go through the generator; no one hand-writes the bundle.

## kebab-case selectors, no prefix

Class names mirror fpkit upstream verbatim — kebab-case, no library prefix, no hashing:

```html
<div class="bg-primary p-4 rounded-md">…</div>
```

The validator (`scripts/validate_utilities.py`) enforces this with a single regex: `\.[a-z][a-z0-9-]*` with an optional `\<prefix>:` escape (see [breakpoints](#responsive-variants-and-the-escaped-colon)) and an optional pseudo-class. PascalCase, underscores, and library-style prefixes (`acss-`, `u-`) all fail validation.

See [`references/naming-convention.md`](../skills/utilities/references/naming-convention.md) for the full grammar.

## Mandatory `var()` fallbacks

Every CSS custom property reference in a utility class **must** include a hardcoded fallback:

```css
.bg-primary { background-color: var(--color-primary, transparent); }   /* correct */
.bg-primary { background-color: var(--color-primary); }                /* wrong */
```

This rule comes from [`scss-conventions.md`](../../../.claude/rules/scss-conventions.md), and the validator checks every emitted file. Fallbacks let utility classes work in isolation — drop the bundle into a project with no theme and `.bg-primary` still renders something visible (`transparent` for color-bg, `currentColor` for color-text and color-border).

When `acss-kit` or another theme is loaded, the variable resolves to the theme's value and the fallback is shadowed.

## Responsive variants and the escaped colon

Five prefixes ship by default: `sm`, `md`, `lg`, `xl`, `print`. The breakpoint widths come from `assets/utilities.tokens.json#breakpoints`:

| Prefix | Width | Generated rule |
|---|---|---|
| `sm` | 30rem | `@media (width >= 30rem) { .sm\:hide { … } }` |
| `md` | 48rem | `@media (width >= 48rem)` |
| `lg` | 62rem | `@media (width >= 62rem)` |
| `xl` | 80rem | `@media (width >= 80rem)` |
| `print` | — | `@media print { .print-hide { … } }` (only `hide` is emitted) |

Responsive class names use a plain hyphen prefix — no escaping in the stylesheet or in JSX:

```tsx
<div className="hide md-show lg-hide">…</div>
```

See [`references/breakpoints.md`](../skills/utilities/references/breakpoints.md) for the full breakpoint table and class-naming rules.

Not every family is responsive. Color, type, radius, shadow, position, and z-index emit only base classes. Spacing, display, flex, and grid emit the full `sm-/md-/lg-/xl-` set. The `families.<name>.responsive` flag in the tokens file controls this.

## `!important` is reserved for display and visibility

Utility classes generally compose with component styles. They do **not** stamp `!important` on every property, because the user should be able to override `.bg-primary` with a more specific component rule.

The exceptions are `display`, `visibility`, and the `print-hide` / `sm-hide` family — these need to win over any positioning or layout rule that the component author may have set. So:

```css
.hide { display: none !important; }
.invisible { visibility: hidden !important; }
.bg-primary { background-color: var(--color-primary, transparent); }   /* no !important */
```

This matches fpkit upstream policy and is documented in [`references/naming-convention.md`](../skills/utilities/references/naming-convention.md).

## The token bridge

Utility classes reference fpkit-style token names (`--color-error`, `--color-error-bg`, `--color-primary-light`). `acss-kit` defines roles under different names (`--color-danger`, no `-bg` variants, no `-light` variants). The bridge — `assets/token-bridge.css` — closes the gap:

```css
:root {
  --color-error:        var(--color-danger, #dc2626);
  --color-error-bg:     color-mix(in oklch, var(--color-danger, #dc2626) 12%, var(--color-background, #ffffff));
  --color-primary-light: color-mix(in oklch, var(--color-primary, #2563eb) 80%, white);
}
[data-theme="dark"] {
  --color-error:        var(--color-danger, #f87171);
  --color-error-bg:     color-mix(in oklch, var(--color-danger, #f87171) 18%, var(--color-background, #0f172a));
  --color-primary-light: color-mix(in oklch, var(--color-primary, #7dd3fc) 70%, black);
}
```

You import it **before** `utilities.css`, so the aliases are defined when utility classes resolve them:

```ts
import "./styles/token-bridge.css";   // first — defines aliases
import "./styles/utilities.css";       // then — utility classes consume them
```

If you don't run `acss-kit`, the bridge's hex fallbacks resolve standalone — every utility still renders. See [`references/token-bridge.md`](../skills/utilities/references/token-bridge.md) for the full mapping.

## Dark-mode parity is enforced

Every alias defined in `:root` **must** also be defined in `[data-theme="dark"]`. Without the second block, every `.bg-error` / `.text-error` / `.border-error` resolves to the light-mode fallback even when the page is in dark mode. The validator's bridge mode flags any missing alias by name:

```text
token-bridge.css: bridge dark-mode parity gap — declared in :root
but missing in [data-theme="dark"]: --color-error, --color-success-bg
```

`/utility-bridge` always emits both blocks. If you hand-edit the file, run `validate_utilities.py path/to/token-bridge.css` to confirm parity before committing.

## Bundle-size budget

`assets/utilities.tokens.json#bundleSizeBudgetKb` (default 80) is a soft ceiling. The validator reads it from the tokens file when no `--max-kb` flag is passed:

```text
utilities.css: bundle size 84520 bytes exceeds budget 80 KB (81920 bytes)
```

If you grow a family or add a new one, raise the budget in the tokens file or remove unused families via `--families=`. The CLI flag (`--max-kb 120`) overrides the tokens value when you need a one-off check.

## Generation flow at a glance

```text
utilities.tokens.json  ──▶  generate_utilities.py  ──▶  utilities/<family>.css
                                                  └──▶  utilities.css (concatenated bundle)

utilities.css         ──▶  validate_utilities.py  ──▶  reasons array (exit 0/1)
token-bridge.css      ──▶  validate_utilities.py  ──▶  reasons array (exit 0/1)
```

`/utility-tune` runs the generator and the validator in sequence, reverting tokens edits if the validator complains. `/utility-bridge` reads your acss-kit theme and writes a new `token-bridge.css`, then validates it for parity.
