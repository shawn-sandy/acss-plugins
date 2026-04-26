# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin marketplace** — not a Node.js or Python package. There are no build scripts, no `npm install`, and no CI pipeline.

**Stack:** Claude Code plugin format, Python 3 (scripts), SCSS/CSS custom properties (generated output).

The repo contains a single plugin:

- `plugins/acss-kit` — accessible React components and CSS themes for fpkit/acss projects. Two top-level skills (`components`, `styles`) plus the `component-form` pilot skill.

Install from a Claude Code session:
```
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-kit@shawn-sandy-acss-plugins
```

History note: as of v0.3.0, `acss-kit` consolidated and replaced four predecessor plugins (`acss-kit-builder`, `acss-theme-builder`, `acss-app-builder`, `acss-component-specs`). See [`plugins/acss-kit/CHANGELOG.md`](./plugins/acss-kit/CHANGELOG.md) for the migration notes.

## Plugin structure

The plugin follows this layout:

```
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

1. `plugin.json` version bumped (use `/release-plugin acss-kit`)
2. All SKILL.md references to fpkit source use full GitHub URLs, not repo-relative paths
3. `marketplace.json` description updated if the change is user-facing
4. Plugin-level `README.md` and `CHANGELOG.md` updated if commands or behavior changed

## Git workflow

Feature branches + PR. Branch from `main`, open a PR, merge when ready. No direct commits to `main` for plugin changes.

`.claude/worktrees/` is Claude Code session scratch — ignored by git.

`CLAUDE.local.md` (not committed) — use for machine-local or personal overrides.

## Testing locally

Run `tests/setup.sh` from the repo root to scaffold a disposable Vite+React+TS sandbox at `tests/sandbox/` (gitignored), then `cd tests/sandbox && claude` and paste the recipe the script printed. See [`tests/README.md`](./tests/README.md) for the full workflow, including the `--reset` flag.

Full validation: manual SKILL.md review → local install → smoke-test slash commands → run Python scripts against a sample project.

## Python scripts

Scripts in `plugins/acss-kit/scripts/` follow this contract:

- Python 3 stdlib only, no external dependencies
- Output JSON to stdout
- Exit 0 on success, 1 on failure
- Include a `"reasons"` array in JSON output for human-readable error messages

Current scripts: `detect_target.py` (manages `.acss-target.json`), `generate_palette.py` (OKLCH palette math), `tokens_to_css.py` (palette → CSS), `css_to_tokens.py` (CSS → palette), `validate_theme.py` (WCAG 2.2 AA contrast).

## fpkit/acss cross-references

All references to fpkit source in SKILL.md and reference docs must use full GitHub URLs (e.g. `https://github.com/shawn-sandy/acss/blob/main/...`). This allows plugin users and contributors to click through without a local clone.

For contributors editing reference docs: keep `shawn-sandy/acss` cloned as a sibling directory for local verification — see `CONTRIBUTING.md`.
