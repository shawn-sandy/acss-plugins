// Render generated kit components to static HTML for axe-core inspection.
//
// Bundles each component with esbuild (stubbing SCSS/CSS imports) and
// renders it via react-dom/server's renderToStaticMarkup. Output: one
// .html file per component under <outDir>.
//
// The component prop fixtures live in DEFAULT_PROPS below — they're
// minimal-but-realistic invocations meant to produce representative HTML
// (a button with text, an input with a label, etc.). Components not listed
// are skipped with a warning rather than failing the run, so adding a new
// component to the catalog doesn't immediately break this harness; the
// maintainer adds a fixture entry when they want a11y coverage.
//
// CLI:
//   node tests/lib/render_components.mjs <componentsDir> <outDir>
//
//   componentsDir: absolute path to the sandbox's components folder
//                  (e.g. tests/sandbox/src/components/fpkit). Must contain
//                  ui.tsx and one subdirectory per generated component
//                  (e.g. button/button.tsx, link/link.tsx).
//   outDir:        absolute path to write rendered .html files into.
//                  Created if missing.

import { mkdirSync, writeFileSync, readdirSync, statSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { build } from 'esbuild'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'

const HERE = dirname(fileURLToPath(import.meta.url))

// Fixture: how each component should be invoked for the render check. Keep
// to minimal, semantically valid invocations — the goal is realistic HTML
// that exercises the component's accessible-name and ARIA story, not full
// prop coverage.
const DEFAULT_PROPS = {
  button: { children: 'Save' },
  link: { children: 'Read more', href: '#' },
  input: { 'aria-label': 'Search', type: 'text', name: 'q' },
  // checkbox/radio/etc. are added when their component fixtures are
  // verified to render meaningful HTML in jsdom.
}

// esbuild plugin: turn `*.scss` / `*.css` imports into no-op stubs so we
// can bundle component TSX without resolving the styles.
const cssStubPlugin = {
  name: 'css-stub',
  setup(b) {
    b.onResolve({ filter: /\.(scss|css)$/ }, (args) => ({
      path: args.path,
      namespace: 'css-stub',
    }))
    b.onLoad({ filter: /.*/, namespace: 'css-stub' }, () => ({
      contents: 'export default {}',
      loader: 'js',
    }))
  },
}

async function bundleAndImport(entryPath) {
  const result = await build({
    entryPoints: [entryPath],
    bundle: true,
    write: false,
    platform: 'node',
    format: 'esm',
    target: 'es2022',
    jsx: 'automatic',
    plugins: [cssStubPlugin],
    external: ['react', 'react-dom', 'react-dom/server'],
    logLevel: 'silent',
  })
  const code = result.outputFiles[0].text
  // Write to a temp file with .mjs so dynamic import treats it as ESM,
  // then load. Using a data URL would skip the disk hop but jsdom/jest
  // historically wobble on import.meta in data URLs.
  const tmpPath = join(HERE, '.tmp-bundle.mjs')
  writeFileSync(tmpPath, code)
  const mod = await import(pathToFileURL(tmpPath).href + `?cb=${Date.now()}`)
  return mod
}

function findComponentEntries(componentsDir) {
  const entries = []
  for (const child of readdirSync(componentsDir)) {
    const childPath = join(componentsDir, child)
    if (!statSync(childPath).isDirectory()) continue
    const tsxPath = join(childPath, `${child}.tsx`)
    try {
      if (statSync(tsxPath).isFile()) {
        entries.push({ name: child, entry: tsxPath })
      }
    } catch {
      // No top-level <name>.tsx — skip silently. Compound files (e.g.
      // form/input.tsx alongside form/textarea.tsx) need explicit fixtures.
    }
  }
  return entries
}

async function main() {
  const [, , componentsDir, outDir] = process.argv
  if (!componentsDir || !outDir) {
    console.error('Usage: render_components.mjs <componentsDir> <outDir>')
    process.exit(2)
  }

  mkdirSync(outDir, { recursive: true })

  const entries = findComponentEntries(componentsDir)
  if (entries.length === 0) {
    console.error(`No components found under ${componentsDir}`)
    process.exit(1)
  }

  const rendered = []
  const skipped = []
  for (const { name, entry } of entries) {
    const props = DEFAULT_PROPS[name]
    if (!props) {
      skipped.push(name)
      continue
    }
    const mod = await bundleAndImport(entry)
    const Component = mod.default ?? mod[Object.keys(mod)[0]]
    if (typeof Component !== 'function' && typeof Component !== 'object') {
      console.error(`  ${name}: no default export, skipping`)
      continue
    }
    const html = renderToStaticMarkup(React.createElement(Component, props))
    const wrapped =
      `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${name}</title></head>` +
      `<body><main>${html}</main></body></html>`
    const outPath = join(outDir, `${name}.html`)
    writeFileSync(outPath, wrapped)
    rendered.push(outPath)
  }

  console.log(`rendered ${rendered.length} component(s) to ${outDir}`)
  if (skipped.length > 0) {
    console.log(`skipped (no fixture): ${skipped.join(', ')}`)
  }
  for (const p of rendered) process.stdout.write(`${p}\n`)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
