# acss-kit-builder — Developer Guide

This directory contains the developer guide for the `acss-kit-builder` Claude Code plugin. For installation and a command overview, see the [plugin README](../README.md).

## For consumers

Developers using the plugin to generate fpkit-style components into their own projects.

| Guide | What it covers |
|-------|---------------|
| [tutorial.md](tutorial.md) | A guided walkthrough: generate, import, and customize your first component |
| [concepts.md](concepts.md) | The mental model: UI base component, data-\* variants, CSS-var fallbacks, aria-disabled, generation flow, and cross-plugin coordination |
| [commands.md](commands.md) | Full reference for `/kit-add` and `/kit-list` |
| [recipes.md](recipes.md) | Step-by-step walkthroughs for the most common tasks |
| [troubleshooting.md](troubleshooting.md) | Concrete failure modes and how to resolve them |

## For contributors

Developers maintaining or extending the plugin itself (SKILL.md, reference docs, component catalog).

| Guide | What it covers |
|-------|---------------|
| [architecture.md](architecture.md) | Plugin internals: SKILL.md structure, how to add a component reference, cross-plugin wiring, version-bump checklist |

## Reference material (canonical sources)

These files are the authoritative source of truth. The guides in this folder summarize and link into them rather than duplicate them.

| File | Purpose |
|------|---------|
| [`../skills/acss-kit-builder/SKILL.md`](../skills/acss-kit-builder/SKILL.md) | Full generation workflow (Steps A–F) invoked by Claude on every `/kit-add` call |
| [`../skills/acss-kit-builder/references/architecture.md`](../skills/acss-kit-builder/references/architecture.md) | UI polymorphic types, `classes` vs `className`, compound component pattern, data-attribute selectors |
| [`../skills/acss-kit-builder/references/accessibility.md`](../skills/acss-kit-builder/references/accessibility.md) | WCAG rationale, full `useDisabledState` hook source, WCAG checklist per component category |
| [`../skills/acss-kit-builder/references/composition.md`](../skills/acss-kit-builder/references/composition.md) | Component categories, generation decision tree, inline-types pattern |
| [`../skills/acss-kit-builder/references/css-variables.md`](../skills/acss-kit-builder/references/css-variables.md) | Naming convention, approved abbreviations, logical properties, rem conversion |
| [`../skills/acss-kit-builder/references/components/`](../skills/acss-kit-builder/references/components/) | Per-component Generation Contracts, props, CSS vars, usage snippets |
