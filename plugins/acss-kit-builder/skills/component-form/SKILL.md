---
name: component-form
description: Use when the user asks to create a form, scaffold a form, build a signup/contact/login form, generate form components, add form validation, or design accessible form layouts. Triggers include "create a form", "add a form", "build a form component", "scaffold a form", "form with fields", "form scaffolding". This is the kit-builder pilot for per-component skills — promoted from `references/components/form.md` because forms are high-iteration and benefit from auto-discoverable triggering.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
metadata:
  version: "0.2.0"
  pilot: true
---

# SKILL: component-form

Generate a self-contained, accessible React form component into the developer's project. The form is composed from the kit-builder's `Field`, `Input`, and `Checkbox` reference components; if any of those don't yet exist in the target directory, this skill walks the user through `/kit-add field input checkbox` first.

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). The form composition pattern follows the upstream `components/form/form.tsx` structure (a top-level `<form>` with composed Fields), but the vendored version targets a single self-contained generated file rather than the multi-file upstream split (`form.tsx` + `fields.tsx` + `inputs.tsx` + `checkbox.tsx` + `form.types.ts`).

## Pilot status

This is the **only** per-component skill in `acss-kit-builder` v0.2.0. It exists to validate the per-component skill discovery pattern. If the trigger reliability proves out in real-world usage, additional components (Dialog, Card, Table, Popover) may be promoted to skills in a future release. Until then, those remain reference docs.

If you're authoring a component reference doc and unsure whether to promote it to a skill, default to a reference doc. Promotion adds discovery surface but also doubles authoring overhead (frontmatter trigger phrases need testing) and adds a skill loadout cost.

---

## Authoring Modes

### Mode 1 — Natural-language description (preferred for v0.2.0+)

The user describes the form in plain English; this skill derives the field list and generates the form.

Examples:
- "Create a signup form with email, password, and a role dropdown."
- "Build a contact form with name, email, message, and a checkbox to subscribe to the newsletter."
- "Scaffold a login form."

### Mode 2 — Legacy JSON schema

The user passes an existing JSON schema file (e.g. `schema.example.json`). This is preserved for backward compatibility with `acss-app-builder` v0.1.x usage. The skill reads the file, derives the field list, and generates the form.

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

The full set of supported types matches the `/app-form` advertised contract: `text`, `email`, `password`, `url`, `number`, `tel`, `date`, `select`, `textarea`, `checkbox`, `radio`. Native HTML input types (`number`, `date`) work inside the kit-builder `Input` component without further wrapping — `Input` accepts all standard `HTMLInputAttributes` via its `Omit<...>` spread.

If the user's description specifies a type the skill doesn't support directly — currently file upload (`type="file"`), color picker (`type="color"`), or range slider (`type="range"`) — surface the gap explicitly: "The kit-builder form components support text/email/password/tel/url/number/date, textarea, select, checkbox, and radio out of the box. For file uploads or color pickers, use the native `<input type="file" />` directly — they don't need a kit-builder wrapper."

### A3. Form name

Derive a PascalCase form name from the description:
- "signup form" → `SignupForm`
- "contact us" → `ContactForm`
- "user profile editor" → `UserProfileForm`

Confirm the name with the user only if it's ambiguous.

---

## Step B — Verify dependencies

The generated form imports `Field`, `Input`, and `Checkbox` from the user's `componentsDir` (via `.acss-target.json`). If any of these don't exist in that directory, the form file won't compile.

### B1. Check componentsDir

Read `.acss-target.json` at the project root. Get `componentsDir` (default: `src/components/fpkit`).

### B2. Probe required components

Check for:
- `<componentsDir>/field/field.tsx`
- `<componentsDir>/input/input.tsx`
- `<componentsDir>/checkbox/checkbox.tsx` (only if any field has `type: 'checkbox'`)
- `<componentsDir>/ui.tsx` (foundation)

### B3. Generate missing components

If any are missing, run `/kit-add field input` (and `checkbox` if needed) before generating the form. The kit-add flow walks the dependency tree and previews before writing.

