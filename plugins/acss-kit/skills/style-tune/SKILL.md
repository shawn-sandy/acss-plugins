---
name: style-tune
description: Use when the user asks to adjust visual feel of a named acss-kit component or theme role using natural language. Triggers must reference a component (button, card, alert, dialog, input, nav) or a theme role (primary, accent, danger, warning, info, success, brand) — bare adjectives in prose contexts do NOT trigger. Phrases include "warmer button", "softer card", "calmer alert", "more spacious cards", "more elevated dialog", "tone down the primary", "deeper accent for primary", "make buttons feel sharper", "give the input a quieter look", "bolder primary", "smaller buttons", "bigger dialog", "narrower dialog", "wider input", "shorter dialog", "taller dialog". Routes between theme-role edits (delegated to /theme-update with WCAG pre-validation) and component SCSS token edits (--btn-*, --card-*, --alert-*, --dialog-*, --input-*, --nav-*). Pilot per-feel skill — promoted because feel-based iteration is high-touch and benefits from auto-discoverable triggering.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.4.1"
  pilot: true
---

# SKILL: style-tune

Adjust the visual feel of acss-kit components or theme roles using
natural language. Routes a free-form prompt ("make the dialog feel
more elevated") to either a theme-role edit (delegated to
`/theme-update`) or a component SCSS token edit, applies the delta
from the intent vocabulary, and atomically validates before writing.

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest
> tagged ref to npm `6.6.0`). The skill operates on the same token
> surface as the components and styles skills — it does not introduce
> new tokens, only adjusts existing ones.

## Pilot status

This is the second per-feel skill in `acss-kit` (after
`component-form`). It exists to validate natural-language adjective
triggering on a token surface. Vocabulary, trigger phrases, and
component coverage may shift in 0.4.x point releases as real-world
usage surfaces gaps.

---

## Two layers, one skill

The kit exposes two parallel token surfaces:

- **Theme-level roles** — 18 semantic `--color-*` properties in
  `src/styles/theme/{light,dark}.css` (and `brand-*.css`), governed by
  `/theme-update` and validated against WCAG 2.2 AA contrast pairs.
- **Component-level tokens** — `--btn-*`, `--card-*`, `--alert-*`,
  `--dialog-*`, `--input-*`, `--nav-*` declarations inside each
  vendored component SCSS file at
  `<componentsDir>/<component>/<component>.scss`.

Step A resolves the named subject from the prompt and routes the edit
to the appropriate layer.

---

## Step A — Resolve intent

### A0. Load the intent vocabulary

Read `${CLAUDE_PLUGIN_ROOT}/skills/style-tune/references/intent-vocabulary.md`.
Each row maps a modifier (and synonyms) to a token family + canonical
delta + "var-only fallback" route.

### A1. Tokenize the prompt and match modifiers

Parse the prompt for vocabulary matches. Each match yields a
`(token-family, delta, layer-hint)` tuple. Record the matches; do not
write yet.

### A2. Resolve the subject

Map subject nouns to a target layer:

| Subject in prompt | Layer | Target |
|---|---|---|
| `primary`, `accent`, `danger`, `warning`, `info`, `success`, `brand`, `theme`, `app` | theme | named role (or `--color-primary` for "the theme") |
| `button` / `btn`, `card`, `alert`, `dialog`, `input`, `nav`, `form` | component | named component, edit globally |
| Bare `this` / `it` / `the component` / `everything` | ambiguous | AskUserQuestion to choose |

"This button" / "the button" / "buttons" all map to a **global** edit
of the component's SCSS file. The skill never emits inline `style={...}`
props or scoped variant classes.

### A3. Confirm low-confidence intents

Use `AskUserQuestion` (one consolidated question, ≤ 4 options) when:

- The prompt is a single bare adjective with no subject ("warmer").
- A modifier has multiple plausible token families (e.g. "louder" →
  border vs shadow vs both).
- Modifiers contradict each other in one prompt ("calmer but bolder").
- The subject is "alert" and the modifier is a color modifier — ask
  whether to tune base tokens only (default) or to include the four
  severity variants (`--alert-{info,success,warning,error}-*`).

For unambiguous prompts, skip A3 and proceed.

---

## Step B — Verify dependencies and locate files

