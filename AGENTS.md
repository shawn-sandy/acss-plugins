# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## What this repo is

A Claude Code **plugin marketplace** - not a Node.js or Python package. There are no repo-level build scripts, no repo-level `npm install`, and no CI pipeline.

**Stack:** Claude Code plugin format, Python 3 (scripts), SCSS/CSS custom properties (generated output).

The repo contains two plugins:

- `plugins/acss-kit` - accessible React components and CSS themes for fpkit/acss projects.
- `plugins/acss-utilities` - Tailwind-style atomic CSS utility classes paired with `acss-kit`'s OKLCH theme tokens via a bridge file.

Maintainer tooling for working on this repo lives at `.claude/` (review agents, authoring/release skills, validation commands, advisory rules, hooks) — see [`.claude/README.md`](./.claude/README.md) for the index.

Install from a Claude Code session:
```
/plugin marketplace add shawn-sandy/agentic-acss-plugins
/plugin install acss-kit@shawn-sandy-agentic-acss-plugins
/plugin install acss-utilities@shawn-sandy-agentic-acss-plugins
```

## Plugin structure

The plugin follows this layout:

```
plugins/acss-kit/
├── .claude-plugin/plugin.json   # manifest, authoritative version source
├── README.md                    # user-facing docs
├── commands/*.md                # slash command definitions
├── skills/components/SKILL.md         # component generation workflow
├── skills/styles/SKILL.md             # theme generation workflow
├── skills/setup/SKILL.md              # cross-domain bootstrap (/setup)
├── skills/component-form/SKILL.md     # form pilot — natural-language form requests
├── skills/component-creator/SKILL.md  # creator-mode pilot — natural-language single-component requests (/kit-create)
├── skills/style-tune/SKILL.md         # style-feel pilot (/style-tune)
├── scripts/*.py                       # Python 3 stdlib helpers
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

Plugin versions live in one authoritative place per plugin:

- `plugins/<plugin>/.claude-plugin/plugin.json` - Claude Code and `/plugin update` read this
- `.claude-plugin/marketplace.json` - omit a per-plugin `version` field here

Bump only `plugin.json`. Do not add a `version` key to `marketplace.json` entries.

## Pre-submit checklist

Before committing any plugin change:

1. `plugin.json` version bumped (use `/release-plugin <plugin-name>`)
2. All SKILL.md references to fpkit source use full GitHub URLs, not repo-relative paths
3. `marketplace.json` description updated if the change is user-facing
4. Plugin-level `README.md` updated if commands or behavior changed

## Git workflow

Feature branches + PR. Branch from `main`, open a PR, merge when ready. No direct commits to `main` for plugin changes.

`.claude/worktrees/` is Claude session scratch - ignored by git.

`CLAUDE.local.md` (not committed) - use for machine-local or personal overrides.

## Testing locally

```bash
# In a disposable project or Claude Code test session:
/plugin marketplace add /absolute/path/to/agentic-acss-plugins
/plugin install acss-kit@<local-marketplace-name>
```

Full validation: manual SKILL.md review → local install → smoke-test slash commands → run Python scripts against a sample project.

## Python scripts

Scripts in `plugins/acss-kit/scripts/` follow this contract:

- Python 3 stdlib only, no external dependencies
- Output JSON to stdout
- Exit 0 on success, 1 on failure
- Include a `"reasons"` array in JSON output for human-readable error messages

See `plugins/acss-kit/scripts/` for the current script list and individual docstrings.

## fpkit/acss cross-references

All references to fpkit source in SKILL.md and reference docs must use full GitHub URLs pinned to a tag or commit SHA — never `blob/main` (e.g. `https://github.com/shawn-sandy/acss/blob/v6.5.0/...`). This allows plugin users and contributors to click through without a local clone, and freezes the link target so future fpkit refactors do not silently break the docs. See `.claude/rules/fpkit-references.md` for the full policy.

For contributors editing reference docs: keep `shawn-sandy/acss` cloned as a sibling directory for local verification — see `CONTRIBUTING.md`.
