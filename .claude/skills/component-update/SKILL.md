---
name: component-update
description: Re-verify and refresh an existing component reference doc against its captured fpkit ref. Use when the maintainer asks to update a component, refresh a button reference doc, bump the fpkit verification on a component, or check whether a component has drifted from upstream.
disable-model-invocation: false
---

# /component-update

Usage: `/component-update <component-name>`

Example: `/component-update button`

Re-verifies an existing component reference doc against its captured fpkit ref, surfaces any drift in the TSX or SCSS templates, and runs the canonical-shape reviewer agent. Does NOT scaffold new components — use `/component-author` for that.

## Steps

1. **Confirm the reference doc exists.**
   - Resolve `<component-name>` to `plugins/acss-kit/skills/components/references/components/<component-name>.md`.
   - If the file does not exist, halt and suggest `/component-author <component-name>` instead.

2. **Read the verification banner and Generation Contract.**
   - Capture `<ref>` from the `**Verified against fpkit source:**` line at the top of the file.
   - Capture `<export_name>`, `<file>`, `<scss>`, `<imports>`, `<dependencies>` from the Generation Contract.
   - Capture the existing `<divergences>` from the verification banner (everything after "Intentional divergences from upstream:").

3. **Fetch the upstream fpkit source at `<ref>`.**
   - Build the raw URL first: `https://raw.githubusercontent.com/shawn-sandy/acss/<ref-as-tag-or-sha>/packages/fpkit/src/components/<component-name>/<component-name>.tsx`. The raw form returns the actual file contents; the `github.com/.../blob/...` form returns rendered HTML, which would corrupt the diff in step 4.
   - Use WebFetch on the raw URL. If the captured `<ref>` is `@fpkit/acss@<version>`, translate to the matching git tag (typically `v<version>` or `<version>`).
   - Repeat for the `.scss` companion if `<scss>` is not `(none)`, using the same raw URL form.
   - If WebFetch returns 404, try the alternate translated ref (e.g. `<version>` if `v<version>` failed) or verify the component path. Only as a last resort fall back to the rendered `https://github.com/shawn-sandy/acss/blob/<ref>/...` URL and warn the maintainer that the diff may include HTML noise. If still 404, surface the error and ask the maintainer for a corrected ref or path.

4. **Diff upstream vs local templates.**
   - Read the `## TSX Template` fenced block from the local reference doc.
   - Compare structurally to the upstream TSX (ignore the documented `<divergences>` — those are expected gaps).
   - Repeat for `## SCSS Template`.
   - Surface drift as a unified diff or section-by-section summary: "Upstream adds prop X", "Upstream renames hook Y", etc.

5. **Surface findings via AskUserQuestion.**
   Present the drift summary and ask the maintainer:
   - Is the upstream change intentional and should be applied? (If yes, edit the TSX/SCSS Template blocks to match.)
   - Does the verification banner need an updated divergence note? (If yes, edit the banner.)
   - Should the catalog row's Status be updated? (Default: keep current.)
   If the maintainer chooses "No drift detected", proceed to step 7 without edits.

6. **Apply approved edits.**
   - Use Edit to replace the TSX Template fence content if the maintainer approved an upstream pull.
   - Use Edit to replace the SCSS Template fence content if approved.
   - Use Edit to update the verification banner if `<divergences>` changed or the maintainer wants to bump `<ref>` to a newer tag.
   - Use Edit to update the catalog row in `plugins/acss-kit/skills/components/references/components/catalog.md` if the Status changed.

7. **Warn about export_name changes.**
   If the maintainer's edits changed `<export_name>` in the Generation Contract, print a prominent warning:

   > Changing `export_name` is a breaking change for existing `/kit-add` consumers. The generated `<file>` will export a different identifier; downstream imports will break on regenerate. Confirm this is intentional before committing.

   Use Grep to scan `plugins/acss-kit/skills/components/SKILL.md` and the catalog for any other references to the old export_name and surface them.

8. **Run the reviewer agent.**
   Invoke `component-reference-reviewer` against the file. Surface its report inline.

9. **Print a summary.**
   - Files modified (or "No changes — no drift detected").
   - Reviewer agent verdict (PASS / N issues found).
   - Reminder if `<export_name>` changed: re-run any downstream consumers.

This skill does not bump the plugin version. After committing the reference doc change, run `/release-plugin acss-kit <new-version>` if the change should ship.
