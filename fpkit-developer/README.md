# fpkit-developer

> **⚠️ DEPRECATED — superseded by [`acss-app-builder`](../acss-app-builder/).**
>
> The composition / extension / accessibility workflows in this plugin have been
> absorbed into `acss-app-builder` as the `/app-compose` command, alongside
> new app-level scaffolding (`/app-init`, `/app-layout`, `/app-page`,
> `/app-theme`, `/app-form`, `/app-pattern`). This plugin is kept in place for
> one release cycle so existing installs keep working, then will be removed.
>
> **Migrating:**
>
> 1. Uninstall the old plugin to avoid duplicate skills loading:
>    `/plugin uninstall fpkit-developer@shawn-sandy-acss-plugins`
> 2. Install or enable `acss-app-builder`.
> 3. Replace calls to `/fpkit-developer:fpkit-dev` with `/app-compose`.

---

A Claude Code plugin for building applications with **[@fpkit/acss](https://www.npmjs.com/package/@fpkit/acss)** React components. It activates automatically when you work with fpkit components, and adds a `/fpkit-developer:fpkit-dev` slash command for starting the guided workflow directly.

## What it does

- Guides component composition from fpkit primitives
- Validates and customizes CSS variables against fpkit naming conventions
- Extends fpkit components with custom behavior while preserving accessibility
- Ensures WCAG AA compliance in fpkit-based UIs

**Not for:** developing the `@fpkit/acss` library itself — use the `fpkit-component-builder` skill for that.

---

## Prerequisites

- **Claude Code** >= v1.0.33 (run `claude --version` to check)
- **`@fpkit/acss`** >= v0.1.x installed in your project
- **Python 3.x** for the CSS variable validation script — verify: `python --version`

---

## Installation

### Option A — Marketplace install (recommended)

This installs the plugin directly from the GitHub repository without cloning.

**Step 1 — Add the marketplace:**

```shell
/plugin marketplace add shawn-sandy/acss-plugins
```

**Step 2 — Install the plugin:**

```shell
/plugin install fpkit-developer@shawn-sandy-acss-plugins
```

Claude Code copies the plugin to its local cache. Restart Claude Code when prompted.

**To update later:**

```shell
/plugin marketplace update shawn-sandy-acss-plugins
```

**To uninstall:**

```shell
/plugin uninstall fpkit-developer@shawn-sandy-acss-plugins
```

---

### Option B — Manual install via GitHub clone

Clone the repository and copy the plugin manually.

```bash
git clone https://github.com/shawn-sandy/acss-plugins.git
```

**User-level** (available across all your projects):

```bash
mkdir -p ~/.claude/plugins/
cp -r acss-plugins/fpkit-developer ~/.claude/plugins/
```

**Project-level** (this project only):

```bash
mkdir -p .claude/plugins/
cp -r acss-plugins/fpkit-developer .claude/plugins/
```

---

### Option C — Standalone skill (no `/fpkit-developer:fpkit-dev` command)

If you only need the skill without the plugin command:

**User-level:**

```bash
mkdir -p ~/.claude/skills/
cp -r acss-plugins/fpkit-developer/skills/fpkit-developer ~/.claude/skills/
```

**Project-level:**

```bash
mkdir -p .claude/skills/
cp -r acss-plugins/fpkit-developer/skills/fpkit-developer .claude/skills/
```

---

### Verify installation

```shell
# In Claude Code, check the skill is registered:
/plugin
```

Go to the **Installed** tab to confirm `fpkit-developer` appears. The `/fpkit-developer:fpkit-dev` command should be available in the command palette (`/`).

For standalone skill installs, ask Claude: "What skills are available?" — `fpkit-developer` should be listed.

---

## Usage

**Automatic** — Claude activates the skill when the conversation involves `@fpkit/acss` component work: composing components, customizing CSS variables, or fixing accessibility.

**Manual** — Invoke the command with an optional component name or description:

```shell
/fpkit-developer:fpkit-dev StatusButton
/fpkit-developer:fpkit-dev card with a dismissible alert inside
```

---

## Plugin contents

```text
fpkit-developer/
├── .claude-plugin/
│   └── plugin.json                     # Plugin manifest
├── commands/
│   └── fpkit-dev.md                    # /fpkit-developer:fpkit-dev command
├── skills/
│   └── fpkit-developer/
│       ├── SKILL.md                    # Skill workflow (7-step guide)
│       ├── references/
│       │   ├── accessibility.md        # WCAG AA patterns
│       │   ├── architecture.md         # fpkit design patterns (as prop, polymorphism)
│       │   ├── composition.md          # 5 composition patterns + real examples
│       │   ├── css-variables.md        # CSS variable reference + naming rules
│       │   ├── storybook.md            # Storybook story patterns
│       │   └── testing.md             # Vitest + RTL + jest-axe patterns
│       └── scripts/
│           └── validate_css_vars.py    # Validates CSS variable naming (requires Python 3)
├── README.md
└── LICENSE
```

---

## Compatibility

- `@fpkit/acss` >= v0.1.x
- macOS, Linux, Windows
- Claude Code >= v1.0.33

## License

MIT — see [LICENSE](./LICENSE)
