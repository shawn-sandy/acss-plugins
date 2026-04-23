# acss-plugins User Guide

End-to-end guide for installing and using the acss-plugins marketplace. Covers install, plugin selection, every slash command, a full new-project walkthrough, migration off the deprecated `fpkit-developer` plugin, and troubleshooting.

## Contents

1. [What this is](#1-what-this-is)
2. [Prerequisites](#2-prerequisites)
3. [Install, update, list, and uninstall](#3-install-update-list-and-uninstall)
4. [Choose the right plugin](#4-choose-the-right-plugin)
5. [`acss-app-builder` command reference](#5-acss-app-builder-command-reference)
6. [`acss-kit-builder` command reference](#6-acss-kit-builder-command-reference)
7. [End-to-end walkthrough](#7-end-to-end-walkthrough)
8. [Migrating from `fpkit-developer`](#8-migrating-from-fpkit-developer)
9. [Troubleshooting](#9-troubleshooting)
10. [Further reading](#further-reading)

---

## 1. What this is

`acss-plugins` is a Claude Code plugin marketplace for the **fpkit design system**. `@fpkit/acss` is a React component library built on CSS custom-property design tokens and WCAG 2.1 AA accessibility patterns. Its source lives at [`shawn-sandy/acss`](https://github.com/shawn-sandy/acss); the plugins in this marketplace help you install, compose, and customize components without writing boilerplate.

**How slash commands work.** Every command in this guide runs inside a Claude Code session, not in your terminal. Open Claude Code in your project directory, type `/` to open the command menu, pick a command (e.g. `/app-init`), answer any argument prompts in-session, and Claude edits the files in the current project directly. You never run these commands with `node`, `npx`, or `npm run`.

## 2. Prerequisites

- **Claude Code >= v1.0.33** — run `claude --version` to check. Older versions do not support `/plugin marketplace add`.
- **For `acss-app-builder`** — a Vite + React + TypeScript project with `sass` (or `sass-embedded`) in `devDependencies`. [`detect_vite_project.py`](plugins/acss-app-builder/scripts/detect_vite_project.py) enforces the Vite + React parts at preflight; `/app-init` additionally checks for sass and halts with an install hint if it's missing.
- **For `acss-kit-builder` alone** — React + TypeScript, with `sass` (or `sass-embedded`) in `devDependencies`. No Vite requirement, no `@fpkit/acss` npm install. Components are generated as `.tsx` files, so TypeScript is required.
- **Clean git working tree** — most commands refuse to run on a dirty tree unless you pass `--force`. Commit or stash first.

If you already have a project scaffolded with Vite (`npm create vite@latest my-app -- --template react-ts`) and `sass` installed (`npm install -D sass`), you're ready.

## 3. Install, update, list, and uninstall

All plugin management happens inside a Claude Code session.

**Add the marketplace** (once per machine):

```
/plugin marketplace add shawn-sandy/acss-plugins
```

The marketplace name `shawn-sandy-acss-plugins` is auto-derived from the GitHub org + repo slug. You use it as the suffix when installing individual plugins.

**Install plugins:**

```
/plugin install acss-app-builder@shawn-sandy-acss-plugins
/plugin install acss-kit-builder@shawn-sandy-acss-plugins
```

Install only the plugins you need — see [Section 4](#4-choose-the-right-plugin) for guidance.

**Install from a local path** (useful for testing a fork):

```
/plugin marketplace add /absolute/path/to/acss-plugins
/plugin install acss-app-builder@<local-marketplace-name>
```

The local-marketplace name is reported when `/plugin marketplace add` completes.

**List what's installed:**

```
/plugin list
```

This shows every installed plugin and the commands each exposes. Use it when a slash command isn't appearing in the `/` menu.

**Update:**

```
/plugin update
```

Claude Code compares the installed version against the upstream `plugin.json` and pulls newer versions. The authoritative per-plugin version lives in each plugin's `.claude-plugin/plugin.json`. The `plugins[]` entries inside `.claude-plugin/marketplace.json` intentionally omit a per-plugin `version` to avoid drift — the marketplace file's own top-level `version` tracks marketplace-wide releases separately.

**Uninstall:**

```
/plugin uninstall acss-app-builder@shawn-sandy-acss-plugins
```

## 4. Choose the right plugin

Three plugins ship in this marketplace. Pick based on what you're trying to do:

| You want to… | Use |
|---|---|
| Start a new Vite + React + TS app with the fpkit design system (themes, layouts, pages, forms, patterns) | `acss-app-builder` |
| Copy fpkit-style components into your project without installing `@fpkit/acss` from npm | `acss-kit-builder` |
| Generate component source **and** scaffold an app around it | Install both — `acss-app-builder` auto-detects generated source via [`detect_component_source.py`](plugins/acss-app-builder/scripts/detect_component_source.py) and the `.acss-target.json` config |
| Compose or extend an existing fpkit component | `acss-app-builder` → `/app-compose` |
| Migrate off the old `fpkit-developer` plugin | See [Section 8](#8-migrating-from-fpkit-developer) |

**The two-plugin handshake.** When both plugins are installed, they share `.acss-target.json` at the project root. `acss-kit-builder` writes components to `<componentsDir>/`, and `acss-app-builder` reads the same config to figure out where to import them from. A minimal config:

```json
{ "componentsDir": "src/components/fpkit" }
```

Falls back to `src/components/fpkit` automatically if the file is absent.

## 5. `acss-app-builder` command reference

Seven commands. Six of them run a **shared preflight** (Vite project detection, component source detection, theme base check) before taking any action. `/app-init` is exempt — it creates the files (`.acss-target.json`, `src/styles/theme/base.css`) those checks would otherwise verify. All seven refuse to overwrite non-empty files unless you pass `--force`, and all refuse to run with a dirty git tree for the same reason.

### `/app-init`

```
/app-init [--with=theme,layout] [--force]
```

Bootstrap a Vite + React + TS project for the fpkit design system. Creates `src/app/`, `src/pages/`, `src/styles/theme/`, copies a base theme CSS, ensures `.acss-target.json` exists, and appends a sentinel-bounded `import './styles/theme/base.css'` to the entry file. The `--with=theme,layout` shortcut delegates to `/app-theme light` and `/app-layout sidebar` inline.

Run this first in any new project.

### `/app-layout`

```
/app-layout <holy-grail|sidebar|centered> [--force]
```

Generate `src/app/AppShell.tsx` and `src/app/AppShell.scss` from one of three responsive layout templates:

- `holy-grail` — header + nav + main + aside + footer (three-column responsive grid)
- `sidebar` — fixed sidebar + content + footer
- `centered` — single centered column for auth or error pages

Prints the import snippet you should add to `src/App.tsx` when done.

### `/app-page`

```
/app-page <template> [name] [--force]
```

Stamp a page template into `src/pages/<Name>.tsx`. Available templates: `dashboard`, `auth-login`, `auth-signup`, `settings`, `list-detail`, `landing`, `error-404`, `error-500`.

If `name` is omitted, Claude derives PascalCase from the template (e.g. `auth-login` → `AuthLogin`). If the template imports an fpkit component that isn't available locally in `source=generated` mode, the command halts and prints a `/kit-add <component>` hint.

### `/app-form`

```
/app-form <schema.json> [--name=FormName] [--force]
```

Generate an accessible React form from a JSON field schema at `src/forms/<FormName>.tsx`. Supported field types: `text`, `email`, `password`, `url`, `number`, `tel`, `date`, `select`, `textarea`, `checkbox`, `radio`.

Each field gets a unique id of the form `<FormName>-<fieldName>`. An example schema ships at [`assets/forms/schema.example.json`](plugins/acss-app-builder/assets/forms/schema.example.json). The generated form uses `Field`, `Input`, `Checkbox`, and `Button` from fpkit — native `<select>` and `<textarea>` are used inside `<Field>`.

### `/app-theme`

```
/app-theme <light|dark|both|brand-neutral|brand-vibrant> [--mode=light|dark|both]
```

Generate theme CSS under `src/styles/theme/` and wire the imports into the entry file. Presets:

- `light` — `light.css`
- `dark` — `dark.css` (scoped under `[data-theme="dark"]`)
- `both` — writes both files
- `brand-neutral` — accent overrides only
- `brand-vibrant` — saturated accent palette

Runs `validate_theme.py` for WCAG contrast checks on palette files. Contrast failures are reported as warnings, not errors.

### `/app-pattern`

```
/app-pattern <pattern> [--into=<file>] [--force]
```

Insert a reusable UI pattern. Available patterns: `data-table`, `empty-state`, `loading-skeleton`, `hero`, `pricing-grid`, `notification-toast`.

Two modes:

- **Standalone** (no `--into`) — writes `src/patterns/<Name>.tsx` as a new component.
- **Inline** (`--into=<file>`) — replaces the first `{/* @acss-app-builder:insert */}` marker in the target file with the pattern's JSX body and merges imports. Refuses if the marker is absent.

### `/app-compose`

```
/app-compose <name> [description]
```

Guided workflow for building a new component from `@fpkit/acss` primitives, or extending an existing one. Walks through a four-step decision tree:

1. Can the requirement be met by an existing fpkit export with CSS variable customization? Use it directly.
2. Can it be built by composing 2+ fpkit primitives? **Compose** (≤ 3 levels deep).
3. Can an existing component be wrapped with added behavior? **Extend** (preserve `aria-disabled`, focus, event prevention).
4. Otherwise → **Custom** (semantic HTML, rem units, CSS variables per the naming standard).

Applies an accessibility gate before finishing: semantic HTML, keyboard reachability, visible focus, WCAG AA contrast, and CSS variable validation via `scripts/validate_css_vars.py`. This command replaces the deprecated `/fpkit-dev` from `fpkit-developer` — see [Section 8](#8-migrating-from-fpkit-developer).

## 6. `acss-kit-builder` command reference

Two commands. `acss-kit-builder` generates fpkit-style React components directly into your project, so you own the source and don't depend on an npm package.

### `/kit-list`

```
/kit-list [component]
```

Without arguments, prints the full component catalog grouped by category (Simple, Interactive, Layout, Complex). With a component name, prints the full reference for that component: file paths, dependencies, props, CSS variables, and a usage example.

Use `/kit-list` to explore what's available before running `/kit-add`.

### `/kit-add`

```
/kit-add <component> [component2 …]
```

Generate one or more components directly into `<componentsDir>/` (default: `src/components/fpkit/`). The command resolves the full dependency tree, shows you what will be written, and generates bottom-up — dependencies first, then the requested components. Files that already exist are skipped (the new component imports the existing one instead of overwriting it).

**First-run requirement.** The first time you run `/kit-add` in a project, Claude prompts for the components directory (default `src/components/fpkit`) and writes `.acss-target.json` + a minimal `ui.tsx` foundation file. Subsequent runs skip the prompt.

Examples:

```
/kit-add badge
/kit-add button card alert
/kit-add dialog
```

## 7. End-to-end walkthrough

From zero to a running app with the full design system. **Commit between scaffolding steps** — the shared preflight refuses to run on a dirty git tree (see [Section 5](#5-acss-app-builder-command-reference)), so we stage and commit after each mutation.

**Step 1 — Prepare a Vite project.**

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
npm install -D sass
git init && git add . && git commit -m "initial vite app"
```

**Step 2 — Install the marketplace and both plugins.** Open Claude Code in the project directory, then run:

```
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-app-builder@shawn-sandy-acss-plugins
/plugin install acss-kit-builder@shawn-sandy-acss-plugins
```

Expected: `/plugin list` now shows both plugins and their commands.

**Step 3 — Bootstrap the app with a theme and a layout.**

```
/app-init --with=theme,layout
```

Expected: new directories `src/app/`, `src/pages/`, `src/styles/theme/`. Base theme CSS is written. `.acss-target.json` is created at project root (you'll be prompted for the components directory the first time; accept the default `src/components/fpkit`). A light theme and a `sidebar` shell are generated via the `--with` shortcuts. The entry file gets a sentinel-bounded `import` block.

Commit before moving on:

```bash
git add . && git commit -m "scaffold app shell and theme"
```

**Step 4 — Generate fpkit components locally.**

```
/kit-add button card link
```

Expected: `src/components/fpkit/button/button.tsx`, `src/components/fpkit/button/button.scss`, `src/components/fpkit/card/card.tsx`, `src/components/fpkit/card/card.scss`, `src/components/fpkit/link/link.tsx`, `src/components/fpkit/link/link.scss`, plus `ui.tsx` on the first run. Commit before the next command so the preflight stays happy:

```bash
git add . && git commit -m "generate fpkit button, card, link"
```

**Step 5 — Stamp a landing page.**

```
/app-page landing Home
```

Expected: `src/pages/Home.tsx` using the locally generated Button, Link, and Card. Because `ui.tsx` exists, `/app-page` detects `source=generated` and uses relative imports (no `@fpkit/acss` package required). Claude prints a wiring snippet for `src/App.tsx`.

> **Template choice.** This walkthrough uses `landing` because all of its imports — Button, Link, Card, CardTitle, CardContent — are available in `acss-kit-builder`'s catalog. The `dashboard` template imports a table (`TBL`) that only ships via `@fpkit/acss` on npm; to use dashboard under `source=generated`, either switch this flow to `source=npm` by running `npm install @fpkit/acss` in Step 1, or pick a template listed in the [app-builder reference](plugins/acss-app-builder/skills/acss-app-builder/references/pages.md).

**Step 6 — Wire the page into your entry.** Apply the snippet Claude printed in step 5 (typically an import + a route or conditional render in `src/App.tsx`).

**Step 7 — Verify.**

```bash
npx tsc --noEmit
npm run dev
```

Open the dev server URL. You should see the landing page rendered with the light theme, sidebar shell, and the components you generated.

## 8. Migrating from `fpkit-developer`

The `fpkit-developer` plugin is **deprecated** and superseded by `acss-app-builder`. It's kept for one release cycle — supported through the next plugin release and planned for removal thereafter. New projects should skip it entirely.

**Coexistence during migration.** Both plugins can be installed at the same time while you try the new workflow. The command namespaces don't collide: the old command is `/fpkit-dev` (from `fpkit-developer`), and the new one is `/app-compose` (from `acss-app-builder`). Uninstall `fpkit-developer` only once you're confident the new workflow fits.

**Three-step migration:**

1. Install the new plugin first so you can compare:

   ```
   /plugin install acss-app-builder@shawn-sandy-acss-plugins
   ```

2. Map your existing usage:

   | Before | After |
   |---|---|
   | `/fpkit-dev <component>` | `/app-compose <component>` |

   `fpkit-developer` was advisory-only — it guided composition and ran CSS variable checks, but didn't generate files. `/app-compose` is the direct successor and adds a full accessibility gate (semantic HTML, keyboard, focus, WCAG AA contrast, `validate_css_vars.py`).

3. Once your workflow uses the new command, uninstall the old plugin:

   ```
   /plugin uninstall fpkit-developer@shawn-sandy-acss-plugins
   ```

## 9. Troubleshooting

**"Command not found" / the slash command doesn't appear in the menu.**

Run `/plugin list` to confirm the plugin is installed. If it isn't, re-run `/plugin install <plugin>@shawn-sandy-acss-plugins`. Confirm the marketplace suffix is exactly `shawn-sandy-acss-plugins` — truncated variants like `shawn-sandy-acss` won't resolve.

**"No Vite project detected" / the command refuses to run.**

`acss-app-builder` commands expect a Vite + React + TS project. Check that `vite.config.ts` or `vite.config.js` exists at the project root and that `react` and `typescript` are in your `package.json`. If the components directory is non-default, ensure `.acss-target.json` is present and valid:

```json
{ "componentsDir": "src/components/fpkit" }
```

**"Refused: dirty git tree".**

Most commands won't run when your working tree has uncommitted changes — this protects you from accidentally overwriting in-progress work. Commit or `git stash`, then retry. Pass `--force` only if you've reviewed what the command will write.

**"CSS variable validation failed" from `validate_css_vars.py`.**

Component CSS variables must follow the pattern `--{component}-{element?}-{variant?}-{property}` (e.g. `--btn-bg`, `--card-header-color`, `--btn-primary-bg`). Every `var()` call needs a hardcoded fallback: `var(--btn-bg, transparent)` rather than bare `var(--btn-bg)`. This validator only runs on component SCSS (`/app-compose`, `/kit-add`), not on design tokens or theme files.

**`/plugin update` doesn't pick up a new version.**

The authoritative per-plugin version is in each plugin's `.claude-plugin/plugin.json`. The `plugins[]` entries inside `.claude-plugin/marketplace.json` deliberately omit a per-plugin `version` — having it in both places invites drift, and Claude Code's documented behavior is "the plugin manifest wins silently." If a version bump isn't detected, confirm the upstream `plugin.json` reflects the new version.

## Further reading

For contributor workflows, the sibling-clone layout, and version-bump rules, see [CONTRIBUTING.md](CONTRIBUTING.md). For plugin-specific deep dives, see each plugin's README — [`acss-app-builder`](plugins/acss-app-builder/README.md), [`acss-kit-builder`](plugins/acss-kit-builder/README.md), and [`fpkit-developer`](plugins/fpkit-developer/README.md) (deprecated). The live fpkit source lives at [`shawn-sandy/acss`](https://github.com/shawn-sandy/acss), and Claude Code's `/plugin` command reference is documented in the official [Claude Code docs](https://docs.claude.com/en/docs/claude-code/overview).
