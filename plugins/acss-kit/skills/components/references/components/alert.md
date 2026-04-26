# Component: Alert

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). Generated Alert inlines the severity icon SVGs and `useAlertBehavior` hook for self-contained vendoring (no Icon component dependency, no separate hooks file).

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

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

// [Inline SEVERITY_ICONS map and useAlertBehavior hook from above]

const ROLE_FOR_SEVERITY: Record<Severity, 'alert' | 'status' | undefined> = {
  default: undefined,
  info: 'status',
  success: 'status',
  warning: 'status',
  error: 'alert',
}

const SR_ONLY: React.CSSProperties = {
  position: 'absolute', width: 1, height: 1,
  overflow: 'hidden', clip: 'rect(0,0,0,0)',
}

export const Alert = ({
  open,
  severity = 'default',
  children,
  title,
  dismissible = false,
  onDismiss,
  variant = 'outlined',
  autoHideDuration,
  pauseOnHover = true,
  hideIcon = false,
  titleLevel,
  actions,
  ...props
}: AlertProps) => {
  const { isVisible, shouldRender, handleDismiss, pause, resume } = useAlertBehavior(
    open, onDismiss, dismissible, autoHideDuration, pauseOnHover,
  )

  if (!shouldRender) return null

  const TitleEl = titleLevel ? (`h${titleLevel}` as 'h2' | 'h3' | 'h4' | 'h5' | 'h6') : 'strong'
  const role = ROLE_FOR_SEVERITY[severity]
  const ariaLive: 'polite' | 'assertive' | undefined =
    role === 'alert' ? 'assertive' : role === 'status' ? 'polite' : undefined

  return (
    <UI
      as="div"
      classes={`alert alert--${severity} alert--${variant}${isVisible ? '' : ' alert--hidden'}`}
      role={role}
      aria-live={ariaLive}
      onMouseEnter={pause}
      onMouseLeave={resume}
      onFocus={pause}
      onBlur={resume}
      {...props}
    >
      <span style={SR_ONLY}>{severity}: </span>
      {!hideIcon && SEVERITY_ICONS[severity] && (
        <span className="alert-icon">{SEVERITY_ICONS[severity]}</span>
      )}
      <UI as="div" classes="alert-content">
        {title && <UI as={TitleEl} classes="alert-title">{title}</UI>}
        <UI as="div" classes="alert-message">{children}</UI>
        {actions && <UI as="div" classes="alert-actions">{actions}</UI>}
      </UI>
      {dismissible && (
        <button
          type="button"
          className="alert-dismiss"
          aria-label="Dismiss alert"
          onClick={handleDismiss}
        >
          ×
        </button>
      )}
    </UI>
  )
}

export default Alert
Alert.displayName = 'Alert'
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

## SCSS Template

