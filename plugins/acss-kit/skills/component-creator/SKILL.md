---
name: component-creator
description: Use when the user describes a UI element in natural language and wants it generated — "create a primary pill button that says Add to cart", "make me a large outline button labeled Sign in", "build a danger button for Delete account", "scaffold a primary submit button", "design a rounded button". Triggers include "create a button", "make me a button", "build a button", "design a button", "generate a button", "scaffold a button". v0.1 covers Button only; additional components follow once parse → match → generate proves out.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.1.0"
  pilot: true
---

# SKILL: component-creator

Generate a self-contained, accessible React snippet (or component file) from a natural-language description. The user describes the element ("primary pill button that says Add to cart"); this skill parses the description, maps it to the matching component reference doc's variants and props, and emits a TSX block that uses the vendored `acss-kit` components.

> **Verified against fpkit source:** uses the canonical `references/components/button.md` reference (verified against `@fpkit/acss@6.5.0`). Variant and prop vocabulary mirror that doc — no behaviour is invented in this skill.

## Pilot status

This is the second per-component skill in `acss-kit` (after `component-form`). v0.1 is intentionally scoped to **Button** only so the parse → match → generate loop can be validated on the highest-traffic component before being expanded to the rest of the catalog.

If a description names a component other than Button (e.g. *"create a card with…"*, *"make me an alert"*), this skill should hand off rather than guess: surface that v0.1 is Button-only and point to `/kit-add <component>` plus the matching reference doc until the next release expands coverage.

If you're authoring a description and unsure whether this skill applies: descriptions of Button shape, copy, colour, or size belong here; structural composition (forms, layouts, multi-component cards) belong in `component-form` or a dedicated `/kit-add` flow.

---

## Authoring Modes

### Mode 1 — Natural-language description (preferred)

The user describes the button in plain English; this skill derives the variants, props, and content.

Examples:
- "Create a primary pill button that says 'Add to cart'."
- "Make me a large outline button labeled 'Sign in'."
- "Build a danger button for 'Delete account'."
- "Scaffold a small text button that says 'Cancel'."

### Mode 2 — Structured spec (fallback)

The user passes a JSON block describing the button. The skill reads it and generates the snippet directly.

```json
{
  "component": "button",
  "color": "primary",
  "variant": "pill",
  "size": "lg",
  "children": "Add to cart",
  "block": false,
  "disabled": false
}
```

Both modes converge on the same internal contract — a single button spec — and produce identical output.

---

## Step A — Parse the description

### A1. Component dispatch

Match the description's component noun against the reference catalog. v0.1 only handles `button`.

| Phrase contains | Resolves to | v0.1 action |
|-----------------|-------------|-------------|
| `button`, `btn`, `cta`, `call to action` | Button | proceed |
| `alert`, `banner`, `notification` | Alert | halt with v0.1 message |
| `card`, `panel`, `tile` | Card | halt with v0.1 message |
| `link`, `anchor` | Link | halt with v0.1 message |
| `icon button`, `icon-button` | IconButton | halt with v0.1 message |
| anything else | unknown | halt with v0.1 message |

When halting, print:

> creator-mode v0.1 supports Button only. For `<resolved>`, run `/kit-add <name>` to vendor the component, then see `references/components/<name>.md` for usage. Broader coverage lands in v0.2.

### A2. Variant extraction

For Button, parse three variant axes plus two booleans. The vocabulary below is authoritative — synonyms on the left collapse to the prop value on the right. Anything the parser can't resolve must trigger `AskUserQuestion`, never a silent default.

**`color`** (maps to `data-color`):

| Synonym in description | `color` prop |
|------------------------|--------------|
| `primary`, `main`, `cta` | `primary` |
| `secondary` | `secondary` |
| `danger`, `destructive`, `delete`, `remove`, `error` | `danger` |
| `success`, `confirm`, `save`, `submit-positive` | `success` |
| `warning`, `caution` | `warning` |

If the description names no colour, **do not assume** `primary`; ask via `AskUserQuestion` with `primary` as the suggested default.

