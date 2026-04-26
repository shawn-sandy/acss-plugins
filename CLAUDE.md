# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin marketplace** — not a Node.js or Python package. There are no build scripts, no `npm install`, and no CI pipeline.

**Stack:** Claude Code plugin format, Python 3 (scripts), SCSS/CSS custom properties (generated output).

The repo contains a single plugin:

- `plugins/acss-kit` — accessible React components and CSS themes for fpkit/acss projects. Two top-level skills (`components`, `styles`) plus the `component-form` pilot skill.

Install from a Claude Code session:

```text
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-kit@shawn-sandy-acss-plugins
```

## Plugin structure

The plugin follows this layout:

```text
plugins/acss-kit/
├── .claude-plugin/plugin.json     # manifest — authoritative version source
├── README.md                      # user-facing docs
├── CHANGELOG.md                   # version history
├── commands/*.md                  # slash command definitions (YAML front-matter)
├── skills/components/SKILL.md     # components skill (markdown-as-source TSX/SCSS)
├── skills/components/references/  # component reference docs (18 components)
├── skills/styles/SKILL.md         # styles skill (OKLCH theme generation)
├── skills/styles/references/      # role catalogue, palette algorithm, theme schema
├── skills/component-form/SKILL.md # form pilot — auto-triggers on natural language
├── scripts/                       # Python 3 stdlib scripts (detect_target, palette, validate, etc.)
├── assets/                        # foundation/ui.tsx, brand template, internal schema
└── docs/                          # developer guides (architecture, recipes, troubleshooting, tutorial)
```

### Command file front-matter

```yaml
---
description: <one-line description>
argument-hint: [--option] [--force]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---
```

Body delegates to the master SKILL.md, never re-implements logic inline.

## Version bumps

Plugin versions live in **two places** — keep them in sync:

- `<plugin>/.claude-plugin/plugin.json` — **authoritative**; Claude Code and `/plugin update` read this
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

**Project-level skills** (`.claude/skills/`): `add-command`, `component-author`, `component-update`, `plugin-health`, `release-check`, `release-plugin`, `style-author`, `style-update`, `validate-plugin`, `verify-plugins`. Use these for plugin maintenance tasks instead of manual steps.

**Rules** (`.claude/rules/`): `scss-conventions.md` (active, fires on SCSS/CSS edits), `python-scripts.md` (active, fires on `plugins/acss-kit/scripts/**`). See `.claude/rules/README.md` for the full status table.

**Hooks** (`.claude/settings.json`): PostToolUse validates JSON syntax, `plugin.json` required fields, command front-matter, and SKILL.md front-matter on every Write/Edit. PreToolUse blocks commits/pushes to `main`.

## Git workflow

Feature branches + PR. Branch from `main`, open a PR, merge when ready. No direct commits to `main` for plugin changes.

`.claude/worktrees/` is Claude Code session scratch — ignored by git.

`CLAUDE.local.md` (not committed) — use for machine-local or personal overrides.

## Testing locally

The default check is `tests/run.sh` from the repo root — automated structural validation in ~30 seconds. It extracts and syntax-checks every component reference, validates the SCSS contract, runs WCAG contrast on theme files, and replicates the manifest checks. One-time install: `npm --prefix tests ci` and `pip3 install --user tinycss2`.

For end-to-end smoke testing of slash commands (rendering output, exercising `/kit-add` and `/theme-create`), `tests/setup.sh` scaffolds a disposable Vite+React+TS sandbox at `tests/sandbox/` (gitignored). For render-sensitive changes, `tests/storybook.sh` runs the optional Storybook + axe-playwright deep check (~3–4 min). See [`tests/README.md`](./tests/README.md) for the full workflow.

Full validation: manual SKILL.md review → local install → smoke-test slash commands → run Python scripts against a sample project.

## Python scripts

All scripts in `plugins/acss-kit/scripts/` use **Python 3 stdlib only** with no external dependencies. Two contract families coexist — detector (JSON to stdout, `reasons` array, exit 0/1) and generator/validator (data to stdout, errors to stderr, exit 0/1/2). See `.claude/rules/python-scripts.md` for the full contract and current script inventory.

When adding a new script: use the detector contract if a slash command parses the output; use the generator/validator contract if it is a pipeline transformer or human-readable validator.

## fpkit/acss cross-references

All references to fpkit source in SKILL.md and reference docs must use full GitHub URLs (e.g. `https://github.com/shawn-sandy/acss/blob/main/...`). This allows plugin users and contributors to click through without a local clone.

For contributors editing reference docs: keep `shawn-sandy/acss` cloned as a sibling directory for local verification — see `CONTRIBUTING.md`.
