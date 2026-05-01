# acss-utilities

A Claude Code plugin that adds a Tailwind-style atomic CSS layer to fpkit/acss projects. Generates a single `utilities.css` (committed bundle) and a `token-bridge.css` that aliases the [`acss-kit`](../acss-kit) plugin's OKLCH color roles to the fpkit-style names utility classes reference.

For a guided walkthrough, mental model, command reference, recipes, troubleshooting, and maintainer architecture, see the [developer guide in `docs/`](docs/README.md).

## Pairs with `acss-kit`

This plugin is designed to sit alongside `acss-kit`. `acss-kit` owns components and themes; `acss-utilities` owns the utility-class layer. They are decoupled — install one, both, or use `acss-utilities` standalone with a hand-written theme.

| Plugin | Owns |
|---|---|
| [`acss-kit`](../acss-kit) | Components, themes (light/dark/brand), OKLCH role catalogue |
| `acss-utilities` (this) | Utility classes (`.bg-primary`, `.mt-4`, `.sm-hide`), token-bridge |

## Why utility classes

Components in `acss-kit` already get scoped CSS variables and `data-*` variants. Utility classes complement that with **layout glue** (spacing between cards, responsive show/hide, quick color overrides) without authoring new SCSS files. The plugin's class names are patterned on fpkit upstream so behavior is portable to other fpkit projects without a runtime dependency.

## Installation

```shell
/plugin marketplace add shawn-sandy/agentic-acss-plugins
/plugin install acss-utilities@shawn-sandy-agentic-acss-plugins
```

If you also want `acss-kit`:

```shell
/plugin install acss-kit@shawn-sandy-agentic-acss-plugins
```

## Quick start

```shell
/utility-add
```

Auto-detects your React project root, copies `utilities.css` into `src/styles/utilities.css`, and copies `token-bridge.css` alongside. Add the imports to your app entry:

```ts
import "./styles/token-bridge.css";   // first — defines fpkit-style aliases
import "./styles/utilities.css";       // then — utility classes consume them
```

If `acss-kit` is also installed, the bridge will resolve `--color-error`, `--color-primary-light`, etc. against acss-kit's `--color-danger`, `--color-primary`, … in both light and dark modes.

## Commands

### `/utility-add [--target=<dir>] [--families=<list>] [--no-bridge]`

Copy `utilities.css` (and `token-bridge.css` unless `--no-bridge`) into the target. With `--families=color-bg,spacing` only those family partials are copied (still concatenated into a single file). Family names match `assets/utilities.tokens.json#families` (`color-bg`, `color-text`, `color-border`, `spacing`, `display`, `flex`, `grid`, `type`, `radius`, `shadow`, `position`, `z-index`).

```shell
/utility-add
/utility-add --target=apps/web/src/styles
/utility-add --families=color-bg,color-text,spacing,display
/utility-add --no-bridge   # using your own theme without acss-kit
```

### `/utility-list [family]`

Read-only catalogue. No-arg lists every family; pass a family name to print every class in that family with the CSS custom property it references.

```shell
/utility-list
/utility-list color-bg
/utility-list spacing
```

### `/utility-tune <natural-language>`

Adjust the spacing baseline, breakpoints, or family list via natural language. Edits `assets/utilities.tokens.json`, regenerates the bundle, runs the validator.

```shell
/utility-tune use a 4px spacing baseline
/utility-tune add an xs breakpoint at 20rem
/utility-tune disable shadow utilities
```

### `/utility-bridge [--theme=<file>]`

Regenerate `token-bridge.css` against your active acss-kit theme. Always emits both `:root` and `[data-theme="dark"]` blocks so utility colors resolve correctly in dark mode.

```shell
/utility-bridge                              # uses src/styles/theme/light.css + dark.css
/utility-bridge --theme=apps/web/src/styles/theme/light.css
```

## Utility families (v1)

Mirroring fpkit upstream where present, plus standard atomic-CSS additions (see [ATTRIBUTION.md](./ATTRIBUTION.md) for the upstream-vs-extended split):