### B1. Detect the target project

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <project_root>`.
Capture `source` and `componentsDir` from the JSON output.

### B2. Branch on layer

**Theme layer:**

1. Locate `src/styles/theme/light.css` and `src/styles/theme/dark.css`.
   When **both** exist, edit both with the same OKLCH delta
   (auto-mirror — same perceptual shift, mode-appropriate hex per
   file). When only one exists, edit that one.
2. `brand-*.css` files are NOT edited unless the user names the brand
   explicitly ("warmer acme brand", "tone down acme primary"). When
   brand files are present and the user did not name them, surface a
   hint in Step F: "Brand `acme` is present and unchanged. To tune
   it, say 'tune the acme brand'."
3. If no theme files are found, halt: "No theme files at
   `src/styles/theme/`. Run `/theme-create #seedhex` first."

**Component layer:**

1. Require `source: "generated"` from B1.
2. Probe `<componentsDir>/<component>/<component>.scss`. If missing,
   halt: "Component `<name>` isn't vendored yet. Run
   `/kit-add <name>` first." Do not auto-install — this is a styling
   task, not a scaffolding task.
3. Reject components outside the v1 coverage list (button, card,
   alert, dialog, input, nav). Halt with:
   "Component `<name>` doesn't have a token mapping in v1. Open an
   issue to request coverage."

---

## Step C — Compute deltas

### C0. Read current state

Always re-read current values from disk — the skill is stateless
across invocations. Iteration ("warmer" then "cooler") works because
each pass starts from the just-written value.

### C1. Theme layer

For each `(role, delta)` from Step A:

1. Read the current hex from each in-scope theme file via
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/css_to_tokens.py <theme-file>`.
2. Compute the new hex via
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/oklch_shift.py <currentHex>
   --hue=±deg --chroma=×float --lightness=±float`. Capture `hex` from
   the JSON output. If `oklch_shift.py` exits 1 (out-of-gamut),
   surface its `reasons` in Step F's summary and skip that role for
   that file.
3. **Paired-role rule:** when shifting `--color-primary`, always shift
   `--color-primary-hover` by the same OKLCH delta. Treat the pair as
   a single batch entry — both values must apply, or both must revert.
4. **Dark-mirror rule:** when both `light.css` and `dark.css` are in
   scope, run the same OKLCH delta against each file's starting hex.
   The two files yield mode-appropriate hex values from a shared
   perceptual shift.
5. Build the full plan as a list of `(file, role, oldHex, newHex)`
   tuples. Do **not** invoke `/theme-update` yet — Step D pre-validates.

### C2. Component layer

For each `(component, family, delta)` from Step A:

1. `Grep` the component SCSS for the targeted token name(s) and read
   the current value(s).
2. **Scalar values** (rem, unitless, hex literals): apply the
   canonical delta from intent-vocabulary directly. Respect clamp
   ranges (radius `[0.125rem, 1rem]`; padding multipliers; etc.).
3. **Var-only references** (`--alert-bg: var(--color-surface, …)`):
   do NOT edit this declaration. Look up the vocabulary's "var-only
   fallback" column and route the edit to the underlying theme role
   instead. Add a note to Step F: "Tuning `<component-token>` requires
   changing `<theme-role>`, which affects every component using it."
4. **Shadow tokens:** the vocabulary lists explicit preset values for
   `flat`, `stronger`, `inset`, etc. — no procedural arithmetic on
   multi-stop shadows. See `references/intent-vocabulary.md` for the
   full preset enumeration.
5. **Compound presets** (rows flagged `preset: true` — inviting,
   businesslike, playful): expand into the listed multi-family
   deltas; apply each independently.
6. Preserve `var(--x, fallback)` wrappers everywhere — only the
   declaration's RHS may change.

---

## Step D — Apply edits

Apply immediately. No preview round-trip. Users review via the Step
F summary or `git diff`.

### D0. Pre-validate the theme batch

Before any `/theme-update` invocation, stage the entire theme batch:

1. Create a tmp directory via `mktemp -d`.
2. For each in-scope theme file, copy it into the tmp dir and apply
   the proposed `--color-<role>` edits in place (preserve comments
   and whitespace).
