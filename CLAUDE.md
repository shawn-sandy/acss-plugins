# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin marketplace** — not a Node.js or Python package. There are no build scripts, no `npm install`, and no CI pipeline. The repo contains three plugins:

- `plugins/acss-app-builder` — scaffolds Vite+React+TS apps with the fpkit design system
- `plugins/acss-kit-builder` — generates fpkit-style components without an npm install
- `plugins/fpkit-developer` — **deprecated**; kept for one release cycle, then remove

Install plugins from a Claude Code session:
```
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-app-builder@shawn-sandy-acss-plugins
```

## Plugin structure

Every plugin lives under `plugins/` and follows this layout:

```
plugins/<plugin>/
├── .claude-plugin/plugin.json   # manifest — authoritative version source
├── README.md                    # user-facing docs
├── commands/*.md                # slash command definitions (YAML front-matter)
├── skills/<plugin>/SKILL.md     # master skill invoked by Claude
├── skills/<plugin>/references/  # knowledge base documents
└── assets/                      # templates and code snippets
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

1. `plugin.json` version bumped (use `/release-plugin <plugin-name>`)
2. All SKILL.md references to fpkit source use full GitHub URLs, not repo-relative paths
3. `marketplace.json` description updated if the change is user-facing
4. Plugin-level `README.md` updated if commands or behavior changed

## Git workflow

Feature branches + PR. Branch from `main`, open a PR, merge when ready. No direct commits to `main` for plugin changes.

`.claude/worktrees/` is Claude Code session scratch — ignored by git.

## Testing locally

```bash
# In a disposable project or Claude Code test session:
/plugin marketplace add /absolute/path/to/acss-plugins
/plugin install acss-app-builder@<local-marketplace-name>
```

Full validation: manual SKILL.md review → local install → smoke-test slash commands → run Python scripts against a sample project.

## Python scripts

Scripts in `plugins/acss-app-builder/scripts/` follow this contract:

- Python 3 stdlib only, no external dependencies
- Output JSON to stdout
- Exit 0 on success, 1 on failure
- Include a `"reasons"` array in JSON output for human-readable error messages

Current scripts:

- `detect_vite_project.py` — detects whether the target directory is a Vite project
- `detect_component_source.py` — locates fpkit component source files in the project tree
- `validate_css_vars.py` — validates SCSS CSS custom properties against fpkit naming conventions and unit rules
- `validate_theme.py` — checks theme CSS files (light/dark/brand) for WCAG AA contrast on semantic role pairs

## CSS variable naming (generated SCSS)

Pattern: `--{component}-{element?}-{variant?}-{property}`
Every `var()` must include a hardcoded fallback: `var(--btn-bg, transparent)`
Disabled state: `[aria-disabled="true"]` selector — never the native `disabled` attribute

## fpkit/acss cross-references

All references to fpkit source in SKILL.md and reference docs must use full GitHub URLs (e.g. `https://github.com/shawn-sandy/acss/blob/main/...`). This allows plugin users and contributors to click through without a local clone.

For contributors editing reference docs: keep `shawn-sandy/acss` cloned as a sibling directory for local verification — see `CONTRIBUTING.md`.
