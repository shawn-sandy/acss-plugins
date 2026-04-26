#!/usr/bin/env node
// Extract TSX/SCSS from acss-kit reference docs into tests/.tmp/extracted/
// and validate the extracted TSX with TypeScript's parser API.
//
// What this validates:
//   - Reference docs have the required sections (TSX Template + SCSS Template
//     unless the component is in COMPONENTS_WITHOUT_SCSS).
//   - Extracted TSX has no banned imports (e.g. @fpkit/acss).
//   - Every import resolves to react or a relative path.
//   - Extracted TSX parses successfully via ts.createSourceFile.
//
// What this does NOT validate (deliberately):
//   - Full type resolution. The reference docs split TSX across Key Pattern
//     sections that contain illustrative JSX or inline-only snippets (e.g.
//     destructuring of `props` outside a function body). Trying to assemble
//     a fully type-checking module fights the markdown's documentary
//     structure. Syntax-level validation catches what regex can't (malformed
//     JSX, broken generics, unclosed strings) without that fight.

import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createRequire } from 'node:module'

import { extractFromFile } from '../plugins/acss-kit/scripts/lib/extract.mjs'

const requireCjs = createRequire(import.meta.url)

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = resolve(__dirname, '..')
const REFS_DIR = join(
  REPO_ROOT,
  'plugins/acss-kit/skills/components/references/components',
)
const TMP_DIR = join(REPO_ROOT, 'tests/.tmp/extracted')
const FIXTURES = join(REPO_ROOT, 'tests/fixtures/component-vars.json')

// Components that legitimately ship without their own SCSS file:
//   - icon: pure SVG dispatcher, no styles
//   - foundation: polymorphic UI base, prose-only SCSS section
//   - form: composes Field/Input/Checkbox; styling lives in those components
const COMPONENTS_WITHOUT_SCSS = new Set(['icon', 'foundation', 'form'])
const BANNED_IMPORTS = [/@fpkit\/acss/]
const ALLOWED_IMPORT_PREFIXES = [/^react$/, /^\.\.?\//]

function loadVars() {
  if (!existsSync(FIXTURES)) return {}
  return JSON.parse(readFileSync(FIXTURES, 'utf8'))
}

function listReferences() {
  return readdirSync(REFS_DIR)
    .filter((f) => f.endsWith('.md') && f !== 'catalog.md')
    .map((f) => join(REFS_DIR, f))
}

function findImports(tsx) {
  const re = /^\s*import\s+[^'"]+from\s+['"]([^'"]+)['"]/gm
  const sources = []
  let m
  while ((m = re.exec(tsx)) !== null) sources.push(m[1])
  return sources
}

function checkImports(name, tsx) {
  const failures = []
  for (const src of findImports(tsx)) {
    for (const banned of BANNED_IMPORTS) {
      if (banned.test(src)) {
        failures.push(`${name}: banned import "${src}"`)
      }
    }
    const allowed = ALLOWED_IMPORT_PREFIXES.some((re) => re.test(src))
    if (!allowed) {
      failures.push(
        `${name}: import "${src}" is not react or relative path`,
      )
    }
  }
  return failures
}

function syntaxCheck(name, filePath, ts) {
  const content = readFileSync(filePath, 'utf8')
  const sf = ts.createSourceFile(
    filePath,
    content,
    ts.ScriptTarget.ES2022,
    /* setParentNodes */ false,
    ts.ScriptKind.TSX,
  )
  // ts.createSourceFile collects parser errors on `.parseDiagnostics`
  // (an internal field — but stable enough for this use). Fall back to
  // re-parsing with the public preProcessFile + scanner if needed.
  const diags = sf.parseDiagnostics ?? []
  return diags.map((d) => {
    const start = d.start ?? 0
    const { line, character } = ts.getLineAndCharacterOfPosition(sf, start)
    const msg = ts.flattenDiagnosticMessageText(d.messageText, '\n')
    return `${name}: parse error at ${line + 1}:${character + 1} — ${msg}`
  })
}

function main() {
  const vars = loadVars()
  if (existsSync(TMP_DIR)) rmSync(TMP_DIR, { recursive: true, force: true })
  mkdirSync(TMP_DIR, { recursive: true })

  const failures = []
  const refs = listReferences()
  let foundationWritten = false

  for (const refPath of refs) {
    const { tsx, scss, name } = extractFromFile(refPath, vars)
    const requiresScss = !COMPONENTS_WITHOUT_SCSS.has(name)

    if (!tsx) {
      failures.push(
        `${name}: reference doc has no \`\`\`tsx fenced block before Accessibility/Usage Examples`,
      )
      continue
    }
    if (requiresScss && !scss) {
      failures.push(
        `${name}: reference doc has no \`## SCSS Template\` section with a \`\`\`scss block`,
      )
    }

    failures.push(...checkImports(name, tsx))

    if (name === 'foundation') {
      writeFileSync(join(TMP_DIR, 'ui.tsx'), tsx)
      foundationWritten = true
    } else {
      const componentDir = join(TMP_DIR, name)
      mkdirSync(componentDir, { recursive: true })
      writeFileSync(join(componentDir, `${name}.tsx`), tsx)
      if (scss) writeFileSync(join(componentDir, `${name}.scss`), scss)
    }
  }

  if (!foundationWritten) {
    failures.push(
      'foundation.md not extracted; component imports of `../ui` will not resolve',
    )
  }

  // Syntax check every written .tsx via TypeScript's parser API.
  // Loaded lazily so we only require typescript when extraction succeeded.
  let ts
  try {
    ts = requireCjs('typescript')
  } catch {
    failures.push(
      'typescript not installed: run `npm --prefix tests ci` first',
    )
    report(failures)
    return
  }

  const tsxFiles = []
  if (foundationWritten) tsxFiles.push(['foundation', join(TMP_DIR, 'ui.tsx')])
  for (const refPath of refs) {
    const name = refPath.split('/').pop().replace(/\.md$/, '')
    if (name === 'foundation') continue
    const candidate = join(TMP_DIR, name, `${name}.tsx`)
    if (existsSync(candidate)) tsxFiles.push([name, candidate])
  }
  for (const [name, file] of tsxFiles) {
    failures.push(...syntaxCheck(name, file, ts))
  }

  report(failures)
}

function report(failures) {
  if (failures.length === 0) {
    console.log('validate_components.mjs: extraction OK')
    process.exit(0)
  }
  console.error('validate_components.mjs: extraction FAIL')
  for (const f of failures) console.error('  -', f)
  process.exit(1)
}

main()
