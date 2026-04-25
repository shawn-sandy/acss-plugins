> **Legacy reference** — When `acss-component-specs` is installed, check for a spec first (kit-builder B0 bridge). Components in this catalog that have specs in v0.1: Button, Card, Dialog, Alert, Nav. Stack is new in acss-component-specs and not in this catalog.

# Component Catalog

Simple and medium-complexity components. Each entry includes the Generation Contract, props, CSS variables, and a usage snippet.

---

## Verification Status

Tracks each component reference doc's verification against canonical fpkit source. Updated as components are backfilled into the embedded-markdown shape (TSX Template + SCSS Template + Accessibility).

| Component | Reference | Verified against | Status |
|-----------|-----------|------------------|--------|
| Button | [`button.md`](button.md) | `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`) | Verified — intentional divergences noted in `button.md` (inlined `useDisabledState` / `resolveDisabledState` for self-contained vendoring) |
| Alert | [`alert.md`](alert.md) | `@fpkit/acss@6.5.0` | Verified — TSX Template + SCSS Template authored from existing fragments; severity icon SVGs and `useAlertBehavior` hook inlined for self-contained vendoring (no `Icon` component dependency) |
| Card | [`card.md`](card.md) | `@fpkit/acss@6.5.0` | Verified — compound assembly (`Card`, `Card.Title`, `Card.Content`, `Card.Footer`) authored as a single `card.tsx`; matches upstream compound pattern |
| Dialog | [`dialog.md`](dialog.md) | `@fpkit/acss@6.5.0` | Verified — uses native `<dialog>` + `showModal()` for focus trap; close button uses `Button` with `variant="icon"` instead of `IconButton` to keep dependency tree shallow |
| IconButton | [`icon-button.md`](icon-button.md) | `@fpkit/acss@6.5.0` | New — wraps `Button` with `variant="icon"`; XOR-typed accessible-name (`aria-label` xor `aria-labelledby`) enforced at compile time per WCAG 1.1.1 |
| Img | [`img.md`](img.md) | `@fpkit/acss@6.5.0` | New — lazy-loading default + memoized SVG-gradient placeholder fallback (zero network requests on error); `alt` prop required by type |
| Popover | [`popover.md`](popover.md) | `@fpkit/acss@6.5.0` | New — uses native HTML Popover API (`popover` attribute + `popovertarget`); no `floating-ui` / `@radix-ui/popover` dependency. Trigger is a raw `<button>` to avoid coupling to `button.tsx` |
| Table | [`table.md`](table.md) | `@fpkit/acss@6.5.0` | New — **intentional divergence**: vendored uses a compound API (`Table`, `Table.Caption`, `Table.Head`, `Table.Body`, `Table.Row`, `Table.HeaderCell`, `Table.Cell`) instead of the upstream `RenderTable` / `TBL` utility; same semantics, more idiomatic, single file |
| Field | [`field.md`](field.md) | `@fpkit/acss@6.5.0` | New — promoted from `form.md`; small label+control wrapper with required `labelFor` (compile-time accessible-name guarantee). Doesn't render error/hint text — that's the wrapped control's job |
| Input | [`input.md`](input.md) | `@fpkit/acss@6.5.0` | New — promoted from `form.md`; full validation state surface (`validationState`, `errorMessage`, `hintText` with auto-generated `aria-describedby` ids) plus inlined `useDisabledState` / `resolveDisabledState` matching the Button vendoring pattern |
| Checkbox | [`checkbox.md`](checkbox.md) | `@fpkit/acss@6.5.0` | New — promoted from `form.md`; thin wrapper over `Input` with boolean `onChange` API, size presets (xs/sm/md/lg via `data-checkbox-size`), and a dev-only controlled/uncontrolled mode-flip warning |
| Icon | [`icon.md`](icon.md) | `@fpkit/acss@6.5.0` | Promoted from inline catalog entry — **intentional divergence**: vendored uses a `name` prop dispatching to a built-in 9-icon SVG set (info, success, warning, error, close, chevron-down, chevron-right, check, external-link), instead of upstream's polymorphic span hosting 30+ externally-imported icon components. Self-contained; covers the icons the kit-builder components consume internally |
| Link | [`link.md`](link.md) | `@fpkit/acss@6.5.0` | Promoted from inline catalog entry — preserves upstream's automatic `rel="noopener noreferrer"` security defaults for `target="_blank"` (with user-rel-token merging) and `prefetch` hint. Drops upstream `IconLink` / `LinkButton` compound subcomponents (trivial enough to add inline if needed) |
| List | [`list.md`](list.md) | `@fpkit/acss@6.5.0` | Promoted from inline catalog entry — preserves upstream compound API (`List` + `List.ListItem`), supports ul/ol/dl variants with appropriate item types (li/dt/dd). Documents the Safari/VoiceOver `list-style: none` gotcha and the `role="list"` workaround |
| Form | `skills/component-form/SKILL.md` | `@fpkit/acss@6.5.0` | **Promoted to skill (pilot)** — the only per-component skill in v0.2.0. `references/components/form.md` is retained as a legacy bundled reference; the skill at `skills/component-form/SKILL.md` is the going-forward source. Composes `Field` + `Input` + `Checkbox`. Cross-plugin invocation from `acss-app-builder`'s `/app-form` command via the Skill tool |
| UI (foundation) | [`foundation.md`](foundation.md) | `@fpkit/acss@6.5.0` | Documented at canonical shape — **but `assets/foundation/ui.tsx` remains the verbatim-copied source** that `/kit-add` ships at first run. The markdown spec captures the polymorphic forwardRef pattern and the `as unknown as UIComponent` double-cast (load-bearing — see foundation.md). Phase 0 audit found `acss-component-specs/skills/.../frameworks/react.md` also depends on `assets/foundation/ui.tsx`; the file is preserved until that cross-plugin coordination is complete |

