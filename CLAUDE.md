# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin marketplace** — not a Node.js or Python package. There are no build scripts, no `npm install`, and no CI pipeline.

**Stack:** Claude Code plugin format, Python 3 (scripts), SCSS/CSS custom properties (generated output).

The repo contains two plugins:

- `plugins/acss-kit` — accessible React components and CSS themes for fpkit/acss projects. Two top-level skills (`components`, `styles`), a cross-domain `setup` skill, and three pilot skills (`component-form`, `component-creator`, `style-tune`).
- `plugins/acss-utilities` — Tailwind-style atomic CSS utility classes paired with `acss-kit`'s OKLCH theme tokens via a bridge file. Generator + validator + four `/utility-*` commands. See [`plugins/acss-utilities/docs/`](plugins/acss-utilities/docs/README.md) for the developer guide.

Install from a Claude Code session:

```text
/plugin marketplace add shawn-sandy/agentic-acss-plugins
/plugin install acss-kit@shawn-sandy-agentic-acss-plugins
/plugin install acss-utilities@shawn-sandy-agentic-acss-plugins
```

## Plugin structure

```text
plugins/acss-kit/
├── .claude-plugin/plugin.json     # manifest — authoritative version source
├── README.md                      # user-facing docs
├── CHANGELOG.md                   # version history
├── commands/*.md                  # slash command definitions (YAML front-matter)
├── skills/components/SKILL.md     # components skill (markdown-as-source TSX/SCSS)
├── skills/components/references/  # component reference docs (see references/components/catalog.md)
├── skills/styles/SKILL.md         # styles skill (OKLCH theme generation)
├── skills/styles/references/      # role catalogue, palette algorithm, theme schema
├── skills/component-form/SKILL.md     # form pilot — auto-triggers on natural language
├── skills/component-creator/SKILL.md  # creator-mode pilot — auto-triggers on "create a <component>" phrasing
├── skills/style-tune/SKILL.md         # style-feel pilot — backs /style-tune
├── skills/setup/SKILL.md              # cross-domain bootstrap — backs /setup
├── scripts/                       # Python 3 stdlib scripts (see .claude/rules/python-scripts.md for inventory)
├── assets/                        # foundation/ui.tsx, brand template, internal schema
└── docs/                          # developer guides (architecture, recipes, troubleshooting, tutorial)
```

`plugins/acss-utilities/` mirrors the same shape (`.claude-plugin/`, `commands/`, `skills/`, `scripts/`, `assets/`, `docs/`) — four `/utility-*` commands plus `detect_utility_target.py`, `generate_utilities.py`, `migrate_classnames.py`, and `validate_utilities.py`. See [`plugins/acss-utilities/docs/README.md`](plugins/acss-utilities/docs/README.md) for the developer guide.

### Command authoring conventions

See `.claude/rules/command-authoring.md` (auto-loads when editing `plugins/*/commands/*.md`).

### SKILL.md front-matter

Required: `name:` and `description:`. The PostToolUse hook validates both on every Write/Edit to a SKILL.md file.

## Version bumps

Plugin versions live in **two places** — keep them in sync:

- `<plugin>/.claude-plugin/plugin.json` — **authoritative**; Claude Code and `/plugin update` read this. Required fields: `name`, `version`, `description`.
- `.claude-plugin/marketplace.json` — **omit the `version` field here** (the manifest always wins silently)

Bump only `plugin.json`. Do not add a `version` key to `marketplace.json` entries.

## Pre-submit checklist

Before committing any plugin change:

1. `tests/run.sh` is green (one-time install: `npm --prefix tests ci && pip3 install --user tinycss2`)
2. `plugin.json` version bumped (use `/release-plugin acss-kit`)
3. All SKILL.md references to fpkit source use full GitHub URLs, not repo-relative paths
4. `marketplace.json` description updated if the change is user-facing
5. Plugin-level `README.md` and `CHANGELOG.md` updated if commands or behavior changed
6. If renaming or removing scripts/plugins, update `.claude/rules/python-scripts.md` glob+inventory and the Bash hooks in `.claude/settings.json`

