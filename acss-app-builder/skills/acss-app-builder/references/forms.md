# Forms Reference

Form generation from a JSON schema via `/app-form`.

## The real Field API (verified at [`packages/fpkit/src/components/form/fields.tsx`](https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/form/fields.tsx))

```tsx
export const Field = ({ label, labelFor, children, ... }: FieldProps) => (
  <UI as="div" data-style="fields">
    <label htmlFor={labelFor}>{label}</label>
    {children}
  </UI>
)
```

**Rules the plugin follows:**

- `label` is required — always pass a string or ReactNode.
- `labelFor` is required — must match the `id` of the input/select/textarea child.
- `children` is the actual form control (input, select, textarea, native or fpkit `Input`/`Checkbox`).
- Do NOT import `FieldLabel`, `FieldInput`, or `FieldTextarea` — they are not exported.

## Field schema shape

```json
{
  "name": "SignupForm",
  "submitLabel": "Create account",
  "fields": [
    { "name": "email",    "label": "Email",    "type": "email",    "required": true },
    { "name": "password", "label": "Password", "type": "password", "required": true, "minLength": 8 },
    { "name": "role",     "label": "Role",     "type": "select",   "options": ["admin", "editor", "viewer"] },
    { "name": "bio",      "label": "Bio",      "type": "textarea", "rows": 4 },
    { "name": "terms",    "label": "I agree to the Terms", "type": "checkbox", "required": true }
  ]
}
```

## Type → renderer mapping

| `type`       | Emitted JSX (simplified) |
|---|---|
| `text`, `email`, `password`, `url`, `number`, `tel`, `date` | `<Field label={label} labelFor={id}><Input id={id} type={type} name={name} required={required} /></Field>` |
| `select`     | `<Field label={label} labelFor={id}><select id={id} name={name}>…options…</select></Field>` |
| `textarea`   | `<Field label={label} labelFor={id}><textarea id={id} name={name} rows={rows} /></Field>` |
| `checkbox`   | `<Field label={label} labelFor={id}><Checkbox id={id} name={name} required={required} /></Field>` |
| `radio`      | A `<fieldset>` with a `<legend>` (replacing Field) wrapping native `<input type="radio">` per option. |

Native `<select>` and `<textarea>` are used because fpkit does not export wrappers for them. Styling cascades from `--input-*` variables defined in fpkit's base styles.

## Accessibility guarantees

- Every field's `id` is unique (generated from `<formName>-<fieldName>`).
- `labelFor` always matches the control's `id`.
- `required` propagates to the control's `aria-required="true"`.
- Error messages use `aria-describedby` pointing at the error element's id.
- Submit button is a `<Button type="submit">`.

## Error handling (v0.1)

The generated component includes a `useState`-based error map and renders inline errors. It does NOT bundle Zod, React Hook Form, or any other validation library — the developer wires those in if desired.

```tsx
const [errors, setErrors] = useState<Record<string, string>>({})
// … on submit, populate errors; render <span id={`${id}-error`} role="alert">…</span>
```
