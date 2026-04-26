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

`validate_theme.py` only validates files whose name matches `^(light|dark|brand-[\w-]+)\.css$`. Anything else (including `<preset>.css` without the `brand-` prefix) is silently skipped with `validate_theme: skipped (no palette files found)` and exit 0 — that path must NOT be treated as a passing validation.

1. Build the candidate file list:
   - Top-level `assets/`: include any `.css` file matching the regex above.
   - `assets/brand-presets/` (if it exists): include any `.css` file matching the regex.
2. For each candidate file, run `python3 plugins/<plugin-name>/scripts/validate_theme.py <file>` with timeout 30s. Capture exit code and stdout.
3. Classify each result:
   - exit 0 + `validate_theme: OK ...` → PASS
   - exit 1 → FAIL with the listed failing pair names
   - stdout contains `no palette files found` → INFO ("filename did not match the validator regex"), do NOT count as PASS
4. Mark the section overall:
   - `OK` if every candidate file is PASS.
   - `FIX` if any candidate is FAIL.
   - `SKIP` if no candidate files were found at all (no bundled themes to validate).

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
