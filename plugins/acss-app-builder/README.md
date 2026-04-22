# acss-app-builder

Scaffold React apps with the **@fpkit/acss** design system. Takes a developer from an empty Vite+React+TS project to a running app with typed pages, responsive layouts, a validated theme, and accessible forms.

Works with **either** source of fpkit components:

- the `@fpkit/acss` npm package, or
- generated source from the companion [`acss-kit-builder`](../acss-kit-builder/) plugin.

Prefers generated source when both are present.

## Supersedes `fpkit-developer`

This plugin **replaces** the deprecated `fpkit-developer` plugin. If you installed the old one via marketplace, uninstall it first to avoid duplicate skills loading:

```
/plugin uninstall fpkit-developer@shawn-sandy-acss
```

All composition / extension / a11y workflows from `fpkit-developer` are preserved as sections of the `/app-compose` command in this plugin.

## Prerequisites

- Vite + React + TypeScript project
- `sass` or `sass-embedded` in `devDependencies`
- Claude Code >= v1.0.33

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

1. If `<componentsDir>/ui.tsx` exists → use **generated** source (relative imports like `../components/fpkit/button/button`). **This wins on tie.**
2. Else if `@fpkit/acss` is in `dependencies` → use **npm** source (`import { Button } from '@fpkit/acss'`).
3. Else → prompt to install or run `/kit-add`.

The components target directory is persisted to `.acss-target.json` at the project root (committed to git) so `/kit-add` and `/app-*` stay in sync.

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
