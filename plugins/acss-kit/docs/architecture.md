# acss-kit — Architecture (Contributor Guide)

This page is for maintainers editing the plugin: adding component references, updating a SKILL workflow, or extending the slash commands.

## Plugin layout

```
plugins/acss-kit/
  .claude-plugin/
    plugin.json                # Authoritative version source; read by Claude Code + /plugin update
  assets/
    foundation/
      ui.tsx                   # Polymorphic UI base — copied verbatim into user projects
  commands/
    kit-add.md                 # /kit-add definition; delegates to SKILL.md
    kit-list.md                # /kit-list definition; delegates to SKILL.md
  skills/
    acss-kit/
      SKILL.md                 # The full generation workflow (Steps A–F)
      references/
        architecture.md        # UI polymorphic chain, compound pattern, data-attr selectors
        accessibility.md       # WCAG rationale, useDisabledState source, WCAG checklist
        composition.md         # Component categories, decision tree, inline-types pattern
        css-variables.md       # Naming convention, fallbacks, rem conversion
        components/
          alert.md             # Generation Contract + full reference
          button.md
          card.md
          catalog.md           # Badge, Tag, Heading, Text, Link, List, Details, Progress, Icon
          dialog.md
          form.md
          nav.md
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

6. **All fpkit source references must use full GitHub URLs** — never repo-relative paths. For example:
   ```
   https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/button/btn.tsx
   ```
   This is a project-level rule from `CLAUDE.md`.

## .acss-target.json — target directory contract

`.acss-target.json` at the project root tells the SKILL where to write generated components. It contains at minimum:

```json
{
  "componentsDir": "src/components/fpkit"
}
```

The SKILL reads the file during Step A3 and writes it if absent (via `scripts/detect_target.py`). Commit it to git so subsequent `/kit-add` runs use the same path.

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
