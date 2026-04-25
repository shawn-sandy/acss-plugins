# acss-component-specs — Troubleshooting

---

## Stale stamps: "/spec-validate --stale" reports outdated files

**Symptom:** Running `/spec-validate --stale` lists project files with stamps older than the current spec version (e.g., `// generated from button.md@0.0.9` but current spec is `0.1.0`).

**Fix:**

```
/spec-render button --target=react
/spec-diff button
/spec-promote button
```

Re-render the component from the updated spec, review the diff, and promote. Repeat for each stale file or framework target.

If you updated the spec without bumping its version field, the stamp check won't flag it. Always bump the spec's patch version in frontmatter when you make meaningful changes to the spec body.

---

## Kit-builder parity drift: pre-commit hook fails

**Symptom:** You edited `specs/button.md` and ran `git commit`. The pre-commit hook ran `check_kitbuilder_parity.py` and exited 1 with a message like "SCSS parity drift for 'button': staged SCSS differs from kit-builder reference."

**Cause:** The SCSS block in your spec (written to `.acss-staging/react/button/button.scss`) no longer matches the `## SCSS Pattern` block in `acss-kit-builder/skills/acss-kit-builder/references/components/button.md`.

**Fix:** You need to reconcile the two. Either:

1. Update the SCSS pattern in `specs/button.md`'s Markdown body to match the kit-builder reference, or
2. Update the kit-builder reference doc's `## SCSS Pattern` block to match the spec (and bump kit-builder's version).

Option 2 is the right call when the spec is intentionally ahead of the bundled reference — the spec is the source of truth. Option 1 is right when you made an unintentional change to the spec body.

After reconciling, re-run `/spec-render button --target=react` to update the staged SCSS, then retry the commit.

---

## fpkit cache miss / network failure in /spec-add

**Symptom:** `/spec-add <component>` aborts or produces a spec with `fpkit_version: "main"` (instead of a real short SHA).

**Cause:** `fetch_fpkit_source.py` could not reach the GitHub API or the raw file URL.

**Check:**

```bash
python3 plugins/acss-component-specs/scripts/fetch_fpkit_source.py button
```

The JSON output includes a `reasons` array explaining the failure. Common reasons:

- Network unavailable.
- GitHub API rate limit hit (returns HTTP 403). Wait or set `GITHUB_TOKEN` in your environment.
- Component path not in the known path map. The script tries `<comp>s/<comp>.tsx` and `<comp>/<comp>.tsx` as fallbacks. If neither exists, it fails.

When the SHA resolve fails but the source fetch succeeds, the version is recorded as `"main"`. The spec is still functional, but the version is not pinned. Re-run with `--refresh` when network access is restored to pin it properly.

---

## Atomic rollback: render fails mid-way

**Symptom:** `/spec-render <component>` reports a failure and `.acss-staging/` is empty (or does not contain the expected files).

**Cause:** The atomic-failure rule in the SKILL rolls back all staged output if any step fails. The staging directory is never left in a partial state.

**Fix:** Read the error message. Common causes:
- `specs/<component>.md` does not exist → run `/spec-add <component>` first.
- A dependency spec is missing (e.g., Dialog needs Button, but `specs/button.md` doesn't exist) → run `/spec-add button`, then retry.
- `validate_spec.py` found a schema error → fix the spec frontmatter, then retry.

---

## Missing theme: "/spec-render" warns about CSS variables

**Symptom:** After running `/spec-render`, you see a warning: "No `:root { --color-primary: … }` found in project CSS/SCSS. Theme values will fall back to hardcoded defaults."

**Cause:** The spec's `theme_dependencies` field declares that the component uses one or more `--color-*` tokens (e.g., `--color-primary`, `--color-text-inverse`). The renderer scanned the project and found no `:root` block defining these tokens.

**This is informational, not an error.** Hardcoded fallbacks are present on every CSS variable, so the component renders correctly without a theme file.

**Fix (optional):** Install `acss-theme-builder` and generate a theme with `/app-theme`. The generated `:root { … }` block will supply the tokens and suppress the warning.

---

## ".acss-staging/ not in .gitignore"

**Symptom:** On first render, you see a prompt: "`.acss-staging/` is not in your project's `.gitignore`. Add it? [Enter/Ctrl+C]"

**Fix:** Press Enter. The staging directory is a transient build artifact — it should not be committed. The prompt is step R6 of the render flow; it fires once per project.

If you dismissed the prompt and accidentally committed `.acss-staging/` contents, remove them:

```bash
echo '.acss-staging/' >> .gitignore
git rm -r --cached .acss-staging/
git commit -m "chore: remove staging directory from tracking"
```

---

## framework in .acss-target.json is overriding --target

**Symptom:** You ran `/spec-render button --target=html` expecting HTML output, but React output appeared instead.

**Cause:** The `--target` flag overrides `.acss-target.json.framework`. If React output appeared despite `--target=html`, check that the `--target` argument was actually passed and that the spec renders correctly to HTML (some specs have incomplete HTML framework notes — check the spec body's HTML section).

**Resolution order (highest priority first):**

1. `--target` flag passed to the command.
2. `framework` field in `.acss-target.json`.
3. Default: render all three.

If `framework` in `.acss-target.json` is set to `react` and you want a one-off HTML render, always pass `--target=html` explicitly.
