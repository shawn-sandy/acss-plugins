# acss-utilities — Developer Guide

This directory contains the developer guide for the `acss-utilities` Claude Code plugin. For installation and a command overview, see the [plugin README](../README.md).

## For consumers

Developers using the plugin to add Tailwind-style atomic CSS utility classes to their own projects.

| Guide | What it covers |
|-------|---------------|
| [tutorial.md](tutorial.md) | A guided walkthrough: drop the bundle into a React project, import it, and confirm it resolves correctly in dark mode |
| [concepts.md](concepts.md) | The mental model: kebab-case classes, mandatory `var()` fallbacks, responsive `\:` escaping, `!important` policy, the token bridge, and dark-mode parity |
| [commands.md](commands.md) | Full reference for `/utility-add`, `/utility-list`, `/utility-tune`, and `/utility-bridge` |
| [recipes.md](recipes.md) | Step-by-step walkthroughs for the most common tasks |
| [troubleshooting.md](troubleshooting.md) | Concrete failure modes and how to resolve them |

## For contributors

Developers maintaining or extending the plugin itself (token catalogue, generator, validator, family emitters).

| Guide | What it covers |
|-------|---------------|
| [architecture.md](architecture.md) | Plugin internals: layout, the generator/validator contract, how to add a new family, the bundle-size budget resolution order, version-bump checklist |

A diagrams-first companion (`visual-guide.md`) is planned but deferred — see the [architecture guide](architecture.md#deferred-work) for the gap.

## Reference material (canonical sources)

These files are the authoritative source of truth. The guides in this folder summarize and link into them rather than duplicate them.

| File | Purpose |
|------|---------|
| [`../skills/utilities/SKILL.md`](../skills/utilities/SKILL.md) | Full per-command workflow invoked by Claude on every `/utility-*` call |
| [`../skills/utilities/references/utility-catalogue.md`](../skills/utilities/references/utility-catalogue.md) | Every family the plugin emits, every class within it, and the CSS custom property each one references |
| [`../skills/utilities/references/naming-convention.md`](../skills/utilities/references/naming-convention.md) | Selector grammar, prefix rules, fallback policy, and the `!important` exemption list |
| [`../skills/utilities/references/breakpoints.md`](../skills/utilities/references/breakpoints.md) | Responsive prefixes, `@media (width >= …)` syntax, and the escaped colon rule |
| [`../skills/utilities/references/token-bridge.md`](../skills/utilities/references/token-bridge.md) | Bridge mapping, dark-mode parity contract, and regeneration workflow |
| [`../assets/utilities.tokens.json`](../assets/utilities.tokens.json) | Source-of-truth for the generator: spacing scale, breakpoints, color roles, family-enable map, bundle-size budget |
| [`../assets/utilities.css`](../assets/utilities.css) | Committed pre-built bundle. Regenerated from the tokens file via `scripts/generate_utilities.py`; idempotency is enforced by `tests/run.sh` |
