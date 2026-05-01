---
name: component-creator
description: Use when the user describes a UI element in natural language and wants it generated — "create a primary pill button that says Add to cart", "make me a soft warning alert titled 'Heads up' with body 'Your card expires next month'", "build a card with a heading 'Plan' and a primary button labelled Upgrade", "design a small filled outline link". Triggers include "create a <component>", "make me a <component>", "build a <component>", "design a <component>", "generate a <component>", "scaffold a <component>" — for any component with a dedicated reference doc under `references/components/<name>.md`.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.1.0"
  pilot: true
---

# SKILL: component-creator

Generate a self-contained, accessible React snippet (or component file) from a natural-language description. The user describes the element ("primary pill button that says Add to cart", "soft warning alert titled 'Heads up'"); this skill loads the matching component reference doc, parses its Props Interface to learn the component's vocabulary, resolves the user's phrases against that vocabulary, and emits a TSX block that uses the vendored `acss-kit` components.

> **Verified against fpkit source:** delegates to whichever component reference doc the user names. Each reference doc carries its own `@fpkit/acss@6.5.0` verification line; this skill does not invent props or variants — it only resolves natural language against what the matched reference doc already declares.

## Pilot status

This is the second per-component skill in `acss-kit` (after `component-form`). It is pilot-status because the **parser → reference-doc → generator** pipeline is the part that needs validation in real-world usage; the breadth of components is a function of how many reference docs exist (currently 16 user-facing components in `references/components/catalog.md`), not of how many tables this skill hard-codes.

The skill does not maintain a per-component synonym table. The reference doc's Props Interface block is the source of truth; the skill resolves user phrases against it at runtime. Two global tables (colour and size words) collapse common synonyms onto whatever colour-like / size-like prop the matched component declares — see Step A3.

If a description names something that's not in `catalog.md`, the skill halts and says so rather than guessing.

### Components without a dedicated reference doc

The runtime parser (Step A2) reads three blocks the canonical embedded-markdown shape declares: `## Generation Contract`, `## Props Interface`, `## Usage Examples`. Components that exist only as **inline catalog entries** in `catalog.md` (currently `Badge`) use a shorter shape (`**Generation Contract:**`, `**Key Props:**`, `**Usage:**`) that the parser cannot consume reliably.

For v0.1, creator mode supports only components with a dedicated `references/components/<name>.md` file. If the user describes a component that lives only as an inline catalog entry, halt with:

> creator-mode v0.1 supports components that have a dedicated reference doc under `references/components/<name>.md`. `<Component>` currently lives only as an inline entry in `catalog.md` — promote it to a dedicated doc with the `component-author` maintainer skill, then re-run.

This avoids quietly mis-parsing `**Key Props:**` as `## Props Interface`.

---

## Authoring Modes

### Mode 1 — Natural-language description (preferred)

The user describes the component in plain English; this skill derives the component, the prop values, and the content.

Examples:
- "Create a primary pill button that says 'Add to cart'."
- "Make me a soft warning alert titled 'Heads up' with body 'Your card expires next month'."
- "Build a card with a heading 'Plan' and a primary button labelled Upgrade."
- "Design a small outline icon-button with `aria-label` 'Close'."

### Mode 2 — Structured spec (fallback)

The user passes a JSON block describing the component. The skill reads it and generates the snippet directly.

```json
{
  "component": "alert",
  "severity": "warning",
  "variant": "soft",
  "title": "Heads up",
  "children": "Your card expires next month",
  "dismissible": true
}
```

Both modes converge on the same internal contract — `{ component, props, content }` — and produce identical output.

---

## Step A — Parse the description

### A1. Component dispatch

Resolve the description's component noun against `references/components/catalog.md`. The catalog's verification table lists every component the kit ships, with a link to its dedicated reference doc.

Recognised noun-to-component mappings (collapse synonyms before lookup):

