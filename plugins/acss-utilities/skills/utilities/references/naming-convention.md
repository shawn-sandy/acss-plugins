# Naming convention

Class names use kebab-case throughout. Responsive variants use a plain hyphen separator — no CSS-escape boilerplate in source or JSX. Token values, breakpoint widths, and media-query syntax still mirror fpkit upstream; class-name form is a deliberate divergence. See [ATTRIBUTION.md](../../../ATTRIBUTION.md) for the upstream/extended split.

## Selector form

```text
.<name><pseudo?>              (base)
.<prefix>-<name><pseudo?>     (responsive variant)
```

- **`<prefix>`** — *optional*. One of `sm`, `md`, `lg`, `xl`, `print`. Followed by a literal hyphen. Examples: `sm-hide`, `md-p-6`, `xl-flex-row`.
- **`<name>`** — kebab-case; lowercase letters, digits, and hyphens. Starts with a letter. Examples: `bg-primary`, `mt-4`, `flex-col-reverse`, `grid-cols-12`.
- **`<pseudo>`** — *optional*. Any standard CSS pseudo-class (`:focus`, `:focus-within`, `:hover`). Used by `sr-only-focusable`.

The validator (`scripts/validate_utilities.py`) enforces this form. PascalCase, snake_case, and old colon-separator syntax (`sm:hide`, `md\:p-6`) all fail.

### Prefix-allowlist rule

The strings `sm`, `md`, `lg`, `xl`, and `print` are **reserved** as prefix namespaces. The validator enforces two structural properties:

1. **Context constraint** — any selector whose body starts with `<prefix>-` is only valid inside the matching `@media` block (`@media (width >= …)` for viewport prefixes; `@media print` for `print-`). A selector like `.sm-foo` at the top level fails with "collides with breakpoint prefix — rename".
2. **Base-class-existence** — for every responsive variant `.sm-foo`, a base class `.foo` must exist in the same file. This prevents generator bugs from silently emitting variants with no base to fall back to.

**Worked example:** adding a top-level `.sm-card` class (perhaps to mean "small card") is invalid — rename it to `.card-sm` or `.card-compact` to avoid the namespace collision.

## Family-name conventions

| Family | Prefix | Property |
|---|---|---|
| `color-bg` | `bg-` | `background-color` |
| `color-text` | `text-` | `color` (when value is a role) |
| `color-border` | `border-` | `border-color` |
| `spacing` | `m-/mt-/mb-/ml-/mr-/mx-/my-/p-/pt-/pb-/pl-/pr-/px-/py-/gap-` | `margin*`, `padding*`, `gap` |
| `display` | `hide`, `show`, `invisible`, `sr-only`, `sr-only-focusable`, `print-hide` | `display`, `visibility` |
| `flex` | `flex`, `flex-*`, `justify-*`, `items-*` | `display`, `flex-*`, `justify-content`, `align-items` |
| `grid` | `grid`, `grid-cols-*`, `grid-rows-*`, `inline-grid` | `display`, `grid-template-*` |
| `type` | `text-{xs,sm,…}`, `font-*`, `leading-*`, `text-{left,center,right,justify}` | `font-size`, `font-weight`, `line-height`, `text-align` |
| `radius` | `rounded`, `rounded-*` | `border-radius` |
| `shadow` | `shadow`, `shadow-*` | `box-shadow` |
| `position` | `static`/`relative`/`absolute`/`fixed`/`sticky` | `position` |
| `z-index` | `z-{0,10,20,30,40,50,auto}` | `z-index` |

## `text-` prefix collision

Both color and size use `.text-`:

- `.text-primary`, `.text-error` — color (resolves to `var(--color-{role})`)
- `.text-xs`, `.text-sm`, `.text-base`, `.text-lg` — font-size (literal value)

This collision is intentional — fpkit and Tailwind both ship it. The names don't overlap in practice (`primary`/`error`/etc. vs `xs`/`sm`/`base`/etc.), and the family-level partition keeps them in separate per-family files.

## `!important` policy

Only **display / visibility** utilities use `!important`:

- `.hide`, `.show`, `.invisible`, all `.<bp>-hide` variants, `.print-hide`

Rationale: utilities that change layout intent (showing or hiding a block) must defeat any component-level `display:` rules. Color / spacing / typography utilities are **composable** and should not use `!important` — they layer on top of component CSS through the cascade.

## CSS custom property fallbacks

Every `var()` reference inside a utility class **must include a fallback**. The validator enforces this contract:

```css
/* OK */
.bg-primary { background-color: var(--color-primary, transparent); }

/* Rejected — no fallback */
.bg-primary { background-color: var(--color-primary); }
```

The fallback's purpose: utility classes should produce a sensible result even when the host project's theme CSS hasn't loaded yet, or when running outside acss-kit. The validator's same-shape check is shared with `acss-kit`'s `validate_components.py` (the SCSS contract harness).

## Source-of-truth

Class generation is fully driven by `assets/utilities.tokens.json`. Naming changes therefore have two surfaces:

1. **Token data** — adding a new role/value/family in `tokens.json`.
2. **Emitter logic** — `generate_utilities.py` decides how a token becomes a class name. New families need a new emitter function and an entry in `EMITTERS` / `FAMILY_ORDER`.

For maintainer workflows, see [`.claude/skills/utility-author/`](../../../../../.claude/skills/utility-author/SKILL.md).
