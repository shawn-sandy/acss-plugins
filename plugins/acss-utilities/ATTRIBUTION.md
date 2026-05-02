# Attribution

This plugin's class-naming conventions, family inventory, and breakpoint values are patterned on the upstream [`fpkit/acss`](https://github.com/shawn-sandy/acss) project. fpkit ships under MIT, as does this plugin.

## Upstream pin

The plugin tracks **`@fpkit/acss@6.5.0`** (the same pin used by `acss-kit`'s component-author skill). Re-verification after upstream tag bumps is a maintainer responsibility — see the deferred `utility-sync` skill noted in the v1 plan.

## What we mirror verbatim

- **Class names** for color (`.bg-*`, `.text-*`, `.border-*`), display (`.hide`, `.show`, `.invisible`, `.sr-only`, `.sr-only-focusable`), and responsive variant base names (`hide`, `show`, `invisible`).
- **Breakpoints**: `sm: 30rem`, `md: 48rem`, `lg: 62rem`, `xl: 80rem`. Identical to `_display.scss` in upstream.
- **Modern range-query syntax** (`@media (width >= …)`) matching fpkit's generated CSS.
- **`!important` policy** for display/visibility utilities (matches `_display.scss`).

**Class-name divergence (intentional):** fpkit upstream uses escaped-colon responsive variants (`.sm\:hide` in CSS, `sm:hide` in JSX). This plugin uses plain hyphen-prefix variants (`.sm-hide` in both). Token values, breakpoints, and media-query syntax remain aligned with fpkit; only the responsive class-name separator differs.

Per-family upstream sources (when applicable):

| Family | Upstream file |
|---|---|
| `color-bg` | [`packages/fpkit/src/sass/utilities/_color-bg.scss`](https://github.com/shawn-sandy/acss/blob/v6.5.0/packages/fpkit/src/sass/utilities/_color-bg.scss) |
| `color-text` | [`packages/fpkit/src/sass/utilities/_color-text.scss`](https://github.com/shawn-sandy/acss/blob/v6.5.0/packages/fpkit/src/sass/utilities/_color-text.scss) |
| `color-border` | [`packages/fpkit/src/sass/utilities/_color-border.scss`](https://github.com/shawn-sandy/acss/blob/v6.5.0/packages/fpkit/src/sass/utilities/_color-border.scss) |
| `display` | [`packages/fpkit/src/sass/utilities/_display.scss`](https://github.com/shawn-sandy/acss/blob/v6.5.0/packages/fpkit/src/sass/utilities/_display.scss) |
| `flex` (sibling) | [`packages/fpkit/src/sass/_layout.scss`](https://github.com/shawn-sandy/acss/blob/v6.5.0/packages/fpkit/src/sass/_layout.scss) |
| `grid` (sibling) | [`packages/fpkit/src/sass/_grid.scss`](https://github.com/shawn-sandy/acss/blob/v6.5.0/packages/fpkit/src/sass/_grid.scss) |
| `type` (sibling) | [`packages/fpkit/src/sass/_type.scss`](https://github.com/shawn-sandy/acss/blob/v6.5.0/packages/fpkit/src/sass/_type.scss) |

## What this plugin extends beyond fpkit

These families are not yet present in fpkit upstream and are added by this plugin in line with conventional atomic-CSS naming. They follow the same kebab-case, no-prefix style and the same responsive-variant syntax.

- `spacing` — `m`, `mt/mb/ml/mr/mx/my`, `p`, `pt/pb/pl/pr/px/py`, `gap`. Driven by `utilities.tokens.json#spacing.scale`.
- `radius` — `rounded`, `rounded-sm`, `rounded-md`, `rounded-lg`, `rounded-full`.
- `shadow` — `shadow-sm`, `shadow-md`, `shadow-lg`, `shadow-xl`, `shadow-none`.
- `position` — `static`, `relative`, `absolute`, `fixed`, `sticky`.
- `z-index` — `z-0`, `z-10`, `z-20`, `z-30`, `z-40`, `z-50`, `z-auto`.

When fpkit upstream adds an equivalent family, this plugin's classes will be reconciled (the v1 deferred `utility-sync` skill will handle the diff).

## Token-naming bridge

fpkit upstream references token names that are not present in `acss-kit`'s role catalogue (e.g. `--color-error`, `--color-error-bg`, `--color-primary-light`). The plugin ships `assets/token-bridge.css` to alias `acss-kit`'s names (`--color-danger`, `--color-primary`, etc.) to the fpkit-style names that the utility classes reference, in both `:root` and `[data-theme="dark"]`. See [`skills/utilities/references/token-bridge.md`](skills/utilities/references/token-bridge.md) for the full mapping.

## License

MIT — same as `acss-kit` and fpkit upstream.
