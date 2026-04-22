# Component: Form

## Overview

A set of form control components: Input, Textarea, Select, Checkbox, and Toggle. Each is a standalone component that can be generated individually. The Form wrapper provides layout and label associations.

## Generation Contract

```
export_name: Input | Textarea | Select | Checkbox | Toggle | FormField
file: form.tsx (or individual files: input.tsx, textarea.tsx, etc.)
scss: form.scss (shared) or individual scss files
imports: UI from '../ui'
dependencies: []
```

When a developer requests `/kit-add form`, generate `form.tsx` containing Input, Textarea, Select, Checkbox, Toggle, and FormField as named exports. Individual components can also be requested: `/kit-add input`.

## Props Interfaces

```tsx
// Shared base for all form controls
type FormControlProps = {
  /** Label text (associated via htmlFor) */
  label?: string
  /** Error message (uses aria-describedby) */
  error?: string
  /** Helper text shown below the field */
  helperText?: string
  /** Field id (required for label association) */
  id: string
  /** Whether field is required */
  required?: boolean
  /** Accessible disabled (aria-disabled pattern) */
  disabled?: boolean
}

export type InputProps = FormControlProps & {
  /** Input type — text | email | password | number | tel | url | search */
  type?: React.HTMLInputTypeAttribute
  /** Controlled value */
  value?: string
  /** Change handler */
  onChange?: React.ChangeEventHandler<HTMLInputElement>
  /** Placeholder text */
  placeholder?: string
  /** Whether the input value is invalid */
  invalid?: boolean
} & Omit<React.ComponentPropsWithoutRef<'input'>, 'disabled' | 'id'>

export type TextareaProps = FormControlProps & {
  value?: string
  onChange?: React.ChangeEventHandler<HTMLTextAreaElement>
  placeholder?: string
  rows?: number
  invalid?: boolean
} & Omit<React.ComponentPropsWithoutRef<'textarea'>, 'disabled' | 'id'>

export type SelectProps = FormControlProps & {
  value?: string
  onChange?: React.ChangeEventHandler<HTMLSelectElement>
  children: React.ReactNode  // <option> elements
  invalid?: boolean
} & Omit<React.ComponentPropsWithoutRef<'select'>, 'disabled' | 'id'>

export type CheckboxProps = {
  id: string
  label: string
  checked?: boolean
  onChange?: React.ChangeEventHandler<HTMLInputElement>
  disabled?: boolean
  error?: string
} & Omit<React.ComponentPropsWithoutRef<'input'>, 'type' | 'disabled' | 'id'>

export type ToggleProps = CheckboxProps & {
  /** Show ON/OFF label text (default: false) */
  showLabels?: boolean
}
```

## Key Pattern: Label Association

Always associate labels with inputs via `htmlFor` + `id`:

```tsx
const FormField = ({ id, label, error, helperText, required, children }: {
  id: string
  label: string
  error?: string
  helperText?: string
  required?: boolean
  children: React.ReactNode
}) => {
  const errorId = error ? `${id}-error` : undefined
  const helpId = helperText ? `${id}-help` : undefined

  return (
    <UI as="div" classes="form-field">
      <UI as="label" classes={`form-label${required ? ' is-required' : ''}`} htmlFor={id}>
        {label}
        {required && <UI as="span" aria-hidden="true" classes="form-required"> *</UI>}
      </UI>
      {children}
      {helperText && <UI as="p" id={helpId} classes="form-helper">{helperText}</UI>}
      {error && (
        <UI as="p" id={errorId} classes="form-error" role="alert">
          {error}
        </UI>
      )}
    </UI>
  )
}
```

## Key Pattern: Input with aria-describedby

```tsx
export const Input = ({
  id,
  label,
  error,
  helperText,
  required,
  disabled,
  invalid,
  type = 'text',
  ...props
}: InputProps) => {
  const errorId = error ? `${id}-error` : undefined
  const helpId = helperText ? `${id}-help` : undefined

  return (
    <FormField id={id} label={label || ''} error={error} helperText={helperText} required={required}>
      <UI
        as="input"
        type={type}
        id={id}
        classes={`input${invalid ? ' is-invalid' : ''}${disabled ? ' is-disabled' : ''}`}
        aria-disabled={disabled}
        aria-invalid={invalid || undefined}
        aria-describedby={[errorId, helpId].filter(Boolean).join(' ') || undefined}
        aria-required={required}
        {...props}
      />
    </FormField>
  )
}
```

