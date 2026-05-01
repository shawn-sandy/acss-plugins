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

If the description names no style, omit the `variant` prop.

> **Note — `variant: "icon"` is intentionally excluded from creator-mode v0.1.** The `Button` reference doc supports it, but icon-only buttons need a resolved icon glyph (not a Lucide-style placeholder) and a meaningful `aria-label`. Generating an icon-less icon button produces a broken control. When the description says "icon button", halt with the v0.2 placeholder from A1 and point the user at `IconButton` once it lands.

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
- Two synonyms collide within an axis (e.g. *"large compact button"* — pick one; never silently keep the last-seen).

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

## Step G — Refinement turns

After a successful generation, the skill holds the resolved spec in conversation memory. The next user turn is treated as a **refinement** rather than a new request when **both** of the following are true:

1. The turn does not name a different component (no "card", "alert", etc.).
2. The turn reads as a delta on the existing button (imperative tweak verbs: "make it…", "swap…", "change…", "add…", "remove…", "drop the…", or single-axis adjectives: "larger", "secondary", "outline").

If either fails, treat the turn as a fresh Step A entry.

### G1. Delta vocabulary

Map common refinement phrasings to a single-axis change. The synonym tables in A2 are reused — the only new vocabulary is the comparative / removal language.

| Phrase | Effect |
|--------|--------|
| `make it larger`, `bigger`, `bump the size` | `size` → next step up (`md` → `lg` → `xl` → `2xl`); halt at the ceiling rather than wrap |
| `make it smaller`, `smaller` | `size` → next step down (`md` → `sm` → `xs`); halt at the floor |
| `swap to <color>`, `change the color to <color>`, `make it <color>` | `color` → resolved value from A2 |
| `make it <variant>` (e.g. `pill`, `outline`, `text`) | `variant` → resolved value from A2 |
| `add full width`, `make it full-width`, `stretch it` | `block: true` |
| `drop the full width`, `not full-width anymore` | `block: false` |
| `disable it`, `mark it disabled` | `disabled: true` |
| `enable it`, `not disabled`, `re-enable it` | `disabled: false` |
| `change the text to "<X>"`, `say "<X>"` instead | `children` → `<X>` |
| `clear the <axis>`, `remove the <axis>`, `drop the <axis>` | unset the named axis (so the prop is omitted on regeneration) |

Anything outside this vocabulary that isn't a clean restatement should round-trip through `AskUserQuestion` rather than being guessed at.

### G2. Regeneration

A refinement turn re-runs Steps A4 (ambiguity check on the merged spec) → D (compose JSX) → F (summary). Steps B and C are skipped because the dependency was already vendored on the first pass.

In **file mode**, the skill rewrites the same `src/components/<Name>.tsx` produced by the original turn. If the user-renamed the file or moved it, ask before overwriting — never search-and-replace blindly.

In **snippet mode**, print a fresh snippet. Do not ask the user to "diff" the previous output; emit the full new JSX so it's still copy-paste ready.

### G3. Summary on refinement

The Step F summary on a refinement turn lists only the **changed** axes plus the unchanged spec for context:

```
Refined AddToCartButton:
  size: md → lg            ← changed
  color=primary  variant=pill  children="Add to cart"   (unchanged)
```

This makes the conversational diff legible without forcing the user to scroll.

### G4. Resetting the context

The user can drop the refinement context by:
- Naming a different component (handed off to a fresh Step A).
- Saying *"start over"*, *"reset"*, or *"forget that"* — the in-memory spec is cleared and the next turn is treated as a fresh prompt.
- Closing the session — refinement state is in-memory only.

---

## Step H — Validation matrix

Run these checks **after** Step A and **before** Step D writes anything. Each row is either a hard halt (bug-out before generation) or a confirmation prompt (`AskUserQuestion`). The skill should not silently accept any of them.

