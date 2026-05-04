---
name: kit-sync
description: Use when the user wants to bulk-install every acss-kit component and theme into a project at once, or to safely re-copy unmodified components after a plugin update. Backs /kit-sync (bulk install) and /kit-update (drift-safe re-copy). Maintains .acss-kit/manifest.json as the source of truth for what was generated, and uses sha256 drift detection to skip user-modified files.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.1.0"
---

# SKILL: kit-sync

Bulk install every shipped component + foundation + theme into a developer's project in one shot, then safely re-copy on subsequent plugin upgrades — without clobbering user customizations.

## Purpose

`/kit-add` is per-component. `/setup` is one-time bootstrap. Neither helps a developer who wants to:

1. **Bulk-install everything** — vendor every component listed in `references/components/catalog.md` plus the foundation and a starter theme in a single command.
2. **Stay current safely** — re-copy unmodified components after an `acss-kit` upgrade without overwriting files they've edited.

This skill closes both gaps via a manifest at `<project>/.acss-kit/manifest.json` that records the sha256 of every generated file at the moment it was written. Drift detection compares on-disk content to that recorded hash to classify each tracked file as `clean`, `modified`, or `missing`.

## Manifest format

`<project-root>/.acss-kit/manifest.json`:

```json
{
  "schemaVersion": 1,
  "pluginVersion": "0.9.0",
  "targetDir": "src/components/fpkit",
  "stylesDir": "src/styles",
  "themeFile": "acss-kit.theme.json",
  "generatedAt": "2026-05-03T14:22:11Z",
  "files": {
    "src/components/fpkit/ui.tsx": {
      "source": "asset:foundation/ui.tsx",
      "sha256": "<hex>",
      "pluginVersion": "0.9.0",
      "kind": "foundation"
    },
    "src/components/fpkit/button.tsx": {
      "source": "ref:components/button.md#tsx-template",
      "sha256": "<hex>",
      "pluginVersion": "0.9.0",
      "kind": "component",
      "component": "button"
    },
    "src/styles/theme/light.css": {
      "source": "generator:tokens_to_css.py",
      "sha256": "<hex>",
      "pluginVersion": "0.9.0",
      "kind": "style"
    }
  }
}
```

