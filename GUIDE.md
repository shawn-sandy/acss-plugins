# acss-plugins User Guide

`acss-plugins` is a Claude Code plugin marketplace for building accessible React components and CSS themes for fpkit/acss projects.

As of `0.3.0`, the marketplace ships one plugin: `acss-kit`.

## Install

Run these commands inside a Claude Code session:

```text
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-kit@shawn-sandy-acss-plugins
```

For local testing from this repo:

```text
/plugin marketplace add /absolute/path/to/acss-plugins
/plugin install acss-kit@acss-plugins
```

Use `/plugin list` to confirm the plugin is installed and to see available slash commands.

## Prerequisites

- React + TypeScript project
- `sass` or `sass-embedded` in `devDependencies`

```sh
npm install -D sass
```

## Commands

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
/plugin uninstall acss-kit-builder@shawn-sandy-acss-plugins
/plugin uninstall acss-theme-builder@shawn-sandy-acss-plugins
/plugin uninstall acss-app-builder@shawn-sandy-acss-plugins
/plugin uninstall acss-component-specs@shawn-sandy-acss-plugins
/plugin install acss-kit@shawn-sandy-acss-plugins
```

Existing `.acss-target.json` files remain compatible.

## Further Reading

- [Root README](README.md) for marketplace overview and install notes.
- [acss-kit README](plugins/acss-kit/README.md) for full plugin behavior.
- [acss-kit developer docs](plugins/acss-kit/docs/README.md) for contributor workflows.
- [tests README](tests/README.md) for local smoke testing.
