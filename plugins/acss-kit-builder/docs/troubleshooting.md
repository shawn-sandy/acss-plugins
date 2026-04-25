# acss-kit-builder — Troubleshooting

---

## "sass or sass-embedded not found in devDependencies"

**Symptom:** `/kit-add` aborts immediately with a message about missing sass.

**Fix:**

```bash
npm install -D sass
```

Then re-run `/kit-add`. The plugin reads `package.json`'s `devDependencies` key — make sure the install completed and the key is present before retrying.

If your project uses `sass-embedded` instead:

```bash
npm install -D sass-embedded
```

Either package satisfies the check.

---

## "Components are generating into the wrong directory"

**Symptom:** Files appear in a different folder than expected.

**Cause:** `.acss-target.json` at the project root contains a `componentsDir` value from a previous `/kit-add` run or from `acss-app-builder`.

**Fix:** Open `.acss-target.json` and update `componentsDir` to the path you want:

```json
{
  "componentsDir": "src/components/fpkit"
}
```

Future `/kit-add` runs will use the new path. Existing generated files in the old directory are not moved — rename the directory manually and update your imports if you change the path after files have already been generated.

---

## Component name not recognized

**Symptom:** `/kit-add frobniz` fails or produces an empty preview.

**Fix:** Run `/kit-list` to see the full list of available component names. Names are lowercase and exact — `dialog`, not `Dialog` or `modal`. The available components are: badge, tag, heading, text, link, list, details, progress, icon, button, alert, card, nav, dialog, form.

If you need a component that is not listed, it does not yet have a bundled reference doc. Use `/kit-list` to check for aliases, or author a spec via `acss-component-specs` and `/spec-add`.

---

## "acss-component-specs is installed but the spec isn't being used"

**Symptom:** `/kit-add button` generates from the bundled reference doc even though you installed `acss-component-specs`.

**Cause:** The B0 spec-bridge probe checks two paths. If neither resolves to an actual file, it silently falls back to the bundled reference.

**Check the two probe paths:**

1. `$CLAUDE_PLUGIN_ROOT/../acss-component-specs/skills/acss-component-specs/specs/<component>.md`
2. `~/.claude/plugins/cache/acss-component-specs/skills/acss-component-specs/specs/<component>.md`

If the spec file exists but the first path is wrong (e.g., the plugins are in different directories), the probe silently skips it. Confirm that `acss-component-specs` is installed at the expected sibling path relative to `acss-kit-builder`.

If the spec file does not exist yet, run `/spec-add <component>` first.

---

## "ui.tsx already exists but looks different from what the plugin expects"

**Symptom:** After running `/kit-add`, you notice that the `ui.tsx` in your project does not match the `assets/foundation/ui.tsx` in the plugin. Your generated components import from it, but something behaves unexpectedly.

**Cause:** The skip-existing rule means `/kit-add` never overwrites `ui.tsx` once it exists. If you or another plugin wrote a different `ui.tsx` first, the generated components will import from that file.

**Fix:** Compare your `ui.tsx` against [`assets/foundation/ui.tsx`](../assets/foundation/ui.tsx). If they have diverged, copy the plugin's version and reconcile any local modifications. The `UI` component's polymorphic type chain (`PolymorphicRef<C>` → `UIProps<C>` → `UIComponent`) must be intact for generated components to type-check correctly.

---

## "Bottom-up generation order is surprising"

**Symptom:** You expected `alert` to be generated before `button`, but they were generated in the opposite order.

**Explanation:** The plugin generates leaf dependencies first. If Alert depends on Button, Button is generated first (it is closer to the leaf). This is intentional — it guarantees that every dependency exists on disk before the component that imports it is written.

If you are surprised by which component depends on which, run `/kit-list <component>` to see the full dependency list before running `/kit-add`.

---

## "My edited component was overwritten"

**Symptom:** You edited a generated file, then re-ran `/kit-add` and your changes were gone.

**This should not happen.** The skip-existing rule means `/kit-add` does not write to a file that already exists. If your edits were lost, check:

1. Did you delete and recreate the file before running `/kit-add`?
2. Was the file in the correct `componentsDir` at the time of the second run? (Check `.acss-target.json`.)
3. Did you run `/spec-promote` instead of `/kit-add`? The `spec-promote` command does overwrite — that is its documented behavior.

---

## Import paths resolve incorrectly after renaming a component file

**Symptom:** After renaming `button/button.tsx` to `button/btn.tsx`, the Dialog component breaks because it imports from `../button/button`.

**Cause:** Import paths in generated files are resolved at generation time from the component's `file` field in its Generation Contract. Renaming files after generation requires updating imports manually.

**Fix:** Update all `import` statements that reference the old filename. There is no automated re-import for post-generation renames.
