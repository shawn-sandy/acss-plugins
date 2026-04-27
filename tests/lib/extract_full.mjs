// Type-checkable component extractor for tests/e2e.sh.
//
// MIRRORS what /kit-add does at runtime — see the components SKILL.md
// "TSX Template — Copy this verbatim" prose. The shared lib/extract.mjs
// used by tests/run.sh is intentionally syntax-only and concatenates
// `## Props Interface(s)` + `## TSX Template`, which is enough for
// `ts.createSourceFile` to validate but produces duplicate type aliases
// (link, icon, img, list, ...) and unresolved helper references (button,
// input — they use `// [inline NAME and NAME here]` marker comments) at
// the type-check level.
//
// This module:
//   1. Pulls ONLY the `## TSX Template` block (the canonical generated
//      file). Props Interface blocks are skipped because TSX Template
//      already re-declares the type.
//   2. Resolves marker comments of the form
//        // [inline NAME1 and NAME2 here]
//      by replacing them with the bodies of `## Key Pattern: NAME1` /
//      `## Key Pattern: NAME2` (case-insensitive).
//   3. Pulls `## SCSS Template` / `## SCSS Pattern` SCSS the same way
//      lib/extract.mjs does.
//
// If marker substitution drifts between this module and /kit-add, the
// e2e type-check will fail loudly — which is the point.

import { readFileSync } from 'node:fs'

// Marker format is approximately: `// [inline X and Y here]`. Some refs
// substitute "as above" or "as in button.tsx" for "here", so accept any
// trailing words inside the brackets.
const MARKER_RE = /^(\s*)\/\/\s*\[inline\s+([^\]]+?)\]\s*$/i

