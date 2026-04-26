---
name: style-author
description: Scaffold a new bundled brand preset, palette role, or theme-schema field for the acss-kit plugin. Use when the maintainer asks to add a brand preset to the plugin, extend the role catalogue with a new color role, scaffold a bundled brand template, or tweak the OKLCH palette algorithm.
disable-model-invocation: false
---

# /style-author

Three sub-flows scaffold new style assets bundled with the acss-kit plugin. The maintainer picks one at the start. Each sub-flow ends with a contrast-pair re-validation summary so any change is gated by WCAG 2.2 AA.

This skill is for **maintainer-side** scaffolding (extending the plugin itself). It is NOT the same as the user-facing `/theme-create` and `/theme-brand` commands which generate themes for end-user projects.

## Step 0 — Choose a sub-flow

Use AskUserQuestion to ask which kind of style asset to scaffold:

- **Brand preset** — add a new `assets/brand-presets/<name>.css` file shipped with the plugin
- **New role** — add a new `--color-*` role to the role catalogue, schema, and Python role groups
- **Palette algorithm tweak** — adjust the OKLCH lightness anchors or hue offsets

Branch to the matching step set below.

---

## Sub-flow A — Brand preset

Usage: `/style-author <preset-name> --from=<hex>` (e.g. `/style-author sunset --from=#f97316`)

The output filename is always `brand-<preset-name>.css` (with the `brand-` prefix). Two scripts are involved:
- `generate_palette.py --mode=brand` outputs `{seed, reasons, brand_overrides: {light, dark}}` — note the singular `brand_overrides` shape, distinct from the `modes` shape `--mode=both` produces.
- `tokens_to_css.py` consumes a tokens document with `{brands: {<name>: {light, dark}}}` and writes one CSS file per brand named `brand-<name>.css`.
- Because the two shapes differ, sub-flow A inserts a JSON reshape step between them.

### A1. Validate inputs

- `<preset-name>` is lowercase kebab-case (alphanumeric + hyphens). The `brand-` prefix is added automatically — do not include it in `<preset-name>`.
- `<hex>` is a 3- or 6-digit hex color.
- Refuse if `plugins/acss-kit/assets/brand-presets/brand-<preset-name>.css` already exists.

### A2. Create the brand-presets directory if missing

If `plugins/acss-kit/assets/brand-presets/` does not exist, create it. This directory is a new convention for bundled brand presets — distinct from the existing `assets/brand-template.css` user-facing template.

### A3. Generate, reshape, and write CSS

Run from the worktree root as a single pipeline:

```
python3 plugins/acss-kit/scripts/generate_palette.py "<hex>" --mode=brand \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps({'brands': {'<preset-name>': d['brand_overrides']}}))" \
  | python3 plugins/acss-kit/scripts/tokens_to_css.py --stdin --out-dir=plugins/acss-kit/assets/brand-presets/
```

The middle stage transforms `{brand_overrides: {...}}` into `{brands: {'<preset-name>': {...}}}`, which is what `tokens_to_css.py` consumes. It also short-circuits on `reasons` from `generate_palette.py` (non-empty `reasons` ⇒ exit 1, JSON to stderr).

If any stage of the pipeline returns non-zero, print the captured stderr and halt. Confirm the output file `plugins/acss-kit/assets/brand-presets/brand-<preset-name>.css` was written (`tokens_to_css.py` prints `wrote: <path>` on success).

### A4. Validate WCAG contrast

Run:

```
python3 plugins/acss-kit/scripts/validate_theme.py plugins/acss-kit/assets/brand-presets/brand-<preset-name>.css
```

The filename `brand-<preset-name>.css` matches the `^(light|dark|brand-[\w-]+)\.css$` regex in `validate_theme.py`. If validation prints `validate_theme: skipped (no palette files found)`, the filename is wrong — verify the brand- prefix was added by `tokens_to_css.py` and re-run.

If any contrast pair fails (exit code 1), surface the failures. Ask the maintainer whether to (a) keep the preset as-is with documented divergences (add a `/* divergences: ... */` comment header to the file), (b) tune the seed hex and regenerate, or (c) discard. Only proceed if the maintainer accepts the result.

### A5. Update styles SKILL.md

Read `plugins/acss-kit/skills/styles/SKILL.md`. Find or create a "Bundled brand presets" section (place it just before the "Error handling" section near the bottom). Append:

```markdown
- **<preset-name>** (`assets/brand-presets/brand-<preset-name>.css`) — derived from `<hex>` via `generate_palette.py --mode=brand`. <one-line description>
```

If the section did not exist, create it with a short intro line.

### A6. Print summary

- Files created: `assets/brand-presets/brand-<preset-name>.css`
- Files modified: `skills/styles/SKILL.md`
- WCAG validation: PASS / N pairs failed (with names)
- Reminder: bump `acss-kit` plugin version via `/release-plugin acss-kit <new-version>` if this preset should ship.

---

## Sub-flow B — New role

Usage: `/style-author --role=<--color-name>` (e.g. `/style-author --role=--color-accent-muted`)

### B1. Validate the role name

- Must start with `--color-`.
- Must be kebab-case after the prefix.
- Refuse if the role already appears in `plugins/acss-kit/assets/theme.schema.json` `$defs.palette.properties`.

