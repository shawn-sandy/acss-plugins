# acss-kit — Architecture (Contributor Guide)

This page is for maintainers editing the plugin: adding component references, updating a SKILL workflow, or extending the slash commands.

> Prefer diagrams? See [visual-guide.md §7](visual-guide.md#7-authoring-a-new-component-reference) for the maintainer authoring loop as a flowchart.

## Plugin layout

```
plugins/acss-kit/
  .claude-plugin/
    plugin.json                # Authoritative version source; read by Claude Code + /plugin update
  assets/
    foundation/
      ui.tsx                   # Polymorphic UI base — copied verbatim into user projects
  commands/
    kit-add.md                 # /kit-add; delegates to skills/components/SKILL.md
    kit-list.md                # /kit-list; delegates to skills/components/SKILL.md
    theme-create.md            # /theme-create; delegates to skills/styles/SKILL.md
    theme-brand.md             # /theme-brand; delegates to skills/styles/SKILL.md
    theme-update.md            # /theme-update; delegates to skills/styles/SKILL.md
    theme-extract.md           # /theme-extract; delegates to skills/styles/SKILL.md
  skills/
    components/
      SKILL.md                 # Component generation workflow (Steps A–F)
      references/
        architecture.md        # UI polymorphic chain, compound pattern, data-attr selectors
        accessibility.md       # WCAG rationale, useDisabledState source, WCAG checklist
        composition.md         # Component categories, decision tree, inline-types pattern
        css-variables.md       # Naming convention, fallbacks, rem conversion
        components/
          catalog.md           # Verification status table + leaf components (Badge, Tag, Heading, Text, Details, Progress)
          button.md            # Canonical 9-section example
          alert.md, card.md, dialog.md, popover.md, table.md, img.md, icon.md
          link.md, list.md, field.md, input.md, checkbox.md, icon-button.md
          form.md, nav.md      # nav.md retains the legacy shape
    styles/
      SKILL.md                 # Theme generation workflow (4 flows)
      references/
        role-catalogue.md      # 15 required + 3 optional --color-* roles, contrast pairings
        palette-algorithm.md   # OKLCH lightness targets, state hue offsets
        theme-schema.md        # Internal JSON schema for the round-trip scripts
    component-form/
      SKILL.md                 # Pilot per-component skill (auto-triggers on "create a form")
```

## Command → SKILL delegation

Command files are intentionally thin. Each one:

1. Documents the command signature and a brief description (for the Claude Code command palette).
2. Points at the relevant SKILL.md section for the actual workflow.

The logic lives entirely in `SKILL.md`. Do not duplicate generation logic inside a command file — changes would need to be maintained in two places and would drift.

## How to add a new component reference

1. **Create `references/components/<name>.md`** (or add the component to `catalog.md` for simple leaf components).

2. **Add a Generation Contract block:**

   ```markdown
   ## Generation Contract

   \`\`\`
   export_name:  ComponentName
   file:         component-name/component-name.tsx
   scss:         component-name/component-name.scss
   imports:      [../ui]
   dependencies: [other-component-name]
   \`\`\`
   ```

   Every field is required. `dependencies` is an array of component names (lowercase, matching their reference doc names). An empty array `[]` means a leaf component.

3. **Add the props interface, CSS variables, and a usage snippet** following the pattern in existing reference docs (see `references/components/button.md` for the most complete example).

4. **Cross-link the relevant shared references** within the doc body:
   - Polymorphic `UI` type chain → `references/architecture.md`
   - `useDisabledState` hook → `references/accessibility.md`
   - Compound component pattern → `references/composition.md`
   - CSS variable naming / fallback strategy → `references/css-variables.md`

5. **Update `catalog.md` if the component is a simple leaf.** Simple components (no state, no deps, one `.tsx` + one `.scss`) belong in `catalog.md` rather than a dedicated file, to keep the file count manageable.

6. **All fpkit source references must use full GitHub URLs pinned to a tag or commit SHA** — never repo-relative paths and never `blob/main`. For example:
   ```text
   https://github.com/shawn-sandy/acss/blob/v6.5.0/packages/fpkit/src/components/button/btn.tsx
   ```
   See `.claude/rules/fpkit-references.md` for the full policy.

## .acss-target.json — target directory contract

`.acss-target.json` at the project root tells the SKILL where to write generated components, and (since 0.5.0) what the user's build stack looks like so integration advice is correct for the framework. The full shape:

```json
{
  "componentsDir": "src/components/fpkit",
  "utilitiesDir": "src/styles",
  "stack": {
    "framework": "vite",
    "frameworkVersion": "5.4.0",
    "bundler": "vite",
    "cssPipeline": ["sass"],
    "tsconfig": true,
    "entrypointFile": "src/main.tsx",
    "cssEntryFile": "src/styles/index.scss",
    "detectedAt": "2026-05-01T00:00:00Z"
  }
}
```

`componentsDir` and `utilitiesDir` are optional — the detectors fall back to `src/components/fpkit` and `src/styles` and refuse stale entries that point at deleted directories. The `stack` block is also optional; downstream scripts (`verify_integration.py`) emit a reason pointing back to `detect_stack.py` when it is absent.

`stack.cssEntryFile` is added by `/setup` Step 7.5 (`scripts/detect_css_entry.py`) when the user picks (or supplies) a CSS/SCSS entry to receive the generated `light.css` / `dark.css` `@import` lines. It is independent of `entrypointFile`: `entrypointFile` is the TSX root (typically `src/main.tsx`), while `cssEntryFile` is the stylesheet root (e.g. `src/styles/index.scss`). `verify_integration.py` accepts theme imports living in either file, so projects that route all styles through SCSS no longer trip the validator with an empty TSX entrypoint.

The SKILL reads the file during Step A3 and writes it if absent (`scripts/detect_target.py`), then refines it during Step A3.1 (`scripts/detect_stack.py`). Step G runs `scripts/verify_integration.py` to confirm the entrypoint actually imports the generated artifacts. Commit `.acss-target.json` to git so subsequent `/kit-add` and `/theme-create` runs reuse the same configuration.

## Version bump checklist

Before committing any plugin change, per the repo-level pre-submit checklist:

1. Bump the version in `.claude-plugin/plugin.json` using `/release-plugin acss-kit` (or manually).
2. Confirm that all new `references/` file links to fpkit source use full GitHub URLs.
3. Update `marketplace.json` description if the change is user-facing. Do not add a `version` key to the `marketplace.json` entry — `plugin.json` is the authoritative version source.
4. Update `README.md` if commands or behavior changed.

Docs-only additions (new `docs/*.md` files) do not require a version bump, as they do not change command behavior or generated output.

## assets/foundation/ui.tsx

This file is copied verbatim into user projects. Changes to it are rare and high-impact: every project that has already run `/kit-add` keeps the old copy (skip-existing rule). Treat changes to `ui.tsx` like a breaking change — note them prominently in the CHANGELOG and consider bumping the minor version.

If you modify the polymorphic type chain (the `PolymorphicRef<C>` → `UIProps<C>` ladder), verify that the generated component `.tsx` files in the reference docs still type-check against the new types. The reference docs contain inline TSX examples that must be kept consistent with `ui.tsx`.
