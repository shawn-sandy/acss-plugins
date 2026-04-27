// Compound-component dependency walker for the e2e harness.
//
// MIRRORS the recursive resolution logic in
// plugins/acss-kit/skills/components/SKILL.md (Step B3, "Resolve the
// dependency tree"). The skill itself walks dependencies at /kit-add time
// based on the `dependencies:` line in each reference doc's Generation
// Contract section. The harness needs the same walk to know which files to
// extract before tsc/sass/jsdom can run against compound output.
//
// If the SKILL.md prose changes (different field name, nested format, etc.)
// keep this module in sync. The format today is a single line inside a
// fenced block under `## Generation Contract`:
//
//     dependencies: [name1, name2]
//
// or `dependencies: []` for leaf components.

import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'

const REFS_DIR_REL = 'plugins/acss-kit/skills/components/references/components'

function readContractDeps(refPath) {
  const content = readFileSync(refPath, 'utf8')
  const lines = content.split('\n')
  let inContract = false
  let inFence = false
  for (const line of lines) {
    if (/^##\s+Generation Contract\b/i.test(line)) {
      inContract = true
      continue
    }
    if (inContract && /^##\s+/.test(line)) {
      // Left the Generation Contract section without finding deps.
      return []
    }
    if (inContract) {
      if (/^```/.test(line)) {
        inFence = !inFence
        continue
      }
      if (!inFence) continue
      const m = line.match(/^\s*dependencies:\s*\[(.*)\]\s*$/i)
      if (m) {
        return m[1]
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean)
      }
    }
  }
  return []
}

/**
 * Walk dependencies recursively starting from `seedNames`.
 * Returns an ordered list (leaves first, composites last) of unique
 * component names. Throws if a dependency reference doc is missing.
 *
 * @param {string} repoRoot - absolute path to the agentic-acss-plugins repo
 * @param {string[]} seedNames - component slugs (e.g. ['dialog', 'button'])
 * @returns {string[]}
 */
export function resolveDeps(repoRoot, seedNames) {
  const refsDir = join(repoRoot, REFS_DIR_REL)
  const visited = new Set()
  const order = []

  function visit(name) {
    if (visited.has(name)) return
    visited.add(name)
    const refPath = join(refsDir, `${name}.md`)
    let deps
    try {
      deps = readContractDeps(refPath)
    } catch (err) {
      throw new Error(`Reference doc missing for component "${name}": ${refPath}`)
    }
    for (const dep of deps) visit(dep)
    order.push(name)
  }

  for (const seed of seedNames) visit(seed)
  return order
}

// CLI: `node tests/lib/resolve_deps.mjs <repoRoot> <comp1> [comp2] ...`
// Prints one resolved name per line. Useful for shell consumers.
if (import.meta.url === `file://${process.argv[1]}`) {
  const [, , repoRoot, ...names] = process.argv
  if (!repoRoot || names.length === 0) {
    console.error('Usage: resolve_deps.mjs <repoRoot> <component> [component...]')
    process.exit(2)
  }
  try {
    const order = resolveDeps(repoRoot, names)
    for (const n of order) process.stdout.write(`${n}\n`)
  } catch (err) {
    console.error(err.message)
    process.exit(1)
  }
}