3. Run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_theme.py <staged-file>`
   on each staged copy.
4. If **any** contrast pair fails on **any** file, halt the entire
   batch — do not write anything to disk. Print the failure(s),
   the offending role/file, and a hint: "Re-run with a smaller delta
   (e.g. `chroma × 0.85` instead of `× 0.75`), or pick an explicit
   hex via `/theme-update`."

This guarantees atomicity: paired roles never desync, light/dark stay
in sync, and a failed contrast pair never leaves the project in a
half-applied state.

### D1. Theme layer

With the batch pre-validated, invoke `/theme-update <file>
--color-<role>=#<hex> [...]` once per theme file. Existing command
writes in place. `/theme-update` runs `validate_theme.py` again
internally; given D0, that should always pass.

If `/theme-update`'s post-write validation ever fires (rounding
mismatch between `oklch_shift.py` and `validate_theme.py`), surface
the discrepancy as a bug and roll back manually via `git`.

### D2. Component layer

Build the entire updated SCSS file in memory; `Edit` atomically.

Critical safety rules:

- Never strip a `var()` wrapper — only the declaration's RHS may
  change.
- Never rename a token.
- Never inline a hex literal where a `var(--color-*, …)` reference
  exists.
- Never edit lines outside the targeted `--{c}-*` declarations.

### D3. Multi-target edits

When one modifier touches multiple tokens (e.g. "more elevated dialog"
→ `--dialog-shadow` + `--dialog-radius`), batch into one Edit pass per
file.

---

## Step E — Validate and revert

### E1. Theme layer

D0's pre-validation guarantees no in-flight reverts. `/theme-update`'s
own validation is a safety net.

### E2. Component layer

Structural integrity check after each Edit:

1. Re-`Grep` the file for `var(` occurrences — count must be unchanged
   before and after.
2. Re-`Grep` for each edited token name — must appear exactly once on
   a declaration LHS.

On failure, restore from the in-memory pre-edit copy and surface the
diff. Halt the batch.

### E3. Idempotency

If the computed value equals the current value within tolerance (hex
equality, or rem within 0.0001), skip the write and report "already
at target" in Step F. This does NOT prevent cumulative drift across
iterations — `× 0.75` then `× 1.25` lands at `× 0.9375`, not the
original. Document this in the Step F "Next" hint when a chroma or
scale modifier is applied.

### E4. Drift detection

After applying any theme-layer color shift, inspect the post-edit
OKLCH of the tuned role. If `chroma < 0.05` OR
`|hue − palette-derived hue| > 30°`, append a drift hint to Step F:
"Note: `--color-<role>` has drifted from its palette-derived value.
Consecutive tunes accumulate hex round-trip noise; if the result
feels off, run `/theme-create #seedhex` to reset."

The "palette-derived hue" reference is the seed used by the most
recent `/theme-create` invocation. If unknown, derive an approximate
reference by reading the current `--color-success` hex (which is hue
145° by construction) and computing the implied seed-hue offset.

---

## Step F — Summary

Print a structured table mirroring `/theme-update`'s output:

```
Layer:       <theme | component | both>
Files:       <list>

Modifier         Token / Role               Old           New           Status
warmer           --color-primary            #2563eb       #3265ec       accepted
warmer           --color-primary-hover      #1e4dc7       #294fc8       accepted
softer           --btn-radius               0.375rem      0.5625rem     accepted
calmer           --color-danger             #dc2626       #d8413b       reverted (contrast)

Notes:
  - Tuning --alert-bg routed to --color-surface (affects all components).
  - Brand `acme` is present and unchanged. To tune it, say "tune the acme brand".

Next:
  - Try "now go a touch sharper" to dial back radius.
  - Or use /theme-update for explicit hex values.
```

Always include the "Next" hint so users know iteration is cheap and
bounded.

---

## Reference documents

- `references/intent-vocabulary.md` — full modifier → token-family
  table with deltas, clamp ranges, var-only fallbacks, and worked
  examples.
- `${CLAUDE_PLUGIN_ROOT}/skills/styles/references/role-catalogue.md`
  — semantic role list and contrast pairings.
- `${CLAUDE_PLUGIN_ROOT}/skills/styles/references/palette-algorithm.md`
  — OKLCH lightness targets and state-color hue offsets.
- `${CLAUDE_PLUGIN_ROOT}/skills/components/references/css-variables.md`
  — full component-token surface.
