---
description: Generate any acss-kit component from a natural-language description (creator mode)
argument-hint: <description>
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

# /kit-create

Creator mode — describe a UI element in plain English and have it generated as a paste-ready snippet (or standalone component file). Works with any component that has a dedicated reference doc under `references/components/<name>.md` (Button, Alert, Card, Dialog, Link, Input, Field, Checkbox, IconButton, Img, Icon, List, Table, Popover, Nav). Components that exist only as inline entries in `catalog.md` — currently Badge, Tag, Heading, Text/Paragraph, Details, Progress — are **not** supported in v0.1; promote them via the `component-author` maintainer skill first.

## Usage

```bash
/kit-create <description>
```

**Examples:**

```bash
/kit-create primary pill button that says "Add to cart"
/kit-create soft warning alert titled "Heads up" with body "Your card expires next month"
/kit-create card with a heading "Plan" and content "Premium tier with all features"
/kit-create small outline icon-button with aria-label "Close"
```

The skill auto-triggers on natural-language phrases like *"create a <component>…"* / *"make me a <component>…"* — this command is the explicit fallback when you want to invoke creator mode by name.

## Workflow

When this command is invoked, follow the workflow documented in the `component-creator` skill at `${CLAUDE_PLUGIN_ROOT}/skills/component-creator/SKILL.md`.

### Quick reference

1. **Dispatch** — match the component noun against `references/components/catalog.md`; halt if no match.
2. **Parse** — load the matched reference doc, read its Props Interface, and resolve the user's phrases against the prop set (global colour/size synonyms + per-component union literals).
3. **Resolve target** — `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py` to locate `componentsDir`.
4. **Vendor** — run `/kit-add <component> [...dependencies]` if any of them aren't yet present.
5. **Validate** — generic rules (empty slots, > 80-char content, two-axis conflicts, missing required props) plus any `## Generation Notes — Creator Mode` rules the matched reference doc declares.
6. **Choose mode** — snippet (default) or standalone file at `src/components/<Name>.tsx`.
7. **Generate** — emit JSX with only the props the description resolved; never silently default a colour-family prop.
8. **Summarise** — print the resolved spec, any deferred sub-components, and a "Refine" prompt for follow-up tweaks.

### Refinement

After a generation, follow-up phrases like *"make it larger"*, *"swap to secondary"*, *"drop the full width"*, *"change the title to '<X>'"* merge into the in-memory spec and re-emit. Say *"start over"* to clear the spec and treat the next turn as a fresh prompt.

### Out of scope for v0.1

- **Multi-component compositions in one prompt** ("a card with a switch and a slider") — generate the outer component, then refine to add inner components one at a time. Multi-component prompts land in v0.3.
- **Form-shaped descriptions** ("signup form with email and password") — handled by the `component-form` skill, not this one.

### Full workflow

See `SKILL.md` for the complete step-by-step including the global synonym tables, the per-reference-doc parsing rules, the validation matrix, and worked examples for Button, Alert, and Card.
