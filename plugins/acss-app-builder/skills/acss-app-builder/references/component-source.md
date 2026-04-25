# Component Source Detection

The critical shared logic every command depends on. Determines where to import fpkit components FROM.

> **Compatibility ceiling — `@fpkit/acss@6.6.0`** *(captured at acss-app-builder v0.2.0 release)*
>
> The `npm` resolution path is **deprecated as of v0.2.0**. Projects on the npm path keep working through a soft-deprecation window — `detect_component_source.py` continues returning `source: "npm"` and exits 0 — but the JSON output now includes `"deprecated": true` and `"sunsetVersion": "6.6.0"`. Slash commands surface a one-line migration suggestion in chat when the deprecation flag is set. The npm path is scheduled for removal in a future major release; use `/kit-add` (acss-kit-builder) to vendor components into the project before then.

## Resolution order

`detect_component_source.py` returns one of three states. The first matching state wins:

1. **`generated`** *(preferred)* — `<componentsDir>/ui.tsx` exists locally. **Wins on tie** even if `@fpkit/acss` is also installed.
2. **`npm`** *(deprecated)* — `@fpkit/acss` in `dependencies` or `devDependencies` of the nearest `package.json`. Returns deprecation flags in the JSON output.
3. **`none`** — neither present. Command halts and prints install hints (recommending `/kit-add` over `npm install @fpkit/acss`).

`<componentsDir>` is read from `.acss-target.json` at project root, falling back to `src/components/fpkit` on first run.

## Import maps

### `source=generated`

Relative imports, one component per statement. No path aliases.

```tsx
import Button from '../components/fpkit/button/button'
import Card from '../components/fpkit/cards/card'
import Link from '../components/fpkit/link/link'
```

Every generated file imports its own SCSS:

```tsx
import '../components/fpkit/button/button.scss'
```

### `source=npm` *(deprecated; legacy reference only)*

This path is preserved for projects that haven't yet migrated to vendored components. It will be removed in a future major release. Prefer `source=generated` via `/kit-add`.

Named imports from the package:

```tsx
import { Button, Card, Link } from '@fpkit/acss'
import '@fpkit/acss/styles'
```

## Verified exports (authoritative: [`packages/fpkit/src/index.ts`](https://github.com/shawn-sandy/acss/blob/main/packages/fpkit/src/index.ts))

Do not invent imports. The package CLAUDE.md is out of date — `src/index.ts` is the source of truth.

| Category | Exported names |
|---|---|
| Buttons | `Button`, `IconButton` |
| Cards | `Card`, `CardTitle`, `CardContent`, `CardFooter` |
| Alert | `Alert` |
| Forms | `Field`, `Input`, `Checkbox` |
| Icons | `Icon`, `Img` |
| Link | `Link` (default export) |
| List | `List` (default export) |
| Modal/Dialog | `Modal`, `Dialog`, `DialogModal`, `Popover` |
| Table | `TBL` (alias of `RenderTable`) |

**Do NOT import:** `FieldLabel`, `FieldInput`, `FieldTextarea`, `Select`, `Textarea`, `Table`, `Header`, `Main`, `Footer`, `Aside`, `Nav`. These are either not exported by name or only exported from secondary entry points.

For layout landmarks, use the **polymorphic `UI`** component with an `as` prop (when source is generated) or the exported landmarks from a layout sub-module (verify before importing).

## Template substitution

Templates in `assets/` use `{{IMPORT_SOURCE:Button,Card,Link}}` at the top. Before writing the target file, the workflow:

1. Parses the token's comma-separated component list.
2. For each component, looks it up in the active import map.
3. Replaces the token with real import statements (one per component for `generated`, one combined statement for `npm`).
4. For `generated`, also emits the matching SCSS imports.

## Tie-break rationale

When both sources are present (a developer has `@fpkit/acss` installed AND ran `/kit-add` to generate local copies), the generated source wins. This matches the intent of `acss-kit-builder`: developer-owned code should not be silently bypassed by a package dependency.

## Error state

When `source="none"`:

```
Neither @fpkit/acss nor generated components were detected.

Recommended:
  /kit-add <component>       (uses the acss-kit-builder plugin to generate local copies)

Legacy (deprecated; sunsetting in a future major release):
  npm install @fpkit/acss

Then re-run this command.
```

Never fall back silently. Never import from a path that does not exist.

## Deprecation flag handling

When `detect_component_source.py` returns JSON with `"deprecated": true` (i.e. the project is on the npm path), every slash command that consumes the script should append a single-line migration nudge in chat after generating the requested artifact:

```
Note: this project still uses the @fpkit/acss npm path (deprecated;
sunset in <sunsetVersion>). Run /kit-add to vendor components.
```

This keeps the deprecation visible to users actually running commands without breaking generation. The script never writes to stderr — strict JSON-stdout-only contract per the project Python script convention.
