# Component: Checkbox

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). Wraps the kit-builder `Input` with `type="checkbox"` and exposes a boolean `onChange` API. Adds size variants (`xs` | `sm` | `md` | `lg`), an automatic visible label, and a controlled-vs-uncontrolled-mode warning in development. Inherits all validation, disabled, and ARIA logic from `Input`.

## Overview

A checkbox input with simplified ergonomics: boolean `onChange` (not the native `ChangeEvent`), bundled visible label, size presets, and full validation passthrough to the underlying `Input`. Renders the standard `<input type="checkbox">` plus an associated `<label>` inside a wrapper `<div>` that carries the size attribute for SCSS targeting.

## Generation Contract

```
export_name: Checkbox
file: checkbox.tsx
scss: checkbox.scss
imports: Input from '../input/input', type InputProps
dependencies: [input]
```

Checkbox depends on `Input`. Generate `input.tsx` first if it isn't already present.

## Props Interface

```tsx
export interface CheckboxProps extends Omit<
  InputProps,
  'type' | 'value' | 'onChange' | 'defaultValue' | 'placeholder'
> {
  /** Required for label association */
  id: string
  /** Visible label text */
  label: React.ReactNode
  /** Size preset (default: 'md') */
  size?: 'xs' | 'sm' | 'md' | 'lg'
  /** Controlled checked state */
  checked?: boolean
  /** Uncontrolled initial state */
  defaultChecked?: boolean
  /** Form-submission value when checked (default: 'on') */
  value?: string
  /** Boolean change handler — receives true/false, not a ChangeEvent */
  onChange?: (checked: boolean) => void
  /** Wrapper div CSS classes */
  classes?: string
  /** Input element CSS classes (default: 'checkbox-input') */
  inputClasses?: string
  /** CSS custom properties for theming / custom sizing */
  styles?: React.CSSProperties
}
```

## TSX Template

```tsx
import React from 'react'
import Input, { type InputProps } from '../input/input'

export interface CheckboxProps extends Omit<
  InputProps,
  'type' | 'value' | 'onChange' | 'defaultValue' | 'placeholder'
> {
  id: string
  label: React.ReactNode
  size?: 'xs' | 'sm' | 'md' | 'lg'
  checked?: boolean
  defaultChecked?: boolean
  value?: string
  onChange?: (checked: boolean) => void
  classes?: string
  inputClasses?: string
  styles?: React.CSSProperties
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(({
  id,
  label,
  checked,
  defaultChecked,
  value = 'on',
  onChange,
  classes,
  inputClasses,
  styles,
  size,
  name,
  disabled,
  required,
  validationState,
  errorMessage,
  hintText,
  onBlur,
  onFocus,
  autoFocus,
  ...props
}, ref) => {
  // Adapt boolean onChange to native ChangeEvent
  const handleChange = React.useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e.target.checked)
    },
    [onChange],
  )

  const isControlled = checked !== undefined
  const checkedProp = isControlled ? { checked } : {}
  const defaultCheckedProp = !isControlled && defaultChecked !== undefined
    ? { defaultChecked }
    : {}

  // Dev-only: warn on controlled <-> uncontrolled mode flip.
  const wasControlledRef = React.useRef(isControlled)
  React.useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      if (wasControlledRef.current !== isControlled) {
        // eslint-disable-next-line no-console
        console.warn(
          `Checkbox id="${id}" is changing from ${wasControlledRef.current ? 'controlled' : 'uncontrolled'} to ${isControlled ? 'controlled' : 'uncontrolled'}. Pick one and stick with it.`,
        )
      }
      wasControlledRef.current = isControlled
    }
  }, [isControlled, id])

  return (
    <div className={classes} style={styles} data-checkbox-size={size}>
      <Input
        ref={ref}
        type="checkbox"
        id={id}
        name={name}
        value={value}
        {...checkedProp}
        {...defaultCheckedProp}
        classes={inputClasses || 'checkbox-input'}
        disabled={disabled}
        required={required}
        validationState={validationState}
        errorMessage={errorMessage}
        hintText={hintText}
        onChange={handleChange}
        onBlur={onBlur}
        onFocus={onFocus}
        autoFocus={autoFocus}
        {...props}
      />
      <label htmlFor={id} className="checkbox-label">
        {label}
        {required && (
          <span className="checkbox-required" aria-label="required">{' *'}</span>
        )}
      </label>
    </div>
  )
})

Checkbox.displayName = 'Checkbox'
export default Checkbox
```

