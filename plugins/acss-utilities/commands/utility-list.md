---
description: List utility families and their classes
argument-hint: [family]
allowed-tools: Read, Glob, Grep
---

Read-only catalogue printer for the acss-utilities bundle.

Follow the `/utility-list` section of `${CLAUDE_PLUGIN_ROOT}/skills/utilities/SKILL.md`.

**Arguments:**

- `family` — *optional*. One of `color-bg`, `color-text`, `color-border`, `spacing`, `display`, `flex`, `grid`, `type`, `radius`, `shadow`, `position`, `z-index`. When given, the command prints every class in that family with the property and CSS custom property each one references.

**Quick steps:**

### `/utility-list` (no arguments)

1. Read `${CLAUDE_PLUGIN_ROOT}/assets/utilities.tokens.json`.
2. Print every entry from `families` with `enabled` and `responsive` status.
3. Print the spacing scale and breakpoints (since they parameterize multiple families).
4. Suggest `/utility-list <family>` for class-level detail.

### `/utility-list <family>`

1. Read `${CLAUDE_PLUGIN_ROOT}/assets/utilities/<family>.css`.
2. Print every selector with the property it sets, one line per class.
3. For families that reference `--color-*` tokens, also print the `var()` chain and how `token-bridge.css` resolves it.
4. Print class count and file size.

This command writes nothing.
