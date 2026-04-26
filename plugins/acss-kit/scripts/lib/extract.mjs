// Shared markdown-as-source extractor for acss-kit reference docs.
//
// MIRROR THIS IN /kit-add: this module is a deterministic re-implementation
// of the assembly logic that /kit-add performs at runtime. If you change
// substitution rules, section names, or extraction order here, mirror the
// change in plugins/acss-kit/skills/components/SKILL.md and any /kit-add
// command prose. Drift between this module and /kit-add silently breaks the
// validation harness.
//
// Public API:
//   extractFromMarkdown(content, vars?) -> { tsx, scss, name, foundation }
//
// Extraction rules:
//   - TSX: only ```tsx blocks under `## Props Interface(s)` and
//     `## TSX Template`. Key Pattern sections are intentionally excluded
//     because some contain illustrative JSX (e.g. `<Card><Card.Title>...`)
//     or inline-only snippets (e.g. destructuring `props` outside a
//     function body) that aren't valid at module scope. The TSX Template
//     block is the canonical file `/kit-add` writes — Key Pattern bodies
//     are inlined into it at runtime via marker comments, so we don't
//     need to assemble them ourselves for syntax validation.
//   - SCSS: only the first ```scss block within a `## SCSS Template`
//     or `## SCSS Pattern` section. `## CSS Variables` blocks are
//     documentation only — excluded.
//   - Placeholder substitution: {{NAME}}, {{IMPORT_SOURCE:...}}, {{FIELDS}}
//     against an optional vars object. Current reference docs use no
//     placeholders; substitution is forward-compatible scaffolding.

import { readFileSync } from 'node:fs'
import { basename } from 'node:path'

const TSX_SECTION_HEADINGS = [
  /^Props Interfaces?\b/i,
  /^TSX Template\b/i,
]

const SCSS_TEMPLATE_HEADINGS = [
  /^SCSS Template\b/i,
  /^SCSS Pattern\b/i,
  /^CSS Variables \/ SCSS Template\b/i,
]

function isTsxSectionHeading(heading) {
  return TSX_SECTION_HEADINGS.some((re) => re.test(heading))
}

function isScssTemplateHeading(heading) {
  return SCSS_TEMPLATE_HEADINGS.some((re) => re.test(heading))
}

function substitute(text, vars) {
  if (!vars) return text
  let out = text
  for (const [key, val] of Object.entries(vars)) {
    if (key === 'IMPORT_SOURCE_MAP') continue
    out = out.replaceAll(`{{${key}}}`, String(val))
  }
  if (vars.IMPORT_SOURCE_MAP && typeof vars.IMPORT_SOURCE_MAP === 'object') {
    out = out.replaceAll(/\{\{IMPORT_SOURCE:([^}]+)\}\}/g, (_, names) => {
      const list = names.split(',').map((n) => n.trim())
      const sources = new Set(
        list.map((n) => vars.IMPORT_SOURCE_MAP[n] ?? `'../${n.toLowerCase()}'`),
      )
      return [...sources].join(', ')
    })
  }
  return out
}

export function extractFromMarkdown(content, vars) {
  const lines = content.split('\n')
  const tsxBlocks = []
  let scssBlock = null
  let inFence = false
  let fenceLang = ''
  let fenceBuffer = []
  let inTsxSection = false
  let inScssTemplateSection = false
  let scssBlockClaimed = false

  for (const line of lines) {
    const headingMatch = line.match(/^##\s+(.+?)\s*$/)
    if (headingMatch && !inFence) {
      const heading = headingMatch[1].trim()
      inTsxSection = isTsxSectionHeading(heading)
      inScssTemplateSection = isScssTemplateHeading(heading)
      continue
    }

    const fenceMatch = line.match(/^```(\w*)\s*$/)
    if (fenceMatch) {
      if (!inFence) {
        inFence = true
        fenceLang = fenceMatch[1].toLowerCase()
        fenceBuffer = []
      } else {
        const body = fenceBuffer.join('\n')
        if (fenceLang === 'tsx' && inTsxSection) {
          tsxBlocks.push(body)
        } else if (
          fenceLang === 'scss' &&
          inScssTemplateSection &&
          !scssBlockClaimed
        ) {
          scssBlock = body
          scssBlockClaimed = true
        }
        inFence = false
        fenceLang = ''
        fenceBuffer = []
      }
      continue
    }

    if (inFence) {
      fenceBuffer.push(line)
    }
  }

  const tsx = tsxBlocks.length > 0 ? tsxBlocks.join('\n\n') : null
  const scss = scssBlock

  return {
    tsx: tsx ? substitute(tsx, vars) : null,
    scss: scss ? substitute(scss, vars) : null,
  }
}

export function extractFromFile(path, vars) {
  const content = readFileSync(path, 'utf8')
  const result = extractFromMarkdown(content, vars)
  result.name = basename(path, '.md')
  return result
}