## Maintainer tooling

**Project-level skills** (`.claude/skills/`): `add-command`, `changelog-entry`, `component-author`, `component-update`, `plugin-health`, `release-check`, `release-plugin`, `style-author`, `style-update`, `test-component`, `validate-plugin`, `verify-plugins`. Use these for plugin maintenance tasks instead of manual steps.

**Rules** (`.claude/rules/`): `scss-conventions.md` (active, fires on SCSS/CSS edits), `python-scripts.md` (active, fires on `plugins/*/scripts/**`), `command-authoring.md` (active, fires on `plugins/*/commands/*.md`), `fpkit-references.md` (active, fires on reference docs). See `.claude/rules/README.md` for the full status table.

**Hooks** (`.claude/settings.json`): PostToolUse validates JSON syntax, `plugin.json` required fields, command front-matter, and SKILL.md front-matter on every Write/Edit. PreToolUse blocks commits/pushes to `main`.

## Git workflow

Feature branches + PR. Branch from `main`, open a PR, merge when ready. A PreToolUse hook blocks all direct commits and pushes to `main` regardless of what changed.

Claude Code on the web sessions develop on `claude/<slug>` branches assigned per session — push there, not to a hand-named feature branch.

`.claude/worktrees/` is Claude Code session scratch — ignored by git.

`CLAUDE.local.md` (not committed) — use for machine-local or personal overrides.

## Slash commands shipped by the plugins

| Plugin | Commands |
|---|---|
| `acss-kit` | `/kit-add`, `/kit-create`, `/kit-list`, `/prompt-book`, `/setup`, `/style-tune`, `/theme-brand`, `/theme-create`, `/theme-extract`, `/theme-update` |
| `acss-utilities` | `/utility-add`, `/utility-bridge`, `/utility-list`, `/utility-tune` |

Each command's body is in `plugins/<plugin>/commands/<name>.md`; logic lives in the corresponding SKILL.md.

## Testing locally

The default check is `tests/run.sh` from the repo root — automated structural validation in ~30 seconds. It extracts and syntax-checks every component reference, validates the SCSS contract, runs WCAG contrast on theme files, and replicates the manifest checks. One-time install: `npm --prefix tests ci` and `pip3 install --user tinycss2`.

`tests/run.sh` and `tests/e2e.sh` orchestrate the helpers in `tests/` (`validate_components.{mjs,py}`, `validate_manifest.py`, `run_axe.mjs`, `lib/`) — call those entry scripts, not the helpers directly.

For end-to-end smoke testing of slash commands (rendering output, exercising `/kit-add` and `/theme-create`), `tests/setup.sh` writes a minimal verification fixture at `tests/sandbox/` (gitignored) — `package.json` + `tsconfig.json` + ambient SCSS module declaration, no Vite, no app shell. For render-sensitive changes, `tests/e2e.sh` runs the deeper opt-in check (extracts components, runs `tsc --noEmit`, compiles SCSS, runs jsdom + axe-core a11y on rendered HTML, ~30s after `npm --prefix tests ci`). See [`tests/README.md`](./tests/README.md) for the full workflow.

Full validation: manual SKILL.md review → local install → smoke-test slash commands → run Python scripts against a sample project.

To test a local plugin install without publishing: `claude --plugin-dir ./plugins/acss-kit` from the repo root.

## Python scripts

All scripts in `plugins/acss-kit/scripts/` use **Python 3 stdlib only** with no external dependencies. Two contract families coexist — detector (JSON to stdout, `reasons` array, exit 0/1) and generator/validator (data to stdout, errors to stderr, exit 0/1/2). See `.claude/rules/python-scripts.md` for the full contract and current script inventory.

When adding a new script: use the detector contract if a slash command parses the output; use the generator/validator contract if it is a pipeline transformer or human-readable validator.

## fpkit/acss cross-references

All references to fpkit source in SKILL.md and reference docs must use full GitHub URLs pinned to a tag or commit SHA — never `blob/main` (e.g. `https://github.com/shawn-sandy/acss/blob/<tag-or-sha>/...`). This allows plugin users and contributors to click through without a local clone.
