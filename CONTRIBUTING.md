# Contributing to agentic-acss-plugins

This repo hosts the Claude Code plugins for `@fpkit/acss`. The live fpkit source lives in a separate repo: [`shawn-sandy/acss`](https://github.com/shawn-sandy/acss).

## Sibling-clone workflow

Plugin work often needs to reference the fpkit source — either to check what's exported, review a component's implementation, or verify a CSS variable naming convention. Keep both repos cloned as siblings:

```
~/work/
├── acss/               # shawn-sandy/acss — live fpkit library
└── agentic-acss-plugins/       # this repo
```

The plugins do not assume this layout at runtime. All references to fpkit source in `SKILL.md` files and generated-code comments use full GitHub URLs (e.g. `https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/index.ts`) so plugin users need only this repo to be installed.

The sibling layout is for **contributors** editing plugin skill docs: open the fpkit source locally, verify the current exports, then update the plugin reference docs to match.

## Repo structure

```
agentic-acss-plugins/
├── .claude/                # project-local maintainer tooling — see .claude/README.md
├── .claude-plugin/
│   └── marketplace.json    # catalog listing acss-kit
├── plugins/
│   └── acss-kit/           # components, themes, and form pilot
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

Each plugin directory follows the Claude Code plugin convention:
- `.claude-plugin/plugin.json` — manifest (name, version, description)
- `README.md` — user-facing docs
- `commands/*.md` — slash command definitions
- `skills/*/SKILL.md` — skill definitions invoked by Claude
- `skills/*/references/` — knowledge base documents where applicable
- `assets/` — templates and code snippets used by the plugin

## Maintainer tooling

The `.claude/` directory at the repo root holds project-local Claude Code definitions used while developing the plugin: review agents, authoring/release skills, validation slash commands, advisory rules, and `settings.json` hooks. See [`.claude/README.md`](./.claude/README.md) for the index — it includes an "I want to..." quick-reference table mapping common maintainer tasks to the right tool.

## Version bumps

Plugin versions live in two places:
- `<plugin>/.claude-plugin/plugin.json` — **authoritative** (Claude Code reads this silently when plugins are installed via this repo directly or via git-subdir from the legacy redirect)
- `.claude-plugin/marketplace.json` plugin entries — **omit version here** to avoid conflict (per Claude Code docs: "The plugin manifest always wins silently")

Bump the version in `plugin.json` when shipping changes — `/plugin update` uses it to detect new versions.

## Testing locally

`tests/run.sh` from the repo root is the default structural-validation gate — ~30 seconds, no browser. It extracts each component reference, syntax-checks the TSX, validates the SCSS contract, runs WCAG contrast on themes, and replicates manifest checks. One-time setup: `npm --prefix tests ci && pip3 install --user tinycss2`.

```sh
tests/run.sh
```

For render-sensitive changes, `tests/storybook.sh` is an optional Storybook + axe-playwright deep check (~3–4 min, requires `npx playwright install` on first run).

For end-to-end slash-command verification — when changing slash-command prose or exercising `/kit-add` and `/theme-create` interactively — `tests/setup.sh` scaffolds a disposable Vite + React + TypeScript sandbox at `tests/sandbox/` (gitignored). The script prints a copy-pasteable Claude Code recipe that adds the local marketplace and installs `acss-kit`.

```sh
tests/setup.sh
cd tests/sandbox && claude
```

See [`tests/README.md`](./tests/README.md) for the full workflow:

- `acss-kit` smoke flows with what to verify after each command
- A verification checklist (including `npm run build` in the sandbox)
- Reset and custom-recipe guidance
- Troubleshooting

Local-path marketplaces work the same as git-hosted ones. When satisfied, push to GitHub and let users install from `shawn-sandy/agentic-acss-plugins`.

## Before submitting a change

1. `tests/run.sh` passes from the repo root
2. `plugin.json` version bumped
3. SKILL.md references to fpkit source are full GitHub URLs, not repo-relative paths
4. `marketplace.json` description reflects any user-facing change
5. Relevant `README.md` (plugin-level or repo-level) updated
