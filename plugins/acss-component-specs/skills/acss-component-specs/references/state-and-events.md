# State and Events Reference

Patterns for stateful components and event handling across all three framework renderers.

---

## Dialog: Open/Close State

Dialog is the primary stateful component. Its open state is managed by the consumer, not internally.

### React Pattern

Use a `ref` to the native `<dialog>` element. `showModal()` opens the dialog; `close()` closes it. The native dialog provides focus trapping and `::backdrop` automatically.

```tsx
const dialogRef = useRef<HTMLDialogElement>(null)

// Open
const openDialog = () => dialogRef.current?.showModal()

// Close
const closeDialog = () => dialogRef.current?.close()

// Wire ref to Dialog
<Dialog dialogRef={dialogRef} onClose={closeDialog} title="Confirm">
  <p>Are you sure?</p>
  <Dialog.Footer>
    <Button type="button" variant="outline" onClick={closeDialog}>Cancel</Button>
    <Button type="button" color="primary" onClick={handleConfirm}>Confirm</Button>
  </Dialog.Footer>
</Dialog>
```

### HTML Pattern

```html
<button type="button" onclick="document.getElementById('dialog-1').showModal()">Open</button>

<dialog id="dialog-1" class="dialog" aria-labelledby="dialog-title-1">
  ...
</dialog>
```

Use `showModal()` (not `show()`) so focus is trapped inside the dialog.

### Astro Pattern

```astro
<button type="button" id="open-btn">Open Dialog</button>
<Dialog id="dialog-1" title="Confirm" />

<script>
  document.getElementById('open-btn').addEventListener('click', function() {
    document.getElementById('dialog-1').showModal()
  })
</script>
```

---

## Dialog: Backdrop Click Dismiss

```tsx
// React
const handleBackdropClick = (e: React.MouseEvent<HTMLDialogElement>) => {
  if (e.currentTarget === e.target) {
    e.currentTarget.close()
    onClose?.()
  }
}
```

```html
<!-- HTML -->
<script>
document.getElementById('dialog-1').addEventListener('click', function(e) {
  if (e.target === e.currentTarget) e.currentTarget.close();
});
</script>
```

---

## Dialog: Focus Restoration

The native `<dialog>` element returns focus to the element that triggered `showModal()` when `close()` is called. This is built-in — no manual focus restoration needed.

If the trigger element is dynamic (rendered after dialog close), wire `onClose` to manually call `triggerRef.current?.focus()`.

---

## Alert: Auto-Dismiss

Alert supports optional `autoDismiss` behavior.

### React Pattern

```tsx
useEffect(() => {
  if (!autoDismiss || !onDismiss) return
  const timer = setTimeout(onDismiss, autoDismissMs ?? 5000)
  return () => clearTimeout(timer)
}, [autoDismiss, onDismiss, autoDismissMs])
```

### HTML Pattern

```html
<div class="alert" id="alert-1" data-severity="info" role="alert">
  <p>Alert message here.</p>
</div>

<script>
// Auto-dismiss after 5s when data-auto-dismiss attribute is present
var alert = document.getElementById('alert-1');
if (alert && alert.hasAttribute('data-auto-dismiss')) {
  setTimeout(function() {
    alert.setAttribute('aria-hidden', 'true');
    alert.style.display = 'none';
  }, parseInt(alert.getAttribute('data-auto-dismiss')) || 5000);
}
</script>
```

### Astro Pattern

Use a client script block with the same logic as the HTML pattern.

---

## Interactive Cards: Click + Keyboard

Cards with `interactive=true` must handle both click and keyboard Enter/Space.

```tsx
// React
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault()
    onClick?.()
  }
}

<UI
  as={as ?? 'div'}
  role="button"
  tabIndex={interactive ? 0 : undefined}
  data-card={interactive ? 'interactive' : undefined}
  onClick={interactive ? onClick : undefined}
  onKeyDown={interactive ? handleKeyDown : undefined}
  aria-label={interactive ? ariaLabel : undefined}
  ...
>
```

```html
<!-- HTML -->
<div class="card" role="button" tabindex="0" data-card="interactive"
     aria-label="View product details"
     onclick="handleCardClick(this)"
     onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();handleCardClick(this);}">
  ...
</div>
```

---

## aria-disabled Pattern

All interactive components in acss-component-specs use `aria-disabled` instead of the native `disabled` attribute. This keeps elements in the tab order (WCAG 2.1.1).

### React

Inline `useDisabledState` in each interactive component (see `references/frameworks/react.md`).

### HTML

```html
<button class="btn" aria-disabled="true">Disabled (still focusable)</button>

<script>
document.querySelectorAll('[aria-disabled="true"]').forEach(function(el) {
  el.addEventListener('click', function(e) {
    e.preventDefault(); e.stopPropagation();
  });
});
</script>
```

### Astro

```astro
---
const { disabled = false } = Astro.props
---
<button aria-disabled={disabled ? 'true' : undefined} ...>
  <slot />
</button>

<script>
// Client script handles click prevention
document.querySelectorAll('[aria-disabled="true"]').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.preventDefault(); e.stopPropagation();
  });
});
</script>
```

---

## Nav: Active State

Nav links use an `active` prop/attribute to indicate the current page.

```tsx
// React
<Nav.Link href="/about" active>About</Nav.Link>
// → aria-current="page" + data-nav="active"
```

```html
<!-- HTML -->
<a href="/about" class="nav-link" aria-current="page" data-nav="active">About</a>
```

`aria-current="page"` is the correct ARIA attribute for the current page link (WCAG 2.4.4).

---

## Event Passthrough Pattern

All three renderers support event passthrough — passing arbitrary event handlers from the consumer to the underlying element without explicitly listing every possible event.

### React
```tsx
// Spread ...rest onto the element after explicit props
<UI as="button" {...restProps} {...wrappedHandlers}>
```

### HTML
Event passthrough is implicit via HTML attribute spreading — the snippet shows a subset; consumers add their own event attributes.

### Astro
```astro
---
const { onClick, onKeyDown, ...rest } = Astro.props
---
<button {...rest}>...</button>
```
