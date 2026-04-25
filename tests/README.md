# Local plugin testing

Smoke-test the plugins in this marketplace by installing them into a disposable Vite + React + TypeScript sandbox.

The sandbox lives at `tests/sandbox/` and is **gitignored** — it never lands in commits or PRs. Only the scaffolding (`setup.sh`, this file) is committed, so any contributor can recreate the same starting point with one command.

## Contents

1. [Prerequisites](#prerequisites)
2. [One-shot setup](#one-shot-setup)
3. [Running the recipe](#running-the-recipe)
4. [Per-plugin smoke flows](#per-plugin-smoke-flows)
5. [Verification checklist](#verification-checklist)
6. [Reset](#reset)
7. [Custom recipes](#custom-recipes)
8. [What this does NOT cover](#what-this-does-not-cover)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

- **Node 20+** and **npm** on `PATH`
- **Claude Code CLI** (`claude`) on `PATH` — `claude --version` should print >= 1.0.33

## One-shot setup

From the repo root:

```sh
tests/setup.sh
```

The script:

1. Verifies `node`, `npm`, and that you're inside the acss-plugins repo (looks for `.claude-plugin/marketplace.json`).
2. Scaffolds a fresh Vite + React + TypeScript project at `tests/sandbox/`.
3. Installs `sass` (every plugin that writes SCSS depends on it).
4. Initializes a git repo inside the sandbox and makes one bootstrap commit, so plugin "dirty-tree" guards have a clean anchor for the developer's first run.
5. Writes `tests/sandbox/RECIPE.md` and prints the same recipe to stdout.

Re-running without `--reset` errors out with a hint — see [Reset](#reset).

## Running the recipe

```sh
cd tests/sandbox
claude
```

Inside the Claude Code session, paste the block from `RECIPE.md` (or the script's stdout). It registers the local marketplace and installs all four plugins:

```
/plugin marketplace add <absolute path printed by the script>
/plugin install acss-app-builder@acss-plugins
/plugin install acss-kit-builder@acss-plugins
/plugin install acss-theme-builder@acss-plugins
/plugin install acss-component-specs@acss-plugins
```

The marketplace name suffix is `acss-plugins` (the `name` field in `marketplace.json`) — different from the GitHub-source form (`shawn-sandy-acss-plugins`) shown in the root [README.md](../README.md).

Then exercise plugins per the flows below.

## Per-plugin smoke flows

These are the minimum runs that prove a plugin's core paths work after a code change. Run them in the order shown — `/app-init` bootstraps the structure that the other plugins write into.

### acss-app-builder

```
/app-init
/app-page dashboard
/app-layout sidebar
/app-form contact
/app-pattern data-table
```

What to verify:

- `/app-init` creates `src/app/`, `src/pages/`, `src/styles/theme/`, and updates `src/main.tsx` with theme imports.
- `/app-page dashboard` writes `src/pages/Dashboard.tsx`.
- `/app-layout sidebar` writes `src/app/AppShell.tsx` + `AppShell.scss` and updates the entry file.
- `/app-form contact` writes `src/forms/ContactForm.tsx` (or similar — check argument hint).
- `/app-pattern data-table` writes `src/patterns/DataTable.tsx`.

Read [`plugins/acss-app-builder/README.md`](../plugins/acss-app-builder/README.md) for the full command reference.

### acss-kit-builder

```
/kit-list
/kit-add badge
/kit-add button card
```

What to verify:

- `/kit-list` is read-only — prints the component catalog with no file changes.
- `/kit-add badge` creates `<componentsDir>/badge/badge.tsx` + `badge.scss`, plus `<componentsDir>/ui.tsx` (re-exports) and a top-level `.acss-target.json` recording the chosen path on first run. `<componentsDir>` defaults to `src/components/fpkit/` and is configurable on first run.
- `/kit-add button card` adds two components in one invocation under the same `<componentsDir>`.

### acss-theme-builder

```
/theme-create "#4f46e5"
/theme-update src/styles/theme/light.css --color-primary="#2563eb"
/theme-brand forest --from="#0f766e"
```

What to verify:

- `/theme-create "#4f46e5"` creates both `src/styles/theme/light.css` and `dark.css` with WCAG-AA contrast for all 10 semantic role pairs. Watch for the validation summary in the response.
- `/theme-update` edits an existing theme file in place and re-validates contrast — if a change drops below AA, it reverts and reports.
- `/theme-brand forest` creates `src/styles/theme/brand-forest.css` with light/dark overrides scoped to `[data-brand="forest"]`.

### acss-component-specs

```
/spec-list
/spec-validate
/spec-render button --target=react
```

What to verify:

- `/spec-list` prints the spec catalog (Button, Card, Dialog, Alert, Stack, Nav).
- `/spec-validate` runs schema + stale-stamp validation against all specs and exits with a JSON summary.
- `/spec-render button --target=react` writes a React + SCSS rendering of the Button spec into the project (path depends on plugin config).

## Verification checklist

After running a smoke flow, check:

- [ ] No errors in the Claude Code session output.
- [ ] The expected files appear under `src/` (per the per-plugin flows above).
- [ ] `npm run build` in the sandbox succeeds (catches type errors and broken SCSS imports). This is the most reliable sanity check after generated-code changes.
- [ ] `git status` inside the sandbox shows only the new files you'd expect — nothing modified outside the plugin's documented surface.
- [ ] `git diff src/main.tsx` (or `src/index.tsx`) shows clean import additions when a plugin updates the entry file (no duplicate or orphan imports).

If any check fails, capture the Claude Code response and the file diff in the issue or PR description.

## Reset

```sh
tests/setup.sh --reset
```

Wipes and recreates `tests/sandbox/`. Use this:

- Between unrelated test sessions to avoid cross-contamination.
- When a plugin run leaves the sandbox in a state you can't easily reverse.
- After pulling new plugin changes that affect bootstrap behavior (e.g. `/app-init` adds a new entry-file import).

`--reset` is the only cleanup mechanism — there is no separate `clean.sh`. The sandbox is fully self-contained and removable without affecting anything else in the repo.

## Custom recipes

The default `RECIPE.md` lives inside the sandbox and is gitignored (transitively, via the `tests/sandbox/` rule). You can:

- **Edit it freely.** It's regenerated on `--reset`, so don't store anything you can't reproduce.
- **Save curated flows** as additional files alongside it (e.g. `tests/sandbox/recipe-theme-only.md`) — also gitignored.
- **Pin a recipe across resets** by keeping it as a personal note in `CLAUDE.local.md` (committed-ignore) or in your shell history.

For sharing a recipe with other contributors, propose adding it as a **Next Steps** item in a PR description, or open an issue. The repo intentionally avoids a `tests/recipes/` directory until there's a proven need for multiple curated flows.

## What this does NOT cover

- **Python script tests** — for the validation/detection scripts under `plugins/*/scripts/`, use the [`/review-script`](../plugins/) and `/review-scripts` skills (defined globally in your Claude Code setup).
- **Static plugin validation** — for manifest, SKILL.md, and structural checks, use `/validate-plugin <plugin>` or `/verify-plugins` (sweeps all plugins).
- **Automated assertions on slash command output** — review side effects manually inside the sandbox. There is no headless command harness; running the plugins requires a live Claude Code session.
- **Cross-plugin integration tests** — the smoke flows above hit one plugin at a time. The shared sandbox enables ad-hoc multi-plugin sequences (e.g. `/app-init` → `/kit-add badge` → `/app-pattern data-table`), but those are exercised by the developer, not by an automated runner.

## Troubleshooting

**`Run this script from inside the acss-plugins repo`**
The script is invoked from a path where it can't find `.claude-plugin/marketplace.json`. `cd` to the repo root and re-run.

**`Sandbox already exists at: <path>. Re-run with --reset to wipe and recreate it.`**
Expected behavior on second run. Pass `--reset` if you want a clean rebuild; otherwise keep working in the existing sandbox.

**`/plugin marketplace add` fails with "could not load"**
The recipe uses an absolute path. If you copied `RECIPE.md` from another machine or moved the repo, run `tests/setup.sh --reset` to regenerate `RECIPE.md` with the correct path.

**`/plugin install acss-app-builder@acss-plugins` says "not found"**
When the marketplace is added from a local path, Claude Code uses the `name` field from `marketplace.json` as the suffix. Confirm with `/plugin marketplace list` — if the suffix differs (some Claude Code versions normalize differently), use what's listed there.

**Plugin command refuses with "dirty tree"**
The bootstrap commit should prevent this on first run. If you've already executed commands and re-run a plugin that checks the tree, commit your work-in-progress first:
```sh
cd tests/sandbox && git add -A && git commit -m "wip"
```
Or pass `--force` if the command supports it.

**`npm create vite@latest` hangs at "Ok to proceed?"**
The script sets `NPM_CONFIG_YES=true` to skip this prompt. If you've shadowed it in your shell or your npm version handles env vars differently, run:
```sh
echo "yes" | tests/setup.sh
```

**`sass` fails to install**
`tests/sandbox/` runs its own `npm install`. If your machine has a registry-blocking firewall or a stale npm cache, clear it:
```sh
cd tests/sandbox && npm cache clean --force && npm install
```

**Stray nested directory created at `<repo>/Users/...`**
A symptom of an older `create-vite` mishandling absolute paths. The current `setup.sh` works around this by `cd`-ing to `tests/` and passing a bare directory name. If you see this, you're running an outdated copy of the script — `git pull` and re-run.
