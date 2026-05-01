
# agentic-acss-plugins User Guide

`agentic-acss-plugins` is a Claude Code plugin marketplace for building accessible React components and CSS themes for fpkit/acss projects.

The marketplace ships two plugins:

- `acss-kit` — accessible React components and OKLCH CSS themes for fpkit/acss projects.
- `acss-utilities` — Tailwind-style atomic CSS utility classes paired with `acss-kit`'s theme tokens via a bridge file.

## Install

Run these commands inside a Claude Code session:

```text
/plugin marketplace add shawn-sandy/agentic-acss-plugins
/plugin install acss-kit@shawn-sandy-agentic-acss-plugins
/plugin install acss-utilities@shawn-sandy-agentic-acss-plugins
```

For local testing from this repo:

```text
/plugin marketplace add /absolute/path/to/agentic-acss-plugins
/plugin install acss-kit@agentic-acss-plugins
/plugin install acss-utilities@agentic-acss-plugins
```

Use `/plugin list` to confirm the plugins are installed and to see available slash commands.

## Prerequisites

- React + TypeScript project
- `sass` or `sass-embedded` in `devDependencies`

```sh
npm install -D sass
```

## acss-kit Commands

### `/kit-list [component]`

Lists all available component references, or shows details for one component.

```text
/kit-list
/kit-list button
```

### `/kit-add <component> [component2 ...]`

Generates accessible React components into your project using local imports only. On first run, the command asks for a target directory, writes `.acss-target.json`, and copies the `ui.tsx` foundation component.

```text
/kit-add button
/kit-add button card dialog
```

Default component target:

```json
{ "componentsDir": "src/components/fpkit" }
```

### `/theme-create <hex-color> [--mode=light|dark|both]`

Generates semantic CSS theme files from a seed color and validates required WCAG contrast pairs.

```text
/theme-create "#4f46e5" --mode=both
```

### `/theme-brand <name> [--from=<hex-color>]`

Creates a brand override CSS file layered after the light/dark theme files.

```text
/theme-brand forest --from="#0f766e"
```

### `/theme-update <file> <--color-role=#hex> [...]`

Updates specific color roles in an existing theme file and re-validates contrast.

```text
/theme-update src/styles/theme/light.css --color-primary="#2563eb"
```

### `/theme-extract <image-path|figma-url>`

Extracts a primary brand color from design input, then runs the theme generation flow.

## Form Pilot

The `component-form` skill can auto-trigger from natural language:

```text
Create a signup form with email and password.
```

It vendors required form dependencies through `/kit-add` when needed, then writes a self-contained React form under `src/forms/`.

## acss-utilities Commands

The `acss-utilities` plugin adds a Tailwind-style atomic CSS layer (`.bg-primary`, `.mt-4`, `.sm-hide`) and a token-bridge that aliases `acss-kit`'s OKLCH roles to fpkit-style names. See the [`acss-utilities` README](plugins/acss-utilities/README.md) and [developer guide](plugins/acss-utilities/docs/README.md) for the full reference.

### `/utility-add`

Drops the generated `utilities.css` bundle and `token-bridge.css` into your project.

### `/utility-list`

Lists utility families and their classes.

### `/utility-bridge`

Regenerates `token-bridge.css` against the active `acss-kit` theme, emitting both `:root` and `[data-theme="dark"]` blocks for parity.

### `/utility-tune`

Adjusts `utilities.tokens.json` (spacing baseline, breakpoints, family enables) from a natural-language request, regenerates the bundle, and validates the result.

## Migration From Prior Plugins

`acss-kit` replaces the previous marketplace entries:

| Previous plugin | Status |
|---|---|
| `acss-kit-builder` | Rehomed into `acss-kit` components |
| `acss-theme-builder` | Rehomed into `acss-kit` styles |
| `acss-app-builder` | Removed |
| `acss-component-specs` | Removed |

Uninstall old plugins if they are present:

```text
/plugin uninstall acss-kit-builder@shawn-sandy-agentic-acss-plugins
/plugin uninstall acss-theme-builder@shawn-sandy-agentic-acss-plugins
/plugin uninstall acss-app-builder@shawn-sandy-agentic-acss-plugins
/plugin uninstall acss-component-specs@shawn-sandy-agentic-acss-plugins
/plugin install acss-kit@shawn-sandy-agentic-acss-plugins
```

Existing `.acss-target.json` files remain compatible.

## Further Reading

- [Root README](README.md) for marketplace overview and install notes.
- [acss-kit README](plugins/acss-kit/README.md) for full plugin behavior.
- [acss-kit developer docs](plugins/acss-kit/docs/README.md) for contributor workflows.
- [acss-utilities README](plugins/acss-utilities/README.md) for utility-class behavior.
- [acss-utilities developer guide](plugins/acss-utilities/docs/README.md) for the command reference, recipes, and architecture notes.
- [tests README](tests/README.md) for local smoke testing.
