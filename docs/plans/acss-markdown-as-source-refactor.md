# Refactor: markdown-as-source for components + sunset @fpkit/acss + retire JSON schemas

> **⚠️ Superseded by [`acss-consolidate-to-acss-kit.md`](./acss-consolidate-to-acss-kit.md).**
>
> Phases 0, 1, and 4 of this plan were inherited and shipped as part of the consolidation in `acss-kit@0.3.0`. Phases 2 and 3 (npm soft-deprecation in `acss-app-builder` + cross-plugin `/app-form` delegation) were dropped because `acss-app-builder` was deleted entirely. This document is preserved as a historical record of the markdown-as-source design decisions.

## Context

Today the three acss plugins carry a mixed internal representation: TSX template files in `assets/`, an `@fpkit/acss` npm fallback path, and JSON schemas as user-facing input contracts. This refactor unifies the internal representation around **markdown specs as the source of truth**: each component is a markdown document containing the Generation Contract plus the actual TSX/SCSS code embedded as fenced code blocks, plus a required `## Accessibility` section. The model reads markdown and emits React TSX into the user's Vite+React+TS project — the plugin still scaffolds React apps, but the source-of-truth shifts from `.tsx.tmpl` files and an npm package to markdown.

Three coupled motivations:
1. **The npm path** in [`detect_component_source.py:67-101`](plugins/acss-app-builder/scripts/detect_component_source.py:67) ties our lifecycle to an external release cadence we don't control. Pin the current-latest `@fpkit/acss` version as a documented compatibility ceiling, then sunset.
2. **JSON-schema authoring** ([`schema.example.json`](plugins/acss-app-builder/assets/forms/schema.example.json), [`theme.schema.json`](plugins/acss-theme-builder/assets/theme.schema.json)) is high-friction relative to natural-language description or filling a CSS-native template.
3. **TSX template assets** like [`form-from-schema.tsx.tmpl`](plugins/acss-app-builder/assets/forms/form-from-schema.tsx.tmpl) and [`ui.tsx`](plugins/acss-kit-builder/assets/foundation/ui.tsx) split the source of truth across multiple file types. Markdown specs with embedded code blocks consolidate spec, contract, code, and accessibility guidance into one human-readable document.

**Scope discipline:** components + form template convert to markdown. Pages, patterns, layouts, and themes stay as their current TSX/CSS asset format — they're out of scope for this refactor.

## Objective

Land a coordinated refactor across all three plugins that (a) converts `acss-kit-builder` component artifacts to markdown-with-embedded-code, with **only Form** promoted to its own skill in this release as a pattern pilot, (b) converts `acss-app-builder`'s form template to a kit-builder-hosted skill that the `/app-form` command delegates to across plugin boundaries, (c) declares a sunset path for the `@fpkit/acss` npm dependency without breaking projects on the current path, and (d) retires JSON schemas as user-facing input contracts. All three plugins bump to `0.2.0`.

## Steps

### Phase 0 — Pre-refactor audit

1. **Capture the version ceiling.** Run `npm view @fpkit/acss version` and record the captured string. Why: the documented sunset target needs to be a real published version, not a guess.
2. **Audit `assets/foundation/ui.tsx` consumers.** Run `grep -rn "foundation/ui.tsx" plugins/` across all three plugins to find any scripts, command files, or reference docs that read or import that path. Inventory consumers before Phase 1 step 9 deletes the file. Why: silent deletion would break any chain that depends on it.
3. **Audit `.acss-target.json` schema.** Read [`plugins/acss-app-builder/scripts/detect_component_source.py`](plugins/acss-app-builder/scripts/detect_component_source.py) and any kit-builder script that writes `.acss-target.json`. Confirm the field set (currently `componentsDir`) doesn't change as part of this refactor. If it does change, document a migration step. Why: mixed-version projects (0.1.x kit-builder + 0.2.0 app-builder, or vice-versa) must keep reading/writing compatible shapes.

### Phase 1 — Convert kit-builder components to markdown-as-source

