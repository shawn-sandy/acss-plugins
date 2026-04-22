# Accessibility Reference

## The aria-disabled Pattern

### Why Not Native `disabled`?

The native HTML `disabled` attribute removes interactive elements from the keyboard tab order. This violates:
- **WCAG 2.1.1 (Keyboard)** — All functionality must be available via keyboard
- **WCAG 4.1.2 (Name, Role, Value)** — State must be programmatically determinable

With native `disabled`, screen reader users can't discover disabled elements. They can't read tooltips or contextual help that explains why a control is disabled.

**fpkit solution: Use `aria-disabled="true"` instead.**

Benefits:
- Element stays in tab order (keyboard users can reach it)
- Screen readers announce "disabled" state
- Enables tooltip/help text on disabled buttons
- Visual styling can still convey disabled state
- Better WCAG AA contrast compliance control

### Pattern Example

```tsx
// Bad: removes from tab order
<button disabled onClick={handleClick}>Submit</button>

// Good: stays focusable, announces disabled state
<button aria-disabled="true" onClick={handleDisabledClick}>Submit</button>
```

The `onClick` handler must check `aria-disabled` and bail early:

```tsx
const handleDisabledClick = (e: React.MouseEvent) => {
  if (e.currentTarget.getAttribute('aria-disabled') === 'true') {
    e.preventDefault()
    e.stopPropagation()
    return
  }
  actualHandler(e)
}
```

---

## Condensed useDisabledState Hook

Include this in every component that needs disabled state management (Button, IconButton, etc.). It is condensed from the full 247-line version — contains only the core WCAG pattern.

```tsx
/**
 * useDisabledState — WCAG 2.1.1 compliant disabled state for interactive elements.
 * Uses aria-disabled instead of native disabled to maintain keyboard accessibility.
 *
 * @param disabled - Whether the element is disabled
 * @param handlers - Event handlers to wrap with disabled logic
 */
function useDisabledState<T extends HTMLElement = HTMLButtonElement>(
  disabled: boolean | undefined,
  handlers: {
    onClick?: (e: React.MouseEvent<T>) => void
    onKeyDown?: (e: React.KeyboardEvent<T>) => void
    onPointerDown?: (e: React.PointerEvent<T>) => void
  } = {},
  className?: string
) {
  const isDisabled = Boolean(disabled)

  const mergedClassName = [isDisabled ? 'is-disabled' : '', className]
    .filter(Boolean)
    .join(' ')

  const disabledProps = {
    'aria-disabled': isDisabled,
    className: mergedClassName,
  }

  const wrapHandler = <E extends React.SyntheticEvent>(handler?: (e: E) => void) => {
    if (!handler) return undefined
    return (e: E) => {
      if (isDisabled) {
        e.preventDefault()
        e.stopPropagation()
        return
      }
      handler(e)
    }
  }

  return {
    disabledProps,
    handlers: {
      onClick: wrapHandler(handlers.onClick),
      onKeyDown: wrapHandler(handlers.onKeyDown),
      onPointerDown: wrapHandler(handlers.onPointerDown),
      // onFocus is intentionally NOT wrapped — always allow focus for a11y discovery
    },
  }
}
```

### SCSS for Disabled State

```scss
// Covers both aria-disabled and is-disabled class
.btn {
  &[aria-disabled="true"],
  &.is-disabled {
    opacity: var(--btn-disabled-opacity, 0.6);
    cursor: var(--btn-disabled-cursor, not-allowed);
    pointer-events: none;
  }
}
```

---

## resolveDisabledState Helper

Button accepts both `disabled` and `isDisabled` props for compatibility. Inline this one-liner:

```tsx
// Resolves disabled state from both props. `disabled` takes precedence.
const resolveDisabledState = (disabled?: boolean, isDisabled?: boolean): boolean =>
  disabled ?? isDisabled ?? false
```

---

## Focus Management

### Visible Focus Indicators

Always include `:focus-visible` styles (WCAG 2.4.7 — Focus Visible):

```scss
.btn:focus-visible {
  outline: var(--btn-focus-outline, 2px solid currentColor);
  outline-offset: var(--btn-focus-outline-offset, 2px);
}

// Suppress outline for mouse users (not keyboard users)
.btn:focus:not(:focus-visible) {
  outline: none;
}
```

### Dialog Focus Trap

Native `<dialog>` element provides focus trapping automatically when opened via `dialog.showModal()`. This is the key reason fpkit uses native `<dialog>` over custom implementations — no `focus-trap` npm package needed.

```tsx
// Open dialog with focus trap via showModal()
dialogRef.current?.showModal()

// Close dialog
dialogRef.current?.close()
```

The native `<dialog>` element:
- Traps focus within the dialog when opened with `showModal()`
- Restores focus to the trigger element on close
- Responds to Escape key automatically
- Sets `aria-modal="true"` equivalent behavior

---

## WCAG Checklist for Generated Components

### All Components

- [ ] Semantic HTML element (not `<div>` with role when a native element exists)
- [ ] All ARIA attributes forwarded via `...props`
- [ ] Visible focus indicator (`:focus-visible` with 3:1 contrast)
- [ ] Color contrast 4.5:1 for text (3:1 for large text)

### Interactive Components (Button, Link)

- [ ] `aria-disabled` instead of `disabled`
- [ ] `useDisabledState` hook applied
- [ ] Keyboard activatable (Enter/Space for buttons)
- [ ] SCSS `.is-disabled` + `[aria-disabled="true"]` styling

### Compound Components (Card, Nav)

- [ ] `aria-labelledby` or `aria-label` available via props
- [ ] `role` prop available for semantic override
- [ ] Sub-components use semantic HTML (h3 for Card.Title, li for Nav.Item)

### Dialog

- [ ] Opens with `showModal()` for native focus trap
- [ ] Closes with `close()` and on Escape key
- [ ] `aria-labelledby` references the dialog title
- [ ] Focus returns to trigger on close

### Form Controls

- [ ] `<label>` always associated via `htmlFor` + `id`
- [ ] Error messages use `aria-describedby`
- [ ] Required fields use `aria-required` or `required`
- [ ] `aria-disabled` on disabled inputs (same pattern as buttons)
- [ ] `aria-invalid` on invalid fields

---

## Semantic HTML Quick Reference

| Role | Use This | Not This |
|------|---------|---------|
| Button | `<button>` | `<div role="button">` |
| Navigation | `<nav>` | `<div role="navigation">` |
| Dialog | `<dialog>` | `<div role="dialog">` |
| Main content | `<main>` | `<div role="main">` |
| Alert | `role="alert"` on `<div>` | Custom announcer |
| Status | `role="status"` on `<div>` | `<div>` with no role |
| List | `<ul>` / `<ol>` | `<div>` with list items |
| Form label | `<label htmlFor="id">` | `aria-label` on input |

---

## aria-live for Dynamic Content

```tsx
// Alerts announce themselves automatically
<div role="alert" aria-live="assertive">
  Error: Invalid input
</div>

// Status updates (less intrusive)
<div role="status" aria-live="polite">
  Form saved successfully
</div>
```

Use `role="alert"` (assertive) for errors and critical messages. Use `role="status"` (polite) for success messages and progress updates.