| Combination | Action |
|-------------|--------|
| `variant="icon"` requested | Halt — out of v0.1 scope (see A2 note). Direct user to v0.2 / `IconButton`. |
| `variant="text"` + `block: true` | Confirm — text buttons stretched to full width usually look like a heading; ask "did you mean `outline` or `pill` instead?" |
| `size="xs"` or `size="sm"` + no surrounding-density justification | Confirm — these sizes can fall below the WCAG 2.5.8 44 px target. Note the trade-off in the question. |
| `disabled: true` + no other props | Confirm — a disabled button with default everything is almost always a leftover from a refinement; ask whether the user wants a styled disabled button or just the disabled state. |
| `children` is empty / whitespace-only after A3 | Halt — never write a button with no accessible name. |
| `children` length > 60 chars | Confirm — long button labels are usually a sign the user wants a `Link` or a `<Banner>` callout instead. Offer `Link` (v0.2) as an alternative. |
| Two `color` synonyms in one description (e.g. "primary danger button") | Halt — reject as conflicting. Ask the user which they meant. |
| `block: true` + `variant="text"` + `disabled: true` | Halt — three soft signals collapse into "this is not really a button". Ask the user to describe what they actually want shown. |

When halting, print the offending combination and the rule that triggered it. When confirming, frame the question with the user's resolved spec and the safer alternative as the suggested option.

---

## Step I — Worked examples

Each example shows the user's turn, the parser's resolved spec, and the emitted snippet (snippet mode, default). These double as parser test fixtures — if a future change to A2 / G1 breaks one of these, the skill regressed.

### Example 1 — first generation

> **User:** "Create a primary pill button that says 'Add to cart'."

Resolved spec:
- `color: primary` (from "primary")
- `variant: pill` (from "pill")
- `children: "Add to cart"` (quoted)
- everything else omitted

Output:

```tsx
import Button from './fpkit/button/button'
import './fpkit/button/button.scss'

<Button type="button" color="primary" variant="pill">
  Add to cart
</Button>
```

### Example 2 — refinement

> **User (next turn):** "Make it larger and swap to secondary."

Merged spec:
- `color: primary` → `secondary`
- `size: (omitted)` → `lg` (default `md` → next step `lg`)
- `variant: pill` (unchanged)
- `children: "Add to cart"` (unchanged)

Output:

```tsx
<Button type="button" color="secondary" size="lg" variant="pill">
  Add to cart
</Button>
```

### Example 3 — halt on conflict

> **User:** "Build me a primary danger button labeled Save."

Resolved spec triggers Step H row 7 (two `color` synonyms). The skill halts via `AskUserQuestion`:

> "I see both 'primary' and 'danger' in the description. They map to different `color` props (`primary` vs. `danger`). Which did you mean?"

Nothing is written; the next user turn re-enters Step A with the clarified colour.

### Example 4 — confirm on accessibility risk

> **User:** "Make me a tiny outline button labeled X."

Resolved spec:
- `size: xs`, `variant: outline`, `children: "X"`

Step H row 3 fires (size below 44 px target). The skill asks:

> "An `xs` button can fall below the WCAG 2.5.8 44 px target size. Use `xs` only if it sits inside a dense toolbar with surrounding spacing. Keep `xs`, switch to `sm`, or default to `md`?"

Generation continues only after the user confirms.

---

## Anti-patterns

Things creator mode should **never** do:

1. **Silently default `color`** — the user almost certainly has a specific intent ("a button" without colour usually means *neutral*, but the visual difference between primary and outline-no-colour is large enough that the wrong default is worse than asking).
2. **Generate `variant: icon` without an icon** — there's no icon resolution in v0.1; emitting `<Button variant="icon">X</Button>` ships a broken accessible name.
3. **Bake the description into a comment** — no `// User asked for: …` lines. The reference docs are the source of truth; the user's prompt is conversation context, not provenance.
4. **Refine a spec the user dropped** — once Step G4 fires, the in-memory spec is gone. Don't carry colour from three turns ago into a fresh Step A.
5. **Write to disk on a confirm** — Step H confirmations must round-trip through the user before any file is written. Snippet mode can wait too — easier to re-emit than to retract.
6. **Hard-code the components path** — always run `detect_target.py` (Step B) and use the resolved `componentsDir`. Different projects place `fpkit/` in different roots.

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
