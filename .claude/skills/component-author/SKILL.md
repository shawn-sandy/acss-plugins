---
name: component-author
description: Scaffold a new component reference doc for the acss-kit plugin in the canonical embedded-markdown shape. Use when the maintainer asks to add a new component to acss-kit, create a new reference doc under references/components, or scaffold a component spec like Tabs, Toast, Tooltip.
disable-model-invocation: false
---

# /component-author

Usage: `/component-author <component-name>`

Example: `/component-author tabs`

Scaffolds `plugins/acss-kit/skills/components/references/components/<component-name>.md` with all nine canonical sections and adds a placeholder row to the catalog. Does NOT implement the TSX/SCSS — the maintainer fills those in after consulting the upstream fpkit source.

## Steps

1. **Validate inputs.**
   - `<component-name>` must be lowercase kebab-case (alphanumeric + hyphens).
   - Refuse if `plugins/acss-kit/skills/components/references/components/<component-name>.md` already exists.
   - Refuse if a row matching the component already appears in `catalog.md` "Verification Status".

2. **Capture the fpkit ref via AskUserQuestion.**
   Ask the maintainer for the fpkit version this reference will be verified against. Default to the most-common existing ceiling — read the verification banner of `plugins/acss-kit/skills/components/references/components/button.md` (line ~3) and offer that as the default option (currently `@fpkit/acss@6.5.0`). Capture the answer as `<ref>` for the banner and as `<tag-or-sha>` for any GitHub URLs in the body.

3. **Capture intentional divergences via AskUserQuestion.**
   Ask whether this component will diverge from upstream in any documented way (inlined hooks, simplified compound API, dropped subcomponents, etc.). Default: "none". Capture as `<divergences>`. The verification banner is load-bearing for future maintainers — if there are no divergences, write "none" rather than leaving the field empty.

4. **Write the reference doc skeleton** to `plugins/acss-kit/skills/components/references/components/<component-name>.md`. Outer fence uses 4 backticks so the inner triple-backtick blocks render correctly:

    ````markdown
    # Component: <PascalCaseName>

    > **Verified against fpkit source:** `<ref>`. Intentional divergences from upstream: <divergences>.

    ## Overview

    <One-paragraph summary of the component's purpose. Note key WCAG patterns it addresses.>

    ## Generation Contract

    ```
    export_name: <PascalCaseName>
    file: <component-name>.tsx
    scss: <component-name>.scss
    imports: UI from '../ui'
    dependencies: []
    ```

    ## Props Interface

    ```tsx
    export type <PascalCaseName>Props = {
      children?: React.ReactNode
      // TODO: copy props from fpkit source at <ref>
    } & React.ComponentPropsWithoutRef<'div'>
    ```

    ## TSX Template

    ```tsx
    // TODO: copy from https://github.com/shawn-sandy/acss/blob/<tag-or-sha>/packages/fpkit/src/components/<component-name>/<component-name>.tsx
    import React from 'react'
    import UI from '../ui'

    export default function <PascalCaseName>({ children, ...rest }: <PascalCaseName>Props) {
      return <UI as="div" {...rest}>{children}</UI>
    }
    ```

    ## CSS Variables

    ```scss
    // CSS custom properties this component reads
    // --<component-name>-bg
    // --<component-name>-color
    // (extend with the full variable list)
    ```

    ## SCSS Template

    ```scss
    // TODO: copy from https://github.com/shawn-sandy/acss/blob/<tag-or-sha>/packages/fpkit/src/components/<component-name>/<component-name>.scss
    .<component-name> {
      background: var(--<component-name>-bg, transparent);
      color: var(--<component-name>-color, currentColor);
    }
    ```

    ## Accessibility

    - Keyboard interaction: <TODO>
    - ARIA: <TODO>
    - Focus management: <TODO>
    - Target size: <TODO>
    - Color contrast: <TODO>
    - WCAG 2.2 AA criteria addressed: <TODO>

    ## Usage Examples

    ```tsx
    import <PascalCaseName> from './<component-name>/<component-name>'
    import './<component-name>/<component-name>.scss'

    <<PascalCaseName>>Hello</<PascalCaseName>>
    ```
    ````

   Substitute `<component-name>`, `<PascalCaseName>`, `<ref>`, `<tag-or-sha>`, and `<divergences>` at write time. Leave every `TODO:` marker for the maintainer to fill in. The Usage Examples import path uses `./<component-name>/<component-name>` to match the convention in existing reference docs (e.g. `button.md`, `alert.md`) — the `src/components/fpkit/` portion is the project-level path the developer chose during `/kit-add` initialization, not part of the relative import.

5. **Add a row to `catalog.md` Verification Status.**
   Read `plugins/acss-kit/skills/components/references/components/catalog.md`. Find the "Verification Status" table and append a row before the next section header:

   ```
   | <PascalCaseName> | [`<component-name>.md`](<component-name>.md) | `<ref>` | New — pending fpkit verification |
   ```

   Preserve existing rows and table alignment.

6. **Run the reviewer agent.**
   Invoke the `component-reference-reviewer` agent against the new file. Expected outcome on a fresh skeleton: all checks PASS except possibly TSX Template imports (the placeholder uses only React + `'../ui'`, which should pass). Surface the agent's report inline.

7. **Print a summary.**
   - Files created: `<component-name>.md`
   - Files modified: `catalog.md`
   - Reminders:
     - Resolve every `TODO:` placeholder before committing.
     - If the component has dependencies (e.g. wraps Button), update the `dependencies:` field in the Generation Contract.
     - Re-run `/review-component <path>` after filling in the TSX/SCSS templates.
     - Update the catalog row's Status column from "New — pending fpkit verification" to "Verified" after the maintainer confirms parity.

Do not write the TSX or SCSS implementation — those come from the upstream fpkit source at the captured ref. The maintainer fills them in.
