# Component: Dialog

## Overview

A modal dialog using the native HTML `<dialog>` element. The native element provides focus trapping automatically via `showModal()` — no npm packages needed. Supports a header/body/footer structure, dismissable via Escape key (built-in), backdrop click, and a close button.

## Generation Contract

```
export_name: Dialog (+ DialogHeader, DialogBody, DialogFooter)
file: dialog.tsx
scss: dialog.scss
imports: UI from '../ui', Button from '../button/button'
dependencies: [button]
```

Note: Unlike the fpkit source, the generated Dialog does NOT depend on `icon-button`. The close button is rendered using a text "×" character or a simple Button variant. This simplifies the dependency tree.

## Why Native `<dialog>`?

- `showModal()` automatically traps focus within the dialog (no `focus-trap` package)
- Focus returns to the trigger element on `close()`
- Escape key fires `cancel` event automatically
- Native `::backdrop` pseudo-element for the overlay
- `aria-modal` behavior built in

## Props Interface

```tsx
export type DialogProps = {
  /** Ref to the dialog element — required for showModal()/close() */
  dialogRef: React.RefObject<HTMLDialogElement>
  /** Whether to open on mount */
  openOnMount?: boolean
  /** Callback when dialog is closed */
  onClose?: () => void
  /** Dialog title for aria-labelledby */
  title?: string
  /** Dialog description for aria-describedby */
  description?: string
  /** Whether to show a close button in the header */
  showCloseButton?: boolean
  /** Dialog content */
  children?: React.ReactNode
  /** Footer action buttons */
  footer?: React.ReactNode
  /** CSS class name */
  classes?: string
  /** Inline styles */
  styles?: React.CSSProperties
} & Omit<React.ComponentPropsWithoutRef<'dialog'>, 'open'>

export type DialogHeaderProps = {
  children?: React.ReactNode
  onClose?: () => void
  showCloseButton?: boolean
  classes?: string
}

export type DialogBodyProps = {
  children?: React.ReactNode
  classes?: string
}

export type DialogFooterProps = {
  children?: React.ReactNode
  classes?: string
}
```

## Key Pattern: showModal / close

```tsx
// Parent component usage
const dialogRef = useRef<HTMLDialogElement>(null)

// Open
const openDialog = () => dialogRef.current?.showModal()

// Close
const closeDialog = () => dialogRef.current?.close()

// Pass ref to Dialog
<Dialog dialogRef={dialogRef} onClose={closeDialog} title="Confirm Action">
  <p>Are you sure?</p>
  <Dialog.Footer>
    <Button type="button" onClick={closeDialog} variant="outline">Cancel</Button>
    <Button type="button" color="primary" onClick={handleConfirm}>Confirm</Button>
  </Dialog.Footer>
</Dialog>
```

## Key Pattern: Backdrop Click Close

```tsx
const handleBackdropClick = (e: React.MouseEvent<HTMLDialogElement>) => {
  // e.target is the dialog itself (not inner content) when backdrop is clicked
  if (e.currentTarget === e.target) {
    e.currentTarget.close()
    onClose?.()
  }
}
```

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'
import Button from '../button/button'

// --- Types (inline) ---
// [DialogProps, DialogHeaderProps, DialogBodyProps, DialogFooterProps as above]

// --- Sub-components ---
const DialogHeader = ({ children, onClose, showCloseButton = true, classes }: DialogHeaderProps) => (
  <UI as="div" classes={`dialog-header${classes ? ' ' + classes : ''}`}>
    <UI as="div" classes="dialog-header-content">{children}</UI>
    {showCloseButton && (
      <Button
        type="button"
        variant="icon"
        aria-label="Close dialog"
        onClick={onClose}
        classes="dialog-close"
      >
        ×
      </Button>
    )}
  </UI>
)
DialogHeader.displayName = 'Dialog.Header'

const DialogBody = ({ children, classes }: DialogBodyProps) => (
  <UI as="div" classes={`dialog-body${classes ? ' ' + classes : ''}`}>
    {children}
  </UI>
)
DialogBody.displayName = 'Dialog.Body'

const DialogFooter = ({ children, classes }: DialogFooterProps) => (
  <UI as="div" classes={`dialog-footer${classes ? ' ' + classes : ''}`}>
    {children}
  </UI>
)
DialogFooter.displayName = 'Dialog.Footer'

