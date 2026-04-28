# Naming convention

Class names mirror **fpkit/acss upstream** (`@fpkit/acss@6.5.0`) verbatim where present, and follow the same kebab-case pattern for families this plugin extends beyond upstream. See [ATTRIBUTION.md](../../../ATTRIBUTION.md) for the upstream/extended split.

## Selector form

```text
.<prefix>\:<name><pseudo?>
```

- **`<prefix>`** — *optional*. One of `sm`, `md`, `lg`, `xl`, `print`. The `:` separator is escaped to `\:` in CSS but written as `:` in JSX (`<div className="sm:hide">…`).
- **`<name>`** — kebab-case; lowercase letters, digits, and hyphens. Starts with a letter. Examples: `bg-primary`, `mt-4`, `flex-col-reverse`, `grid-cols-12`.
- **`<pseudo>`** — *optional*. Any standard CSS pseudo-class (`:focus`, `:focus-within`, `:hover`). Used by `sr-only-focusable`.

The validator (`scripts/validate_utilities.py`) enforces this form. PascalCase, snake_case, and unrecognized prefixes (`xxl:`, `desktop:`) all fail.

## Family-name conventions

| Family | Prefix | Property |
|---|---|---|
| `color-bg` | `bg-` | `background-color` |
| `color-text` | `text-` | `color` (when value is a role) |
| `color-border` | `border-` | `border-color` |
| `spacing` | `m-/mt-/mb-/ml-/mr-/mx-/my-/p-/pt-/pb-/pl-/pr-/px-/py-/gap-` | `margin*`, `padding*`, `gap` |
| `display` | `hide`, `show`, `invisible`, `sr-only`, `sr-only-focusable`, `print:hide` | `display`, `visibility` |
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

- `.hide`, `.show`, `.invisible`, all `.<bp>:hide` variants, `.print:hide`

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
