---
name: style-update
description: Re-validate and roll forward existing theme assets after a maintainer edits role-catalogue, palette-algorithm, theme-schema, or a bundled brand preset. Use when the maintainer asks to update a theme reference, refine the palette algorithm, refresh the role catalogue, or re-validate themes after a role change.
disable-model-invocation: false
---

# /style-update

Usage: `/style-update <path>` (e.g. `/style-update plugins/acss-kit/skills/styles/references/role-catalogue.md`)

Detects which kind of theme asset was edited and runs the appropriate downstream re-validation. Does not author new assets — use `/style-author` for that.

## Step 1 — Detect the asset kind

Inspect `<path>`. Branch on the matching pattern:

| Path matches | Asset kind | Skip to |
|---|---|---|
| `references/role-catalogue.md` | role-catalogue | Step 2 |
| `references/palette-algorithm.md` | palette-algorithm | Step 3 |
| `references/theme-schema.md` or `assets/theme.schema.json` | theme-schema | Step 4 |
| `assets/brand-template.css` or `assets/brand-presets/*.css` | brand-preset | Step 5 |
| `skills/styles/SKILL.md` | styles SKILL | Step 6 |
| anything else | unknown | Halt with message: `<path> is not a recognized theme asset. Edit role-catalogue.md, palette-algorithm.md, theme-schema.md, theme.schema.json, or a CSS file under assets/.` |

If `<path>` is omitted, ask the maintainer which file they edited via AskUserQuestion.

---

## Step 2 — role-catalogue change

A new role or modified description in the role catalogue should propagate to the JSON schema, the styles SKILL.md inline list, and the Python `ROLE_GROUPS` constant.

1. Read `plugins/acss-kit/skills/styles/references/role-catalogue.md`. Extract the full set of `--color-*` role names.
2. Read `plugins/acss-kit/assets/theme.schema.json` `$defs.palette.properties` keys.
3. Read `plugins/acss-kit/scripts/tokens_to_css.py` `ROLE_GROUPS` constant. Extract every role name across all groups.
4. Diff the three sets. Surface any role that appears in one but not the others.
5. If `theme.schema.json` is missing a role, prompt the maintainer to confirm and Edit the schema. If `tokens_to_css.py:ROLE_GROUPS` is missing a role, surface the manual edit needed (do NOT modify the Python source automatically — print the exact diff the maintainer should apply).
6. Run the `theme-reference-reviewer` agent. Surface its report.

---

## Step 3 — palette-algorithm change

A change to the OKLCH lightness anchors or hue offsets should be reflected in `generate_palette.py` and re-validated against any bundled brand presets that were derived algorithmically.

1. Read `plugins/acss-kit/skills/styles/references/palette-algorithm.md` and extract the documented constants (lightness anchors per role group, hue offsets for state colors).
2. Read `plugins/acss-kit/scripts/generate_palette.py` and extract the corresponding constants.
3. Diff and surface any drift. If drift is detected, surface the exact line and suggested edit; do not modify the Python automatically.
4. After confirming parity (or on the maintainer's confirmation that they will reconcile), regenerate every algorithmically-derived brand preset. `assets/brand-template.css` is the user-facing starter template — hand-authored and explicitly NOT a regeneration target.

   For each `brand-<name>.css` under `assets/brand-presets/`:
   - Parse the `/* seed: #rrggbb */` header comment to recover the seed. If no seed is recorded, skip the file and note it (hand-authored preset).
   - Run the same reshape pipeline used by `style-author` sub-flow A:

     ```
     python3 plugins/acss-kit/scripts/generate_palette.py "<seed>" --mode=brand \
       | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps({'brands': {'<name>': d['brand_overrides']}}))" \
       | python3 plugins/acss-kit/scripts/tokens_to_css.py --stdin --out-dir=plugins/acss-kit/assets/brand-presets/
     ```

   If `assets/brand-presets/` does not exist or is empty, note "no bundled presets to regenerate" and continue.

5. Re-validate every regenerated preset by running `python3 plugins/acss-kit/scripts/validate_theme.py <file>` per `brand-*.css` file under `assets/brand-presets/`. Skip `assets/brand-template.css` (hand-authored, not part of the algorithmic regeneration target).
6. Run the `theme-reference-reviewer` agent.

---

## Step 4 — theme-schema change

A schema change must keep markdown documentation, the JSON schema, and downstream brand presets in agreement.

1. If `<path>` was the markdown reference, also read `assets/theme.schema.json` (and vice versa). Surface drift between the two.
2. For each new property added to the schema, confirm:
   - It is documented in `references/role-catalogue.md` (if it is a role).
   - It is documented in `references/theme-schema.md` (if it is a structural change like a new $defs section).
   - It is reflected in `tokens_to_css.py` if it affects CSS output.
3. Re-run `python3 plugins/acss-kit/scripts/validate_theme.py` against `assets/brand-template.css` and `assets/brand-presets/*.css` to catch schema-related regressions.
4. Run the `theme-reference-reviewer` agent.

---

## Step 5 — brand-preset change

A change to a bundled brand preset CSS file must still satisfy WCAG 2.2 AA contrast pairs.

1. Run `python3 plugins/acss-kit/scripts/validate_theme.py <path>`. Capture exit code + output.
2. If validation fails:
   - Surface the failing pairs.
   - Ask the maintainer whether to (a) accept failures with documented divergences in a comment header in the file, (b) revert the change, or (c) tune the seed and regenerate via `/style-author --from=<hex> <preset-name>`.
3. If validation passes, surface the contrast ratio summary and confirm the file's header comment still records the seed (`/* seed: #... */`) — if missing, prompt the maintainer to add it for future reproducibility.

---

## Step 6 — styles SKILL.md change

A change to the styles SKILL itself usually touches the role list, contrast pair table, or workflow descriptions.

1. Run the `theme-reference-reviewer` agent — it cross-checks the SKILL.md role list and contrast pair table against the schema and `validate_theme.py:PAIRS`.
2. If the change touches command workflows (`/theme-create`, `/theme-brand`, `/theme-update`, `/theme-extract`), also run the `skill-quality-reviewer` agent on the file.
3. Surface both reports inline.

---

## Final summary

Every sub-flow ends with:
- Files modified during the skill run (typically just the schema edit if Step 2 found drift).
- Validation results: contrast pass/fail, reviewer agent verdict.
- Manual follow-ups: any Python edits the maintainer must apply by hand.
- Reminder to bump `acss-kit` version via `/release-plugin acss-kit <new-version>` if the change is user-visible.
