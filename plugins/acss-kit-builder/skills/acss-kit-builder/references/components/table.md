# Component: Table

> **Verified against fpkit source:** `@fpkit/acss@6.5.0` (closest tagged ref to npm `6.6.0`). **Intentional divergence**: upstream exports `Table` plus a `RenderTable` (displayName `TBL`) helper and `RenderHead` / `RenderBody` utilities, with the table-element primitives (`Caption`, `Thead`, `Tbody`, `Tr`) split into a sibling `table-elements.tsx` file. The vendored version consolidates everything into a single `table.tsx` and exposes a compound API (`Table`, `Table.Caption`, `Table.Head`, `Table.Body`, `Table.Row`, `Table.HeaderCell`, `Table.Cell`) — same semantics as the upstream primitives, more idiomatic than the `RenderTable` utility, and self-contained.

## Overview

A semantic HTML table wrapper with compound sub-components. Renders native `<table>` / `<caption>` / `<thead>` / `<tbody>` / `<tr>` / `<th>` / `<td>` elements via the kit-builder polymorphic `UI` component. Carries no opinion on virtualization, sorting, filtering, or pagination — those are application concerns. Use this for the static structural and accessibility scaffolding; layer behaviour on top.

## Generation Contract

```
export_name: Table (compound: Table.Caption, Table.Head, Table.Body, Table.Row, Table.HeaderCell, Table.Cell)
file: table.tsx
scss: table.scss
imports: UI from '../ui'
dependencies: []
```

All sub-components live in the same `table.tsx` file via `Object.assign`, matching the Card and Dialog compound pattern.

## Props Interface

```tsx
export type TableProps = {
  /** Optional accessible name for the table — alternative to <caption> */
  'aria-label'?: string
  /** Optional accessible name reference — alternative to <caption> */
  'aria-labelledby'?: string
  classes?: string
  styles?: React.CSSProperties
  children?: React.ReactNode
} & React.ComponentPropsWithoutRef<'table'>

export type TableCaptionProps = React.ComponentPropsWithoutRef<'caption'>
export type TableHeadProps = React.ComponentPropsWithoutRef<'thead'>
export type TableBodyProps = React.ComponentPropsWithoutRef<'tbody'>
export type TableRowProps = React.ComponentPropsWithoutRef<'tr'>
export type TableHeaderCellProps = React.ComponentPropsWithoutRef<'th'> & {
  /** Required when scope cannot be inferred from position */
  scope?: 'col' | 'row' | 'colgroup' | 'rowgroup'
}
export type TableCellProps = React.ComponentPropsWithoutRef<'td'>
```

## TSX Template

```tsx
import UI from '../ui'
import React from 'react'

const TableCaption = ({ children, ...props }: TableCaptionProps) => (
  <UI as="caption" {...props}>{children}</UI>
)
TableCaption.displayName = 'Table.Caption'

const TableHead = ({ children, ...props }: TableHeadProps) => (
  <UI as="thead" {...props}>{children}</UI>
)
TableHead.displayName = 'Table.Head'

const TableBody = ({ children, ...props }: TableBodyProps) => (
  <UI as="tbody" {...props}>{children}</UI>
)
TableBody.displayName = 'Table.Body'

const TableRow = ({ children, ...props }: TableRowProps) => (
  <UI as="tr" {...props}>{children}</UI>
)
TableRow.displayName = 'Table.Row'

const TableHeaderCell = ({ scope = 'col', children, ...props }: TableHeaderCellProps) => (
  <UI as="th" scope={scope} {...props}>{children}</UI>
)
TableHeaderCell.displayName = 'Table.HeaderCell'

const TableCell = ({ children, ...props }: TableCellProps) => (
  <UI as="td" {...props}>{children}</UI>
)
TableCell.displayName = 'Table.Cell'

const TableRoot = ({ classes, styles, children, ...props }: TableProps) => (
  <UI
    as="table"
    classes={`table${classes ? ' ' + classes : ''}`}
    styles={styles}
    {...props}
  >
    {children}
  </UI>
)
TableRoot.displayName = 'Table'

type TableComponent = typeof TableRoot & {
  Caption: typeof TableCaption
  Head: typeof TableHead
  Body: typeof TableBody
  Row: typeof TableRow
  HeaderCell: typeof TableHeaderCell
  Cell: typeof TableCell
}

export const Table = Object.assign(TableRoot, {
  Caption: TableCaption,
  Head: TableHead,
  Body: TableBody,
  Row: TableRow,
  HeaderCell: TableHeaderCell,
  Cell: TableCell,
}) as TableComponent

export default Table
```

## CSS Variables

```scss
--table-bg: transparent;
--table-color: var(--color-text, inherit);
--table-border-collapse: collapse;
--table-width: 100%;

--table-caption-fs: 0.9375rem;
--table-caption-fw: 600;
--table-caption-padding-block: 0.5rem;
--table-caption-text-align: start;

--table-th-fs: 0.875rem;
--table-th-fw: 600;
--table-th-padding: 0.75rem 1rem;
--table-th-bg: var(--color-surface-subtle, #f5f5f5);
--table-th-border-bottom: 2px solid var(--color-border, #e0e0e0);
--table-th-text-align: start;

--table-td-fs: 0.9375rem;
--table-td-padding: 0.75rem 1rem;
--table-td-border-bottom: 1px solid var(--color-border, #e0e0e0);

--table-row-hover-bg: var(--color-surface-subtle, #f9f9f9);
```

## SCSS Template