## CSS Variables

```scss
// Size tokens (data-checkbox-size attribute)
--checkbox-size-xs: 0.875rem;
--checkbox-size-sm: 1rem;
--checkbox-size-md: 1.25rem;   // default
--checkbox-size-lg: 1.5rem;

--checkbox-size: var(--checkbox-size-md);
--checkbox-radius: 0.25rem;
--checkbox-border-color: var(--color-border, #d0d0d0);
--checkbox-bg: var(--color-surface, #fff);
--checkbox-checked-bg: var(--color-primary, #0066cc);
--checkbox-checked-border: var(--color-primary, #0066cc);
--checkbox-check-color: #fff;

--checkbox-gap: 0.5rem;
--checkbox-label-fs: 1rem;
--checkbox-label-color: var(--color-text, inherit);

--checkbox-focus-ring-color: var(--color-focus-ring, rgba(0, 102, 204, 0.4));
--checkbox-focus-ring: 0 0 0 3px var(--checkbox-focus-ring-color);

--checkbox-disabled-opacity: 0.6;
--checkbox-required-color: var(--color-danger, #dc3545);
```

## SCSS Template

```scss
// checkbox.scss
.checkbox-input {
  // Hide native rendering but keep the input itself accessible
  appearance: none;
  -webkit-appearance: none;
  width: var(--checkbox-size, 1.25rem);
  height: var(--checkbox-size, 1.25rem);
  border: 2px solid var(--checkbox-border-color, #d0d0d0);
  border-radius: var(--checkbox-radius, 0.25rem);
  background: var(--checkbox-bg, #fff);
  cursor: pointer;
  flex-shrink: 0;
  display: inline-grid;
  place-content: center;

  &:checked {
    background: var(--checkbox-checked-bg, #0066cc);
    border-color: var(--checkbox-checked-border, #0066cc);

    &::after {
      content: '';
      width: 60%;
      height: 30%;
      border-bottom: 2px solid var(--checkbox-check-color, #fff);
      border-left: 2px solid var(--checkbox-check-color, #fff);
      transform: rotate(-45deg) translateY(-15%);
    }
  }

  &:focus-visible {
    outline: none;
    box-shadow: var(--checkbox-focus-ring, 0 0 0 3px rgba(0, 102, 204, 0.4));
  }

  &[aria-disabled="true"] {
    cursor: not-allowed;
    opacity: var(--checkbox-disabled-opacity, 0.6);
  }
}

[data-checkbox-size] {
  display: inline-flex;
  align-items: center;
  gap: var(--checkbox-gap, 0.5rem);

  // Size presets — set the --checkbox-size CSS variable based on the data attr
  &[data-checkbox-size="xs"] { --checkbox-size: var(--checkbox-size-xs, 0.875rem); }
  &[data-checkbox-size="sm"] { --checkbox-size: var(--checkbox-size-sm, 1rem); }
  &[data-checkbox-size="md"] { --checkbox-size: var(--checkbox-size-md, 1.25rem); }
  &[data-checkbox-size="lg"] { --checkbox-size: var(--checkbox-size-lg, 1.5rem); }
}

.checkbox-label {
  font-size: var(--checkbox-label-fs, 1rem);
  color: var(--checkbox-label-color, inherit);
  cursor: pointer;
  user-select: none;
}

.checkbox-required {
  color: var(--checkbox-required-color, #dc3545);
  margin-inline-start: 0.125rem;
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `Checkbox` component.

**Label association (required)**
- The `id` and `label` props are both required by type. The component renders `<label htmlFor={id}>` so the label is programmatically associated with the input. Clicking the label toggles the checkbox; screen readers announce the label when the checkbox is focused.
- The label is always visible — Checkbox doesn't render visually-hidden labels. If you need a visually-hidden label, you're better off with a different design pattern.

**Native semantics — preserved**
- Renders a native `<input type="checkbox">`. Browser provides built-in keyboard handling: Space toggles. Tab navigates. Enter does NOT toggle a checkbox (intentional, native behavior — don't add custom Enter handling to mimic Space).
- The visual appearance is custom (`appearance: none` + `::after` checkmark) but the semantics remain native. Screen readers still announce "checkbox", "checked"/"not checked".

**Disabled vs aria-disabled**
- Inherits the kit-builder accessible-disabled pattern from Input: `disabled` prop sets `aria-disabled="true"` (not the native `disabled` attribute). The element stays focusable so screen-reader users discover it (WCAG 2.1.1 Keyboard).
- The `useDisabledState` wrapper from Input gates `onChange` so the boolean callback never fires while disabled.

**Validation states**
- `validationState="invalid"` cascades from Input — `aria-invalid="true"` is set automatically. Screen readers announce the invalid state on focus.
- `errorMessage` and `hintText` work exactly as in Input — the component generates `aria-describedby` ids; render the actual `<p>` elements yourself with matching ids near the checkbox.

**Required**
- `required` renders both `aria-required="true"` (on the input, via Input) and a visible `*` after the label. The asterisk has `aria-label="required"` so screen readers don't announce it as the literal symbol "asterisk".

**Focus visible**
- Native input is hidden visually but stays in tab order. `:focus-visible` adds the focus ring on the visual checkbox via `box-shadow`. The ring color must meet 3:1 against both the page background and the page-adjacent surface (WCAG 1.4.11 Non-text Contrast).

**Color contrast**
- Checkmark color (`--checkbox-check-color`) on checked background (`--checkbox-checked-bg`) must meet 3:1 (icon contrast, WCAG 1.4.11).
- Border color (`--checkbox-border-color`) when unchecked, against the page background, must meet 3:1 — the border is the only visual indicator of the unchecked checkbox.
- Disabled opacity (`--checkbox-disabled-opacity: 0.6`) plus the page background must keep checkmark and border above 3:1 in disabled-checked state. Verify with `validate_theme.py` for custom themes.

**Target size**
- `xs` and `sm` size presets fall below WCAG 2.5.8 Target Size Minimum (44 px). The wrapper's clickable label area expands the effective target size, but only if there's enough horizontal label text or padding. Use `xs`/`sm` only in dense forms where surrounding spacing or pointer accuracy compensates.
- `md` (1.25rem = 20 px) checkbox + label is typically a 44+ px tall row; meets the minimum when label text is present.
- `lg` (1.5rem = 24 px) easily meets the minimum.

**Controlled-mode warning**
- In development, the component logs a console warning if you flip between controlled and uncontrolled modes (e.g., `checked={undefined}` after mounting with `checked={true}`). This catches a common bug where state ownership is unclear. Production builds skip the warning.

**WCAG 2.2 AA criteria addressed**
- 1.3.1 Info and Relationships (label association via htmlFor + id)
- 1.4.3 Contrast Minimum (label text)
- 1.4.11 Non-text Contrast (checkmark, border, focus ring, required asterisk)
- 2.1.1 Keyboard (native checkbox toggling via Space)
- 2.4.7 Focus Visible (`:focus-visible` ring)
- 2.5.5 / 2.5.8 Target Size (md+ presets meet AA; xs/sm need surrounding compensation)
- 3.3.1 Error Identification (inherited from Input via `validationState` + `errorMessage`)
- 3.3.2 Labels or Instructions (label always present and visible)
- 4.1.2 Name, Role, Value (native input + label + state via aria-* attrs)

## Usage Examples

```tsx
import Checkbox from './checkbox/checkbox'
import './input/input.scss'
import './checkbox/checkbox.scss'

// Basic
<Checkbox id="terms" label="I accept the terms and conditions" />

// Controlled
const [agreed, setAgreed] = useState(false)
<Checkbox
  id="terms"
  label="I accept the terms"
  checked={agreed}
  onChange={setAgreed}
  required
/>

// Validation + error
<Checkbox
  id="confirm"
  label="I understand this action is permanent"
  checked={confirmed}
  onChange={setConfirmed}
  validationState={!confirmed ? 'invalid' : 'none'}
  errorMessage={!confirmed ? 'Confirmation required' : undefined}
  required
/>

// Size variants
<Checkbox id="opt-sm" label="Small" size="sm" />
<Checkbox id="opt-lg" label="Large" size="lg" />

// Custom sizing via CSS variables
<Checkbox
  id="opt-custom"
  label="Custom 2rem"
  styles={{ '--checkbox-size': '2rem', '--checkbox-gap': '1rem' } as React.CSSProperties}
/>
```