```scss
// alert.scss
.alert {
  display: var(--alert-display, flex);
  gap: var(--alert-gap, 0.75rem);
  align-items: var(--alert-align, flex-start);
  padding: var(--alert-padding, 1rem);
  margin-block-end: var(--alert-margin-block-end, 1rem);
  border-radius: var(--alert-radius, 0.375rem);
  border: var(--alert-border, 1px solid);
  background: var(--alert-bg, #f0f0f0);
  color: var(--alert-color, inherit);
  font-size: var(--alert-fs, 0.9375rem);
  line-height: var(--alert-line-height, 1.5);
  transition: var(--alert-transition, opacity 0.3s ease);
  opacity: var(--alert-opacity-visible, 1);
  position: relative;

  &--hidden {
    opacity: var(--alert-opacity-hidden, 0);
    pointer-events: none;
  }

  &--info {
    background: var(--alert-info-bg, #d1ecf1);
    border-color: var(--alert-info-border, #bee5eb);
    color: var(--alert-info-color, #0c5460);
  }

  &--success {
    background: var(--alert-success-bg, #d4edda);
    border-color: var(--alert-success-border, #c3e6cb);
    color: var(--alert-success-color, #155724);
  }

  &--warning {
    background: var(--alert-warning-bg, #fff3cd);
    border-color: var(--alert-warning-border, #ffeeba);
    color: var(--alert-warning-color, #856404);
  }

  &--error {
    background: var(--alert-error-bg, #f8d7da);
    border-color: var(--alert-error-border, #f5c6cb);
    color: var(--alert-error-color, #721c24);
  }
}

.alert-icon {
  display: inline-flex;
  align-items: center;
  width: var(--alert-icon-size, 1rem);
  height: var(--alert-icon-size, 1rem);
  color: var(--alert-icon-color, currentColor);
  flex-shrink: var(--alert-icon-flex-shrink, 0);
}

.alert-content { flex: 1; }

.alert-title {
  font-size: var(--alert-title-fs, 1rem);
  font-weight: var(--alert-title-fw, 600);
  margin-block-end: var(--alert-title-margin-block-end, 0.25rem);
  display: block;
}

.alert-message > p:first-child { margin-block-start: 0; }
.alert-message > p:last-child { margin-block-end: 0; }

.alert-actions {
  display: flex;
  gap: var(--alert-actions-gap, 0.5rem);
  margin-block-start: var(--alert-actions-margin-block-start, 0.75rem);
}

.alert-dismiss {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  padding: 0.125rem 0.25rem;
  color: currentColor;
  flex-shrink: 0;

  &:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 2px;
  }
}
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

## Accessibility

WCAG 2.2 AA compliance for the generated `Alert` component.

**Live regions**
- Severity `error` renders with `role="alert"` (assertive live region) — screen readers interrupt the current announcement. Reserve for situations the user must address.
- Severities `info`, `success`, `warning` render with `role="status"` (polite live region) — screen readers announce after the current announcement finishes.
- `default` severity (no value passed) renders without a live-region role. Use only for non-status decorative content; otherwise pick an explicit severity.
- `aria-live` is set to match the role: `assertive` for error, `polite` for the others.

**Severity announcement**
- The severity (e.g. "error:", "success:") is rendered in a visually-hidden span before the alert content, so screen readers read severity AND content. Sighted users get the same information from color + icon.
- The severity icon (`<svg>`) carries `aria-hidden="true"`. The meaning is conveyed by the visually-hidden severity label and the body text — the icon is purely decorative.

**Title & document outline**
- Title renders as `<strong>` by default. Pass `titleLevel={2}` through `titleLevel={6}` to render as a heading (`<h2>`–`<h6>`) when the alert is part of a structured document outline.
- Avoid `titleLevel={1}` — page-level h1 is reserved for the document title.

**Color contrast**
- Each severity's `--alert-*-color` on `--alert-*-bg` must meet 4.5:1 (WCAG 1.4.3 Contrast Minimum, AA). The default palette (`#0c5460` on `#d1ecf1`, etc.) was chosen to meet AA.
- Border at `--alert-*-border` must meet 3:1 against the page background (WCAG 1.4.11 Non-text Contrast) when the border is the sole indicator of the alert boundary.

**Dismissal**
- Dismissible alerts render an explicit `<button aria-label="Dismiss alert">×` so screen readers identify the action. The visual `×` is not an accessible name on its own.
- Pressing `Escape` while a dismissible alert is visible triggers dismissal via the keyboard listener in `useAlertBehavior`. Focus does not need to be inside the alert for this to work — the listener is on `document`.

**Auto-dismiss & pause-on-hover**
- `autoHideDuration` automatically removes the alert after the specified ms. To accommodate users who need more time (WCAG 2.2.1 Timing Adjustable, A), `pauseOnHover` (default: true) pauses the timer when the user hovers OR keyboard-focuses the alert.
- For critical messages, prefer `dismissible` without `autoHideDuration` so the user controls dismissal entirely.

**Focus**
- The dismiss button receives `:focus-visible` outline at 2px currentColor with 2px offset. Color inherits from the alert's severity color so the focus indicator stays visible across all variants.

**WCAG 2.2 AA criteria addressed**
- 1.4.3 Contrast Minimum (severity colors meet 4.5:1)
- 1.4.11 Non-text Contrast (border at 3:1 when sole boundary indicator)
- 2.1.1 Keyboard (Escape dismissal; dismiss button keyboard-activatable)
- 2.2.1 Timing Adjustable (pauseOnHover compensates `autoHideDuration`)
- 2.4.7 Focus Visible (dismiss button focus ring)
- 4.1.2 Name, Role, Value (dismiss button has aria-label; live regions properly typed)
- 4.1.3 Status Messages (role="status" / role="alert" for assistive tech)
