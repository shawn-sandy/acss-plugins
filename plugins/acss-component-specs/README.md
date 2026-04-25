# acss-component-specs

Framework-agnostic component specs for fpkit/acss projects. Author a component once as a spec, render it to React+SCSS, HTML+CSS, or Astro+SCSS.

## What This Plugin Does

The `acss-kit-builder` plugin generates React components. This plugin adds a layer above it: framework-agnostic specs that can produce React, HTML, or Astro output from a single source of truth.

**v0.1 ships 6 component specs:** Button, Card (+ Title/Content/Footer), Dialog, Alert, Stack, Nav (+ Link).

## Install

```
/plugin marketplace add shawn-sandy/acss-plugins
/plugin install acss-component-specs@acss-plugins
```

## Commands

| Command | Description |
|---------|-------------|
| `/spec-add <component> [--refresh]` | Scaffold a new spec from fpkit source |
| `/spec-render <component> [--target=react\|html\|astro\|all]` | Render spec to staging directory |
| `/spec-diff <component> [--target=...]` | Preview what promote would change |
| `/spec-promote <component> [--target=...]` | Move staging output to project |
| `/spec-validate [<component>] [--stale]` | Validate specs and flag stale stamps |
| `/spec-list [<component>]` | List available specs |

## The 3-Step Render Flow

```
/spec-render button            # writes to .acss-staging/
/spec-diff button              # preview changes
/spec-promote button           # move to project
```

Promotion is explicit and never automatic.

## Target Selection

Set `framework` in `.acss-target.json` to configure a per-project default:

```json
{
  "componentsDir": "src/components/fpkit",
  "framework": "react"
}
```

Without `framework`, `/spec-render` renders all three targets. With it, only the specified framework is rendered by default (override with `--target`).

## Spec Format

Specs live at `specs/<component>.md`. Each spec has:

- **YAML frontmatter**: props, events, a11y, framework_notes, css_vars
- **Markdown body**: SCSS pattern, usage examples

The frontmatter is the machine-readable contract. The body is the LLM renderer's knowledge base.

Frontmatter is versioned with `format_version: 1`. Schema changes bump the version. Generated files are stamped: `// generated from button.md@0.1.0`. Use `/spec-validate --stale` to find outdated files.

## Kit-Builder Compatibility

When `acss-kit-builder` is also installed, it probes for specs first. If a spec exists for a component, it takes precedence over kit-builder's bundled reference. This plugin is a passive upgrade — no migration required.

## Theme Integration

Component SCSS uses `var(--color-primary, #0066cc)` patterns. When `acss-theme-builder` output is present in your project, theme values override via CSS cascade. When absent, hardcoded fallbacks apply and `/spec-render` warns you.

## Python Scripts

Scripts in `scripts/` follow the repo contract: stdlib only, JSON to stdout, exit 0/1, `reasons` array.

| Script | Purpose |
|--------|---------|
| `parse_spec.py` | Parse spec frontmatter + body into JSON |
| `validate_spec.py` | Schema validation + stale stamp detection |
| `plan_render.py` | Dependency tree + file manifest for a render target |
| `check_kitbuilder_parity.py` | SCSS drift check between spec and kit-builder |
| `verify_contract_subset.py` | Confirm kit-builder Generation Contracts covered by spec shape |
| `fetch_fpkit_source.py` | Fetch and cache fpkit source from GitHub |

## Developer Guide

Detailed guides are in [`docs/`](docs/):

- [concepts.md](docs/concepts.md) — mental model: specs as source of truth, 7-kind `maps_to`, a11y block, 3-step render flow, atomic failure, version stamps
- [commands.md](docs/commands.md) — full reference for all six `/spec-*` commands
- [spec-authoring.md](docs/spec-authoring.md) — how to author a new component spec end-to-end
- [recipes.md](docs/recipes.md) — step-by-step walkthroughs for common tasks
- [troubleshooting.md](docs/troubleshooting.md) — concrete failure modes and fixes
- [architecture.md](docs/architecture.md) — contributor guide: scripts reference, compound parts, render pipeline, cross-plugin wiring

## v0.1 Limitations

- `format_version: 1` is experimental — breaking schema changes are possible until v1.0.0.
- Web component HTML renderer (`<fpk-button>`) is deferred to v0.2.
- Astro inline `<style>` blocks deferred to v0.2.
- Spec migration tooling (`/spec-migrate`) deferred to v0.2.
- Second-wave components (Form, Badge, Tag, etc.) deferred to v0.2.
