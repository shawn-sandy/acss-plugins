# App Architecture Reference

How `acss-app-builder` organizes a Vite+React+TS app.

## Folder layout after `/app-init`

```
<project-root>/
├── .acss-target.json              # { "componentsDir": "src/components/fpkit" } — committed
├── src/
│   ├── main.tsx                   # mutated once: sentinel-bounded theme imports appended
│   ├── app/
│   │   └── AppShell.tsx           # created by /app-layout
│   ├── pages/
│   │   └── <Page>.tsx             # created by /app-page
│   ├── styles/
│   │   └── theme/
│   │       ├── base.css           # created by /app-init
│   │       ├── light.css          # created by /app-theme light|both
│   │       └── dark.css           # created by /app-theme dark|both
│   ├── forms/                     # created by /app-form (on demand)
│   └── components/
│       └── fpkit/                 # populated by /kit-add (companion plugin)
```

## Entry-file mutation contract

`/app-init` appends a sentinel-bounded block to `src/main.tsx` (or the entry file located by `detect_vite_project.py`):

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'

// @acss-app-builder:begin theme imports
import './styles/theme/base.css'
// @acss-app-builder:end

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

**Rules:**

- The inserted block is bounded by `// @acss-app-builder:begin` and `// @acss-app-builder:end`.
- Insertion point: after the last line matching `^import .* from ['"].*['"];?$`.
- Re-runs locate and update the block in place; they do not create a second block.
- If no `import` statement is present, the command refuses (developer has a non-standard entry).

## Vite detection

`detect_vite_project.py` confirms Vite by:

1. `vite` present in `package.json` dependencies or devDependencies.
2. A `vite.config.(ts|js|mjs)` at project root (preferred) OR an `index.html` at project root with `<script type="module" src="/src/main.tsx">`.
3. Entry file is read from the `index.html` `<script src>` attribute — never assumed.

## Monorepo project root

Project root = nearest ancestor directory containing a `package.json` where `react` appears in `dependencies` or `devDependencies`. `.acss-target.json` is written there.

## What `/app-init` does NOT do

- It does **not** configure path aliases (`@/`). All generated imports are relative.
- It does **not** install `@fpkit/acss`. Run `npm i @fpkit/acss` or `/kit-add <component>` separately.
- It does **not** add Storybook, tests, or routing. v0.1 scope is minimal.