If the user prefers to skip this step (e.g. they're on `acss-app-builder@0.1.x` with the @fpkit/acss npm path), the form's imports must be adjusted to import from `@fpkit/acss` instead. This is the legacy path — generate a deprecation warning along with the form, recommending migration to vendored components.

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
  - Checkbox from '<componentsDir>/checkbox/checkbox'  (only if a checkbox field is present)
fields: [{ name, label, type, required?, autoComplete?, options?, rows?, minLength? }]
```

### TSX Template

```tsx
// {{NAME}}.tsx — generated by component-form skill
import { useState, type FormEvent } from 'react'
{{IMPORT_SOURCE:Field,Input,Checkbox}}

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
    setSubmitting(true)
    setErrors({})
    try {
      const formData = new FormData(e.currentTarget)
      const values = Object.fromEntries(formData.entries()) as {{NAME}}Values
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

      <button
        type="submit"
        aria-disabled={submitting}
        className="btn"
        data-color="primary"
      >
        {submitting ? 'Submitting…' : '{{SUBMIT_LABEL}}'}
      </button>
    </form>
  )
}
```

### Placeholder substitution table

| Placeholder | Substitute with |
|-------------|-----------------|
| `{{NAME}}` | The PascalCase form name (e.g. `SignupForm`) |
| `{{NAME_KEBAB}}` | The kebab-case form name (e.g. `signup-form`). Also used as the prefix for every generated control id (e.g. `signup-form-email`) so two forms with overlapping field names can mount on the same page without duplicate ids. |
| `{{HEADING}}` | The form's visible heading (e.g. `Create your account`) |
| `{{SUBMIT_LABEL}}` | The submit button label (e.g. `Create account`) |
| `{{FIELD_TYPES}}` | One TypeScript line per field: `  fieldName: string` (or `boolean` for checkbox). See Step D's field-types map for the full mapping. |
| `{{FIELDS}}` | The rendered field elements — see Field Renderers below |
| `{{IMPORT_SOURCE:Field,Input,Checkbox}}` | Source-aware import block. Resolves per `detect_component_source.py` output — see "Component-source-aware imports" subsection below. Drop `Checkbox` from the placeholder list when no checkbox field is present. |

### Component-source-aware imports

Step B already determined the component source (`generated` | `npm`) by reading `.acss-target.json` and probing for required components. Use that source when expanding `{{IMPORT_SOURCE:Field,Input,Checkbox}}`:

1. **Compute the relative path** from the form file (`src/forms/<FormName>.tsx`) to the components directory. Default `componentsDir` is `src/components/fpkit`, giving `../components/fpkit`. A custom `componentsDir` of `src/ui-kit` gives `../ui-kit`. Use `path.relative()` semantics; fall back to `../components/fpkit` if `.acss-target.json` is absent.
2. **For `source=generated`**: emit one import per component referenced in the placeholder, plus the matching SCSS imports. Drop `Checkbox` lines if no checkbox field is present:
   ```tsx
   import Field from '<relative>/field/field'
   import Input from '<relative>/input/input'
   import Checkbox from '<relative>/checkbox/checkbox'   // omit if no checkbox field

   import '<relative>/field/field.scss'
   import '<relative>/input/input.scss'
   import '<relative>/checkbox/checkbox.scss'            // omit if no checkbox field
   ```
3. **For `source=npm`**: emit a single combined import (drop `Checkbox` if not needed). Per-form SCSS imports are unnecessary — npm projects load `@fpkit/acss/styles` once at app entry:
   ```tsx
   import { Field, Input, Checkbox } from '@fpkit/acss'
   ```
4. **For `source=none`**: error — Step B should have already run `/kit-add` (or halted with an install hint) before generation reaches this point.

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

The kit-builder `Input` accepts `type="number"` and `type="date"` natively via its `Omit<...>` spread of `HTMLInputAttributes` — no separate renderer needed. Browser-native number/date pickers are used; values come back as strings through `FormData.entries()`, so callers cast at validation time.

### Textarea

```tsx
<Field labelFor="{{form_name_kebab}}-{{name}}" label="{{label}}">
  <textarea
    id="{{form_name_kebab}}-{{name}}"
    name="{{name}}"
    rows={{rows ?? 4}}
    {{REQUIRED_ATTR}}
    aria-required={{required}}
  />
</Field>
```

(Note: there's no kit-builder `Textarea` component yet — fall back to the native `<textarea>` element. Style it via the shared input SCSS, which targets `input, textarea, select` together.)

### Select

```tsx
<Field labelFor="{{form_name_kebab}}-{{name}}" label="{{label}}">
  <select id="{{form_name_kebab}}-{{name}}" name="{{name}}" {{REQUIRED_ATTR}} aria-required={{required}}>
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
| `required: true` | `required` (HTML attribute) and `required={true}` (Input prop) |
| `autoComplete: "email"` | `autoComplete="email"` |
| `minLength: 8` | `minLength={8}` |

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
- `aria-disabled={submitting}` instead of native `disabled` — the button stays focusable so screen readers can announce "submitting" state without losing focus.
- The button's text changes from `{{SUBMIT_LABEL}}` to `Submitting…` while in flight, giving sighted users a visual signal.

**Form validation flow**
- On submit failure (the `onSubmit` callback throws), the `_form` error is rendered in the live region — screen readers announce the error immediately.
- Per-field validation should populate the `errors` state and pass `validationState="invalid"` + `errorMessage={errors[name]}` to the matching Input. The skill's TSX Template does NOT include per-field validation logic — that's application-specific. Document this gap and let the user wire it up.

**Atomic generation**
- Build the entire form file in memory; write to disk only on success. If any field renderer fails (unsupported `type`, missing `options` for `select`), surface the error and write nothing. Partial files break TypeScript compilation in the user's project.

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

## Step F — Cross-plugin invocation

`acss-app-builder`'s `/app-form` slash command delegates to this skill. The cross-plugin invocation contract:

- `/app-form <description-or-schema>` — `acss-app-builder` parses the argument:
  - If it ends in `.json`, read the schema file, build the field list, and pass the field list to this skill via the Skill tool.
  - Otherwise, treat the argument as a natural-language description and pass it directly to this skill.
- This skill returns nothing structured; it writes the form file to disk and prints a summary.
- `/app-form` then surfaces the summary to the user, plus a deprecation notice if `detect_component_source.py` reported `deprecated: true` for the project's component source.

The Skill tool invocation in `acss-app-builder/commands/app-form.md` looks like:

```
Skill {
  skill: "acss-kit-builder:component-form"
  args: <description or { fields: [...], formName: "..." }>
}
```

This pattern lets the kit-builder own all component-template logic while keeping the user-facing slash command in the plugin where users expect it.

---

## Step G — Post-generation summary

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

If the legacy `@fpkit/acss` npm path is in use, append:

```
Note: this project uses the @fpkit/acss npm path (deprecated;
sunset in <sunsetVersion>). Run /kit-add to vendor field, input, and
checkbox so this form's imports resolve to local paths.
```

---

## Reference documents

- `references/components/field.md` — Field props, accessibility patterns
- `references/components/input.md` — Input props, validation states, accessible disabled pattern
- `references/components/checkbox.md` — Checkbox boolean onChange API, size presets
- `references/forms.md` (in acss-app-builder) — legacy JSON schema shape for backward compatibility
