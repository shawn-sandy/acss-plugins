---
description: Generate a button from a natural-language description (creator mode, v0.1 = Button only)
argument-hint: <description>
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /kit-create

Creator mode — describe a UI element in plain English and have it generated as a paste-ready snippet (or standalone component file). v0.1 is scoped to **Button**; broader coverage lands in v0.2.

## Usage

```
/kit-create <description>
```

**Examples:**

```
/kit-create primary pill button that says "Add to cart"
/kit-create large outline button labeled Sign in
/kit-create danger button for "Delete account"
/kit-create small text button that says Cancel
```

The skill auto-triggers on natural-language phrases like *"create a button…"* / *"make me a button…"* — this command is the explicit fallback when you want to invoke creator mode by name.

## Workflow

When this command is invoked, follow the workflow documented in the `component-creator` skill at `${CLAUDE_PLUGIN_ROOT}/skills/component-creator/SKILL.md`.

### Quick reference

1. **Parse** — extract component (Button only in v0.1), color/size/variant, block/disabled, children text.
2. **Resolve target** — `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py` to locate `componentsDir`.
3. **Vendor** — run `/kit-add button` if `button.tsx` isn't yet present.
4. **Choose mode** — snippet (default) or standalone file at `src/components/<Name>.tsx`.
5. **Generate** — emit JSX with only the props the description resolved; never silently default `color`.
6. **Summarise** — print the resolved spec and a "Refine" prompt for follow-up tweaks.

### Out of scope for v0.1

If the description names a component other than Button (Alert, Card, Link, etc.), the skill halts and points to `/kit-add <component>` plus the matching reference doc. v0.2 expands coverage.

### Full workflow

See `SKILL.md` for the complete step-by-step including the synonym tables for color/size/variant, the ambiguity rules that trigger `AskUserQuestion`, and the file-mode TSX template.
