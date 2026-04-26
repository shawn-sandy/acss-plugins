# Component: Popover

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). Uses the native HTML Popover API (`popover` attribute + `popovertarget` + `showPopover()` / `hidePopover()`). Browser support: Chrome 125+, Edge 125+, Safari 17.4+, Firefox 125+. The native API provides automatic top-layer rendering, light dismiss, and keyboard handling — no `floating-ui`, `@radix-ui/popover`, or `react-popper` dependency.

## Overview

A popover anchored to a trigger button, built on the native HTML Popover API. Supports auto-mode (light dismiss on outside click or Escape) and manual mode (explicit close button required). Optional positioning arrow, controlled or uncontrolled open state, and custom trigger element. Generates a unique ID via `useId` so multiple popovers on the same page don't collide.

## Generation Contract

```
export_name: Popover
file: popover.tsx
scss: popover.scss
imports: React with useEffect, useId, useRef
dependencies: []
```

Trigger is a raw `<button>` rather than the kit-builder `Button`, so Popover doesn't depend on `button.tsx`. If you want a kit-builder Button as the trigger, pass it via the `trigger` prop and the component will clone it with the required `popovertarget` attributes.

## Props Interface

```tsx
export interface PopoverProps {
  /** Unique ID — defaults to a generated id; required for popovertarget linking */
  id?: string
  /** Content rendered inside the popover */
  children: React.ReactNode
  /** Custom trigger element (default: `<button>` with triggerLabel) */
  trigger?: React.ReactNode
  /** aria-label for the default trigger button */
  triggerLabel?: string
  /** "auto" (light dismiss) or "manual" (explicit close required) */
  mode?: 'auto' | 'manual'
  /** Visual placement hint relative to the trigger */
  placement?: 'top' | 'bottom' | 'left' | 'right'
  /** Controlled open state */
  isOpen?: boolean
  /** Toggle callback */
  onToggle?: (open: boolean) => void
  /** Show close button (default: true for manual mode, false for auto) */
  showCloseButton?: boolean
  /** aria-label for the close button */
  closeButtonLabel?: string
  /** Show positioning arrow (default: true) */
  showArrow?: boolean
  /** Custom CSS class on the popover element */
  className?: string
  /** Inline CSS variables / styles */
  styles?: React.CSSProperties
}
```

## TSX Template

```tsx
import React, { useEffect, useId, useRef } from 'react'

export interface PopoverProps {
  id?: string
  children: React.ReactNode
  trigger?: React.ReactNode
  triggerLabel?: string
  mode?: 'auto' | 'manual'
  placement?: 'top' | 'bottom' | 'left' | 'right'
  isOpen?: boolean
  onToggle?: (open: boolean) => void
  showCloseButton?: boolean
  closeButtonLabel?: string
  showArrow?: boolean
  className?: string
  styles?: React.CSSProperties
}

export const Popover: React.FC<PopoverProps> = ({
  id,
  children,
  trigger,
  triggerLabel = 'Open',
  mode = 'auto',
  placement = 'bottom',
  isOpen,
  onToggle,
  showCloseButton,
  showArrow = true,
  closeButtonLabel = 'Close',
  className = '',
  styles,
}) => {
  const generatedId = useId()
  const popoverId = id || generatedId
  const popoverRef = useRef<HTMLDivElement>(null)

  const shouldShowCloseButton =
    showCloseButton !== undefined ? showCloseButton : mode === 'manual'

  // Controlled open state — drive showPopover() / hidePopover()
  useEffect(() => {
    const popover = popoverRef.current
    if (!popover || isOpen === undefined) return

    try {
      const isCurrentlyOpen =
        popover.matches(':popover-open') || popover.hasAttribute('data-popover-open')
      if (isOpen && !isCurrentlyOpen) popover.showPopover()
      else if (!isOpen && isCurrentlyOpen) popover.hidePopover()
    } catch {
      const isCurrentlyOpen = popover.hasAttribute('data-popover-open')
      if (isOpen && !isCurrentlyOpen) popover.showPopover()
      else if (!isOpen && isCurrentlyOpen) popover.hidePopover()
    }
  }, [isOpen])

  // Toggle callback — listen to the native ToggleEvent
  useEffect(() => {
    const popover = popoverRef.current
    if (!popover || !onToggle) return

    const handleToggle = (event: Event) => {
      const toggleEvent = event as ToggleEvent
      onToggle(toggleEvent.newState === 'open')
    }
    popover.addEventListener('toggle', handleToggle)
    return () => popover.removeEventListener('toggle', handleToggle)
  }, [onToggle])

  const renderTrigger = () => {
    if (trigger) {
      return React.cloneElement(trigger as React.ReactElement, {
        popovertarget: popoverId,
        popovertargetaction: 'toggle',
      })
    }
    return (
      <button
        type="button"
        popovertarget={popoverId}
        popovertargetaction="toggle"
        aria-label={triggerLabel}
        className="popover-trigger"
      >
        {triggerLabel}
      </button>
    )
  }

  return (
    <>
      {renderTrigger()}
      <div
        ref={popoverRef}
        id={popoverId}
        popover={mode}
        className={`popover ${className}`.trim()}
        data-placement={placement}
        style={styles}
      >
        {showArrow && <div className="popover-arrow" data-placement={placement} />}
        <div className="popover-content">
          {children}
          {shouldShowCloseButton && (
            <button
              type="button"
              popovertarget={popoverId}
              popovertargetaction="hide"
              aria-label={closeButtonLabel}
              className="popover-close"
            >
              ×
            </button>
          )}
        </div>
      </div>
    </>
  )
}

Popover.displayName = 'Popover'
export default Popover
```