```scss
// table.scss
.table {
  width: var(--table-width, 100%);
  border-collapse: var(--table-border-collapse, collapse);
  background: var(--table-bg, transparent);
  color: var(--table-color, inherit);

  caption {
    caption-side: top;
    font-size: var(--table-caption-fs, 0.9375rem);
    font-weight: var(--table-caption-fw, 600);
    padding-block: var(--table-caption-padding-block, 0.5rem);
    text-align: var(--table-caption-text-align, start);
  }

  th {
    font-size: var(--table-th-fs, 0.875rem);
    font-weight: var(--table-th-fw, 600);
    padding: var(--table-th-padding, 0.75rem 1rem);
    background: var(--table-th-bg, #f5f5f5);
    border-bottom: var(--table-th-border-bottom, 2px solid #e0e0e0);
    text-align: var(--table-th-text-align, start);
  }

  td {
    font-size: var(--table-td-fs, 0.9375rem);
    padding: var(--table-td-padding, 0.75rem 1rem);
    border-bottom: var(--table-td-border-bottom, 1px solid #e0e0e0);
  }

  tbody tr:hover {
    background: var(--table-row-hover-bg, #f9f9f9);
  }
}
```

## Accessibility

WCAG 2.2 AA compliance for the generated `Table` component.

**Accessible name (required)**
- Always give a data table an accessible name. Use one of:
  - `<Table.Caption>` as the first child of `<Table>` — the most semantically rich option, visible to all users.
  - `aria-label="..."` on the table when a caption would be redundant with surrounding heading text.
  - `aria-labelledby="heading-id"` to point at an existing heading near the table.
- The compound API does not enforce one of these; authoring guidance is critical. Code review should reject tables without an accessible name.

**Header cells & scope**
- `<Table.HeaderCell>` defaults `scope="col"` since column headers are the most common case. Pass `scope="row"` for row headers.
- For complex tables with both row and column headers, set `scope` explicitly on each header cell. The default may be wrong for spanning headers — use `scope="colgroup"` / `scope="rowgroup"` for spans, or `headers="id1 id2"` on body cells when scope alone can't disambiguate.
- Avoid using styled `<td>` cells for header content. Screen readers rely on `<th scope="...">` to announce "column X" / "row Y" context as the user navigates cells.

**Native semantics — do not override**
- Don't add `role="grid"` unless you're building a fully-interactive grid (cell-level navigation, editing, multi-select). For static or read-only tables, native `<table>` semantics are exactly right; ARIA grid would *reduce* accessibility by overriding the simpler native behaviour.
- Don't add `role="presentation"` to remove table semantics for layout — use CSS for layout (Flexbox, Grid). Layout tables defeat AT navigation.

**Layout & responsiveness**
- Wide tables on narrow viewports: prefer horizontal scrolling (`overflow-x: auto` on a wrapper) over collapsing rows into cards. Scrolling preserves the row-column relationship that AT users rely on.
- Don't use `display: block` / `flex` / `grid` on `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>` — it strips the implicit table semantics in some screen readers.

**Color contrast**
- Header text at `--table-th-fs` on `--table-th-bg` must meet 4.5:1 (or 3:1 if the text is large per WCAG 1.4.3).
- Body text at `--table-td-fs` on `--table-bg` must meet 4.5:1.
- Row hover background (`--table-row-hover-bg`) must keep body-text contrast above 4.5:1.
- Border at `--table-td-border-bottom` provides row separation; in dense tables it must meet 3:1 against the surrounding cell background (WCAG 1.4.11) when borders are the sole visual separation.

**Keyboard / focus**
- Static tables don't have keyboard interaction beyond browser-provided text selection.
- If body cells contain interactive content (links, buttons), they receive native focus order and `:focus-visible` from those elements' own styles — no table-level intervention needed.

**WCAG 2.2 AA criteria addressed**
- 1.3.1 Info and Relationships (native table semantics + `scope` on header cells)
- 1.4.3 Contrast Minimum (text and headers)
- 1.4.11 Non-text Contrast (row separator borders when sole indicator)
- 2.4.6 Headings and Labels (via `<Table.Caption>` or `aria-label[ledby]`)
- 4.1.2 Name, Role, Value (native table + accessible name)

## Usage Examples

```tsx
import Table from './table/table'
import './table/table.scss'

// Basic data table with caption
<Table>
  <Table.Caption>Quarterly revenue, 2024</Table.Caption>
  <Table.Head>
    <Table.Row>
      <Table.HeaderCell>Quarter</Table.HeaderCell>
      <Table.HeaderCell>Revenue</Table.HeaderCell>
      <Table.HeaderCell>YoY change</Table.HeaderCell>
    </Table.Row>
  </Table.Head>
  <Table.Body>
    <Table.Row>
      <Table.HeaderCell scope="row">Q1</Table.HeaderCell>
      <Table.Cell>$1.2M</Table.Cell>
      <Table.Cell>+5%</Table.Cell>
    </Table.Row>
    <Table.Row>
      <Table.HeaderCell scope="row">Q2</Table.HeaderCell>
      <Table.Cell>$1.4M</Table.Cell>
      <Table.Cell>+18%</Table.Cell>
    </Table.Row>
  </Table.Body>
</Table>

// Accessible name via aria-labelledby (when caption duplicates a nearby heading)
<>
  <h2 id="users-heading">Active users</h2>
  <Table aria-labelledby="users-heading">
    <Table.Head>
      <Table.Row>
        <Table.HeaderCell>Name</Table.HeaderCell>
        <Table.HeaderCell>Email</Table.HeaderCell>
      </Table.Row>
    </Table.Head>
    <Table.Body>
      <Table.Row>
        <Table.Cell>Alice</Table.Cell>
        <Table.Cell>alice@example.com</Table.Cell>
      </Table.Row>
    </Table.Body>
  </Table>
</>

// Wide table, scrollable wrapper
<div style={{ overflowX: 'auto' }}>
  <Table>
    {/* ...many columns... */}
  </Table>
</div>
```