function splitMarker(names) {
  // "X and Y" / "X, Y" / "X, Y and Z" / "X". Strip trailing connector
  // phrases like "here" / "as above" / "as in button.tsx".
  const cleaned = names.replace(/\b(here|as above|as in [^,]+)\b/gi, '')
  return cleaned
    .replace(/\band\b/gi, ',')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

function collectKeyPatterns(content) {
  const lines = content.split('\n')
  const patterns = new Map()
  let currentName = null
  let inFence = false
  let fenceLang = ''
  let buffer = []

  for (const line of lines) {
    const headingMatch = line.match(/^##\s+Key Pattern:\s*(.+?)\s*$/i)
    if (headingMatch && !inFence) {
      currentName = headingMatch[1].trim()
      continue
    }
    const otherHeading = line.match(/^##\s+(?!Key Pattern:)/i)
    if (otherHeading && !inFence) {
      currentName = null
      continue
    }
    const fenceMatch = line.match(/^```(\w*)\s*$/)
    if (fenceMatch) {
      if (!inFence) {
        inFence = true
        fenceLang = fenceMatch[1].toLowerCase()
        buffer = []
      } else {
        if (currentName && fenceLang === 'tsx' && !patterns.has(currentName)) {
          patterns.set(currentName.toLowerCase(), buffer.join('\n'))
        }
        inFence = false
        fenceLang = ''
        buffer = []
      }
      continue
    }
    if (inFence) buffer.push(line)
  }
  return patterns
}

function extractTsxBlocks(content) {
  // Collect first tsx block under `## Props Interface(s)` and first tsx
  // block under `## TSX Template`. Some reference docs declare the props
  // type only in Props Interface (button, input); others re-declare it in
  // TSX Template (link, icon, img, list). We include both and dedupe the
  // top-level `export type X = {...}` redeclarations afterwards.
  const lines = content.split('\n')
  let inProps = false
  let inTemplate = false
  let inFence = false
  let fenceLang = ''
  let buffer = []
  let propsBlock = null
  let templateBlock = null
  for (const line of lines) {
    const heading = line.match(/^##\s+(.+?)\s*$/)
    if (heading && !inFence) {
      const h = heading[1].trim()
      inProps = /^Props Interfaces?\b/i.test(h)
      inTemplate = /^TSX Template\b/i.test(h)
      continue
    }
    const fenceMatch = line.match(/^```(\w*)\s*$/)
    if (fenceMatch) {
      if (!inFence) {
        inFence = true
        fenceLang = fenceMatch[1].toLowerCase()
        buffer = []
      } else {
        if (fenceLang === 'tsx') {
          if (inTemplate && templateBlock === null) {
            templateBlock = buffer.join('\n')
          } else if (inProps && propsBlock === null) {
            propsBlock = buffer.join('\n')
          }
        }
        inFence = false
        fenceLang = ''
        buffer = []
      }
      continue
    }
    if (inFence) buffer.push(line)
  }
  return { propsBlock, templateBlock }
}

function dedupeExportedTypes(source) {
  // Walk source line-by-line. When we encounter `export type Name = {`,
  // capture lines until braces balance. If `Name` was seen earlier, drop
  // those lines. Conservative: only drops blocks whose declaration starts
  // with `export type Name = {`.
  const lines = source.split('\n')
  const out = []
  const seen = new Set()
  let dropping = false
  let dropDepth = 0
  for (const line of lines) {
    if (!dropping) {
      const m = line.match(/^export type ([A-Z]\w*) =\s*\{(.*)$/)
      if (m) {
        const name = m[1]
        if (seen.has(name)) {
          dropping = true
          dropDepth = 0
          // Count braces on this opening line.
          for (const ch of line) {
            if (ch === '{') dropDepth++
            else if (ch === '}') dropDepth--
          }
          if (dropDepth <= 0) dropping = false
          continue
        }
        seen.add(name)
      }
      out.push(line)
    } else {
      for (const ch of line) {
        if (ch === '{') dropDepth++
        else if (ch === '}') dropDepth--
      }
      if (dropDepth <= 0) dropping = false
    }
  }
  return out.join('\n')
}

function extractScss(content) {
  const lines = content.split('\n')
  let inSection = false
  let inFence = false
  let fenceLang = ''
  let buffer = []
  let result = null
  for (const line of lines) {
    const heading = line.match(/^##\s+(.+?)\s*$/)
    if (heading && !inFence) {
      const h = heading[1].trim()
      inSection = /^SCSS Template\b/i.test(h) || /^SCSS Pattern\b/i.test(h)
      continue
    }
    const fenceMatch = line.match(/^```(\w*)\s*$/)
    if (fenceMatch) {
      if (!inFence) {
        inFence = true
        fenceLang = fenceMatch[1].toLowerCase()
        buffer = []
      } else {
        if (inSection && fenceLang === 'scss' && result === null) {
          result = buffer.join('\n')
        }
        inFence = false
        fenceLang = ''
        buffer = []
      }
      continue
    }
    if (inFence) buffer.push(line)
  }
  return result
}

function findPattern(patterns, name) {
  // 1. Exact heading match.
  const exact = patterns.get(name.toLowerCase())
  if (exact) return exact
  // 2. Heading-word match — refs like "Condensed useDisabledState" prefix
  //    the name with adjectives.
  const needle = name.toLowerCase()
  for (const [key, body] of patterns) {
    if (key.split(/\s+/).includes(needle)) return body
    if (key.endsWith(needle) || key.startsWith(needle)) return body
  }
  // 3. Body-symbol match — refs like input.md declare multiple helpers in
  //    one Key Pattern block titled "Inline Disabled-State Helpers". Scan
  //    pattern bodies for a top-level declaration of the requested name.
  const decl = new RegExp(
    `^\\s*(?:const|function|let|var|class|export\\s+(?:const|function|type|interface))\\s+${name}\\b`,
    'm',
  )
  for (const body of patterns.values()) {
    if (decl.test(body)) return body
  }
  return null
}

function inlineMarkers(tsx, patterns, refLabel) {
  const lines = tsx.split('\n')
  const out = []
  for (const line of lines) {
    const m = line.match(MARKER_RE)
    if (!m) {
      out.push(line)
      continue
    }
    const names = splitMarker(m[2])
    // Multiple marker names can resolve to the same Key Pattern body
    // (e.g., input.md declares both helpers in one block). Inline each
    // distinct body once.
    const seenBodies = new Set()
    for (const name of names) {
      const body = findPattern(patterns, name)
      if (!body) {
        throw new Error(
          `${refLabel}: marker "${line.trim()}" references "${name}" but no matching "## Key Pattern: ${name}" tsx block found`,
        )
      }
      if (seenBodies.has(body)) continue
      seenBodies.add(body)
      out.push(body)
      out.push('')
    }
  }
  return out.join('\n')
}

export function extractFull(refPath) {
  const content = readFileSync(refPath, 'utf8')
  const { propsBlock, templateBlock } = extractTsxBlocks(content)
  if (!templateBlock) {
    throw new Error(`${refPath}: no "## TSX Template" tsx block found`)
  }
  const patterns = collectKeyPatterns(content)
  const templateInlined = inlineMarkers(templateBlock, patterns, refPath)
  // Props Interface goes first so types are declared before TSX Template
  // references them. Dedupe any `export type X = {...}` redeclarations
  // (link/icon/img/list re-declare the props in TSX Template).
  const combined = propsBlock
    ? `${propsBlock}\n\n${templateInlined}`
    : templateInlined
  const tsx = dedupeExportedTypes(combined)
  const scss = extractScss(content)
  return { tsx, scss }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [, , refPath, kind] = process.argv
  if (!refPath || !['tsx', 'scss'].includes(kind)) {
    console.error('Usage: extract_full.mjs <ref.md> <tsx|scss>')
    process.exit(2)
  }
  try {
    const { tsx, scss } = extractFull(refPath)
    const payload = kind === 'tsx' ? tsx : scss
    if (payload === null) {
      console.error(`no ${kind} block in ${refPath}`)
      process.exit(1)
    }
    process.stdout.write(payload)
  } catch (err) {
    console.error(err.message)
    process.exit(1)
  }
}
