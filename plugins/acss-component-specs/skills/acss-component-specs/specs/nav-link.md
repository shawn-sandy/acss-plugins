---
format_version: 1
name: nav-link
display_name: Nav.Link
description: Navigation link sub-component. Native <a> element. aria-current="page" marks active state.
fpkit_source: https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/components/navs/nav.tsx
fpkit_version: main
component_type: layout
parent: nav
maps_to_parent: compound-part
a11y:
  wcag: ['2.4.4']
  accessible_name: children text content or aria-label for icon-only links
props:
  - name: href
    type: string
    required: true
    maps_to: prop
    description: Link destination URL
  - name: active
    type: boolean
    required: false
    maps_to: aria
    aria_attr: aria-current
    description: Marks current page link. Sets aria-current="page" (WCAG 2.4.4).
  - name: children
    type: React.ReactNode
    required: false
    maps_to: prop
    description: Link text content — provides accessible name
  - name: as
    type: React.ElementType
    required: false
    maps_to: element
    default: a
    description: Root element (use for router Link integration)
  - name: classes
    type: string
    required: false
    maps_to: class
    description: CSS class names
events:
  - name: onClick
    type: "React.MouseEventHandler<HTMLAnchorElement>"
framework_notes:
  react:
    strategy: Emitted inside nav.tsx as NavLink sub-component. Attached as Nav.Link.
    dependencies: [ui.tsx]
    caveats: For React Router integration, pass as={Link} and to={href}. aria-current="page" when active.
  html:
    strategy: Native <a> inside <nav>.
    dependencies: []
    caveats: ""
  astro:
    strategy: Separate NavLink.astro file alongside Nav.astro.
    dependencies: [nav.scss]
    caveats: ""
css_vars: []
theme_dependencies: []
---

## Notes

Nav.Link is emitted inside `nav.tsx` (React) or as `NavLink.astro` (Astro). Not a standalone file in React output.

`active` prop sets `aria-current="page"` — the correct attribute for current-page links (WCAG 2.4.4, SC: "Link Purpose").