| Family | Class examples | Responsive |
|---|---|---|
| `color-bg` | `.bg-primary`, `.bg-success`, `.bg-error`, `.bg-surface`, `.bg-transparent` | no |
| `color-text` | `.text-primary`, `.text-error`, `.text-muted` | no |
| `color-border` | `.border-primary`, `.border-error`, `.border-muted` | no |
| `display` | `.hide`, `.show`, `.invisible`, `.sr-only`, `.sr-only-focusable`, `.print-hide` | yes |
| `spacing` | `.m-4`, `.mt-2`, `.px-6`, `.gap-3` | yes |
| `flex` | `.flex`, `.flex-col`, `.justify-center`, `.items-center` | yes |
| `grid` | `.grid`, `.grid-cols-2`, `.grid-cols-12` | yes |
| `type` | `.text-xs`, `.text-base`, `.text-lg`, `.font-bold` | no |
| `radius` | `.rounded-sm`, `.rounded-md`, `.rounded-lg`, `.rounded-full` | no |
| `shadow` | `.shadow-sm`, `.shadow-md`, `.shadow-lg` | no |
| `position` | `.relative`, `.absolute`, `.fixed`, `.sticky` | no |
| `z-index` | `.z-10`, `.z-20`, `.z-50`, `.z-auto` | no |

Responsive variants use a plain hyphen prefix — `.sm-hide`, `.md-p-6`, `.lg-flex-row`. No CSS escaping needed in the stylesheet or JSX `className` strings. Breakpoints: `sm: 30rem`, `md: 48rem`, `lg: 62rem`, `xl: 80rem`.

### Responsive variants

This plugin diverges from fpkit upstream class naming: instead of the escaped-colon form (`.sm\:hide` / `className="sm:hide"`), all responsive variants use a single hyphen separator (`.sm-hide` / `className="sm-hide"`). Token values, breakpoint widths, and media-query range syntax still mirror fpkit.

**Migrating from 0.1.0:** search-and-replace in JSX `className` strings and CSS `@apply` directives — `sm:` → `sm-`, `md:` → `md-`, `lg:` → `lg-`, `xl:` → `xl-`, `print:` → `print-`. Use `scripts/migrate_classnames.py` for an automated dry-run.

## Token bridge

`utilities.css` references fpkit-style token names (`--color-error`, `--color-primary-light`, `--color-success-bg`). `acss-kit`'s role catalogue uses different names (`--color-danger`, no `-light` or `-bg` variants). `token-bridge.css` aliases between them:

```css
:root {
  --color-error: var(--color-danger, #dc2626);
  --color-error-bg: color-mix(in oklch, var(--color-danger, #dc2626) 12%, var(--color-background, #ffffff));
  --color-primary-light: color-mix(in oklch, var(--color-primary, #2563eb) 80%, white);
}
[data-theme="dark"] {
  --color-error: var(--color-danger, #f87171);
  --color-error-bg: color-mix(in oklch, var(--color-danger, #f87171) 18%, var(--color-background, #0f172a));
  --color-primary-light: color-mix(in oklch, var(--color-primary, #7dd3fc) 70%, black);
}
```

The full mapping is in [`skills/utilities/references/token-bridge.md`](skills/utilities/references/token-bridge.md). The validator enforces that every alias defined in `:root` also appears in `[data-theme="dark"]`.

## Plugin structure

```
plugins/acss-utilities/
├── .claude-plugin/plugin.json
├── README.md
├── CHANGELOG.md
├── ATTRIBUTION.md
├── commands/
│   ├── utility-add.md
│   ├── utility-list.md
│   ├── utility-tune.md
│   └── utility-bridge.md
├── skills/utilities/
│   ├── SKILL.md
│   └── references/
│       ├── utility-catalogue.md
│       ├── naming-convention.md
│       ├── breakpoints.md
│       └── token-bridge.md
├── scripts/
│   ├── generate_utilities.py
│   ├── validate_utilities.py
│   └── detect_utility_target.py        # stack detection + entrypoint verification delegate to acss-kit's
│                                        #   detect_stack.py and verify_integration.py at runtime
└── assets/
    ├── utilities.css                    # committed bundle
    ├── utilities/                       # per-family partials
    ├── token-bridge.css
    └── utilities.tokens.json            # source-of-truth
```

## What this plugin is **not**

- Not a component generator (`acss-kit` owns components).
- Not a theme generator (`acss-kit` owns themes; this plugin only consumes them via the bridge).
- Not a CSS framework with a JS runtime — it ships a CSS file and a bridge. No React components.
- Not a JIT/purge tool. v1 emits the full bundle; scan-and-emit is deferred to v2.

## Verification

```sh
tests/run.sh
```

Runs the shared structural-validation gate plus two `acss-utilities`-specific steps: the validator over `plugins/acss-utilities/assets/` (selector grammar, `var()` fallbacks, bridge dark-mode parity, bundle-size budget) and an idempotency check that regenerates the bundle from `utilities.tokens.json` and diffs against the committed copy. Bad-fixture self-tests are not yet wired in.

## License

MIT. See [ATTRIBUTION.md](./ATTRIBUTION.md) for upstream credits.