## CSS Variables

```scss
--popover-bg: var(--color-surface, #fff);
--popover-color: var(--color-text, inherit);
--popover-border: 1px solid var(--color-border, #e0e0e0);
--popover-radius: 0.375rem;
--popover-padding: 0.75rem 1rem;
--popover-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
--popover-max-width: 20rem;
--popover-z: 10;
--popover-arrow-size: 0.5rem;
```

## SCSS Template

```scss
// popover.scss
.popover {
  // Native popover element resets — re-establish basic block
  margin: 0;
  border: var(--popover-border, 1px solid #e0e0e0);
  border-radius: var(--popover-radius, 0.375rem);
  background: var(--popover-bg, #fff);
  color: var(--popover-color, inherit);
  box-shadow: var(--popover-shadow, 0 4px 12px rgba(0, 0, 0, 0.15));
  max-width: var(--popover-max-width, 20rem);
  z-index: var(--popover-z, 10);
  inset: unset;

  &:popover-open {
    display: block;
  }
}

.popover-content {
  padding: var(--popover-padding, 0.75rem 1rem);
  position: relative;
}

.popover-arrow {
  position: absolute;
  width: var(--popover-arrow-size, 0.5rem);
  height: var(--popover-arrow-size, 0.5rem);
  background: inherit;
  border: inherit;
  transform: rotate(45deg);

  &[data-placement="bottom"] { top: calc(var(--popover-arrow-size, 0.5rem) * -0.5); left: 50%; border-bottom: none; border-right: none; }
  &[data-placement="top"]    { bottom: calc(var(--popover-arrow-size, 0.5rem) * -0.5); left: 50%; border-top: none; border-left: none; }
  &[data-placement="left"]   { right: calc(var(--popover-arrow-size, 0.5rem) * -0.5); top: 50%; border-left: none; border-bottom: none; }
  &[data-placement="right"]  { left: calc(var(--popover-arrow-size, 0.5rem) * -0.5); top: 50%; border-right: none; border-top: none; }
}

.popover-close {
  position: absolute;
  top: 0.25rem;
  right: 0.5rem;
  background: transparent;
  border: none;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  padding: 0.125rem 0.25rem;
  color: currentColor;

  &:focus-visible {
    outline: 2px solid currentColor;
    outline-offset: 2px;
  }
}

.popover-trigger {
  // The default trigger when no `trigger` prop is passed —
  // intentionally minimal so it inherits the parent's button styling
  cursor: pointer;
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `Popover` component.

**Native Popover API**
- `popover="auto"` (default) gives the popover light-dismiss behavior: clicking outside closes it; pressing `Escape` closes it. The browser handles both — no JavaScript listeners needed.
- `popover="manual"` requires an explicit close action. Use for popovers that contain forms or interactive content where accidental dismissal would lose user input.
- Both modes render the popover in the browser's top layer (above all stacking contexts) so `z-index` from sibling elements doesn't matter.

**Keyboard interaction**
- Trigger button activates the popover via `popovertargetaction="toggle"` — Enter or Space on the trigger toggles the popover. No JavaScript click handler needed; this is a native browser behaviour.
- In `auto` mode, `Escape` closes the popover (browser default).
- Focus moves into the popover when opened only if the popover contains a focusable element and the user explicitly tabs into it. Unlike a `<dialog>` modal, focus is *not* trapped — by design, the user can keyboard-navigate to other parts of the page while the popover is open.

**ARIA & screen reader**
- Trigger button has an `aria-label` (default: `"Open"` via `triggerLabel`). When passing a custom `trigger`, ensure the trigger element has an accessible name.
- Close button has an explicit `aria-label="Close"` — the visual `×` glyph is not an accessible name on its own.
- The popover container itself does not get `role="dialog"` or `role="tooltip"` automatically. If the popover is used as a tooltip, add `role="tooltip"` and link the trigger via `aria-describedby`. If used as a menu, consider whether `role="menu"` and the menu-button pattern are more appropriate.

**Focus management on close**
- On close (light dismiss or close button), focus returns to the trigger button — native popover behaviour. This avoids losing the user's place after closing.

**Color contrast**
- Popover text color (`--popover-color`) on background (`--popover-bg`) must meet 4.5:1 (WCAG 1.4.3 AA).
- Popover border (`--popover-border`) provides visual separation from the page; in flat designs without shadow, the border must meet 3:1 against the page background (WCAG 1.4.11 Non-text Contrast).

**Browser support fallback**
- Browsers without Popover API support: the `popover` attribute is ignored, the popover renders as a normal `<div>` inline. Plan for graceful degradation by ensuring the surrounding layout doesn't break when the popover is always-visible. Or feature-detect `'showPopover' in HTMLElement.prototype` and provide an alternative UI.

**WCAG 2.2 AA criteria addressed**
- 1.4.3 Contrast Minimum (text on popover background)
- 1.4.11 Non-text Contrast (popover border)
- 2.1.1 Keyboard (native trigger toggle + Escape dismiss)
- 2.4.3 Focus Order (focus returns to trigger on close)
- 2.4.7 Focus Visible (close button focus ring)
- 4.1.2 Name, Role, Value (trigger and close button have accessible names; user must add `role` if popover serves a specific semantic role)

## Usage Examples

```tsx
import Popover from './popover/popover'
import './popover/popover.scss'

// Default — auto mode (light dismiss)
<Popover id="info" triggerLabel="More info">
  <p>Additional context shown in a popover.</p>
</Popover>

// Manual mode — explicit close required
<Popover
  id="confirm"
  mode="manual"
  triggerLabel="Confirm"
  closeButtonLabel="Cancel confirmation"
>
  <h3>Are you sure?</h3>
  <p>This action cannot be undone.</p>
  <button type="button" onClick={handleConfirm}>Yes, proceed</button>
</Popover>

// Custom trigger
<Popover
  id="user-menu"
  trigger={<button type="button" aria-label="User menu">@alice</button>}
  placement="bottom"
>
  <ul>
    <li><a href="/profile">Profile</a></li>
    <li><a href="/logout">Log out</a></li>
  </ul>
</Popover>

// Controlled
const [open, setOpen] = useState(false)
<Popover
  id="controlled"
  isOpen={open}
  onToggle={setOpen}
  triggerLabel="Toggle externally"
>
  <p>State driven from parent.</p>
</Popover>
```
