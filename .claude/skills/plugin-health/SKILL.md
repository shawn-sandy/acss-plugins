---
name: plugin-health
description: One-shot audit dashboard for the acss-kit plugin — runs structural validation, scans component references for canonical-shape compliance, cross-checks the catalog table, and validates bundled theme assets. Use when the maintainer asks for a plugin health check, what's missing before release, an acss-kit audit, or a status overview.
disable-model-invocation: false
---

# /plugin-health

Usage: `/plugin-health` (defaults to `acss-kit`) or `/plugin-health <plugin-name>`

Produces a single dashboard summarizing the structural and content health of the plugin. Read-only — does NOT modify any files. Run before release or whenever the maintainer wants to know "what's left to fix".

## Step 1 — Resolve target

If no argument is provided, default to `acss-kit`. Confirm `plugins/<plugin-name>/.claude-plugin/plugin.json` exists. If not, list available plugins from `.claude-plugin/marketplace.json` and halt.

## Step 2 — Structural validation

Invoke the existing `validate-plugin` skill on `<plugin-name>`. Capture its output. Surface as the first section of the dashboard ("Structure").

## Step 3 — Component reference scan

For each file under `plugins/<plugin-name>/skills/components/references/components/*.md` (excluding `catalog.md`):

1. Check whether the file contains all nine canonical sections (verification banner, Overview, Generation Contract, Props Interface, TSX Template, CSS Variables, SCSS Template, Accessibility, Usage Examples).
2. Mark the file `OK` if all present, `FIX` if any are missing or out of order.
3. Capture the missing section names for the FIX rows.

Roll up to: `N components OK / M components FIX`. Detailed list goes in the "Components" section.

## Step 4 — Catalog parity

1. Read `plugins/<plugin-name>/skills/components/references/components/catalog.md`. Extract every component name from the "Verification Status" table.
2. Compare to the set of `*.md` files actually present in `references/components/` (excluding `catalog.md`).
3. Report:
   - Files without a catalog row (orphans)
   - Catalog rows without a file (stale)
4. Mark `OK` if both sets match, `FIX` otherwise.

## Step 5 — Theme reference parity

Invoke the `theme-reference-reviewer` agent. Capture its check verdicts. Each FAIL becomes a row in the "Themes" section of the dashboard.

## Step 6 — Bundled theme validation

For each `.css` file under `plugins/<plugin-name>/assets/` and `plugins/<plugin-name>/assets/brand-presets/` (if it exists):

1. Run `python3 plugins/<plugin-name>/scripts/validate_theme.py <file>` with timeout 30s.
2. Capture exit code (0 = pass, 1 = WCAG failures).
3. List failures with the failing pair names.

Mark `OK` if all bundled themes pass, `FIX` otherwise.

## Step 7 — Render the dashboard

Print a single block:

```
== plugin-health: <plugin-name> @ v<version> ==

Structure              [OK | FIX] <one-line summary from validate-plugin>
Components             [OK | FIX] N OK / M FIX
Catalog parity         [OK | FIX] <orphans/stale counts>
Theme references       [OK | FIX] <fail count from theme-reference-reviewer>
Bundled themes         [OK | FIX] <preset pass/fail counts>

-- Detail --

Components needing attention:
  - <name>.md — missing: Accessibility
  - <name>.md — missing: Usage Examples, out-of-order: SCSS Template

Catalog issues:
  - Orphan: <name>.md (file present, no catalog row)
  - Stale: <name> (catalog row, no file)

Theme reference findings:
  - <check name> — <one-line failure>

Bundled theme failures:
  - <file> — <failing pair name>

-- Suggested fixes --

  Run /component-update <name>           (for each FIX row in Components)
  Run /style-update <path>               (for each FIX row in Themes)
  Manual: edit catalog.md                (for each Catalog issue)
```

If everything is OK, replace the Detail section with: `All systems green. Plugin is release-ready.`

## Step 8 — Pre-release reminder

Append:

```
Before opening a PR:
  1. Run /release-plugin <plugin-name> <new-version>
  2. Run /release-check <plugin-name>
  3. Confirm plugins/<plugin-name>/CHANGELOG.md mentions user-visible changes
```

This skill does not modify any files. The maintainer applies fixes via the suggested sub-skills.
