# acss-component-specs — Recipes

Common tasks, step by step. Each recipe assumes the plugin is installed and you are inside a Claude Code session in your project directory.

---

## Render a component to a single framework

```
/spec-render button --target=react
/spec-diff button
/spec-promote button
```

1. `/spec-render` writes `button/button.tsx` and `button/button.scss` to `.acss-staging/react/`.
2. `/spec-diff` shows a unified diff between staging and your current project files (or shows the new files in full if they don't exist yet).
3. `/spec-promote` moves the staged files to `<componentsDir>/button/`.

---

## Render to all three frameworks

```
/spec-render button --target=all
```

Or, if `.acss-target.json` has no `framework` field, render all is the default:

```
/spec-render button
```

This writes output to three staging subdirectories:

```
.acss-staging/
  react/button/button.tsx + button.scss
  html/button/button.html + button.css
  astro/button/Button.astro + button.scss
```

Promote each independently:

```
/spec-promote button --target=react
/spec-promote button --target=html
/spec-promote button --target=astro
```

---

## Configure a per-project default framework

Edit `.acss-target.json`:

```json
{
  "componentsDir": "src/components",
  "framework": "astro"
}
```

Now `/spec-render <component>` defaults to Astro. Override any time with `--target`.

---

## Handle a compound component (Card)

Card has sub-parts (Title, Content, Footer) defined as separate sub-specs. When you render Card, all sub-parts are included automatically:

```
/spec-render card --target=react
```

`plan_render.py` knows about the compound parts and emits them inside the parent component file (using `Object.assign(Card, { Title, Content, Footer })`). No separate files are created for the sub-parts — they live in `card/card.tsx`.

For Astro, sub-parts are emitted as separate files (`card/CardTitle.astro`, etc.) because Astro does not use static properties on components.

See [`references/compound-components.md`](../skills/acss-component-specs/references/compound-components.md) for the full compound pattern.

---

## Handle a stateful component (Dialog)

Dialog requires Button as a dependency. `plan_render.py` resolves this:

```
/spec-render dialog --target=react
```

Preview output:

```
New:
  ui.tsx          (if not present)
  button/button.tsx
  button/button.scss
  dialog/dialog.tsx
  dialog/dialog.scss
```

The Dialog spec uses a native `<dialog>` element for built-in focus management. The React renderer emits `useRef<HTMLDialogElement>` + `dialogRef.current?.showModal()`. No focus-trap library is needed.

See [`references/state-and-events.md`](../skills/acss-component-specs/references/state-and-events.md) for how Dialog, Alert, and interactive Card are handled per framework.

---

## Update a spec and find stale project files

After editing a spec (or after running `/spec-add <component> --refresh` to pull upstream changes), bump the spec's patch version in its frontmatter:

```yaml
# specs/button.md
format_version: 1
name: button
fpkit_version: "newsha1"   # updated by /spec-add --refresh
```

Then find project files that are behind:

```
/spec-validate --stale
```

`validate_spec.py` scans project files for `// generated from button.md@<old-version>` stamps and reports which files need re-rendering.

For each stale file:

```
/spec-render button --target=react
/spec-diff button
/spec-promote button
```

---

## Validate all specs at once

```
/spec-validate
```

Validates every `specs/*.md` against the schema. Useful before committing a batch of new or edited specs, or as part of a pre-PR check.

---

## Check what components are available

```
/spec-list
```

Prints a table of all specs with `name`, `format_version`, and `fpkit_version`. Use `/spec-list <component>` to dump full details for one spec (props, events, CSS vars, a11y block).
