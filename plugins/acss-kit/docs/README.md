# acss-kit — Developer Guide

This directory contains the developer guide for the `acss-kit` Claude Code plugin. For installation and a command overview, see the [plugin README](../README.md).

## For consumers

Developers using the plugin to generate fpkit-style components into their own projects.

| Guide | What it covers |
|-------|---------------|
| [visual-guide.md](visual-guide.md) | A diagrams-first portal: system overview, `/kit-add` lifecycle, component anatomy, composition, theming flow, and a gated maintainer track |
| [tutorial.md](tutorial.md) | A guided walkthrough: generate, import, and customize your first component |
| [concepts.md](concepts.md) | The mental model: UI base component, data-\* variants, CSS-var fallbacks, aria-disabled, generation flow, and the `.acss-target.json` config |
| [commands.md](commands.md) | Full reference for `/kit-add` and `/kit-list` |
| [recipes.md](recipes.md) | Step-by-step walkthroughs for the most common tasks |
| [troubleshooting.md](troubleshooting.md) | Concrete failure modes and how to resolve them |

## For contributors

Developers maintaining or extending the plugin itself (SKILL.md, reference docs, component catalog).

| Guide | What it covers |
|-------|---------------|
| [architecture.md](architecture.md) | Plugin internals: SKILL.md structure, how to add a component reference, the `.acss-target.json` contract, version-bump checklist |

## Reference material (canonical sources)

These files are the authoritative source of truth. The guides in this folder summarize and link into them rather than duplicate them.

| File | Purpose |
|------|---------|
| [`../skills/components/SKILL.md`](../skills/components/SKILL.md) | Full generation workflow (Steps A–F) invoked by Claude on every `/kit-add` call |
| [`../skills/components/references/architecture.md`](../skills/components/references/architecture.md) | UI polymorphic types, `classes` vs `className`, compound component pattern, data-attribute selectors |
| [`../skills/components/references/accessibility.md`](../skills/components/references/accessibility.md) | WCAG rationale, full `useDisabledState` hook source, WCAG checklist per component category |
| [`../skills/components/references/composition.md`](../skills/components/references/composition.md) | Component categories, generation decision tree, inline-types pattern |
| [`../skills/components/references/css-variables.md`](../skills/components/references/css-variables.md) | Naming convention, approved abbreviations, logical properties, rem conversion |
| [`../skills/components/references/components/`](../skills/components/references/components/) | Per-component Generation Contracts, props, CSS vars, usage snippets |