| Phrase contains | Resolves to | Reference doc |
|-----------------|-------------|---------------|
| `button`, `btn`, `cta`, `call to action` | Button | `references/components/button.md` |
| `icon button`, `icon-button` | IconButton | `references/components/icon-button.md` |
| `alert`, `banner`, `notification`, `toast`-like static | Alert | `references/components/alert.md` |
| `card`, `panel`, `tile` | Card | `references/components/card.md` |
| `dialog`, `modal` | Dialog | `references/components/dialog.md` |
| `popover`, `tooltip-like static`, `floating card` | Popover | `references/components/popover.md` |
| `link`, `anchor`, `hyperlink` | Link | `references/components/link.md` |
| `image`, `img`, `picture` | Img | `references/components/img.md` |
| `icon` (standalone, not "icon button") | Icon | `references/components/icon.md` |
| `list`, `bullet list`, `ordered list`, `definition list` | List | `references/components/list.md` |
| `table`, `data table`, `grid` (tabular) | Table | `references/components/table.md` |
| `field`, `form field`, `labelled control` | Field | `references/components/field.md` |
| `input`, `text field`, `email field`, `password field` | Input | `references/components/input.md` |
| `checkbox`, `tickbox` | Checkbox | `references/components/checkbox.md` |
| `nav`, `navigation`, `menu bar` | Nav | `references/components/nav.md` |

When the description names a **multi-component composition** ("a card with a button inside", "an alert with two buttons"), match the **outer** component first; the inner component is generated as a refinement turn (Step G) once the outer scaffolds.

When the description names a form-shaped thing ("signup form", "contact form"), hand off to `component-form` rather than trying to compose it here. Print:

> Form-shaped descriptions are handled by the `component-form` skill — say "create a signup form with email and password" or run `/kit-create` only on the individual fields/buttons inside the form.

When no mapping is found, halt:

> No `acss-kit` component matches "<phrase>". Run `/kit-list` to see the catalog. If you want to add a new component, see `references/components/catalog.md` and the `component-author` maintainer skill.

### A2. Load the matched reference doc

Read the matched reference doc and parse three blocks:

1. **`## Generation Contract`** — yields `export_name`, `file`, and `dependencies`. Drives the import path in Step E.
2. **`## Props Interface`** — yields the prop set, each prop's type (union literal, primitive, `React.ReactNode`, callback, etc.), and the JSDoc above it (used as the prompt-help for `AskUserQuestion` confirmations). Treat union-literal types as the prop's canonical vocabulary.
3. **`## Usage Examples`** — used only to detect compound API usage (e.g. `Card.Title`, `Table.Body`). If the examples reference dotted children, mark the component as **compound**; otherwise mark it as **single-element**.

Do not parse the SCSS or accessibility blocks for parsing; those are reference material that the skill cites in Step F's summary.

### A3. Resolve user phrases against the prop set

For every prop in the parsed Props Interface, attempt to resolve a value from the description in this order — first match wins, no silent defaults. The one carve-out is the **state-control prop** set in A3.5 (`open`, `expanded`, `checked`, `visible`), which receives an explicit demo default and a paired summary note rather than halting; this is the only place the skill emits a value the user did not supply.

#### A3.1. Global synonyms (apply to every component)

Two synonym families resolve regardless of which prop name the component uses, by matching the user's phrase to a value the component's union literal already accepts.

**Colour family** — applies to any prop typed as a colour-like union. Detect colour-like props by name (`color`, `colour`, `severity`, `kind`, `tone`, `palette`) or by the literal members of the union being a subset of the recognised colour vocabulary.

