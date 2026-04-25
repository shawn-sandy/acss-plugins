# acss-component-specs — Developer Guide

This directory contains the developer guide for the `acss-component-specs` Claude Code plugin. For installation and a command overview, see the [plugin README](../README.md).

## For consumers

Developers using the plugin to author specs and render framework-specific component files.

| Guide | What it covers |
|-------|---------------|
| [concepts.md](concepts.md) | The mental model: specs as source of truth, the 7-kind `maps_to` discriminator, the a11y block, the 3-step render flow, atomic failure, version stamps, and cross-plugin coordination |
| [commands.md](commands.md) | Full reference for `/spec-add`, `/spec-render`, `/spec-diff`, `/spec-promote`, `/spec-validate`, `/spec-list` |
| [spec-authoring.md](spec-authoring.md) | How to author a new component spec end-to-end |
| [recipes.md](recipes.md) | Step-by-step walkthroughs for common tasks |
| [troubleshooting.md](troubleshooting.md) | Concrete failure modes and how to resolve them |

## For contributors

Developers maintaining the plugin itself (SKILL.md, specs, references, Python scripts, cross-plugin scripts).

| Guide | What it covers |
|-------|---------------|
| [architecture.md](architecture.md) | Plugin internals: scripts contract and reference, compound-part handling, render pipeline, cross-plugin wiring, v0.2 roadmap |

## Reference material (canonical sources)

| File | Purpose |
|------|---------|
| [`../skills/acss-component-specs/SKILL.md`](../skills/acss-component-specs/SKILL.md) | Full runbook for all six commands; coordination with kit-builder and app-builder |
| [`../skills/acss-component-specs/references/spec-format.md`](../skills/acss-component-specs/references/spec-format.md) | Authoritative spec schema: required fields, 7-kind `maps_to` table, a11y block, stamps, `format_version` bump policy |
| [`../skills/acss-component-specs/references/authoring-guide.md`](../skills/acss-component-specs/references/authoring-guide.md) | 10-step walkthrough for contributors adding a new spec |
| [`../skills/acss-component-specs/references/compound-components.md`](../skills/acss-component-specs/references/compound-components.md) | Compound component sub-spec pattern, React/HTML/Astro per-target conventions |
| [`../skills/acss-component-specs/references/state-and-events.md`](../skills/acss-component-specs/references/state-and-events.md) | Stateful component patterns: Dialog, Alert, interactive Card, aria-disabled, Nav active state |
| [`../skills/acss-component-specs/references/frameworks/react.md`](../skills/acss-component-specs/references/frameworks/react.md) | React+SCSS renderer rulebook |
| [`../skills/acss-component-specs/references/frameworks/html.md`](../skills/acss-component-specs/references/frameworks/html.md) | HTML+CSS renderer rulebook, native element catalog |
| [`../skills/acss-component-specs/references/frameworks/astro.md`](../skills/acss-component-specs/references/frameworks/astro.md) | Astro+SCSS renderer rulebook |
| [`../skills/acss-component-specs/specs/`](../skills/acss-component-specs/specs/) | Bundled reference specs (button, card, dialog, alert, stack, nav) |