`kind` is one of `foundation` (the verbatim `ui.tsx`), `component` (a tracked TSX/SCSS pair), `style` (a generated theme CSS file), or `theme` (the user's seed `theme.json`).

## Hash normalization (load-bearing)

Drift detection runs sha256 on **normalized** content, not raw bytes. Normalize both the freshly generated content (before recording the manifest hash) and the on-disk content (before comparing). The normalization is implemented in `scripts/hash_file.py` and duplicated in `scripts/diff_status.py`:

1. Replace CRLF / CR with LF.
2. Strip trailing whitespace (spaces and tabs) from every line.
3. Collapse trailing blank lines to a single trailing newline.

Without normalization a Prettier or editor save would flip every file to `modified` immediately.

---

## Step 0 — Exit plan mode

Applies to both workflows below (`/kit-sync` bulk install and `/kit-update` safe re-copy). If the session is in plan mode, call `ExitPlanMode` before reaching Step S1 or U1 — both flows write component TSX/SCSS, theme CSS, and the manifest at `.acss-kit/manifest.json`, and they shell out to `detect_target.py`, `manifest_read.py`, `manifest_write.py`, `diff_status.py`, and the palette/token scripts. Plan mode blocks all of those.

Stay in plan mode only when it is absolutely necessary — i.e. the user explicitly asked for a dry-run / preview, **or** they passed `--dry-run` (which already prints the plan tree without writing). In that case, narrate the planned actions per the existing dry-run output without invoking Write/Edit/Bash, and wait for approval before re-entering this skill.

---

## Bulk install workflow (`/kit-sync`)

Triggered by `/kit-sync` and by natural-language phrasing like "install all components", "bulk copy the kit", "sync the entire kit into my project".

### Flags

- `--target=<dir>` — override component directory (default: read `.acss-target.json` `componentsDir`, fallback `src/components/fpkit`).
- `--styles-dir=<dir>` — override styles directory (default: read `.acss-target.json` `stylesDir`, fallback `src/styles`).
- `--seed=<hex>` — seed color for theme generation (default: prompt the developer).
- `--skip-styles` — components-only sync; do not seed theme.
- `--dry-run` — print the plan tree, do not write any files or manifest.

### Step S1 — Preflight

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <cwd>`. If `projectRoot` is `null`, halt with the script's `reasons[0]`.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_stack.py <projectRoot>` and confirm `cssPipeline` includes `sass`. If not, surface the install command from `detect_package_manager.py` and stop.
3. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/manifest_read.py <projectRoot>`. If the manifest already exists, treat this run as a re-sync — proceed to Step S2 but route every file through the diff/skip logic from the safe-update workflow before writing.

### Step S2 — Enumerate the catalog

Read `${CLAUDE_PLUGIN_ROOT}/skills/components/references/components/catalog.md`. Every component named in the **Verification Status** table is in scope, plus the inline catalog entries (Badge, Tag, Heading, Text/Paragraph, Details, Progress) that have a Generation Contract.

Exclude `Form` (lives as a skill, not a reference doc) and `UI (foundation)` (handled separately as `ui.tsx`).

### Step S3 — Resolve dep tree, dedupe

For each in-scope component, walk its Generation Contract `dependencies:` recursively (same logic as the `components` skill Step B3). Union all results into a single ordered list, leaves first.

### Step S4 — Show the plan

Display the full plan to the developer:

```text
/kit-sync plan — bulk install into <projectRoot>:

  Foundation:
    src/components/fpkit/ui.tsx

  Components (15):
    icon.tsx
    button.tsx + button.scss
    icon-button.tsx + icon-button.scss
    ...

  Styles:
    src/styles/theme/light.css   (from seed #4f46e5)
    src/styles/theme/dark.css
    acss-kit.theme.json          (seed record)

  Manifest:
    .acss-kit/manifest.json

Proceed? [Enter to continue, Ctrl+C to cancel]
```

Wait for confirmation. If `--dry-run`, print the plan and exit without writing.

### Step S5 — Generate components bottom-up

For each entry in the dep tree (leaves first):

1. Load the matching reference doc; extract the `## TSX Template` and `## SCSS Template` content.
2. Substitute any `{{IMPORT_SOURCE:...}}` / `{{NAME}}` / `{{FIELDS}}` placeholders (same rules as `/kit-add` Step C).
3. Pipe the rendered TSX through `hash_file.py --stdin` to capture the normalized sha256 **before writing**.
4. Write the file.
5. Repeat for SCSS where the contract has one.
6. Append entries to an in-memory `files[]` payload for `manifest_write.py`.

Re-sync: if a tracked file already exists in the manifest and is `modified` (per Step S1's diff), skip it and add to the `skipped[]` summary instead of overwriting.

### Step S6 — Foundation

Copy `${CLAUDE_PLUGIN_ROOT}/assets/foundation/ui.tsx` to `<targetDir>/ui.tsx`. Hash + record in the manifest payload as `kind: "foundation"`. If the file already exists and is `modified`, skip.

### Step S7 — Styles (skipped under `--skip-styles`)

1. Determine the seed color: `--seed=<hex>` flag, or the `acss-kit.theme.json` `seed` field if it exists, or prompt the developer.
2. Run `generate_palette.py` → palette JSON.
3. Run `tokens_to_css.py` → emit `<stylesDir>/theme/light.css` and `<stylesDir>/theme/dark.css`.
4. Write `<projectRoot>/acss-kit.theme.json` with `{ "seed": "<hex>", "generatedAt": "<iso>" }` for re-runs.
5. Hash all three files; add to the manifest payload as `kind: "style"` (for the CSS files) and `kind: "theme"` (for `acss-kit.theme.json`).
6. Run `validate_theme.py` against the new CSS files. Surface any WCAG failures, but do not block — the developer may want to tune.

### Step S8 — Write the manifest

Pipe the assembled payload to `manifest_write.py`:

```bash
echo '<payload-json>' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/manifest_write.py
```

The payload includes `projectRoot`, `pluginVersion` (read from `.claude-plugin/plugin.json`), `targetDir`, `stylesDir`, `themeFile`, and the `files[]` array.

### Step S9 — Verify integration

Run `verify_integration.py`. Surface any missing-import reasons as a numbered fix-up list.

### Step S10 — Summary

```text
/kit-sync complete:

  Created:  18 files
  Skipped:   2 files (modified — listed below)
  Manifest: .acss-kit/manifest.json

  Skipped (user-modified):
    src/components/fpkit/button.tsx
    src/styles/theme/light.css

  Next:
    /kit-update         — re-sync clean files after future plugin upgrades
    /kit-update --check — preview drift without writing
```

---

## Safe-update workflow (`/kit-update`)

Triggered by `/kit-update [<component>...]` and by natural-language phrasing like "update unmodified components", "re-copy the kit safely", "refresh anything I haven't touched".

### Flags

- `<component>...` — restrict the update to a list of components (e.g. `/kit-update button alert`). Default: every entry in the manifest.
- `--check` — report only; do not write.
- `--force` — overwrite modified files too. Each modified file is backed up to `<file>.bak` before being overwritten.

### Step U1 — Read the manifest

Run `manifest_read.py <projectRoot>`. Three terminating cases:

- **`exists: false`** — manifest missing or malformed. Halt with:

  ```text
  No .acss-kit/manifest.json found. Run /kit-sync first to bulk-install
  the kit and start tracking generated files.
  ```

- **`schemaMismatch: true`** — manifest is on disk but written by a different schemaVersion. Halt with the `reasons[]` from the script — do **not** fall through to a fresh-install path, since that would bypass drift protection on every tracked file.
- Otherwise — proceed to Step U2.

### Step U2 — Compute drift

Run `diff_status.py <projectRoot>`. Capture `clean[]`, `modified[]`, and `missing[]`.

If a positional component filter was passed, intersect each list with the requested set (matching on the `component` field of each entry).

### Step U3 — Show the report

```text
/kit-update report — <projectRoot>:

  Clean (will overwrite):    14 files
  Modified (will skip):       2 files
  Missing (will recreate):    1 file

  Modified — your changes preserved:
    src/components/fpkit/button.tsx
    src/styles/theme/light.css

  Missing — will be regenerated:
    src/components/fpkit/icon.tsx
```

If `--check`, stop here.

### Step U4 — Regenerate clean + missing files

For each entry in `clean[]` and `missing[]`:

1. Re-run the same generation logic the bulk-install workflow uses for that file's `kind` and `source`.
2. Hash the new content.
3. Write the file.
4. Add the new sha to a manifest update payload.

For each entry in `modified[]`:

- If `--force`: copy current content to `<file>.bak`, regenerate, write, hash, update manifest entry.
- Otherwise: skip and add to the summary.

### Step U5 — Rewrite the manifest

Pipe the merged update payload to `manifest_write.py`. Existing entries that were not touched (because they were skipped) keep their previous sha — no spurious churn.

### Step U6 — Summary

```text
/kit-update complete:

  Updated:  14 files
  Skipped:   2 files (modified — pass --force to overwrite with .bak backup)
  Recreated: 1 file
  Manifest: .acss-kit/manifest.json
```

---

## When invoked outside a slash command

If a user phrase auto-triggers this skill (e.g. "copy every acss-kit component into my project"), pick the workflow that fits:

- "install/copy everything", "bulk copy", "vendor the whole kit" → bulk install workflow.
- "update unmodified", "refresh clean components", "safely re-copy" → safe-update workflow.

When ambiguous, ask once: "Bulk install (writes everything) or safe update (only re-copies unmodified files)?"
