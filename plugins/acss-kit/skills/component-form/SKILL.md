---
name: component-form
description: Use when the user asks to create a form, scaffold a form, build a signup/contact/login form, generate form components, add form validation, or design accessible form layouts. Triggers include "create a form", "add a form", "build a form component", "scaffold a form", "form with fields", "form scaffolding". Pilot per-component skill — promoted from `references/components/form.md` because forms are high-iteration and benefit from auto-discoverable triggering.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.3.0"
  pilot: true
---

# SKILL: component-form

Generate a self-contained, accessible React form component into the developer's project. The form is composed from the components skill's `Field`, `Input`, and `Checkbox` reference components; if any of those don't yet exist in the target directory, this skill walks the user through `/kit-add field input checkbox` first.

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). The form composition pattern follows the upstream `components/form/form.tsx` structure (a top-level `<form>` with composed Fields), but the vendored version targets a single self-contained generated file rather than the multi-file upstream split (`form.tsx` + `fields.tsx` + `inputs.tsx` + `checkbox.tsx` + `form.types.ts`).

## Pilot status

This is the only per-component skill in `acss-kit` v0.3.0. It exists to validate the per-component skill discovery pattern. If the trigger reliability proves out in real-world usage, additional components (Dialog, Card, Table, Popover) may be promoted to skills in a future release. Until then, those remain reference docs.

If you're authoring a component reference doc and unsure whether to promote it to a skill, default to a reference doc. Promotion adds discovery surface but also doubles authoring overhead (frontmatter trigger phrases need testing) and adds a skill loadout cost.

---

## Authoring Modes

### Mode 1 — Natural-language description (preferred)

The user describes the form in plain English; this skill derives the field list and generates the form.

Examples:
- "Create a signup form with email, password, and a role dropdown."
- "Build a contact form with name, email, message, and a checkbox to subscribe to the newsletter."
- "Scaffold a login form."

### Mode 2 — JSON schema

The user passes a JSON schema file describing the fields. The skill reads the file, derives the field list, and generates the form.

Both modes converge on the same internal contract — a list of fields, each with `{ name, label, type, required?, autoComplete?, options?, rows?, minLength? }` — and produce identical output.

---

## Step A — Resolve the field list

### A1. Ambiguity check

If the user's description is vague (e.g. "a contact form" with no specified fields), pause with `AskUserQuestion` to clarify. Suggest sensible defaults but don't commit until the user confirms.

Example interaction:

> User: "Add a contact form."
> Skill: AskUserQuestion → "Contact form fields — sensible default is name + email + message. Confirm or edit?"

For the most common form types, the safe defaults are:

| Form type | Default fields |
|-----------|----------------|
| Signup | email (required, autoComplete=email), password (required, minLength=8, autoComplete=new-password) |
| Login | email (required, autoComplete=email), password (required, autoComplete=current-password) |
| Contact | name, email (required), message (textarea, rows=4) |
| Newsletter | email (required, autoComplete=email) |

These are starting points — confirm with the user, then adjust per their description.

### A2. Field shape

Each field must have:

```
{
  name: string,           // form field name (snake_case or camelCase)
  label: string,          // visible label
  type: 'text' | 'email' | 'password' | 'tel' | 'url'
      | 'number' | 'date'
      | 'textarea' | 'select' | 'checkbox' | 'radio',
  required?: boolean,     // adds aria-required + visible *
  autoComplete?: string,  // browser autofill hint (e.g. 'email', 'new-password')
  options?: { value, label }[],  // required when type === 'select' or 'radio'
  rows?: number,          // textarea row count (default 4)
  minLength?: number,     // input length validation
}
```

Supported types: `text`, `email`, `password`, `url`, `number`, `tel`, `date`, `select`, `textarea`, `checkbox`, `radio`. Native HTML input types (`number`, `date`) work inside the `Input` component without further wrapping — `Input` accepts all standard `HTMLInputAttributes` via its `Omit<...>` spread.

If the user's description specifies a type the skill doesn't support directly — currently file upload (`type="file"`), color picker (`type="color"`), or range slider (`type="range"`) — surface the gap explicitly: "The form components support text/email/password/tel/url/number/date, textarea, select, checkbox, and radio out of the box. For file uploads or color pickers, use the native `<input type="file" />` directly — they don't need a wrapper."