## CSS Variables

```scss
// Shared form variables
--form-gap: 1.5rem;
--form-field-gap: 0.375rem;

--form-label-fs: 0.875rem;
--form-label-fw: 500;
--form-label-color: var(--color-text, inherit);

--form-required-color: var(--color-danger, #dc3545);

--form-helper-fs: 0.8125rem;
--form-helper-color: var(--color-text-subtle, #757575);
--form-helper-margin-block-start: 0.25rem;

--form-error-fs: 0.8125rem;
--form-error-color: var(--color-danger, #dc3545);
--form-error-margin-block-start: 0.25rem;

// Input / Textarea / Select (shared)
--input-display: block;
--input-width: 100%;
--input-bg: var(--color-surface, #fff);
--input-color: var(--color-text, inherit);
--input-border: 1px solid var(--color-border, #d0d0d0);
--input-radius: 0.375rem;
--input-padding-inline: 0.75rem;
--input-padding-block: 0.5rem;
--input-fs: 1rem;
--input-line-height: 1.5;
--input-transition: border-color 0.15s ease;

--input-focus-outline: none;
--input-focus-border: var(--color-primary, #0066cc);
--input-focus-ring: 0 0 0 3px rgba(0, 102, 204, 0.2);

--input-invalid-border: var(--color-danger, #dc3545);
--input-invalid-ring: 0 0 0 3px rgba(220, 53, 69, 0.2);

--input-disabled-bg: var(--color-surface-subtle, #f5f5f5);
--input-disabled-opacity: 0.7;
--input-placeholder-color: var(--color-text-subtle, #a0a0a0);

// Checkbox
--checkbox-size: 1.125rem;
--checkbox-radius: 0.25rem;
--checkbox-border: 2px solid var(--color-border, #d0d0d0);
--checkbox-bg: var(--color-surface, #fff);
--checkbox-checked-bg: var(--color-primary, #0066cc);
--checkbox-checked-border: var(--color-primary, #0066cc);
--checkbox-check-color: #fff;

// Toggle
--toggle-width: 2.75rem;
--toggle-height: 1.5rem;
--toggle-bg: var(--color-border, #ccc);
--toggle-checked-bg: var(--color-primary, #0066cc);
--toggle-thumb-size: 1.125rem;
--toggle-thumb-bg: #fff;
--toggle-transition: background 0.2s ease;
```

## Usage Examples

```tsx
import { Input, Textarea, Select, Checkbox, Toggle } from './form/form'
import './form/form.scss'

// Input with validation
const [email, setEmail] = useState('')
const [error, setError] = useState('')

<Input
  id="email"
  type="email"
  label="Email address"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={error}
  required
  placeholder="you@example.com"
/>

// Textarea
<Textarea
  id="message"
  label="Message"
  rows={4}
  placeholder="Enter your message..."
/>

// Select
<Select id="country" label="Country">
  <option value="">Select a country</option>
  <option value="us">United States</option>
  <option value="uk">United Kingdom</option>
</Select>

// Checkbox
<Checkbox
  id="terms"
  label="I agree to the terms and conditions"
  checked={agreed}
  onChange={(e) => setAgreed(e.target.checked)}
/>

// Toggle switch
<Toggle
  id="notifications"
  label="Enable email notifications"
  checked={notifEnabled}
  onChange={(e) => setNotifEnabled(e.target.checked)}
/>
```

## Accessibility Notes

- All inputs have associated `<label>` via `htmlFor` + `id` (WCAG 1.3.1)
- Error messages use `role="alert"` and `aria-describedby` (WCAG 3.3.1)
- Required fields use `aria-required` (WCAG 3.3.2)
- Invalid fields use `aria-invalid` (WCAG 3.3.1)
- Use `aria-disabled` (not native `disabled`) to keep inputs focusable
- Focus indicators meet 3:1 contrast via `--input-focus-ring` (WCAG 2.4.7)
