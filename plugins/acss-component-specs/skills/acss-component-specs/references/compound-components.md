# Compound Components Reference

Compound components are a pattern where a root component and its sub-components share state and are distributed via a clear API. In fpkit, the pattern uses static property attachment: `Card.Title`, `Card.Content`, `Card.Footer`.

---

## When to Use Compound Components

Use compound components when:
- Sub-components share context or state with the root (Dialog open state, Card accessibility linking)
- The sub-components are rarely used independently
- The usage API should read naturally: `<Card><Card.Title>...</Card.Title></Card>`

Do **not** use compound components for:
- Independent components that happen to be used together (Button + Icon)
- Components with no shared state or context

---

## Spec Layout for Compound Components

A compound root gets its own spec (e.g. `card.md`). Each sub-component gets a sibling spec file:

```
specs/
  card.md          ← root spec
  card-title.md    ← sub-component spec
  card-content.md
  card-footer.md
```

Sub-component spec frontmatter references the parent:

```yaml
name: card-title
display_name: Card.Title
parent: card
maps_to_parent: compound-part
```

### A11y blocks in sub-components

Sub-components that are themselves interactive (e.g. a Card.Footer containing buttons) or have their own accessibility semantics should have their own `a11y` block, independent of the parent.

Layout-only sub-components (Card.Content, Card.Footer when it's just a flex row) should use `a11y.layout_only: true`.

---

## React: Static Property Pattern

```tsx
// In card.tsx — all in one file

const CardRoot = React.forwardRef<HTMLElement, CardProps>(({...}, ref) => {
  return <UI as={as ?? 'div'} ref={ref} className="card" ...>...</UI>
})
CardRoot.displayName = 'Card'

const CardTitle = ({as, children, id, className}: CardTitleProps) => (
  <UI as={as ?? 'h3'} classes={`card-title${className ? ' ' + className : ''}`} id={id}>
    {children}
  </UI>
)
CardTitle.displayName = 'Card.Title'

const CardContent = ({as, children}: CardContentProps) => (
  <UI as={as ?? 'article'} classes="card-content">{children}</UI>
)
CardContent.displayName = 'Card.Content'

const CardFooter = ({as, children}: CardFooterProps) => (
  <UI as={as ?? 'div'} classes="card-footer">{children}</UI>
)
CardFooter.displayName = 'Card.Footer'

// Compound assembly
type CardComponent = typeof CardRoot & {
  Title: typeof CardTitle
  Content: typeof CardContent
  Footer: typeof CardFooter
}

export const Card = Object.assign(CardRoot, {
  Title: CardTitle,
  Content: CardContent,
  Footer: CardFooter,
}) as CardComponent

export default Card
```

---

## HTML: Semantic Nesting

For HTML output, compound components become nested semantic elements:

```html
<article class="card" aria-labelledby="card-title-1">
  <h3 class="card-title" id="card-title-1">Card Title</h3>
  <div class="card-content">
    <p>Content here.</p>
  </div>
  <div class="card-footer">
    <!-- footer actions -->
  </div>
</article>
```

Accessibility linking:
- Root `<article>` or `<section>` uses `aria-labelledby` pointing to the `.card-title` id
- IDs must be unique; use a predictable pattern: `card-title-1`, `card-title-2`, etc.

---

## Astro: Separate Component Files

Astro renders compound components as separate `.astro` files (no static property attachment):

```
Card.astro
CardTitle.astro
CardContent.astro
CardFooter.astro
card.scss
```

---

## Dialog Compound Pattern

Dialog has a different structure because it uses `React.forwardRef`:

```tsx
const DialogRoot = React.forwardRef<HTMLDialogElement, DialogProps>(({...}, _ref) => {
  return (
    <UI as="dialog" ref={dialogRef} ...>
      <DialogHeader .../>
      <DialogBody>{children}</DialogBody>
      {footer && <DialogFooter>{footer}</DialogFooter>}
    </UI>
  )
})

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
```

---

## Nav Compound Pattern

Nav uses the same static property pattern, but `Nav.Link` is the primary sub-component:

```tsx
export const Nav = Object.assign(NavRoot, { Link: NavLink }) as NavComponent
```

Usage:
```tsx
<Nav>
  <Nav.Link href="/">Home</Nav.Link>
  <Nav.Link href="/about" active>About</Nav.Link>
</Nav>
```

---

## Dependency Tree for Render Planning

`plan_render.py` knows which compound parts belong to which root via `DEPENDENCY_GRAPH`. When rendering `card`, it emits card + all card-* files in the same component file. When rendering `card-title` individually, it emits nothing (compound parts are generated inside the parent's file).

```python
COMPOUND_PARTS = {'card-title', 'card-content', 'card-footer', 'nav-link'}
```

Rendering a compound root emits all parts. Rendering a compound part alone is a no-op.