### A3. Form name

Derive a PascalCase form name from the description:
- "signup form" → `SignupForm`
- "contact us" → `ContactForm`
- "user profile editor" → `UserProfileForm`

Confirm the name with the user only if it's ambiguous.

---

## Step B — Verify dependencies

The generated form needs `Field`, `Input`, `Button`, and (when a checkbox field is present) `Checkbox`. Step B confirms the project has these vendored and locates them.

### B1. Resolve the target directory

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_target.py <project_root>`. Parse the JSON output. The relevant keys are `source` (`generated` or `none`) and `componentsDir`.

### B2. Branch on source

**`source: "generated"`** — proceed to B3 to probe `<componentsDir>` for the required local files.

**`source: "none"`** — clean project, no `ui.tsx` foundation yet. Skip B3 (nothing to probe) and jump to B4 to bootstrap. Do **not** halt — the `/kit-add` flow handles first-run setup, including prompting for `componentsDir` and writing `.acss-target.json`.

### B3. Probe required components *(only when source is `generated`)*

Read `componentsDir` from the script output (default: `src/components/fpkit`). Check for:

- `<componentsDir>/field/field.tsx`
- `<componentsDir>/input/input.tsx`
- `<componentsDir>/button/button.tsx`
- `<componentsDir>/checkbox/checkbox.tsx` *(only if any field has `type: 'checkbox'`)*
- `<componentsDir>/ui.tsx` *(foundation)*

### B4. Bootstrap or vendor missing components

Run `/kit-add field input button` (and `checkbox` if any field has `type: 'checkbox'`) when **either**:

- `source: "none"` from B1 (clean project — first-run bootstrap), or
- B3 found any missing files in an existing project.

The `/kit-add` flow walks the dependency tree, previews before writing, and on first run prompts for the components directory and writes `.acss-target.json`. After it completes, re-run `detect_target.py` to confirm `source` is now `"generated"` and `componentsDir` is set, then continue to Step C.

If `/kit-add` itself fails (e.g. `sass` missing from `devDependencies`), surface its error and halt — the form cannot be generated without its component dependencies.

---

## Step C — Generate the form file

Write the form to `src/forms/<FormName>.tsx` by default (or wherever the user specifies). Use the TSX Template below.

### Form Generation Contract

```
form_name: <PascalCase>
file: src/forms/<FormName>.tsx
imports:
  - Field from '<componentsDir>/field/field'
  - Input from '<componentsDir>/input/input'
  - Button from '<componentsDir>/button/button'
  - Checkbox from '<componentsDir>/checkbox/checkbox'  (only if a checkbox field is present)
fields: [{ name, label, type, required?, autoComplete?, options?, rows?, minLength? }]
```

### TSX Template

```tsx
// {{NAME}}.tsx — generated by component-form skill
import { useState, type FormEvent } from 'react'
{{IMPORT_SOURCE:Field,Input,Checkbox,Button}}

export type {{NAME}}Values = {
{{FIELD_TYPES}}
}

export type {{NAME}}Errors = Partial<Record<keyof {{NAME}}Values, string>>