**`size`** (maps into `data-btn`):

| Synonym in description | `size` prop |
|------------------------|-------------|
| `extra small`, `xs`, `tiny` | `xs` |
| `small`, `sm`, `compact` | `sm` |
| `medium`, `md`, `default`, `regular` | `md` |
| `large`, `lg`, `big` | `lg` |
| `extra large`, `xl` | `xl` |
| `huge`, `2xl`, `2x large`, `xx large` | `2xl` |

If the description names no size, omit the `size` prop (Button defaults to `md`).

**`variant`** (maps to `data-style`):

| Synonym in description | `variant` prop |
|------------------------|----------------|
| `pill`, `rounded`, `round`, `capsule` | `pill` |
| `outline`, `outlined`, `bordered`, `ghost` | `outline` |
| `text`, `link-style`, `flat` | `text` |
| `icon`, `icon-only` | `icon` |

If the description names no style, omit the `variant` prop.

**`block`** (boolean):

True when the description contains any of: `full width`, `full-width`, `block`, `stretch`, `100% wide`. Otherwise omit.

**`disabled`** (boolean):

True when the description contains any of: `disabled`, `inactive`, `unavailable`. Otherwise omit. Always passed via the typed `disabled` prop, never the raw HTML attribute.

### A3. Content extraction

The button's `children` text is parsed in this order — first match wins:

1. A quoted string: `"Add to cart"`, `'Sign in'`, `“Save”` → use the contents verbatim.
2. The phrase `that says <X>`, `labeled <X>`, `with text <X>`, `for <X>` → use `<X>` (strip surrounding punctuation).
3. Imperative verb-phrase fallback (e.g. *"a delete button"* → `Delete`). Capitalise the first letter; do not pluralise.
4. Nothing inferable → `AskUserQuestion` with no default. Never write a button with placeholder text.

Preserve the user's casing for explicit quoted strings; sentence-case derived phrases.

### A4. Variant-only ambiguity

Halt with `AskUserQuestion` whenever:
- `color` is unresolved AND the description doesn't say "neutral" / "default".
- A synonym maps to two different axes (e.g. *"compact"* could be size `sm` or could mean `block: false`). Disambiguate before generating.
- The description includes `variant: icon` but no `aria-label` content. Icon buttons require an accessible name; ask for it.

---

## Step B — Resolve the target

Identical to `component-form` Step B. Reuses `scripts/detect_target.py`.

### B1. Run the detector

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <project_root>
```

Parse the JSON. Use `source` and `componentsDir`.

### B2. Branch on source

- `source: "generated"` → proceed to B3.
- `source: "none"` → skip B3 and jump to B4 (clean project).

### B3. Probe required component *(only when source is `generated`)*

Check for:
- `<componentsDir>/button/button.tsx`
- `<componentsDir>/button/button.scss`
- `<componentsDir>/ui.tsx`

### B4. Bootstrap or vendor missing files

Run `/kit-add button` when **either**:
- `source: "none"` from B1, or
- B3 found any missing files.

After `/kit-add` completes, re-run `detect_target.py` to confirm `source` is now `"generated"` and `componentsDir` is set, then continue to Step C.

If `/kit-add` fails, surface its error and halt — the snippet cannot land without its component dependency.

---

## Step C — Choose the output mode

Ask once via `AskUserQuestion` (skip if the user already specified):

- **Snippet mode** *(default)* — print a TSX block the user pastes into an existing file. No file is written.
- **File mode** — write a standalone component file at `src/components/<Name>.tsx`. The skill derives `<Name>` from the button's content (e.g. `Add to cart` → `AddToCartButton`).

Once chosen, proceed to Step D.

---

## Step D — Generate output

### D1. Compose the JSX

Build the Button JSX from the parsed spec. Only emit props that are explicitly resolved — omit the rest so the component falls back to its declared defaults.

Skeleton:

```tsx
<Button
  type="button"
  {{COLOR_PROP}}
  {{SIZE_PROP}}
  {{VARIANT_PROP}}
  {{BLOCK_PROP}}
  {{DISABLED_PROP}}
  {{ARIA_LABEL_PROP}}
