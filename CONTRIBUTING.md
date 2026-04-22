# Contributing to acss-plugins

This repo hosts the Claude Code plugins for `@fpkit/acss`. The live fpkit source lives in a separate repo: [`shawn-sandy/acss`](https://github.com/shawn-sandy/acss).

## Sibling-clone workflow

Plugin work often needs to reference the fpkit source — either to check what's exported, review a component's implementation, or verify a CSS variable naming convention. Keep both repos cloned as siblings:

```
~/work/
├── acss/               # shawn-sandy/acss — live fpkit library
└── acss-plugins/       # this repo
```

The plugins do not assume this layout at runtime. All references to fpkit source in `SKILL.md` files and generated-code comments use full GitHub URLs (e.g. `https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/index.ts`) so plugin users need only this repo to be installed.

The sibling layout is for **contributors** editing plugin skill docs: open the fpkit source locally, verify the current exports, then update the plugin reference docs to match.

## Repo structure

```
acss-plugins/
├── .claude-plugin/
│   └── marketplace.json    # catalog listing all plugins
├── acss-app-builder/       # scaffolding plugin
├── acss-kit-builder/       # component generator plugin
├── fpkit-developer/        # deprecated; kept for one release
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

Each plugin directory follows the Claude Code plugin convention:
- `.claude-plugin/plugin.json` — manifest (name, version, description)
- `README.md` — user-facing docs
- `commands/*.md` — slash command definitions
- `skills/<plugin>/SKILL.md` — skill definition invoked by Claude
- `skills/<plugin>/references/` — knowledge base documents
- `assets/` — templates and code snippets used by the plugin

## Version bumps

Plugin versions live in two places:
- `<plugin>/.claude-plugin/plugin.json` — **authoritative** (Claude Code reads this silently when plugins are installed via this repo directly or via git-subdir from the legacy redirect)
- `.claude-plugin/marketplace.json` plugin entries — **omit version here** to avoid conflict (per Claude Code docs: "The plugin manifest always wins silently")

Bump the version in `plugin.json` when shipping changes — `/plugin update` uses it to detect new versions.

## Testing locally

```bash
# In a disposable project or a Claude Code test session:
/plugin marketplace add /absolute/path/to/acss-plugins
/plugin install acss-app-builder@<local-marketplace-name>
```

Local-path marketplaces work the same as git-hosted ones. When satisfied, push to GitHub and let users install from `shawn-sandy/acss-plugins`.

## Before submitting a change

1. `plugin.json` version bumped
2. SKILL.md references to fpkit source are full GitHub URLs, not repo-relative paths
3. `marketplace.json` description reflects any user-facing change
4. Relevant `README.md` (plugin-level or repo-level) updated