export default function {{NAME}}({
  onSubmit,
}: {
  onSubmit?: (values: {{NAME}}Values) => void | Promise<void>
}) {
  const [errors, setErrors] = useState<{{NAME}}Errors & { _form?: string }>({})
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    // Block resubmits while an async onSubmit is in flight. Belt-and-braces
    // alongside the Button's useDisabledState wrapper.
    if (submitting) return
    setSubmitting(true)
    setErrors({})
    try {
      const formData = new FormData(e.currentTarget)
      const raw = Object.fromEntries(formData.entries()) as Record<string, FormDataEntryValue>
      // Coerce checkbox fields: FormData reports 'on' for checked and omits unchecked.
      // Without this normalization, the `boolean` declared in {{NAME}}Values lies at runtime.
      const values = {
        ...raw,
{{CHECKBOX_COERCION}}
{{RADIO_COERCION}}
      } as unknown as {{NAME}}Values
      await onSubmit?.(values)
    } catch (err) {
      setErrors({ _form: (err as Error).message })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      aria-labelledby="{{NAME_KEBAB}}-heading"
      className="form"
    >
      <h2 id="{{NAME_KEBAB}}-heading">{{HEADING}}</h2>

      {errors._form && (
        <div role="alert" className="form-error">{errors._form}</div>
      )}

{{FIELDS}}

      <Button
        type="submit"
        disabled={submitting}
        data-color="primary"
      >
        {submitting ? 'Submitting…' : '{{SUBMIT_LABEL}}'}
      </Button>
    </form>
  )
}
```

The submit button uses the `Button` component (not a plain `<button>`) so the `useDisabledState` wrapper gates pointer/keyboard handlers while `submitting` is true. Combined with the early `if (submitting) return` guard in `handleSubmit`, this prevents duplicate submissions on async handlers — even when the same form mounts twice or the user double-taps Enter.

### Placeholder substitution table

| Placeholder | Substitute with |
|-------------|-----------------|
| `{{NAME}}` | The PascalCase form name (e.g. `SignupForm`) |
| `{{NAME_KEBAB}}` | The kebab-case form name (e.g. `signup-form`). Also used as the prefix for every generated control id (e.g. `signup-form-email`) so two forms with overlapping field names can mount on the same page without duplicate ids. |
| `{{HEADING}}` | The form's visible heading (e.g. `Create your account`) |
| `{{SUBMIT_LABEL}}` | The submit button label (e.g. `Create account`) |
| `{{FIELD_TYPES}}` | One TypeScript line per field: `  fieldName: string` (or `boolean` for checkbox). See Step D's field-types map for the full mapping. |
| `{{FIELDS}}` | The rendered field elements — see Field Renderers below |
| `{{IMPORT_SOURCE:Field,Input,Checkbox,Button}}` | Local import block resolved per `detect_target.py` output — see "Component-source imports" subsection below. Drop `Checkbox` from the placeholder list when no checkbox field is present. `Button` is always included (the submit button uses it). |
| `{{CHECKBOX_COERCION}}` | One indented line per checkbox field: `        <name>: formData.get('<name>') === 'on',`. If the form has no checkbox fields, this expands to the empty string (the spread-only `values` object falls through to the `as unknown as {{NAME}}Values` cast unchanged). |
| `{{RADIO_COERCION}}` | One indented line per radio field: `        <name>: String(formData.get('<name>') ?? ''),`. This keeps optional, unselected radio groups aligned with the declared `string` value type. If the form has no radio fields, this expands to the empty string. |

### Component-source imports

Step B already determined the components are vendored locally and located them via `componentsDir`. Use that path when expanding `{{IMPORT_SOURCE:Field,Input,Checkbox,Button}}`:

1. **Compute the relative path** from the form file (`src/forms/<FormName>.tsx`) to the components directory. Default `componentsDir` is `src/components/fpkit`, giving `../components/fpkit`. A custom `componentsDir` of `src/ui-kit` gives `../ui-kit`. Use `path.relative()` semantics; fall back to `../components/fpkit` if `.acss-target.json` is absent.
2. **Emit one import per component** referenced in the placeholder, plus the matching SCSS imports. Drop `Checkbox` lines if no checkbox field is present; `Button` is always included:
   ```tsx
   import Field from '<relative>/field/field'
   import Input from '<relative>/input/input'
   import Checkbox from '<relative>/checkbox/checkbox'   // omit if no checkbox field
   import Button from '<relative>/button/button'

   import '<relative>/field/field.scss'
   import '<relative>/input/input.scss'
   import '<relative>/checkbox/checkbox.scss'            // omit if no checkbox field
   import '<relative>/button/button.scss'
   ```
3. **`source: "none"` should not reach this step.** Step B4 either successfully bootstraps the project via `/kit-add` (after which `source` becomes `"generated"`) or surfaces a `/kit-add` error and halts. If you somehow reach Step C with `source: "none"`, treat it as a bug and halt before writing.

---

## Step D — Field Renderers

For each field in the form, render the appropriate JSX based on `type`. Substitute these into `{{FIELDS}}` with 6-space indentation (matching the form indentation).

All renderers below use `{{form_name_kebab}}-{{name}}` as the rendered control's `id` (and the matching `Field`'s `labelFor`). The HTML `name` attribute stays as the raw `{{name}}` so `FormData.entries()` produces clean keys for the `{{NAME}}Values` type.

### Text-like inputs (text, email, password, tel, url, number, date)

```tsx
<Field labelFor="{{form_name_kebab}}-{{name}}" label="{{label}}">
  <Input
    id="{{form_name_kebab}}-{{name}}"
    name="{{name}}"
    type="{{type}}"
    {{REQUIRED_PROP}}
    {{AUTOCOMPLETE_PROP}}
    {{MINLENGTH_PROP}}
  />