>
  {{CHILDREN}}
</Button>
```

Substitution table:

| Placeholder | Substitute with |
|-------------|-----------------|
| `{{COLOR_PROP}}` | `color="<value>"` if resolved, else empty |
| `{{SIZE_PROP}}` | `size="<value>"` if resolved, else empty |
| `{{VARIANT_PROP}}` | `variant="<value>"` if resolved, else empty |
| `{{BLOCK_PROP}}` | `block` if true, else empty |
| `{{DISABLED_PROP}}` | `disabled` if true, else empty |
| `{{ARIA_LABEL_PROP}}` | `aria-label="<children>"` only when `variant="icon"` (children is the icon glyph, not an accessible name); else empty |
| `{{CHILDREN}}` | The resolved children string from A3 |

Always emit `type="button"` — the Button reference doc requires it to prevent implicit form submission.

### D2. Imports (file mode only)

Compute the relative path from `src/components/<Name>.tsx` to the components directory (default `src/components/fpkit`, giving `./fpkit`). Use `path.relative()` semantics; fall back to `./fpkit` if `.acss-target.json` is absent.

Wrap the JSX as:

```tsx
// <Name>.tsx — generated by component-creator skill
import Button from '<relative>/button/button'
import '<relative>/button/button.scss'

export default function {{NAME}}({
  onClick,
}: {
  onClick?: React.MouseEventHandler<HTMLButtonElement>
}) {
  return (
    {{JSX_FROM_D1}}
  )
}
```

Wire `onClick` through to the rendered `<Button>` so the file isn't dead-on-arrival; users replace the prop signature with whatever fits their route/page.

### D3. Snippet mode

Print the bare JSX (the result of D1) in a fenced TSX block. Include the import lines above so the snippet is paste-ready, but do **not** write to disk.

### D4. Atomic generation

Build the entire output in memory; write to disk only on success (file mode). If any step in A or D fails, surface the error and write nothing. Partial files break the user's TypeScript compilation.

---

## Step E — Accessibility

The generated Button is WCAG 2.2 AA by construction because it delegates to the vendored `Button` component. Don't strip these patterns when refining:

- **`type="button"` is always emitted** — prevents implicit form submission when the button mounts inside a `<form>`.
- **`disabled` uses the typed prop**, never the raw HTML attribute. The component renders `aria-disabled="true"` and keeps the element in tab order (WCAG 2.1.1).
- **Icon-only buttons require `aria-label`** (D1 enforces this). The icon glyph is not an accessible name on its own (WCAG 4.1.2).
- **Default size hits 44×44 px target** (WCAG 2.5.8). Sizes `xs` and `sm` may fall below — only emit them when the user explicitly asks.

`references/components/button.md` is the authoritative source for the component's full accessibility behaviour.

---

## Step F — Post-generation summary

After generating, print:

```
Generated <Name> using Button with:
  color=<value>  variant=<value>  size=<value>  children="<text>"

[snippet output | wrote src/components/<Name>.tsx]

Refine: try "make it larger", "swap to secondary", "add full width",
        "disable it", or describe a different button.
```

The "Refine" line keeps the conversation primed — subsequent natural-language tweaks re-enter Step A with the previous spec as the starting point. Refinement context lives in-memory only for v0.1; nothing is persisted.

---

## Roadmap

| Version | Scope | Notes |
|---------|-------|-------|
| 0.1.0 | Button only | This release. Validates parse → match → generate. |
| 0.2.0 | Atoms: Alert, Card, Link, Icon-button, Input | Same pipeline; broader registry. |
| 0.3.0 | Composites: Dialog, Popover, Nav, Table | Richer prop shapes (slots, children arrays). |
| 0.4.0 | Compositions | "Card with a primary button inside" — recursion through Step A per nested component. |

## Reference documents

- `references/components/button.md` — Button props, variants, accessibility patterns
- `skills/component-form/SKILL.md` — sister skill; precedent for the auto-trigger and Step B detector flow
