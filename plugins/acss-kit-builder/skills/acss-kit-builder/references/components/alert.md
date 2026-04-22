# Component: Alert

## Overview

A severity-aware notification component for displaying status messages. Supports info/success/warning/error severity levels with matching icons, optional dismissal, optional auto-hide, and three visual variants (outlined/filled/soft).

## Generation Contract

```
export_name: Alert
file: alert.tsx
scss: alert.scss
imports: UI from '../ui'
dependencies: []
```

Note: The generated Alert inlines simple SVG icons rather than depending on a separate Icon component. This keeps the generated file self-contained. The icon SVGs are small and component-specific.

## Props Interface

```tsx
type Severity = 'default' | 'info' | 'success' | 'warning' | 'error'

export type AlertProps = {
  /** Whether the alert is visible */
  open: boolean
  /** Severity level — determines color and icon */
  severity?: Severity
  /** Alert content */
  children: React.ReactNode
  /** Optional title */
  title?: string
  /** Whether the alert can be dismissed */
  dismissible?: boolean
  /** Callback when dismissed */
  onDismiss?: () => void
  /** Visual variant: outlined (default) | filled | soft */
  variant?: 'outlined' | 'filled' | 'soft'
  /** ms before auto-dismiss — undefined = never */
  autoHideDuration?: number
  /** Pause auto-dismiss on hover/focus (default: true) */
  pauseOnHover?: boolean
  /** Whether to show the severity icon (default: true) */
  hideIcon?: boolean
  /** h2-h6 heading level for title — undefined = <strong> */
  titleLevel?: 2 | 3 | 4 | 5 | 6
  /** Action buttons rendered after the message */
  actions?: React.ReactNode
} & Omit<React.HTMLAttributes<HTMLDivElement>, 'title' | 'children'>
```

## Key Pattern: Severity Icon SVGs

Inline these minimal SVGs in the generated component:

```tsx
// Inline SVGs for severity icons — no Icon component dependency
const SEVERITY_ICONS: Record<Severity, React.ReactNode> = {
  default: null,
  info: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
    </svg>
  ),
  success: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
    </svg>
  ),
  warning: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
    </svg>
  ),
  error: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
    </svg>
  ),
}
```

## Key Pattern: useAlertBehavior Hook

Inline this hook in the generated file:

```tsx
function useAlertBehavior(
  open: boolean,
  onDismiss: (() => void) | undefined,
  dismissible: boolean,
  autoHideDuration: number | undefined,
  pauseOnHover: boolean,
) {
  const [isVisible, setIsVisible] = React.useState(open)
  const [shouldRender, setShouldRender] = React.useState(open)
  const [isPaused, setIsPaused] = React.useState(false)

  const handleDismiss = React.useCallback(() => {
    setIsVisible(false)
    setTimeout(() => { setShouldRender(false); onDismiss?.() }, 300)
  }, [onDismiss])

  React.useEffect(() => {
    if (open) { setShouldRender(true); setIsVisible(true) }
    else setIsVisible(false)
  }, [open])

  React.useEffect(() => {
    if (!autoHideDuration || !isVisible || isPaused) return
    const t = setTimeout(handleDismiss, autoHideDuration)
    return () => clearTimeout(t)
  }, [autoHideDuration, isVisible, isPaused, handleDismiss])

  React.useEffect(() => {
    if (!dismissible || !isVisible) return
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') handleDismiss() }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [dismissible, isVisible, handleDismiss])

  return {
    isVisible,
    shouldRender,
    handleDismiss,
    pause: () => { if (pauseOnHover && autoHideDuration) setIsPaused(true) },
    resume: () => { if (pauseOnHover && autoHideDuration) setIsPaused(false) },
  }
}
```

## CSS Variables

```scss
--alert-display: flex;
--alert-gap: 0.75rem;
--alert-align: flex-start;
--alert-padding: 1rem;
--alert-margin-block-end: 1rem;
--alert-radius: 0.375rem;
--alert-border: 1px solid;
--alert-bg: var(--color-surface, #f0f0f0);
--alert-color: inherit;
--alert-fs: 0.9375rem;
--alert-line-height: 1.5;
--alert-transition: opacity 0.3s ease;
--alert-opacity-hidden: 0;
--alert-opacity-visible: 1;

// Icon
--alert-icon-size: 1rem;
--alert-icon-color: currentColor;
--alert-icon-flex-shrink: 0;

// Title
--alert-title-fs: 1rem;
--alert-title-fw: 600;
--alert-title-margin-block-end: 0.25rem;

// Actions
--alert-actions-gap: 0.5rem;
--alert-actions-margin-block-start: 0.75rem;

// Severity variants — outlined (default)
--alert-info-bg: #d1ecf1;
--alert-info-border: #bee5eb;
--alert-info-color: #0c5460;

--alert-success-bg: #d4edda;
--alert-success-border: #c3e6cb;
--alert-success-color: #155724;

--alert-warning-bg: #fff3cd;
--alert-warning-border: #ffeeba;
--alert-warning-color: #856404;

--alert-error-bg: #f8d7da;
--alert-error-border: #f5c6cb;
--alert-error-color: #721c24;
```

## Usage Examples

```tsx
import Alert from './alert/alert'
import './alert/alert.scss'

// Basic
<Alert open={true} severity="info">
  Your session will expire in 5 minutes.
</Alert>

// With title and dismiss
<Alert
  open={isOpen}
  severity="error"
  title="Payment failed"
  dismissible
  onDismiss={() => setIsOpen(false)}
>
  Please check your card details and try again.
</Alert>

// Auto-dismiss after 5s
<Alert
  open={showSuccess}
  severity="success"
  autoHideDuration={5000}
  onDismiss={() => setShowSuccess(false)}
>
  Your changes have been saved.
</Alert>

// With actions
<Alert
  open={true}
  severity="warning"
  title="Unsaved changes"
  actions={
    <>
      <button onClick={saveChanges}>Save</button>
      <button onClick={discard}>Discard</button>
    </>
  }
>
  You have unsaved changes.
</Alert>
```

## Accessibility Notes

- Uses `role="alert"` (assertive live region) for error severity
- Uses `role="status"` (polite live region) for info/success/warning
- Severity icon has `aria-hidden="true"` — meaning conveyed by color + text
- A visually hidden `<span>` announces severity to screen readers:
  ```tsx
  <span style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
    {severity}:
  </span>
  ```
- Title uses `<strong>` by default; use `titleLevel` prop for heading levels (h2-h6) to maintain document outline