Components not yet listed have not been verified against fpkit source under the new canonical shape; their existing reference doc content remains usable as the legacy generation guide.

---

## Badge

Status indicator for displaying counts or labels.

**Generation Contract:**
```
export_name: Badge
file: badge.tsx + badge.scss
imports: UI from '../ui'
dependencies: []
```

**Key Props:**
```tsx
type BadgeProps = {
  children?: React.ReactNode
  variant?: 'rounded'  // Circular badge
} & React.ComponentPropsWithoutRef<'sup'>
```

**Key Pattern:** Nested `<sup><span>` structure required by SCSS architecture:
```tsx
<UI as="sup" data-badge={variant} role="status" {...props}>
  <UI as="span">{children}</UI>
</UI>
```

**CSS Variables:**
```scss
--badge-bg: var(--color-surface-subtle, #e9ecef);
--badge-color: var(--color-text, #212529);
--badge-fs: 0.75rem;
--badge-fw: 600;
--badge-padding-inline: 0.375rem;
--badge-padding-block: 0.125rem;
--badge-radius: 0.25rem;
--badge-rounded-size: 1.5625rem;  // Fixed size for circular variant
```

**Usage:**
```tsx
<Badge aria-label="3 unread messages">3</Badge>
<Badge variant="rounded" aria-label="99+ notifications">99+</Badge>
```

---

## Tag

Categorical label with optional dismissal.

**Generation Contract:**
```
export_name: Tag
file: tag.tsx + tag.scss
imports: UI from '../ui'
dependencies: []
```

**Key Props:**
```tsx
type TagProps = {
  children?: React.ReactNode
  onRemove?: () => void   // Shows remove button if provided
  variant?: 'outlined'
} & React.ComponentPropsWithoutRef<'span'>
```

**CSS Variables:**
```scss
--tag-bg: var(--color-surface-subtle, #e9ecef);
--tag-color: var(--color-text, #212529);
--tag-fs: 0.8125rem;
--tag-fw: 500;
--tag-padding-inline: 0.5rem;
--tag-padding-block: 0.25rem;
--tag-radius: 0.25rem;
--tag-gap: 0.25rem;
--tag-border: 1px solid transparent;
--tag-outlined-border: 1px solid currentColor;
```

**Usage:**
```tsx
<Tag>Design</Tag>
<Tag variant="outlined" onRemove={() => removeTag('react')}>React</Tag>
```

---

## Heading

Semantic headings with consistent styling.

**Generation Contract:**
```
export_name: Heading
file: heading.tsx + heading.scss
imports: UI from '../ui'
dependencies: []
```

**Key Props:**
```tsx
type HeadingProps = {
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'  // default: h2
  children?: React.ReactNode
  variant?: 'display' | 'title' | 'subtitle'
} & React.ComponentPropsWithoutRef<'h2'>
```

**CSS Variables:**
```scss
--h1-fs: 2.5rem;
--h2-fs: 2rem;
--h3-fs: 1.75rem;
--h4-fs: 1.5rem;
--h5-fs: 1.25rem;
--h6-fs: 1rem;
--heading-fw: 700;
--heading-line-height: 1.2;
--heading-color: var(--color-text, inherit);
--heading-margin-block-end: 0.5rem;
```

**Usage:**
```tsx
<Heading as="h1">Page Title</Heading>
<Heading as="h2" variant="display">Hero Heading</Heading>
```

---

## Text / Paragraph

Text with variants for body, caption, and inline use.

**Generation Contract:**
```
export_name: Text
file: text.tsx + text.scss
imports: UI from '../ui'
dependencies: []
```

**Key Props:**
```tsx
type TextProps = {
  as?: 'p' | 'span' | 'div' | 'strong' | 'em' | 'small'  // default: p
  variant?: 'body' | 'caption' | 'small' | 'lead'
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'p'>
```

**CSS Variables:**
```scss
--text-fs: 1rem;
--text-fw: 400;
--text-line-height: 1.6;
--text-color: var(--color-text, inherit);
--text-margin-block-end: 1rem;
--text-caption-fs: 0.8125rem;
--text-caption-color: var(--color-text-subtle, #757575);
--text-lead-fs: 1.25rem;
--text-lead-fw: 300;
--text-small-fs: 0.875rem;
```

