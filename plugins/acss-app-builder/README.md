# acss-app-builder

Scaffold React apps with the **@fpkit/acss** design system. Takes a developer from an empty Vite+React+TS project to a running app with typed pages, responsive layouts, a validated theme, and accessible forms.

Works with **either** source of fpkit components:

- the `@fpkit/acss` npm package, or
- generated source from the companion [`acss-kit-builder`](../acss-kit-builder/) plugin.

Prefers generated source when both are present.

## Supersedes `fpkit-developer`

This plugin **replaces** the deprecated `fpkit-developer` plugin. If you installed the old one via marketplace, uninstall it first to avoid duplicate skills loading:

```
/plugin uninstall fpkit-developer@shawn-sandy-acss-plugins
```

All composition / extension / a11y workflows from `fpkit-developer` are preserved as sections of the `/app-compose` command in this plugin.

## Prerequisites

- Vite + React + TypeScript project
- `sass` or `sass-embedded` in `devDependencies`
- Claude Code >= v1.0.33

## Installation

### Marketplace install (recommended)

```shell
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-app-builder@shawn-sandy-acss-plugins
```

### Manual install via GitHub clone

```bash
git clone https://github.com/shawn-sandy/acss-plugins.git
mkdir -p ~/.claude/plugins/
cp -r acss-plugins/plugins/acss-app-builder ~/.claude/plugins/
```

For project-level install, substitute `~/.claude/plugins/` with `.claude/plugins/` inside your project.

## Commands

| Command | Purpose |
|---|---|
| `/app-init [--force]` | Bootstrap folders, seed `base.css`, wire imports in the entry file |
| `/app-layout <holy-grail\|sidebar\|centered>` | Generate `AppShell.tsx` + `AppShell.scss` with grid areas |
| `/app-page <template> [name]` | Stamp a page template (`dashboard`, `auth-login`, `auth-signup`, `settings`, `list-detail`, `landing`, `error-404`, `error-500`) |
| `/app-theme <preset> [--mode]` | Generate theme files (`light`, `dark`, `both`, `brand-neutral`, `brand-vibrant`) |
| `/app-form <schema.json> [--name]` | Generate an accessible form from a field schema |
| `/app-pattern <pattern> [--into]` | Insert a common UI pattern (`data-table`, `empty-state`, `loading-skeleton`, `hero`, `pricing-grid`, `toast`) |
| `/app-compose <name>` | Composition / extension workflow (migrated from `fpkit-developer`) |

## Safety contract

Every command:

- **Refuses on a dirty git tree** unless `--force`.
- **Refuses to overwrite existing non-empty files** unless `--force`.
- Mutates entry files only with **sentinel-bounded insertions** (`// @acss-app-builder` markers) so re-runs are idempotent.

## Component source detection

The plugin detects which source to import from on every run:

1. **`generated`** *(preferred)* — `<componentsDir>/ui.tsx` exists locally. Relative imports like `../components/fpkit/button/button`. **Wins on tie** even if `@fpkit/acss` is also installed.
2. **`npm`** *(deprecated as of v0.2.0)* — `@fpkit/acss` in `dependencies`. Imports like `import { Button } from '@fpkit/acss'`.
3. **`none`** — neither present. Command halts with `/kit-add` recommendation.

The components target directory is persisted to `.acss-target.json` at the project root (committed to git) so `/kit-add` and `/app-*` stay in sync.

### `@fpkit/acss` npm path — deprecation

> **Compatibility ceiling:** `@fpkit/acss@6.6.0` (captured at v0.2.0 release).

The npm path is **deprecated as of v0.2.0**. Projects on the npm path keep working through a soft-deprecation window — `detect_component_source.py` continues returning `source: "npm"` and exits 0 — but the JSON output now includes `"deprecated": true` and `"sunsetVersion": "6.6.0"`. Slash commands surface a one-line migration suggestion in chat after generating their artifact:

```
Note: this project still uses the @fpkit/acss npm path (deprecated;
sunset in 6.6.0). Run /kit-add to vendor components.
```

The npm path will be removed in a future major release. To migrate now:

1. Run `/kit-add <component>` (from the companion `acss-kit-builder` plugin) for each component the project uses.
2. The kit-builder generates self-contained `.tsx` + `.scss` files into `<componentsDir>` and writes `.acss-target.json`.
3. Re-run any `/app-*` command and confirm `source: "generated"` (no deprecation flag in the JSON).
4. Remove `@fpkit/acss` from `package.json` once all components have been vendored.

## Form scaffolding (cross-plugin)

`/app-form` delegates to the `acss-kit-builder:component-form` skill — a per-component skill pilot in `acss-kit-builder` v0.2.0. The slash command is the user-facing entry point (and surfaces deprecation nudges); the kit-builder skill owns the form template, field renderers, and accessibility patterns.

Both authoring modes are supported:

- **Natural language** *(preferred)*: `/app-form "signup form with email, password, and a role select"`. The skill derives the field list, asking via `AskUserQuestion` when ambiguous.
- **Legacy JSON schema** *(preserved for backward compatibility)*: `/app-form path/to/schema.json`. Example schema at `assets/forms/schema.example.json`. The shape is documented in `references/forms.md`.

Both modes converge on the same internal field-list contract and produce identical output: a single self-contained `src/forms/<FormName>.tsx` file using `Field`, `Input`, and `Checkbox` from the active component source. See the "Cross-plugin skill invocation" subsection in `skills/acss-app-builder/SKILL.md` for the contract, or [`acss-kit-builder/skills/component-form/SKILL.md`](../acss-kit-builder/skills/component-form/SKILL.md) for the generation logic.

## Plugin contents

```
acss-app-builder/
├── .claude-plugin/plugin.json
├── README.md
├── commands/                       # 7 slash commands
├── skills/acss-app-builder/
│   ├── SKILL.md                    # single top-level skill, sections per command
│   └── references/                 # 12 reference docs (5 copied from fpkit-developer, 7 new)
├── scripts/                        # Python helpers (Vite + source detection, theme validator)
└── assets/                         # layouts, pages, themes, forms, patterns templates
```

## Verification

After any command runs:

```bash
npx tsc --noEmit
npx eslint .
npx vitest run
```

Plus an axe-core a11y check on generated pages:

```bash
npx vite build && npx vite preview &
npx @axe-core/cli http://localhost:4173/<route>
```

## License

MIT