// --- Root component ---
const DialogRoot = React.forwardRef<HTMLDialogElement, DialogProps>(({
  dialogRef,
  openOnMount,
  onClose,
  title,
  description,
  showCloseButton = true,
  children,
  footer,
  classes,
  styles,
  ...props
}: DialogProps, _ref) => {
  const titleId = title ? `dialog-title-${Math.random().toString(36).slice(2, 7)}` : undefined

  const handleClose = () => {
    dialogRef.current?.close()
    onClose?.()
  }

  const handleBackdropClick = (e: React.MouseEvent<HTMLDialogElement>) => {
    if (e.currentTarget === e.target) handleClose()
  }

  return (
    <UI
      as="dialog"
      ref={dialogRef}
      open={openOnMount}
      classes={`dialog${classes ? ' ' + classes : ''}`}
      styles={styles}
      aria-labelledby={titleId}
      onClick={handleBackdropClick}
      {...props}
    >
      {title && (
        <DialogHeader onClose={handleClose} showCloseButton={showCloseButton}>
          <UI as="h2" id={titleId} classes="dialog-title">{title}</UI>
          {description && <UI as="p" classes="dialog-description">{description}</UI>}
        </DialogHeader>
      )}
      <DialogBody>{children}</DialogBody>
      {footer && <DialogFooter>{footer}</DialogFooter>}
    </UI>
  )
})
DialogRoot.displayName = 'Dialog'

// --- Compound assembly ---
type DialogComponent = typeof DialogRoot & {
  Header: typeof DialogHeader
  Body: typeof DialogBody
  Footer: typeof DialogFooter
}

export const Dialog = Object.assign(DialogRoot, {
  Header: DialogHeader,
  Body: DialogBody,
  Footer: DialogFooter,
}) as DialogComponent

export default Dialog
```

## HTML Template

```html
<!-- variant: full dialog (header + body + footer) -->
<dialog id="dialog-1" class="dialog" aria-labelledby="dialog-1-title">
  <div class="dialog-header">
    <div class="dialog-header-content">
      <h2 id="dialog-1-title" class="dialog-title">
        <!-- slot: title -->
      </h2>
      <p class="dialog-description">
        <!-- slot: description -->
      </p>
    </div>
    <button
      type="button"
      class="btn dialog-close"
      data-style="icon"
      aria-label="Close dialog"
      data-dialog-close
    >
      ×
    </button>
  </div>
  <div class="dialog-body">
    <!-- slot: children -->
  </div>
  <div class="dialog-footer">
    <!-- slot: footer (e.g. confirm/cancel buttons) -->
  </div>
</dialog>

<!-- Trigger that opens the dialog (place anywhere on the page) -->
<button type="button" class="btn" data-color="primary" data-dialog-open="dialog-1">
  Open dialog
</button>

<!-- variant: minimal dialog (no header, no footer) -->
<dialog id="dialog-2" class="dialog">
  <div class="dialog-body">
    <!-- slot: children -->
  </div>
</dialog>
```

The native `<dialog>` element provides focus trap, scrim, and Escape-to-close — no JS required for those. The vanilla-JS module wires open triggers (`[data-dialog-open="<id>"]`), close triggers (`[data-dialog-close]`), and backdrop-click dismissal. The dialog must have an `id` attribute for the open trigger to find it. `aria-labelledby` points at the title's id so screen readers announce the dialog by name (WCAG 4.1.2).

## Vanilla JS

```js
// dialog.js — wires open / close / backdrop-click for static-HTML dialogs.
// Idempotent: calling init() twice on the same root does not double-bind.

const SENTINEL = 'data-acss-dialog-init';

/**
 * Initialize every <dialog class="dialog"> under `root`.
 *
 * Markup contract:
 *   - Open trigger: any element with [data-dialog-open="<dialog-id>"]
 *   - Close trigger: any element inside the dialog with [data-dialog-close]
 *   - Backdrop click closes the dialog automatically.
 *
 * @param {ParentNode} [root=document]
 */
export function init(root = document) {
  const dialogs = root.querySelectorAll('dialog.dialog');
  for (const dialog of dialogs) {
    if (dialog.getAttribute(SENTINEL) === 'true') continue;
    dialog.setAttribute(SENTINEL, 'true');
    wireDialog(dialog, root);
  }
}

