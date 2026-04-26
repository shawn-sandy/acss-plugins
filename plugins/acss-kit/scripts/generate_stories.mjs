#!/usr/bin/env node
// Generate Storybook stories from the `## Usage Examples` blocks of each
// component reference doc. Used by the Storybook deep-check harness at
// plugins/acss-kit/.harness/.
//
// Strategy:
//   1. For each reference doc, parse all ```tsx blocks under
//      `## Usage Examples`. Each top-level JSX expression becomes one story.
//   2. Stories are emitted under .harness/src/generated/<name>/<name>.stories.tsx.
//   3. The component itself comes from extract.mjs's TSX extraction —
//      we vendor extracted components into .harness/src/generated/<name>/
//      so stories can `import { ComponentName } from './<name>'`.
//
// This script is wired up but currently best-effort: usage-example blocks
// vary in shape (some are full snippets with `const x = ...`, some are
// raw JSX, some are interspersed with explanatory prose). The story
// generator captures what it can; manual review of the .harness/ output
// is expected before merging render-sensitive changes.

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

import { extractFromMarkdown } from './lib/extract.mjs'

const __dirname = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = resolve(__dirname, '../../..')
const REFS_DIR = join(
  REPO_ROOT,
  'plugins/acss-kit/skills/components/references/components',
)
const OUT_DIR = join(
  REPO_ROOT,
  'plugins/acss-kit/.harness/src/generated',
)

const SKIP = new Set(['catalog', 'foundation'])

function parseUsageExamples(content) {
  // Only look at the `## Usage Examples` section.
  const lines = content.split('\n')
  const blocks = []
  let inSection = false
  let inFence = false
  let fenceLang = ''
  let buffer = []

  for (const line of lines) {
    const heading = line.match(/^##\s+(.+?)\s*$/)
    if (heading) {
      const h = heading[1].trim()
      if (/^Usage Examples\b/i.test(h)) {
        inSection = true
        continue
      }
      if (inSection) {
        // Any subsequent ## ends the Usage Examples section.
        break
      }
    }

    const fence = line.match(/^```(\w*)\s*$/)
    if (fence && inSection) {
      if (!inFence) {
        inFence = true
        fenceLang = fence[1].toLowerCase()
        buffer = []
      } else {
        if (fenceLang === 'tsx' || fenceLang === 'jsx') {
          blocks.push(buffer.join('\n'))
        }
        inFence = false
        buffer = []
      }
      continue
    }

    if (inFence) buffer.push(line)
  }

  return blocks
}

function pascalCase(name) {
  return name
    .split(/[-_]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join('')
}

function emitStoryFile(name, blocks) {
  const componentName = pascalCase(name)
  const stories = blocks
    .map((body, i) => {
      const storyName = `Example${i + 1}`
      // Best-effort: dump the block body as a render() story. Authors are
      // expected to clean these up if they include declarations or imports.
      const cleaned = body
        .replace(/^\s*import[^;\n]*[;\n]/gm, '')
        .trim()
      return `export const ${storyName}: StoryObj = {
  render: () => {
    return (
      <>
${cleaned
  .split('\n')
  .map((l) => '        ' + l)
  .join('\n')}
      </>
    )
  },
}`
    })
    .join('\n\n')

  return `// AUTO-GENERATED from ../references/components/${name}.md.
// Run plugins/acss-kit/scripts/generate_stories.mjs to regenerate.
import type { Meta, StoryObj } from '@storybook/react-vite'
import { ${componentName} } from './${name}'

const meta: Meta = {
  title: 'Components/${componentName}',
  component: ${componentName} as never,
}

export default meta

${stories}
`
}

function main() {
  if (existsSync(OUT_DIR)) rmSync(OUT_DIR, { recursive: true, force: true })
  mkdirSync(OUT_DIR, { recursive: true })

  const refs = readdirSync(REFS_DIR).filter((f) => f.endsWith('.md'))
  let storiesEmitted = 0

  for (const refFile of refs) {
    const name = refFile.replace(/\.md$/, '')
    if (SKIP.has(name)) continue

    const refPath = join(REFS_DIR, refFile)
    const content = readFileSync(refPath, 'utf8')
    const blocks = parseUsageExamples(content)
    if (blocks.length === 0) continue

    const componentDir = join(OUT_DIR, name)
    mkdirSync(componentDir, { recursive: true })

    // Vendor the component itself from the extractor's outputs.
    const { tsx, scss } = extractFromMarkdown(content)
    if (tsx) writeFileSync(join(componentDir, `${name}.tsx`), tsx)
    if (scss) writeFileSync(join(componentDir, `${name}.scss`), scss)

    const storyContent = emitStoryFile(name, blocks)
    writeFileSync(join(componentDir, `${name}.stories.tsx`), storyContent)
    storiesEmitted += blocks.length
  }

  console.log(
    `generate_stories.mjs: emitted stories for ${
      readdirSync(OUT_DIR).length
    } components (${storiesEmitted} story exports)`,
  )
}

main()