</Field>
```

The `Input` component accepts `type="number"` and `type="date"` natively via its `Omit<...>` spread of `HTMLInputAttributes` — no separate renderer needed. Browser-native number/date pickers are used; values come back as strings through `FormData.entries()`, so callers cast at validation time.

### Textarea

```tsx
<Field labelFor="{{form_name_kebab}}-{{name}}" label="{{label}}">
  <textarea
    id="{{form_name_kebab}}-{{name}}"
    name="{{name}}"
    {{ROWS_ATTR}}
    {{REQUIRED_ATTR}}
    {{ARIA_REQUIRED_ATTR}}
  />
</Field>
```

(Note: there's no `Textarea` component yet — fall back to the native `<textarea>` element. Style it via the shared input SCSS, which targets `input, textarea, select` together.)

### Select

```tsx
<Field labelFor="{{form_name_kebab}}-{{name}}" label="{{label}}">
  <select
    id="{{form_name_kebab}}-{{name}}"
    name="{{name}}"
    {{REQUIRED_ATTR}}
    {{ARIA_REQUIRED_ATTR}}
  >
    <option value="">Select…</option>
    {{OPTIONS}}
  </select>
</Field>
```

Where `{{OPTIONS}}` expands to one line per option:

```tsx
    <option value="{{value}}">{{label}}</option>
```

### Checkbox

```tsx
<Checkbox
  id="{{form_name_kebab}}-{{name}}"
  name="{{name}}"
  label="{{label}}"
  {{REQUIRED_PROP}}
/>
```

(Checkbox renders its own label inside; don't wrap in `Field`.)

### Radio (group)

Radio fields render as a `<fieldset>` + `<legend>` group containing one `<input type="radio">` per option. All radios in the group share the same `name` attribute (browser groups them); each gets a distinct `id` and `value`:

```tsx
<fieldset>
  <legend>{{label}}</legend>
  {{OPTIONS_AS_RADIOS}}
</fieldset>
```

Where `{{OPTIONS_AS_RADIOS}}` expands to one `<label>` + `<input>` pair per option:

```tsx
    <label>
      <input
        type="radio"
        id="{{form_name_kebab}}-{{name}}-{{value}}"
        name="{{name}}"
        value="{{value}}"
        {{REQUIRED_ATTR}}
      />
      {{option_label}}
    </label>
