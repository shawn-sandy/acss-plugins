// Reference renderers — one per field type.
// /app-form selects the matching renderer per field and inlines its JSX into the generated form.
// These are NOT written to the developer's project; they document the rendering contract.
//
// All renderers use the real, verified exports from @fpkit/acss:
//   Field, Input, Checkbox  — see https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/index.ts
// Native <select> and <textarea> wrap inside <Field> because fpkit does not export wrappers.
// {{IMPORT_SOURCE:Field,Input,Checkbox}}

// ---------- text / email / password / url / number / tel / date ----------
export function renderTextLike({
  id, name, label, type, required, autoComplete, describedBy,
}: {
  id: string
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'url' | 'number' | 'tel' | 'date'
  required?: boolean
  autoComplete?: string
  describedBy?: string
}) {
  return (
    <Field label={label} labelFor={id}>
      <Input
        id={id}
        name={name}
        type={type}
        required={required}
        autoComplete={autoComplete}
        aria-describedby={describedBy}
      />
    </Field>
  )
}

// ---------- select ----------
export function renderSelect({
  id, name, label, options, required,
}: {
  id: string
  name: string
  label: string
  options: Array<{ value: string; label: string }>
  required?: boolean
}) {
  return (
    <Field label={label} labelFor={id}>
      <select id={id} name={name} required={required}>
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </Field>
  )
}

// ---------- textarea ----------
export function renderTextarea({
  id, name, label, rows, required,
}: {
  id: string
  name: string
  label: string
  rows?: number
  required?: boolean
}) {
  return (
    <Field label={label} labelFor={id}>
      <textarea id={id} name={name} rows={rows ?? 4} required={required} />
    </Field>
  )
}

// ---------- checkbox ----------
export function renderCheckbox({
  id, name, label, required,
}: {
  id: string
  name: string
  label: string
  required?: boolean
}) {
  return (
    <Field label={label} labelFor={id}>
      <Checkbox id={id} name={name} required={required} />
    </Field>
  )
}

// ---------- radio group ----------
// A fieldset + legend is used instead of Field, because a group of radios
// needs a single accessible label shared across all options (WCAG 3.3.2).
export function renderRadioGroup({
  name, label, options, required,
}: {
  name: string
  label: string
  options: Array<{ value: string; label: string }>
  required?: boolean
}) {
  return (
    <fieldset>
      <legend>{label}</legend>
      {options.map((o) => {
        const id = `${name}-${o.value}`
        return (
          <div key={o.value}>
            <input type="radio" id={id} name={name} value={o.value} required={required} />
            <label htmlFor={id}>{o.label}</label>
          </div>
        )
      })}
    </fieldset>
  )
}