| Synonym in description | Maps to first matching literal in {`primary`, `secondary`, `tertiary`, `info`, `success`, `warning`, `danger`, `error`, `default`, `neutral`} |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| `primary`, `main`, `cta` | `primary` |
| `secondary` | `secondary` |
| `tertiary`, `accent` | `tertiary` |
| `info`, `informational` | `info` |
| `success`, `confirm`, `save`, `submit-positive` | `success` |
| `warning`, `caution`, `alert-yellow` | `warning` |
| `danger`, `destructive`, `delete`, `remove`, `error` | `danger` (or `error` if that's the literal the prop accepts) |
| `neutral`, `default`, `muted` | `default` (or `neutral`) |

If the resolved synonym is not in the matched prop's union literal (e.g. user says "tertiary" but the prop is `'primary' \| 'secondary' \| 'danger'`), halt with `AskUserQuestion` listing the supported values. Never silently substitute the closest one.

**Size family** — applies to any prop typed as a size-like union (prop name `size`, `scale`, `density`, or union literal subset of recognised size vocabulary).

| Synonym in description | Maps to first matching literal in {`xs`, `sm`, `md`, `lg`, `xl`, `2xl`} |
|------------------------|--------------------------------------------------------------------------|
| `extra small`, `xs`, `tiny` | `xs` |
| `small`, `sm`, `compact` | `sm` |
| `medium`, `md`, `default`, `regular` | `md` |
| `large`, `lg`, `big` | `lg` |
| `extra large`, `xl` | `xl` |
| `huge`, `2xl`, `2x large`, `xx large` | `2xl` |

Same halt rule: if the resolved size isn't in the prop's union, ask. Some components only accept a subset (e.g. Checkbox is xs/sm/md/lg only) — the union literal is authoritative.

#### A3.2. Per-component union literals

For every other union-typed prop on the component (e.g. Button's `variant: 'text' | 'pill' | 'icon' | 'outline'`, Alert's `variant: 'outlined' | 'filled' | 'soft'`, Card's `as: 'div' | 'section' | 'article'`), match the user's description literally against the union members. Common adjective-style synonyms also apply:

| Synonym group | Resolves to whichever union member matches |
|---------------|--------------------------------------------|
| `pill`, `rounded`, `round`, `capsule` | `pill` |
| `outline`, `outlined`, `bordered`, `ghost` | `outline` or `outlined` |
| `filled`, `solid` | `filled` |
| `soft`, `subtle`, `tonal` | `soft` |
| `text`, `link-style`, `flat` | `text` |
| `dismissible`, `closable`, `with close button` | `dismissible: true` |

If a synonym maps to a literal that doesn't exist on the matched component, **fall back to the literal as written** if it exists on the component, else `AskUserQuestion`. Never invent a literal the component doesn't accept.

#### A3.3. Boolean props

Any prop typed `boolean` is set to `true` when the description contains an affirmative phrase for that prop's name or its JSDoc. Examples:

| Prop name | Triggers `true` when description contains |
|-----------|-------------------------------------------|
| `disabled` | `disabled`, `inactive`, `unavailable` |
| `block` | `full width`, `full-width`, `block`, `stretch`, `100% wide` |
| `dismissible` | `dismissible`, `closable`, `with close button`, `with X button` |
| `pauseOnHover` | omit unless explicitly named — defaults are component-defined |
| `hideIcon` | `no icon`, `hide the icon`, `without an icon` |
| `external` (Link) | `external`, `opens in a new tab`, `target blank` |

Booleans not mentioned are omitted (the component's declared default applies).

#### A3.4. Slot / content props

Props typed `React.ReactNode`, `string`, or marked as content slots in the JSDoc receive content from the description. Common slot vocabulary:

| Slot prop (typical names) | Source in description |
|---------------------------|-----------------------|
| `children` | Quoted string, `that says <X>`, `labeled <X>`, `with text <X>` (see A4) |
| `title`, `heading` | `titled "<X>"`, `with the title "<X>"`, `header "<X>"` |
| `body`, `description`, `message` | `body "<X>"`, `with body "<X>"`, `message "<X>"` |
| `actions` | "with a primary button labelled <X>" → defer to refinement turn (Step G); **omit the prop entirely** so the component's declared default (typically `undefined`) applies, and list the deferred sub-component in the post-generation summary. Do **not** emit `actions={null}` — `null` and `undefined` are not equivalent for a `React.ReactNode` slot. |
| `aria-label` | `with aria-label "<X>"`, or — for icon-only components — required separately (see Step H) |

Compound APIs (Card with `Card.Title` / `Card.Content` / `Card.Footer`, Table with rows/cells, List with items) follow the slot pattern but render as nested elements rather than props — see Step E2.

#### A3.5. State-control props (demo defaults)

Some required props are not "content" but state — they bind the rendered component to caller state (Alert / Dialog `open`, Disclosure `expanded`, Checkbox `checked` when used in controlled mode). For these, the snippet emits an explicit demo default so the rendered example is visible, and Step F's summary lists them as TODOs to wire up. This is the **only** carve-out from the no-silent-defaults rule in A3.

| Prop name (exact match) | Demo default in snippet | Summary note |
|-------------------------|-------------------------|--------------|
| `open` | `true` | "`open` is a demo default — wire it to caller state (e.g. `useState`)." |
| `expanded` | `true` | (same) |
| `visible` | `true` | (same) |
| `checked` | `false` | "`checked` defaults to `false` for the snippet — wire to caller state." |

Two rules:
1. The carve-out applies only to props whose **name** matches the table above. Any other required prop (`alt` on Img, `labelFor` on Field, `href` on Link, `title` on a slot-bearing component) follows the halt-on-unresolved rule from A5.
2. When a state-control prop has an `on*` callback sibling (e.g. `open` + `onDismiss`, `checked` + `onChange`), emit a no-op `() => {}` placeholder for the callback and add a paired summary line so the snippet is paste-ready. Never emit a state-control prop without its callback wired (TypeScript would fail and the snippet would be useless).

#### A3.6. Component-declared safe defaults

Distinct from A3.5 (state placeholders), some required props have a safe default that's **always** correct unless the user explicitly overrides it. These are documented in the matched component's reference doc (typically inline in the Props Interface JSDoc) and emitted unconditionally — no summary note, no halt.

| Component | Prop | Safe default | Source |
|-----------|------|--------------|--------|
| Button | `type` | `"button"` | `references/components/button.md` Props Interface: *"Required — prevents implicit submit in forms"*. The reference doc's TSX Template also defaults to `type = 'button'`. |

The skill detects this case by reading the matched reference doc's Props Interface for a JSDoc starting with `Required — ...` paired with a default value in the TSX Template's destructured signature. If both are present, the default is treated as A3.6-safe.

This is a one-row table at v0.1; v0.2 surfaces the pattern via each reference doc's `## Generation Notes — Creator Mode` block so new components can declare their own safe defaults without editing this skill.

### A4. Content extraction

Quoted strings in the description are the primary source for slot content. Resolution order:

1. Quoted strings in the order they appear: `"Add to cart"`, `'Sign in'`, `“Save”` → assigned to slots in the order the slots are declared in the Props Interface (children first, then title, then body, then actions). When a slot prop is named explicitly in the description ("titled 'Heads up'"), that slot wins regardless of order.
2. The phrases `that says <X>`, `labeled <X>`, `with text <X>`, `for <X>` → assigned to `children` (or the component's primary content slot if `children` is absent).
3. Imperative verb-phrase fallback (e.g. *"a delete button"* → `Delete` for `children`). Capitalise the first letter; do not pluralise.
4. Nothing inferable for a required slot → `AskUserQuestion`. Never write a component with placeholder content.

Preserve the user's casing for explicit quoted strings; sentence-case derived phrases.

### A5. Ambiguity check

Halt with `AskUserQuestion` whenever:
- A required prop (per the Props Interface — e.g. `labelFor` for Field, `alt` for Img, `href` for Link) is unresolved AND its name is **not** covered by A3.5 (state-control demo defaults: `open`, `expanded`, `visible`, `checked`) or A3.6 (component-declared safe defaults: Button's `type`). Props in those carve-outs take their declared default instead of halting.
- A colour-family prop is unresolved AND the description doesn't say "neutral" / "default".
- A synonym maps to two different prop axes (e.g. *"compact"* could be size `sm` or could mean `block: false`).
- Two synonyms collide within an axis (e.g. *"large compact button"* — pick one; never silently keep the last-seen).
- A union-literal resolution falls outside the component's accepted values.

---

## Step B — Resolve the target

Identical to `component-form` Step B. Reuses `scripts/detect_target.py`.

### B1. Run the detector

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <project_root>
```

Parse the JSON. Use `source` and `componentsDir`.

### B2. Branch on source

- `source: "generated"` → proceed to B3.
- `source: "none"` → skip B3 and jump to B4 (clean project).

### B3. Probe required component(s) *(only when source is `generated`)*

Check for the matched component's TSX + SCSS at `<componentsDir>/<file-stem>/<file-stem>.tsx` (and `.scss`). Also probe every entry in the matched component's `dependencies:` (parsed from its Generation Contract — e.g. Dialog depends on Button).

### B4. Bootstrap or vendor missing files

Run `/kit-add <component> [...dependencies]` when **either**:
- `source: "none"` from B1, or
- B3 found any missing files.

After `/kit-add` completes, re-run `detect_target.py` to confirm `source` is now `"generated"` and `componentsDir` is set, then continue to Step C.

If `/kit-add` fails, surface its error and halt — the snippet cannot land without its component dependencies.

---

## Step C — Choose the output mode

Ask once via `AskUserQuestion` (skip if the user already specified):

- **Snippet mode** *(default)* — print a TSX block the user pastes into an existing file. No file is written.
- **File mode** — write a standalone component file at `src/components/<Name>.tsx`. The skill derives `<Name>` from the resolved content (e.g. `"Add to cart"` button → `AddToCartButton`; alert titled `"Heads up"` → `HeadsUpAlert`).

Once chosen, proceed to Step D.

---

## Step D — Validate

Run the validation matrix in Step H against the resolved spec **before** generating. Any halt rule means: stop, print the offending combination, do not write. Any confirm rule means: round-trip through `AskUserQuestion`, only continue once the user accepts.

---

## Step E — Generate output

### E1. Single-element components

For components flagged single-element in A2 (Button, IconButton, Alert, Link, Img, Icon, Input, Checkbox, Field, Popover trigger), emit:

```tsx
<{{COMPONENT}} {{PROPS}}>
  {{CHILDREN}}
</{{COMPONENT}}>
```

Substitution:
- `{{COMPONENT}}` — the `export_name` from the Generation Contract.
- `{{PROPS}}` — one space-separated `key={value}` (or boolean shorthand) per resolved prop, in the order they appear in the Props Interface. Omit unresolved props so the component's declared default applies.
- `{{CHILDREN}}` — the resolved `children` slot from A3.4. Self-closing `<{{COMPONENT}} />` if the component has no children content (e.g. Img, Icon).

For self-closing components and required props (e.g. `Img` requires `alt`, `Field` requires `labelFor`), the absence-check in A5 has already halted if missing.

### E2. Compound components

For components flagged compound in A2 (Card, Table, List), emit the root + the slots the description named, in document order. The reference doc's Usage Examples block defines the slot order:

Card example:
```tsx
<{{COMPONENT}}>
  {{TITLE_SLOT?}}
  {{CONTENT_SLOT}}
  {{FOOTER_SLOT?}}
</{{COMPONENT}}>
```

Where each `{{*_SLOT}}` expands to the dotted child (e.g. `<Card.Title>Plan</Card.Title>`) only when the description provided content for that slot. Skip empty slots — never emit a placeholder.

If the description names a sub-component the matched compound doesn't expose ("a card with a switch"), halt: the user is asking for a composition this skill can't synthesise from one prompt. Suggest generating each piece separately and refining (Step G).

### E3. Imports (file mode only)

Compute the relative path from `src/components/<Name>.tsx` to the components directory (default `src/components/fpkit`, giving `./fpkit`). Use `path.relative()` semantics; fall back to `./fpkit` if `.acss-target.json` is absent.

Wrap the JSX as:

```tsx
// <Name>.tsx — generated by component-creator skill
import {{COMPONENT}} from '<relative>/<file-stem>/<file-stem>'
import '<relative>/<file-stem>/<file-stem>.scss'

export default function {{NAME}}({{HANDLER_SIGNATURE}}) {
  return (
    {{JSX_FROM_E1_OR_E2}}
  )
}
```

`{{HANDLER_SIGNATURE}}` is the typed callback prop forwarded to the rendered component when the component declares one (e.g. `onClick` for Button, `onDismiss` for Alert). When the component has no callback, omit the parameter and the wrapper takes no props. Wire-through is so the file isn't dead-on-arrival; users replace the signature with whatever fits their route/page.

### E4. Snippet mode

Print **the import lines followed by the JSX from E1 or E2**, both inside a single fenced TSX block, so the user can paste a self-contained snippet. Snippet mode does **not** reuse E3's relative path — E3 is anchored at `src/components/<Name>.tsx`, but a snippet is pasted into an arbitrary file (often `src/App.tsx`, a route file, or a layout) where that anchor doesn't apply.

Resolve the import path in this order:

1. **`stack.entrypointFile` from `.acss-target.json`** — when present, compute the relative path from `<entrypointFile>` to `componentsDir`. For a typical Vite project with `entrypointFile: src/App.tsx` and `componentsDir: src/components/fpkit`, this gives `./components/fpkit`.
2. **No stack info** — fall back to a path relative to the project root (e.g. `src/components/fpkit/<file-stem>/<file-stem>`) and prepend a one-line comment to the snippet noting that the user should adjust the import to match the file they're pasting into.

The fallback comment looks like:

```tsx
// adjust import path to your file's location relative to <componentsDir>
import Button from 'src/components/fpkit/button/button'
```

When the entrypoint-relative path resolves cleanly, omit the comment — the snippet is paste-ready as-is for files at that depth. Do **not** write to disk in either branch.

### E5. Atomic generation

Build the entire output in memory; write to disk only on success (file mode). If any step in A or D fails, surface the error and write nothing.

---

## Step F — Accessibility

The generated component is WCAG 2.2 AA by construction because it delegates to the vendored component. Each reference doc's `## Accessibility` section is the authoritative spec; this skill only enforces that the **generation** doesn't strip those guarantees:

- Required-prop halts (A5) prevent emitting components with missing accessible names (`aria-label` on icon-only controls; `alt` on Img; `labelFor` on Field).
- Boolean disabled flags use the typed `disabled` prop, never the raw HTML attribute, so `aria-disabled` + tab-order patterns survive.
- Compound components (E2) emit slot content only when provided, so empty `<Card.Title>` placeholders never ship and never break the aria-labelledby chain.

The Step G summary's "Refine" line includes a link back to the matched reference doc's Accessibility section so users can verify before pasting.

---

## Step G — Refinement turns

After a successful generation, the skill holds the resolved spec in conversation memory. The next user turn is treated as a **refinement** rather than a new request when **both** of the following are true:

1. The turn does not name a different component (no "card", "alert", etc. when the previous was a button).
2. The turn reads as a delta on the existing spec (imperative tweak verbs: "make it…", "swap…", "change…", "add…", "remove…", "drop the…", or single-axis adjectives: "larger", "secondary", "outline").

If either fails, treat the turn as a fresh Step A entry.

### G1. Delta vocabulary

The synonym tables in A3 are reused — the only new vocabulary is the comparative / removal language. Each delta operates on whichever prop axis the matched component declares (so "make it larger" works on any component with a size-family prop; on a component without one, the skill responds that the axis isn't tunable).

| Phrase | Effect |
|--------|--------|
| `make it larger`, `bigger`, `bump the size` | size-family prop → next step up; halt at the ceiling |
| `make it smaller`, `smaller` | size-family prop → next step down; halt at the floor |
| `swap to <colour>`, `change the colour to <X>`, `make it <X>` | colour-family prop → resolved value from A3.1 |
| `make it <variant>` (e.g. `pill`, `outline`, `soft`, `filled`) | variant-style prop → resolved from A3.2 |
| `add full width`, `make it full-width`, `stretch it` | `block: true` (or whichever boolean prop matches) |
| `drop the full width`, `not full-width anymore` | `block: false` |
| `disable it`, `mark it disabled` | `disabled: true` |
| `enable it`, `not disabled`, `re-enable it` | `disabled: false` |
| `change the text to "<X>"`, `say "<X>"` instead | primary content slot → `<X>` |
| `change the title to "<X>"`, `retitle "<X>"` | `title` slot → `<X>` |
| `clear the <axis>`, `remove the <axis>`, `drop the <axis>` | unset the named axis (so the prop is omitted on regeneration) |
| `add a primary button labelled <X>` (compound only) | populate `actions` / nested-slot with the new sub-component, generated as a sub-call to Step A |

Anything outside this vocabulary that isn't a clean restatement should round-trip through `AskUserQuestion` rather than being guessed at.

### G2. Regeneration

A refinement turn re-runs A5 (ambiguity check on the merged spec) → D (validate) → E (compose JSX) → G3 summary. Steps B and C are skipped because the dependencies were already vendored on the first pass.

In **file mode**, the skill rewrites the same `src/components/<Name>.tsx` produced by the original turn. If the user renamed or moved the file, ask before overwriting — never search-and-replace blindly.

In **snippet mode**, print a fresh snippet. Do not ask the user to "diff" the previous output; emit the full new JSX so it's still copy-paste ready.

### G3. Summary on refinement

Lists only the **changed** axes plus the unchanged spec for context:

```text
Refined HeadsUpAlert:
  variant: outlined → soft     ← changed
  severity=warning  title="Heads up"  body="Your card expires next month"   (unchanged)
```

### G4. Resetting the context

The user can drop the refinement context by:
- Naming a different component (handed off to a fresh Step A).
- Saying *"start over"*, *"reset"*, or *"forget that"* — the in-memory spec is cleared.
- Closing the session — refinement state is in-memory only.

---

## Step H — Validation matrix

Run after Step A and before Step E writes anything. Each row is either a hard halt (bug-out before generation) or a confirmation prompt (`AskUserQuestion`).

### H1. Generic rules (every component)

| Combination | Action |
|-------------|--------|
| Required prop unresolved (per Props Interface, excluding A3.5 state-control and A3.6 safe-default props) | Halt — the absence-check in A5 already fires; H1 is the safety net. |
| Resolved value not in the prop's union literal | Halt — list the supported values. |
| Two same-axis synonyms in one description (e.g. "primary danger button", "small large alert") | Halt — reject as conflicting. |
| Slot content empty / whitespace-only after A4 | Halt — never write a component with no accessible content. |
| Slot content > 80 chars | Confirm — long inline labels are usually a sign the user wants a different component. Offer the most likely alternative (Button-text → Alert; Alert-title → Card; Link-text → Alert or Card) drawn from `catalog.md`. |

### H2. Component-flagged rules

The skill loads any `## Generation Notes — Creator Mode` block from the matched reference doc (when present) and applies its halt/confirm entries verbatim. This lets each reference doc declare its own creator-mode invariants without bloating this skill. Examples a reference doc might declare:

- Button: confirm on `size: xs|sm` due to WCAG 2.5.8 target-size minimum.
- IconButton: halt unless `aria-label` is resolved.
- Img: halt unless `alt` is resolved (the Props Interface already requires it; H2 is just the friendlier surface).
- Dialog: confirm unless `open` is wired through to caller state (a hard-coded `open={true}` ships a dialog that can't be closed).

If the matched reference doc has no `## Generation Notes — Creator Mode` block, only H1 applies.

When halting, print the offending combination and the rule that triggered it. When confirming, frame the question with the user's resolved spec and the safer alternative as the suggested option.

---

## Step I — Worked examples

Each example shows the user's turn, the parser's resolved spec, and the emitted snippet (snippet mode, default). These double as parser test fixtures — if a future change to A3 / G1 breaks one of these, the skill regressed.

### Example 1 — Button (single-element)

> **User:** "Create a primary pill button that says 'Add to cart'."

Resolved spec:
- component: `button`
- `color: primary`, `variant: pill`, `children: "Add to cart"`
- `size`, `block`, `disabled` omitted

Output:

```tsx
import Button from './fpkit/button/button'
import './fpkit/button/button.scss'

<Button type="button" color="primary" variant="pill">
  Add to cart
</Button>
```

### Example 2 — Alert (single-element with multiple slots)

> **User:** "Make me a soft warning alert titled 'Heads up' with body 'Your card expires next month' that's dismissible."

Resolved spec:
- component: `alert`
- `severity: warning` (colour-family resolves onto `severity`, since Alert has no `color` prop)
- `variant: soft`
- `title: "Heads up"` (named slot wins over positional)
- `children: "Your card expires next month"` (body / message)
- `dismissible: true`
- `open: true` (A3.5 state-control demo default, paired with a no-op `onDismiss` callback per A3.5 rule 2; summary flags both as wire-to-caller-state TODOs)

Output:

```tsx
import Alert from './fpkit/alert/alert'
import './fpkit/alert/alert.scss'

<Alert
  open={true}
  severity="warning"
  variant="soft"
  title="Heads up"
  dismissible
  onDismiss={() => {}}
>
  Your card expires next month
</Alert>
```

Summary notes that `open` and `onDismiss` should be wired to caller state.

### Example 3 — Card (compound)

> **User:** "Build a card with a heading 'Plan' and content 'Premium tier with all features.'"

Resolved spec:
- component: `card` (compound)
- `Card.Title`: `"Plan"`
- `Card.Content`: `"Premium tier with all features."`
- `Card.Footer`: omitted (description doesn't mention one)

Output:

```tsx
import Card from './fpkit/card/card'
import './fpkit/card/card.scss'

<Card>
  <Card.Title>Plan</Card.Title>
  <Card.Content>Premium tier with all features.</Card.Content>
</Card>
```

### Example 4 — Refinement turn

> **User (next turn after Example 1):** "Make it larger and swap to secondary."

Merged spec:
- `color: primary` → `secondary`
- `size: (omitted)` → `lg` (default `md` → next step `lg`)
- `variant: pill` (unchanged), `children: "Add to cart"` (unchanged)

Output:

```tsx
<Button type="button" color="secondary" size="lg" variant="pill">
  Add to cart
</Button>
```

### Example 5 — Halt on conflict

> **User:** "Build me a primary danger button labeled Save."

Two same-axis synonyms (H1 row 3 fires). The skill halts via `AskUserQuestion`:

> "I see both 'primary' and 'danger' in the description. They map to different `color` values (`primary` vs. `danger`). Which did you mean?"

Nothing is written; the next user turn re-enters Step A with the clarified colour.

### Example 6 — Halt on out-of-catalogue

> **User:** "Make me a kanban column with three cards."

A1 finds no `acss-kit` component for "kanban column" and halts:

> "No `acss-kit` component matches 'kanban column'. Run `/kit-list` to see the catalog. To add a kanban-column component, see `references/components/catalog.md` and the `component-author` maintainer skill."

---

## Anti-patterns

Things creator mode should **never** do:

1. **Silently default a colour-family prop** — the user almost certainly has a specific intent. The wrong default is worse than asking.
2. **Substitute a literal the component doesn't declare** — if the user says "tertiary" and the union is `'primary' | 'secondary' | 'danger'`, halt; don't pick the closest one.
3. **Bake the description into a comment** — no `// User asked for: …` lines. The reference docs are the source of truth.
4. **Refine a spec the user dropped** — once Step G4 fires, the in-memory spec is gone. Don't carry colour from three turns ago into a fresh Step A.
5. **Write to disk on a confirm** — Step H confirmations must round-trip through the user before any file is written.
6. **Hard-code the components path** — always run `detect_target.py` (Step B) and use the resolved `componentsDir`.
7. **Generate compound slots the user didn't name** — `<Card.Footer>` / `<Card.Title>` only when the description provided content. Empty slots break the visual rhythm and the aria-labelledby chain.
8. **Synthesise a multi-component layout from a single prompt** — "card with a switch and a slider" is two refinement turns away from "card", not one prompt.

---

## Roadmap

| Version | Scope | Notes |
|---------|-------|-------|
| 0.1.0 | Any single-element or compound component in `references/components/catalog.md` | This release. The parser is reference-doc-driven. |
| 0.2.0 | `## Generation Notes — Creator Mode` block on every reference doc | Each reference doc declares its own H2 invariants (size minimums, required slots) instead of the skill carrying a per-component table. |
| 0.3.0 | Multi-component compositions in one prompt | "Card with a primary button inside" → root + nested generation in a single Step A pass. |
| 0.4.0 | Project-convention awareness | Read the user's existing `src/components/` for naming + casing conventions; match them. |

## Reference documents

- `references/components/catalog.md` — the dispatch table for A1
- Every reference doc under `references/components/*.md` — Props Interface and Usage Examples drive the parser
- `skills/component-form/SKILL.md` — sister skill; precedent for the auto-trigger and Step B detector flow