```

The `<fieldset>` + `<legend>` pairing is the WCAG-correct grouping pattern for radio options. Don't wrap individual radios in `Field` — radios are grouped semantics, not per-field labelled controls. The first `id` is `{{form_name_kebab}}-{{name}}-{{value}}` so each option is uniquely addressable across the page.

### Conditional attributes

| Field property | Substitution |
|----------------|--------------|
| `required: true` | `{{REQUIRED_ATTR}}` -> `required`; `{{REQUIRED_PROP}}` -> `required={true}`; `{{ARIA_REQUIRED_ATTR}}` -> `aria-required={true}` |
| `required: false` or omitted | Remove `{{REQUIRED_ATTR}}` / `{{REQUIRED_PROP}}`; `{{ARIA_REQUIRED_ATTR}}` -> `aria-required={false}` |
| `autoComplete: "email"` | `autoComplete="email"` |
| `minLength: 8` | `minLength={8}` |
| `rows: 6` | `{{ROWS_ATTR}}` -> `rows={6}` for textarea; if omitted, use `rows={4}` |
| `options` | Expand each option into the renderer-specific `<option>` or radio input block. Halt without writing if `select` or `radio` has no options. |

### Field-types map for `{{FIELD_TYPES}}`

| Field `type` | TypeScript type |
|--------------|-----------------|
| text, email, password, tel, url, textarea, select, radio | `string` |
| number, date | `string` *(FormData entries serialize numbers and dates as strings; cast at validation time if you need typed values)* |
| checkbox | `boolean` |

---

## Step E — Accessibility

The generated form is WCAG 2.2 AA compliant by construction. Don't strip these patterns during customization.

**Form-level**
- `<form noValidate>` — disables native browser validation tooltips so `errorMessage` / `aria-describedby` is the single source of error truth. The generated form should validate via the `onSubmit` handler, not native HTML5 validation.
- `aria-labelledby="<form>-heading"` — the form's `<h2>` id is referenced so screen readers announce the form's purpose on entry.
- A `_form` error (top-level submission failure) renders inside `<div role="alert">` so screen readers announce it immediately when set.

**Field-level**
- `Field` provides `<label htmlFor={id}>` association for every Input, Textarea, and Select. Required by the `Field` type.
- `Input` automatically sets `aria-required`, `aria-invalid` (from `validationState="invalid"`), and `aria-describedby` linking to `${id}-error` and `${id}-hint` when those are set.
- Checkbox renders its own visible label and inherits Input's a11y from underneath.

**Submit button**
- Renders the `Button` component with `disabled={submitting}`. `Button` propagates `aria-disabled="true"` to the underlying element while keeping it in the tab order — screen readers announce "dimmed/unavailable" without focus loss (WCAG 2.1.1).
- `Button`'s `useDisabledState` wrapper short-circuits pointer and keyboard handlers while `submitting` is true. Combined with the early `if (submitting) return` guard in `handleSubmit`, double-submits (rapid clicks, Enter held, two simultaneous form mounts) are blocked at both the component and the handler levels.
- The button text swaps from `{{SUBMIT_LABEL}}` to `Submitting…` while in flight, giving sighted users a visual signal that pairs with the accessibility-tree state change.

**Form validation flow**
- On submit failure (the `onSubmit` callback throws), the `_form` error is rendered in the live region — screen readers announce the error immediately.
- Per-field validation should populate the `errors` state and pass `validationState="invalid"` + `errorMessage={errors[name]}` to the matching Input. The skill's TSX Template does NOT include per-field validation logic — that's application-specific. Document this gap and let the user wire it up.

**Atomic generation**
- Build the entire form file in memory; write to disk only on success. If any field renderer fails (unsupported `type`, missing `options` for `select` or `radio`), surface the error and write nothing. Partial files break TypeScript compilation in the user's project.

**WCAG 2.2 AA criteria addressed**
- 1.3.1 Info and Relationships (label-control association via Field; aria-describedby for errors/hints)
- 2.1.1 Keyboard (native `<form>` + `<input>` + native submit-on-Enter; aria-disabled keeps submit button focusable)
- 2.4.3 Focus Order (native form fields tab in DOM order)
- 2.4.7 Focus Visible (inherits from button.scss, input.scss, etc.)
- 3.3.1 Error Identification (form-level role="alert"; field-level aria-invalid + aria-describedby)
- 3.3.2 Labels or Instructions (Field always provides a visible label)
- 4.1.2 Name, Role, Value (native form/input/select/textarea + accessible names)
- 4.1.3 Status Messages (form-error region uses role="alert"; submitting state announced by `aria-disabled` + label change)

---

## Step F — Post-generation summary

After writing the form, print:

```
Generated src/forms/<FormName>.tsx

Imports:
  Field from <componentsDir>/field/field
  Input from <componentsDir>/input/input
  {{Checkbox if used}}

Field summary:
  email      (text, required, autoComplete=email)
  password   (password, required, minLength=8)
  role       (select: admin / editor / viewer)

Next steps:
  - Wire onSubmit handler in your route/page
  - Add per-field validation (the skill scaffolds the structure but
    leaves field-level validation for your application logic)
  - Style overrides via CSS variables — see field.scss / input.scss
```

---

## Reference documents

- `references/components/field.md` — Field props, accessibility patterns
- `references/components/input.md` — Input props, validation states, accessible disabled pattern
- `references/components/checkbox.md` — Checkbox boolean onChange API, size presets