4. **Establish the canonical embedded-markdown shape.** Edit [`plugins/acss-kit-builder/skills/acss-kit-builder/references/components/button.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/button.md) to add three required sections after the existing Generation Contract:
   - `## TSX Template` — fenced ```tsx``` code block containing the full component implementation that `/kit-add` writes into the user's project. Imports use the `{{IMPORT_SOURCE:...}}` placeholder pattern; substitution happens at write time.
   - `## SCSS Template` — fenced ```scss``` block with the component's styles, using CSS variables with hardcoded fallbacks per the existing pattern.
   - `## Accessibility` — required section per the new spec contract. Documents keyboard interaction, ARIA roles/attributes, focus management, screen reader behavior, and the relevant WCAG 2.2 AA criteria. For Button: keyboard `Enter`/`Space` activation, `aria-disabled` (not `disabled`) for "submitting" states, focus-visible styling, 44×44px minimum touch target.
   This becomes the canonical embedded-markdown shape for every component reference and every component skill. Why: consolidates spec, contract, code, and accessibility into one file; eliminates the gap where Claude has to guess implementation or a11y patterns from prose alone.
5. **Backfill verification workflow per existing component.** Before authoring TSX/SCSS code blocks in any existing reference doc, perform this sequence per component:
   1. Resolve the captured `@fpkit/acss` ceiling version (Phase 0 step 1) to the matching immutable source revision — a git tag or commit SHA in the `shawn-sandy/acss` repo. WebFetch from `https://github.com/shawn-sandy/acss/blob/<tag-or-sha>/packages/fpkit/src/<component>/...` (not `blob/main`). If no matching tag/commit exists for that npm version, inspect the published npm tarball for that exact version instead.
   2. Read the existing reference doc's prose / Generation Contract for the component.
   3. Diff intent: confirm the existing prose accurately describes the fpkit behavior. Note any drift.
   4. Author the `## TSX Template` and `## SCSS Template` blocks to match fpkit semantics (with relative-path imports — never `@fpkit/acss`).
   5. Author the `## Accessibility` section per the canonical shape.
   6. Log verification status in [`references/components/catalog.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/catalog.md): `verified: true | drift-noted: <description> | new`.
   Why: prevents copying existing inaccuracies forward; produces an audit trail that future contributors can extend.
6. **Backfill the existing simple-component reference docs.** Apply Phase 1 step 5 to: Button (already extended in step 4 — verify), Card (compound pattern: `Card`, `Card.Title`, `Card.Content`, `Card.Footer` — all in a single `card.tsx` file), Alert, Checkbox, Field, Icon, Link, List, Input, Dialog, Popover, Table. (Form is in step 8.) Each gains TSX/SCSS/Accessibility sections.
7. **Vendor the four missing simple components** as new markdown reference docs following the canonical shape:
   - [`references/components/icon-button.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/icon-button.md)
   - [`references/components/img.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/img.md)
   - Confirm Popover and Table from step 6 are net-new docs if they don't already exist.
   Use the canonical fpkit source on GitHub (full URLs per repo policy) as the design reference.
8. **Promote Form to its own skill (pilot).** Create [`plugins/acss-kit-builder/skills/component-form/SKILL.md`](plugins/acss-kit-builder/skills/component-form/SKILL.md) with frontmatter:
   ```
   name: component-form
   description: Use when the user asks to create a form, scaffold a form, build a signup/contact/login form, generate form components, add form validation, or design accessible form layouts. Triggers include "create a form", "add a form", "build a form component", "scaffold a form", "form with fields".
   ```
   Body follows the canonical embedded-markdown shape (Generation Contract, TSX Template, SCSS Template, Accessibility) plus a `## Field Renderers` section with one fenced ```tsx``` block per field type (text/email/password, select, textarea, checkbox), pulled from [`form-from-schema.tsx.tmpl`](plugins/acss-app-builder/assets/forms/form-from-schema.tsx.tmpl), and an `## Authoring Modes` section describing both the natural-language path and the legacy JSON path (preserved for backward compatibility). Why: per Round 1, this is a pattern pilot — adopt for additional components only after observing trigger reliability. Skill is colocated under kit-builder per Round 3, so all component-template logic has one home.
9. **Convert [`assets/foundation/ui.tsx`](plugins/acss-kit-builder/assets/foundation/ui.tsx) to a markdown spec** at [`references/components/foundation.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/foundation.md) with the polymorphic base component embedded as a fenced ```tsx``` block. Include the Accessibility section per the canonical shape. **Delete `assets/foundation/ui.tsx`** only after the Phase 0 step 2 audit confirms no remaining consumers.
10. **Update [`references/components/catalog.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/catalog.md)** to list every component with its location (reference path or skill path), verification status from step 5, and a one-line summary. Form's entry points at the new skill path.
11. **Update [`plugins/acss-kit-builder/skills/acss-kit-builder/SKILL.md`](plugins/acss-kit-builder/skills/acss-kit-builder/SKILL.md)** to:
    - Document the markdown-as-source pattern (how to read TSX/SCSS code blocks, perform `{{...}}` substitution, write to user's project).
    - Document the "Reference vs Skill" hybrid rule: simple components are references; the Form pilot is a skill. Future component skill candidates require demonstrated trigger reliability.
    - Document the required `## Accessibility` section.
12. **Add a contributor recipe.** Append a new "Adding a new component" section to [`plugins/acss-kit-builder/README.md`](plugins/acss-kit-builder/README.md) walking through: pick a name, fetch fpkit source, author TSX/SCSS/Accessibility sections, log catalog status. Why: prevents the markdown-as-source pattern from becoming tribal knowledge.
13. **Bump [`plugins/acss-kit-builder/.claude-plugin/plugin.json`](plugins/acss-kit-builder/.claude-plugin/plugin.json)** from `0.1.2` to `0.2.0` via `/release-plugin acss-kit-builder`. Update [`README.md`](plugins/acss-kit-builder/README.md) to describe the new structure, list the components, and document the Form skill pilot.

### Phase 2 — Soft-deprecate the @fpkit/acss npm path (`acss-app-builder`)

14. **Edit [`detect_component_source.py:96-104`](plugins/acss-app-builder/scripts/detect_component_source.py:96)** to add deprecation signaling when `source == "npm"`. **JSON output only — no stderr** (per Round 3, strict project Python contract):
    - Add `"deprecated": true` and `"sunsetVersion": "<captured>"` keys to the JSON output.
    - Append to a `"reasons"` array: `["@fpkit/acss npm path is deprecated; vendor components via /kit-add to migrate.", "Sunset version: <captured>"]`.
    - Keep `return 0` — existing projects must keep working.
    - Update the script's docstring with hand-run examples showing the new keys.
    Why: warn-but-pass posture lets the plugin keep working through the sunset window. JSON-only signaling stays compliant with the project Python script contract documented in [`CLAUDE.md`](CLAUDE.md).
15. **Edit slash commands that call `detect_component_source.py`** to surface the deprecation reason in chat. After parsing the script's JSON, if `deprecated == true`, the command appends a one-line notice: "Note: this project still uses the @fpkit/acss npm path (deprecated; sunset in `<sunsetVersion>`). Run `/kit-add` to vendor components." Affects [`commands/app-page.md`](plugins/acss-app-builder/commands/app-page.md), [`commands/app-pattern.md`](plugins/acss-app-builder/commands/app-pattern.md), [`commands/app-layout.md`](plugins/acss-app-builder/commands/app-layout.md), [`commands/app-form.md`](plugins/acss-app-builder/commands/app-form.md), [`commands/app-compose.md`](plugins/acss-app-builder/commands/app-compose.md). Why: per Round 2a, the deprecation must be visible to users actually running slash commands — not buried in JSON.
16. **Edit [`plugins/acss-app-builder/skills/acss-app-builder/references/component-source.md`](plugins/acss-app-builder/skills/acss-app-builder/references/component-source.md)** to add a "Compatibility ceiling" callout at top with the captured version, and demote the npm resolution path to a "Deprecated: legacy reference only" subsection.
17. **Edit [`plugins/acss-app-builder/skills/acss-app-builder/SKILL.md`](plugins/acss-app-builder/skills/acss-app-builder/SKILL.md)** to note the npm branch is deprecated and recommend `/kit-add` first throughout the slash-command guidance.

### Phase 3 — Form skill cross-plugin invocation (`acss-app-builder` → `acss-kit-builder`)

18. **Edit [`plugins/acss-app-builder/commands/app-form.md`](plugins/acss-app-builder/commands/app-form.md)** to delegate to the kit-builder skill:
    - Change `argument-hint` from `<schema.json> [--name=FormName] [--force]` to `<description-or-schema> [--name=FormName] [--force]`.
    - Body step 1: detect input mode — if argument is a `.json` path, follow legacy schema-driven path; otherwise treat as a natural-language description.
    - Body step 2 (natural-language mode): invoke the `acss-kit-builder:component-form` skill via the Skill tool, passing the description as args. The skill handles contract derivation (with `AskUserQuestion` to clarify when fields are ambiguous, per Round 2a) and writes the form file atomically (build in memory, write only on success — Round 2a).
    - Body step 2 (legacy JSON mode): read the schema, build the contract, hand off to the same skill via Skill tool with explicit field list. Preserves backward compatibility.
    - If `detect_component_source.py` reports `deprecated == true`, append the migration suggestion in chat per Phase 2 step 15.
    Why: command stays in app-builder (where users expect `/app-form`); template/contract logic lives in kit-builder (where all components live). Cross-plugin invocation via Skill tool is the documented mechanism.
19. **Add a "Cross-plugin skill invocation" subsection** to [`plugins/acss-app-builder/skills/acss-app-builder/SKILL.md`](plugins/acss-app-builder/skills/acss-app-builder/SKILL.md) documenting:
    - When and why `/app-form` invokes `acss-kit-builder:component-form`.
    - The contract for arguments passed across the boundary (description string OR field-list-from-JSON).
    - The expected return shape (the kit-builder skill writes the file; the app-builder command surfaces success/failure to the user).
    Why: cross-plugin coupling will surprise contributors otherwise. This subsection is the single place to look up how the boundary works.
20. **Keep [`assets/forms/schema.example.json`](plugins/acss-app-builder/assets/forms/schema.example.json) on disk** as a legacy reference. Update [`references/forms.md`](plugins/acss-app-builder/skills/acss-app-builder/references/forms.md) to label the JSON shape "legacy input format — natural-language description preferred."
21. **Delete [`assets/forms/form-from-schema.tsx.tmpl`](plugins/acss-app-builder/assets/forms/form-from-schema.tsx.tmpl)** after the Form skill ships in Phase 1 step 8. Why: the markdown-hosted code blocks in `component-form/SKILL.md` are now the source of truth.

### Phase 4 — CSS Token Convention (`acss-theme-builder`)

22. **Add a "CSS Token Convention" section to [`plugins/acss-theme-builder/skills/acss-theme-builder/SKILL.md`](plugins/acss-theme-builder/skills/acss-theme-builder/SKILL.md)** documenting all 18 defined `--color-*` semantic variable names (15 required roles + 3 optional roles: `--color-surface-subtle`, `--color-text-subtle`, `--color-brand-accent`) from [`theme.schema.json`](plugins/acss-theme-builder/assets/theme.schema.json) `$defs/palette`. Names stay byte-compatible with [`assets/themes/*.css`](plugins/acss-theme-builder/assets/themes) — no renames, no removals. Group by Backgrounds / Text / Borders / Brand+semantic / Focus, matching `ROLE_GROUPS` in [`tokens_to_css.py`](plugins/acss-theme-builder/scripts/tokens_to_css.py).
23. **Add a "Required Contrast Pairings" subsection** to the CSS Token Convention listing the WCAG 2.2 AA pairings that must pass: `--color-text` on `--color-background` (4.5:1), `--color-text-muted` on `--color-background` (4.5:1), `--color-text-inverse` on `--color-primary` (4.5:1), focus ring on relevant backgrounds (3:1 UI), etc. Reference [`validate_theme.py`](plugins/acss-theme-builder/scripts/validate_theme.py) as the validator. Why: per Round 2b, contrast is documented declaratively and validated by the existing tool.
24. **Mark [`theme.schema.json`](plugins/acss-theme-builder/assets/theme.schema.json) deprecated with a sunset version.** Add a top-level `"deprecated": true` and `"x-sunset-version": "0.3.0"` field. Edit [`references/theme-schema.md`](plugins/acss-theme-builder/skills/acss-theme-builder/references/theme-schema.md) to add a deprecation banner: "Deprecated as user-facing contract; scheduled for removal in `acss-theme-builder@0.3.0`. The CSS Token Convention in SKILL.md is the going-forward authoring format. Schema retained for internal use by `tokens_to_css.py` / `css_to_tokens.py` in the interim."
25. **Delete [`assets/theme.tokens.example.json`](plugins/acss-theme-builder/assets/theme.tokens.example.json).** Why: with the CSS Token Convention as canonical, this file is misleading documentation.
26. **Edit [`commands/theme-create.md`](plugins/acss-theme-builder/commands/theme-create.md), [`commands/theme-brand.md`](plugins/acss-theme-builder/commands/theme-brand.md), [`commands/theme-update.md`](plugins/acss-theme-builder/commands/theme-update.md), [`commands/theme-extract.md`](plugins/acss-theme-builder/commands/theme-extract.md)** to confirm no `argument-hint` references `theme.tokens.json` as user input. Update prose that calls JSON the "input format" to call CSS the input format. The `theme-extract` command's round-trip prose changes to "export."

### Phase 5 — Cross-plugin closeout

27. **Bump [`plugins/acss-app-builder/.claude-plugin/plugin.json`](plugins/acss-app-builder/.claude-plugin/plugin.json) to `0.2.0`** via `/release-plugin acss-app-builder`. Update [`README.md`](plugins/acss-app-builder/README.md) with deprecation notes (npm path), the new natural-language form flow, and a pointer to the cross-plugin skill invocation subsection.
28. **Bump [`plugins/acss-theme-builder/.claude-plugin/plugin.json`](plugins/acss-theme-builder/.claude-plugin/plugin.json) to `0.2.0`** via `/release-plugin acss-theme-builder`. Update [`README.md`](plugins/acss-theme-builder/README.md) with the CSS Token Convention pointer.
29. **Verify [`marketplace.json`](.claude-plugin/marketplace.json) descriptions** for all three plugins still accurately reflect the new structure; update if needed.

## Rollback Strategy

If 0.2.0 reveals a regression in any plugin after release:

1. **Hotfix patch (preferred):** ship `0.2.1` reverting the regressed phase only. Each plugin's phases are independent enough that one phase can revert without unwinding the others. For example, if Form skill triggering proves unreliable, revert Phase 1 step 8 (delete the skill, keep `form-from-schema.tsx.tmpl`) without touching kit-builder's component backfills.
2. **Plugin-level rollback (last resort):** revert a single plugin's `plugin.json` from `0.2.0` to `0.1.x` in a hotfix PR. Users do `/plugin update` to roll back. Other plugins remain at `0.2.0`. Use only when a plugin is fundamentally broken.
3. **Coordinated rollback (worst case):** revert all three to `0.1.x` if the cross-plugin contract (`.acss-target.json`, Form skill invocation) is structurally broken.

The Form skill being a "pilot" (Round 1) means the rollback risk is concentrated in one place: if the per-component skill pattern doesn't work, only Phase 1 step 8 + Phase 3 step 18 need reverting.

## Verification

Bootstrap the sandbox per [`tests/README.md`](tests/README.md):

```
tests/setup.sh
cd tests/sandbox && claude
```

End-to-end smoke tests:

1. **kit-builder markdown-as-source (Phase 1):** `/kit-add icon-button`, `/kit-add img`, `/kit-add button`, `/kit-add card`, `/kit-add dialog`, `/kit-add popover`, `/kit-add table`. Confirm files generate from the embedded TSX/SCSS code blocks. Confirm dependency walks complete and `.acss-target.json` is updated. Read each generated `.tsx` to confirm imports use only relative local paths.
2. **Form skill triggering (Phase 1 step 8):** in a fresh sandbox session, ask Claude "create a signup form with email, password, and a role select." Expect the `acss-kit-builder:component-form` skill to auto-trigger (without explicit `/app-form` invocation) and produce a working form. Repeat with "add a contact form" — expect AskUserQuestion to clarify fields per Round 2a.
3. **Form via slash command (Phase 3 step 18):** `/app-form "signup form with email, password, role select"`. Expect the command to delegate to the kit-builder skill and produce the same output as test 2. Then `/app-form assets/forms/schema.example.json` (after copying it into the sandbox) — expect the legacy JSON path to still work via cross-plugin handoff.
4. **Atomic write failure (Phase 3 step 18):** intentionally corrupt the generated TSX during construction (e.g. force a placeholder substitution failure). Confirm no partial file lands on disk and the user sees a clear error message.
5. **npm-path soft-deprecation (Phase 2):** `npm install @fpkit/acss` (no `/kit-add` first), then run `python3 plugins/acss-app-builder/scripts/detect_component_source.py tests/sandbox` from the repo root. Expect JSON with `"source": "npm"`, `"deprecated": true`, `"sunsetVersion": "<captured>"`, and the deprecation `reasons` array — **no stderr output**. Then `/app-page dashboard` in the sandbox — expect the in-chat migration notice. `/kit-add button` and re-run — expect `"source": "generated"`, no deprecation flag, no migration notice.
6. **Theme CSS Token Convention (Phase 4):** `/theme-create #4f46e5 --mode=both`. Confirm `light.css` + `dark.css` are written and pass [`validate_theme.py`](plugins/acss-theme-builder/scripts/validate_theme.py) for all required contrast pairings. `/theme-update src/styles/theme/light.css --color-primary=#0066cc`. Confirm no flow references `theme.tokens.example.json` (deleted) or instructs the user to author JSON.
7. **Marketplace install:** `/plugin marketplace add` against the local repo and `/plugin install acss-app-builder@…`. Confirm `0.2.0` resolves and the deprecation note surfaces.
8. **Audit verifications (Phase 0):** confirm `grep -rn "foundation/ui.tsx"` returns no remaining consumers after Phase 1 step 9. Confirm `.acss-target.json` written by 0.2.0 kit-builder is readable by the existing 0.1.x app-builder script (cross-version compat) and vice-versa.

## Critical files

**Plugin: acss-kit-builder**
- [`skills/acss-kit-builder/references/components/button.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/button.md) — canonical embedded-markdown shape (extend first with TSX/SCSS/Accessibility sections)
- [`skills/acss-kit-builder/references/components/`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components) — backfill all existing simple-component docs; new docs for icon-button, img, plus Popover/Table if not present
- [`skills/acss-kit-builder/references/components/foundation.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/foundation.md) — new (replaces deleted `assets/foundation/ui.tsx`)
- [`skills/acss-kit-builder/references/components/catalog.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/catalog.md) — verification log + skill/reference pointers
- [`skills/component-form/SKILL.md`](plugins/acss-kit-builder/skills/component-form/SKILL.md) — new, the pilot per-component skill
- [`skills/acss-kit-builder/SKILL.md`](plugins/acss-kit-builder/skills/acss-kit-builder/SKILL.md) — document new pattern + hybrid rule + Accessibility requirement
- [`assets/foundation/ui.tsx`](plugins/acss-kit-builder/assets/foundation/ui.tsx) — convert to markdown then delete (after Phase 0 step 2 audit)
- [`.claude-plugin/plugin.json`](plugins/acss-kit-builder/.claude-plugin/plugin.json), [`README.md`](plugins/acss-kit-builder/README.md) — version + docs + contributor recipe

**Plugin: acss-app-builder**
- [`scripts/detect_component_source.py`](plugins/acss-app-builder/scripts/detect_component_source.py) — JSON-only deprecation signaling
- [`commands/app-form.md`](plugins/acss-app-builder/commands/app-form.md) — delegate to kit-builder skill
- [`commands/app-page.md`](plugins/acss-app-builder/commands/app-page.md), [`app-pattern.md`](plugins/acss-app-builder/commands/app-pattern.md), [`app-layout.md`](plugins/acss-app-builder/commands/app-layout.md), [`app-compose.md`](plugins/acss-app-builder/commands/app-compose.md) — surface deprecation in chat when on npm path
- [`assets/forms/form-from-schema.tsx.tmpl`](plugins/acss-app-builder/assets/forms/form-from-schema.tsx.tmpl) — delete after kit-builder Form skill ships
- [`assets/forms/schema.example.json`](plugins/acss-app-builder/assets/forms/schema.example.json) — keep as legacy reference
- [`skills/acss-app-builder/SKILL.md`](plugins/acss-app-builder/skills/acss-app-builder/SKILL.md) — Cross-plugin skill invocation subsection + npm deprecation
- [`skills/acss-app-builder/references/component-source.md`](plugins/acss-app-builder/skills/acss-app-builder/references/component-source.md) — sunset callout
- [`.claude-plugin/plugin.json`](plugins/acss-app-builder/.claude-plugin/plugin.json), [`README.md`](plugins/acss-app-builder/README.md) — version + docs

**Plugin: acss-theme-builder**
- [`skills/acss-theme-builder/SKILL.md`](plugins/acss-theme-builder/skills/acss-theme-builder/SKILL.md) — CSS Token Convention + Required Contrast Pairings
- [`assets/theme.schema.json`](plugins/acss-theme-builder/assets/theme.schema.json) — mark deprecated with sunset version
- [`skills/acss-theme-builder/references/theme-schema.md`](plugins/acss-theme-builder/skills/acss-theme-builder/references/theme-schema.md) — deprecation banner
- [`assets/theme.tokens.example.json`](plugins/acss-theme-builder/assets/theme.tokens.example.json) — delete
- [`commands/theme-*.md`](plugins/acss-theme-builder/commands) — argument-hint and prose
- [`.claude-plugin/plugin.json`](plugins/acss-theme-builder/.claude-plugin/plugin.json), [`README.md`](plugins/acss-theme-builder/README.md) — version + docs

## Existing utilities to reuse

- **Generation Contract pattern:** [`button.md`](plugins/acss-kit-builder/skills/acss-kit-builder/references/components/button.md) is the seed for the new embedded-markdown shape. Phase 1 step 4 extends this single file first; everything else mirrors.
- **`/release-plugin <name>`** handles `plugin.json` version bumps and `marketplace.json` description sync.
- **Sandbox:** [`tests/setup.sh`](tests/setup.sh) + [`tests/README.md`](tests/README.md) is the existing smoke-test path.
- **WebFetch tool:** used per-component in Phase 1 step 5 to retrieve canonical fpkit source from `https://github.com/shawn-sandy/acss/blob/main/...` for verification before backfilling code blocks.
- **Skill invocation across plugins:** the Skill tool is the documented mechanism for `/app-form` (acss-app-builder) to invoke `acss-kit-builder:component-form`.
- **fpkit cross-references:** all GitHub URLs use full URLs per repo policy. Markdown specs reference fpkit as design source without depending on the npm package.
- **Token substitution:** the existing `{{IMPORT_SOURCE:...}}` / `{{NAME}}` / `{{FIELDS}}` placeholder convention from the deleted `.tsx.tmpl` carries over into the markdown spec's TSX code blocks — Claude does substitution at write time.
- **`validate_theme.py`** validates contrast pairings declared in the CSS Token Convention.

## Next steps (out of scope)

- Plan the `0.3.0` cycle that flips `detect_component_source.py` from warn-but-pass to halt-on-npm and removes [`theme.schema.json`](plugins/acss-theme-builder/assets/theme.schema.json) from disk (rewriting `tokens_to_css.py` / `css_to_tokens.py` to be CSS-native).
- Promote additional component skills (Dialog, Card, Table, Popover) only after observing the Form skill's trigger reliability in real-world usage.
- Convert [`acss-app-builder/assets/pages/`](plugins/acss-app-builder/assets/pages), [`assets/patterns/`](plugins/acss-app-builder/assets/patterns), [`assets/layouts/`](plugins/acss-app-builder/assets/layouts) to markdown-as-source if the pattern proves out for components and forms.
- Revisit theme assets: if markdown-as-source matures, themes themselves could become markdown specs with embedded CSS code blocks.
- Add Python unit-test infra for the modified `detect_component_source.py` once the repo grows enough scripts to warrant it.

---

## Interview Summary

This section captures decisions and open risks surfaced during the `/plan-interview` stress-test before implementation.

### Key Decisions Confirmed

**Component packaging (Round 1):** Only **Form** gets promoted to a skill in 0.2.0 (pattern pilot). Dialog, Card, Table, Popover stay as reference docs. Form skill lives at `acss-kit-builder/skills/component-form/SKILL.md` (Round 3) — `/app-form` delegates across plugin boundaries.

**Backfill & verification (Rounds 1, 3):** All ~13 existing simple-component reference docs get TSX/SCSS/Accessibility backfill in this single 0.2.0 PR. Each backfill verifies against canonical fpkit source on GitHub before authoring.

**Substitution & runtime (Round 1):** Claude reads markdown specs and writes TSX inline — no Python extraction script. Existing `{{...}}` placeholder convention carries inside fenced ```tsx``` blocks.

**Deprecation signaling (Rounds 1, 3):** `detect_component_source.py` adds `deprecated`, `sunsetVersion`, and `reasons` array to JSON — **no stderr** (strict project Python contract compliance). Slash commands surface a follow-up "Migrate via /kit-add" suggestion in chat (Round 2a).

**UX flows (Round 2a):** Ambiguous `/app-form` descriptions trigger `AskUserQuestion` to clarify fields. `/kit-add` keeps existing preview-before-write. Form generation is atomic: build in memory, write only on success.

**Accessibility quality bar (Round 2b):** Every markdown component spec must have a `## Accessibility` section. Form spec annotates a11y patterns in code blocks AND explains them in the Accessibility section. CSS Token Convention documents required contrast pairings; `validate_theme.py` remains the validator. Dialog/Popover reference docs embed working focus-management code in the TSX block.

**Drift & ownership (Round 3):** Generated TSX files are user-owned post-write. No `/kit-diff` command, no version-tracking header comments. Re-running `/kit-add --force` overwrites local edits (existing behavior).

### Plan Naming

| Element | Current | Issue | Suggested | User decision |
|---------|---------|-------|-----------|---------------|
| Filename | `i-want-to-refactor-peppy-kurzweil.md` | Random pattern (`peppy-kurzweil`) unrelated to content | `acss-markdown-as-source-refactor.md` | Accepted — file renamed |
| H1 Heading | `# Refactor: markdown-as-source for components + sunset @fpkit/acss + retire JSON schemas` | Pass — descriptive | _(no change)_ | n/a |

### Open Risks & Concerns

1. **Cross-plugin skill delegation is a new pattern.** `/app-form` (acss-app-builder) → `component-form` skill (acss-kit-builder) requires the Skill tool to be invokable from a slash command body and able to receive structured arguments. Confirm this works in a sandbox before committing.
2. **`.acss-target.json` schema stability across versions.** Phase 0 step 3 audits this; if a shape change is unavoidable, document a migration step before 0.2.0 ships.
3. **`component-form` skill description must trigger reliably.** The pilot succeeds only if Claude auto-triggers the skill from natural-language phrases like "create a form." If trigger reliability is poor, the skill becomes a hidden artifact only the slash command uses — at which point the skill promotion was unnecessary overhead.
4. **fpkit-source verification adds meaningful scope.** ~13 WebFetch operations × per-component review. Phase 1 step 5 makes this explicit; budget accordingly.
5. **No automated tests for `detect_component_source.py`.** Hand-run examples documented in the docstring are the verification floor. A future Python test infra would close this gap.
6. **Foundation deletion safety hinges on Phase 0 step 2.** If the audit misses a consumer, deletion silently breaks a chain. The audit is the gate.

### Recommended Next Steps (Already Applied to Plan)

The following amendments from the interview have been integrated into the plan body above:

1. Phase 3 step 19: Cross-plugin skill invocation subsection added.
2. Phase 0 added: foundation audit + `.acss-target.json` audit.
3. Phase 1 step 5 added: backfill verification workflow with WebFetch.
4. Rollback Strategy section added.
5. Phase 1 step 4: required `## Accessibility` section in canonical embedded-markdown shape.
6. Phase 1 step 12: contributor recipe added to kit-builder README.
7. Phase 2 step 14: stderr removed; JSON-only deprecation signaling.
8. Phase 1 step 8: skill promotion scope reduced to Form-only (pilot).

### Simplification Opportunities

- **Form skill is borderline overhead for one component.** Plan now makes the pilot rationale explicit ("adopt for additional components only after observing trigger reliability"). If the pattern doesn't validate, rollback is concentrated in Phase 1 step 8 + Phase 3 step 18.