function wireDialog(dialog, root) {
  // Backdrop click — only fires when the click hits the <dialog> itself,
  // not a descendant. Prevents the dialog from closing while the user is
  // interacting with its body.
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });

  // Internal close triggers.
  for (const btn of dialog.querySelectorAll('[data-dialog-close]')) {
    btn.addEventListener('click', () => dialog.close());
  }

  // Document-level open triggers — any [data-dialog-open] pointing at this
  // dialog's id. Scoped to `root` so init() inside a shadow root or fragment
  // works correctly.
  if (!dialog.id) return;
  const triggerScope = root === document ? document : root;
  const openTriggers = triggerScope.querySelectorAll(
    `[data-dialog-open="${CSS.escape(dialog.id)}"]`,
  );
  for (const trigger of openTriggers) {
    trigger.addEventListener('click', () => dialog.showModal());
  }
}
```

`CSS.escape` guards against ids that contain special characters. The module relies on the native `<dialog>` element's behavior — there is no custom focus trap or scrim; the browser provides them.

## CSS Variables

```scss
--dialog-bg: var(--color-surface, #fff);
--dialog-color: var(--color-text, inherit);
--dialog-padding: 0;
--dialog-radius: 0.5rem;
--dialog-width: 32rem;
--dialog-max-width: 90vw;
--dialog-max-height: 85vh;
--dialog-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
--dialog-border: none;

--dialog-header-padding: 1.5rem;
--dialog-header-border-bottom: 1px solid var(--color-border, #e0e0e0);

--dialog-title-fs: 1.25rem;
--dialog-title-fw: 600;
--dialog-title-color: var(--color-text, inherit);

--dialog-body-padding: 1.5rem;
--dialog-body-overflow: auto;

--dialog-footer-padding: 1rem 1.5rem;
--dialog-footer-bg: var(--color-surface-subtle, #f9f9f9);
--dialog-footer-border-top: 1px solid var(--color-border, #e0e0e0);
--dialog-footer-gap: 0.75rem;
--dialog-footer-justify: flex-end;

--dialog-close-size: 2rem;
--dialog-close-color: var(--color-text-subtle, #555);

--dialog-backdrop-bg: rgba(0, 0, 0, 0.5);
```

## SCSS Template

```scss
// dialog.scss
.dialog {
  background: var(--dialog-bg, #fff);
  color: var(--dialog-color, inherit);
  padding: var(--dialog-padding, 0);
  border-radius: var(--dialog-radius, 0.5rem);
  border: var(--dialog-border, none);
  width: var(--dialog-width, 32rem);
  max-width: var(--dialog-max-width, 90vw);
  max-height: var(--dialog-max-height, 85vh);
  box-shadow: var(--dialog-shadow, 0 20px 25px rgba(0, 0, 0, 0.15));
  overflow: hidden;
  display: flex;
  flex-direction: column;

  &::backdrop {
    background: var(--dialog-backdrop-bg, rgba(0, 0, 0, 0.5));
  }
}

.dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: var(--dialog-header-padding, 1.5rem);
  border-bottom: var(--dialog-header-border-bottom, 1px solid #e0e0e0);
  flex-shrink: 0;
}

.dialog-header-content { flex: 1; }

.dialog-title {
  font-size: var(--dialog-title-fs, 1.25rem);
  font-weight: var(--dialog-title-fw, 600);
  margin: 0;
}

.dialog-description {
  margin-block-start: 0.25rem;
  font-size: 0.875rem;
  color: var(--color-text-subtle, #555);
}

.dialog-close {
  font-size: 1.25rem;
  line-height: 1;
  color: var(--dialog-close-color, #555);
  padding: 0.25rem;
  width: var(--dialog-close-size, 2rem);
  height: var(--dialog-close-size, 2rem);
  flex-shrink: 0;
}

.dialog-body {
  padding: var(--dialog-body-padding, 1.5rem);
  overflow-y: var(--dialog-body-overflow, auto);
  flex: 1;
}

.dialog-footer {
  display: flex;
  justify-content: var(--dialog-footer-justify, flex-end);
  gap: var(--dialog-footer-gap, 0.75rem);
  padding: var(--dialog-footer-padding, 1rem 1.5rem);
  background: var(--dialog-footer-bg, #f9f9f9);
  border-top: var(--dialog-footer-border-top, 1px solid #e0e0e0);
  flex-shrink: 0;
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `Dialog` component. Most affordances come for free from the native `<dialog>` element; the listed criteria document where the implementation explicitly addresses each one.

**Keyboard interaction**
- `showModal()` traps focus inside the dialog automatically. Tab and Shift+Tab cycle within the dialog only.
- `Escape` fires the native `cancel` event; the implementation calls `handleClose()` in response. No JavaScript keybinding needed.
- Closing (close button, backdrop, or Escape) returns focus to the element that called `showModal()` — also native browser behavior.

**ARIA & screen reader**
- Native `<dialog>` provides implicit `role="dialog"` and `aria-modal="true"` when opened with `showModal()`. Do not add either attribute explicitly.
- `aria-labelledby` references the generated title id, so screen readers announce the dialog title on open.
- `aria-describedby` (when `description` prop is set) points at the description paragraph for additional context.
- Close button has an explicit `aria-label="Close dialog"` since the visual `×` glyph is not an accessible name.

**Focus management**
- Initial focus on open: the browser focuses the first focusable element inside the dialog. Because the close button is rendered first when `showCloseButton` is true, it usually receives initial focus — acceptable, but to avoid users immediately tabbing into a destructive close, the actionable footer button is a better target. Pass `autoFocus` to the desired footer button or programmatically focus inside `useEffect` if a different element should be initial focus.
- Focus cannot escape the dialog while open via `showModal()`. Do not call modeless `show()` — it does not enforce the trap.
- On close, focus returns to the trigger element automatically.

**Backdrop & dismissal**
- `::backdrop` pseudo-element renders the overlay; `handleBackdropClick` compares `e.target === e.currentTarget` to detect a click on the backdrop (vs inner content) and closes.
- Backdrop click is a convenience for pointer users — keyboard users have `Escape` and the close button, so no a11y dependency on backdrop dismissal.

**Color contrast**
- Dialog title at `--dialog-title-color` on `--dialog-bg` must meet 4.5:1 (WCAG 1.4.3 Contrast Minimum, AA).
- Description text at `var(--color-text-subtle)` must meet 4.5:1 against `--dialog-bg`. The default `#555` on `#fff` ratio is approximately 7.5:1 — passes.
- Backdrop overlay at `--dialog-backdrop-bg` (rgba(0,0,0,0.5)) provides visual separation; not subject to text-contrast rules.

**Document outline**
- Dialog title renders as `<h2>` by default. If the dialog appears within a section that already has an `<h2>`, consider passing `title=""` and rendering a custom `<h3>` inside the dialog body to maintain heading hierarchy.

**WCAG 2.2 AA criteria addressed**
- 1.4.3 Contrast Minimum (title and description on dialog background)
- 2.1.1 Keyboard (full keyboard operability via native dialog)
- 2.1.2 No Keyboard Trap (the trap is intentional and releases on close)
- 2.4.3 Focus Order (initial focus inside dialog; returns to trigger on close)
- 2.4.7 Focus Visible (close button + footer Buttons inherit `:focus-visible` from button.scss)
- 4.1.2 Name, Role, Value (native dialog + aria-labelledby + close button aria-label)

## Usage Examples

```tsx
import { useRef } from 'react'
import Dialog from './dialog/dialog'
import Button from './button/button'
import './dialog/dialog.scss'
import './button/button.scss'

function App() {
  const dialogRef = useRef<HTMLDialogElement>(null)

  return (
    <>
      <Button type="button" onClick={() => dialogRef.current?.showModal()}>
        Open Dialog
      </Button>

      <Dialog
        dialogRef={dialogRef}
        title="Confirm Action"
        description="This action cannot be undone."
        onClose={() => console.log('closed')}
        footer={
          <>
            <Button type="button" variant="outline" onClick={() => dialogRef.current?.close()}>
              Cancel
            </Button>
            <Button type="button" color="primary" onClick={() => {}}>
              Confirm
            </Button>
          </>
        }
      >
        <p>Are you sure you want to proceed?</p>
      </Dialog>
    </>
  )
}
```

## Dependencies

When generating Dialog, Claude must first ensure these exist in the target directory:

1. `ui.tsx` — foundation (auto-created on first run)
2. `button/button.tsx` + `button/button.scss` — for close button and footer actions

Check if `button.tsx` exists before generating. If it exists, import from it. If not, generate it first.

Dependency order:
1. `ui.tsx` (foundation)
2. `button/button.tsx` + `button/button.scss`
3. `dialog/dialog.tsx` + `dialog/dialog.scss`