### B2. Capture role metadata via AskUserQuestion

Ask:
- **Group** — Backgrounds / Text / Borders / Brand & semantic / Focus
- **Required vs optional** — default optional (new roles should not break existing themes)
- **Description** — one line describing the role's purpose
- **Suggested fallback hex** — used when generating brand presets that do not override this role

### B3. Update `assets/theme.schema.json`

Use Edit to add the role to `$defs.palette.properties`. If "required" was selected in B2, also add the role name to `$defs.palette.required` array.

### B4. Update `references/role-catalogue.md`

Use Edit to add a row under the matching group section, mirroring the existing format. Include the role name, description, and any contrast pairings if it interacts with text/background.

### B5. Update `skills/styles/SKILL.md`

Use Edit to add the role to the appropriate group bullet list under "Semantic role names". Mark required vs optional with the same `*(required)*` / `*(optional)*` annotation used by neighboring roles.

### B6. Update `references/theme-schema.md`

Use Edit to document the new role in the schema reference, mirroring existing entries.

### B7. Remind the maintainer about Python parity

Print a prominent reminder:

> The new role must also be added to `plugins/acss-kit/scripts/tokens_to_css.py` `ROLE_GROUPS` constant. Without that update, generated theme files will not include the new role. Edit the appropriate group entry by hand — this skill does not modify Python source.

If the role is required (not optional), also remind:

> Required roles must be present in every bundled `light.css`, `dark.css`, and brand preset. Run `/style-update` after adding the role to backfill existing themes.

### B8. Run the reviewer agent

Invoke `theme-reference-reviewer` to confirm the role appears consistently across markdown and the JSON schema. Surface its report inline.

### B9. Print summary

- Files modified: list them
- Manual follow-up: tokens_to_css.py:ROLE_GROUPS, downstream theme files (if required role)

---

## Sub-flow C — Palette algorithm tweak

Usage: `/style-author --algorithm`

### C1. Confirm scope via AskUserQuestion

Ask which algorithm parameter to tweak:
- Lightness anchors (light-mode background, surface, text, etc.)
- State-color hue offsets (success, warning, danger, info)
- Brand-mode primary derivation (primary-hover, primary-pressed)
- Other (free-text)

### C2. Edit `references/palette-algorithm.md`

Use Edit to apply the maintainer's change to the relevant section. Preserve the existing structure (anchors → offsets → derivation rules).

### C3. Remind about generate_palette.py parity

The OKLCH constants live in both `references/palette-algorithm.md` (documentation) and `plugins/acss-kit/scripts/generate_palette.py` (implementation). Print:

> Update the matching constant in `plugins/acss-kit/scripts/generate_palette.py` to keep the doc and implementation in sync. The `theme-reference-reviewer` agent will flag drift between them.

### C4. Regenerate every bundled brand preset (not the user-facing template)

`assets/brand-template.css` is the user-facing starter template the consumer copies into their project — it is hand-authored and not a candidate for regeneration. The targets here are the bundled `assets/brand-presets/brand-*.css` files (if any exist), each of which records a seed hex in a header comment of the form `/* seed: #rrggbb */`.

For each `brand-<name>.css` under `assets/brand-presets/`:

1. Parse the `/* seed: #rrggbb */` header to recover `<seed>`. If no seed is recorded, skip the file and note it in the summary (hand-authored preset).
2. Re-run the same reshape pipeline used by sub-flow A:

   ```
   python3 plugins/acss-kit/scripts/generate_palette.py "<seed>" --mode=brand \
     | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps({'brands': {'<name>': d['brand_overrides']}}))" \
     | python3 plugins/acss-kit/scripts/tokens_to_css.py --stdin --out-dir=plugins/acss-kit/assets/brand-presets/
   ```

   This rewrites `brand-<name>.css` in place using the updated algorithm constants.

If `assets/brand-presets/` does not exist or is empty, note "no bundled presets to regenerate" and continue.

### C5. Re-validate every bundled preset

Run `python3 plugins/acss-kit/scripts/validate_theme.py <file>` against each `brand-*.css` under `assets/brand-presets/`. Skip `assets/brand-template.css` (it is hand-authored and not part of the algorithmic regeneration target). Surface any contrast failures with the failing pair names.

### C6. Run the reviewer agent

Invoke `theme-reference-reviewer` to confirm the algorithm constants in markdown match the Python script. Surface its report.

### C7. Print summary

- Files modified
- Bundled presets re-validated (PASS / FAIL counts)
- Manual follow-up: bump `acss-kit` version if the algorithm change is user-visible.

---

## Error handling (all sub-flows)

| Situation | Action |
|---|---|
| Seed hex invalid | Halt with: `"<value>" is not a valid hex color. Use #rrggbb or #rgb.` |
| `generate_palette.py` exits 1 | Print each reason from `"reasons"` array. Halt. |
| Output file already exists | Halt with the conflict path. Maintainer must rename or delete. |
| WCAG validation fails | Surface failures and ask the maintainer whether to keep, retune, or discard. |
| theme-reference-reviewer reports drift | Surface findings inline; do not block — the maintainer fixes the drift on next commit. |