---

## Link

Accessible anchor with proper states.

**Generation Contract:**
```
export_name: Link
file: link.tsx + link.scss
imports: UI from '../ui'
dependencies: []
```

**Key Props:**
```tsx
type LinkProps = {
  href: string
  children?: React.ReactNode
  external?: boolean   // Adds target="_blank" + rel="noopener noreferrer"
  variant?: 'default' | 'subtle' | 'button'
} & React.ComponentPropsWithoutRef<'a'>
```

**Key Pattern:**
```tsx
<UI
  as="a"
  href={href}
  target={external ? '_blank' : undefined}
  rel={external ? 'noopener noreferrer' : undefined}
  {...props}
>
  {children}
  {external && <span aria-hidden="true"> ↗</span>}
  {external && <span className="sr-only">(opens in new tab)</span>}
</UI>
```

**CSS Variables:**
```scss
--link-color: var(--color-primary, #0066cc);
--link-hover-color: var(--color-primary-dark, #0052a3);
--link-visited-color: #551a8b;
--link-text-decoration: underline;
--link-hover-text-decoration: none;
--link-focus-outline: 2px solid currentColor;
--link-focus-outline-offset: 2px;
--link-subtle-color: var(--color-text, inherit);
--link-subtle-hover-color: var(--color-primary, #0066cc);
```

---

## List

Styled ordered or unordered list with variants.

**Generation Contract:**
```
export_name: List (compound: List.Item)
file: list.tsx + list.scss
imports: UI from '../ui'
dependencies: []
```

**Key Props:**
```tsx
type ListProps = {
  type?: 'ul' | 'ol'     // default: ul
  'data-list'?: string   // 'unstyled' | 'inline' | 'unstyled block'
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'ul'>

type ListItemProps = {
  type?: 'li'
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'li'>
```

**CSS Variables:**
```scss
--list-padding-inline-start: 1.25rem;
--list-gap: 0.5rem;
--list-item-padding-block: 0.25rem;
--list-marker-color: var(--color-primary, #0066cc);
--list-inline-gap: 1rem;
```

---

## Details

Native collapsible disclosure with summary.

**Generation Contract:**
```
export_name: Details
file: details.tsx + details.scss
imports: UI from '../ui'
dependencies: []
```

**Key Props:**
```tsx
type DetailsProps = {
  summary: React.ReactNode   // Always required for accessibility
  children: React.ReactNode
  open?: boolean
} & React.ComponentPropsWithoutRef<'details'>
```

**CSS Variables:**
```scss
--details-border: 1px solid var(--color-border, #e0e0e0);
--details-radius: 0.375rem;
--details-padding: 1rem;
--details-summary-fw: 600;
--details-summary-cursor: pointer;
--details-summary-padding: 0.75rem 1rem;
--details-summary-marker-display: block;  // Custom marker positioning
```

**Usage:**
```tsx
<Details summary="Advanced Options">
  <p>These are the advanced settings...</p>
</Details>
```

---

## Progress

Native progress indicator.

**Generation Contract:**
```
export_name: Progress
file: progress.tsx + progress.scss
imports: UI from '../ui'
dependencies: []
```

**Key Props:**
```tsx
type ProgressProps = {
  value?: number        // 0-100 or 0 to max
  max?: number          // default: 100
  label?: string        // aria-label for screen readers
  showValue?: boolean   // Display percentage text
} & React.ComponentPropsWithoutRef<'progress'>
```

**CSS Variables:**
```scss
--progress-height: 0.5rem;
--progress-radius: 0.25rem;
--progress-bg: var(--color-surface-subtle, #e9ecef);
--progress-fill: var(--color-primary, #0066cc);
--progress-transition: width 0.3s ease;
```

**Usage:**
```tsx
<Progress value={65} label="Upload progress" showValue />
<Progress />  {/* Indeterminate loading state */}
```

---

## Icon

Inline SVG icon component. No SCSS — styles via props/className.

**Generation Contract:**
```
export_name: Icon
file: icon.tsx
imports: React (only)
dependencies: []
```

**Generated with a curated set of SVG icons. Default set:**
- `info`, `success`, `warning`, `error` (for Alert)
- `close` / `x` (for Dialog close button)
- `chevron-down`, `chevron-right` (for Details, Select)
- `external-link` (for Link)
- `check` (for Checkbox)

**Key Props:**
```tsx
type IconProps = {
  name: 'info' | 'success' | 'warning' | 'error' | 'close' | 'chevron-down' | 'chevron-right' | 'check' | 'external-link'
  size?: number    // SVG width/height in px (default: 16)
  color?: string   // currentColor by default
  'aria-hidden'?: boolean  // true for decorative icons
  'aria-label'?: string    // required for standalone (non-decorative) icons
} & React.SVGProps<SVGSVGElement>
```

**Pattern:**
```tsx
// Decorative icon (within text/button)
<Icon name="info" aria-hidden size={16} />

// Standalone icon (must have accessible name)
<Icon name="close" aria-label="Close dialog" size={20} />
```
