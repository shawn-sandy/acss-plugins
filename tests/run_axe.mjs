// jsdom + axe-core a11y check.
//
// Replaces the Storybook + Playwright + axe-playwright deep check with a
// browserless equivalent. jsdom does not lay out, does not compute styles,
// and does not run real interactivity, so this catches structural a11y
// issues only: missing labels, broken ARIA, illegal nesting, missing alt,
// role/state inconsistencies. Things it does NOT catch: color contrast on
// rendered pixels, focus-indicator visibility, hidden-by-CSS detection,
// keyboard order. Theme contrast is still covered by validate_theme.py
// in tests/run.sh.
//
// Modes:
//   node tests/run_axe.mjs --self-test
//     Reads tests/fixtures/known-bad-a11y/violation.html, runs axe against
//     it, exits 0 only if at least one serious/critical violation is
//     reported. Used by tests/e2e.sh as a smoke test that the harness
//     itself can detect violations.
//
//   node tests/run_axe.mjs --html <file>...
//     Runs axe against each HTML file. Exits 1 if any file produces a
//     serious or critical violation.

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import { JSDOM } from 'jsdom'
import axe from 'axe-core'

const HERE = dirname(fileURLToPath(import.meta.url))
const FAILING_IMPACTS = new Set(['serious', 'critical'])

async function checkHtml(html, label) {
  const dom = new JSDOM(html, {
    runScripts: 'outside-only',
    // jsdom does not implement window.getComputedStyle for pseudo-elements;
    // axe's color-contrast rule relies on it and emits stack traces on every
    // run. We can't measure real contrast in jsdom anyway (theme contrast is
    // covered by validate_theme.py), so swallow the warnings.
    virtualConsole: new (await import('jsdom')).VirtualConsole(),
  })
  const { window } = dom
  // axe-core expects a global `window`, `document`, `Node`, etc. The
  // standard pattern is to inject the axe source into the jsdom window
  // and run it from there.
  window.eval(axe.source)
  const result = await window.axe.run(window.document, {
    resultTypes: ['violations'],
    // Disable rules jsdom can't actually evaluate. color-contrast relies on
    // computed pseudo-element styles; theme contrast is covered separately
    // by validate_theme.py in tests/run.sh.
    rules: { 'color-contrast': { enabled: false } },
  })
  const failing = result.violations.filter((v) => FAILING_IMPACTS.has(v.impact))
  if (failing.length === 0) {
    console.log(`  ok       ${label}`)
    return { ok: true, violations: [] }
  }
  console.log(`  FAIL     ${label}`)
  for (const v of failing) {
    console.log(`    [${v.impact}] ${v.id}: ${v.help}`)
    for (const node of v.nodes.slice(0, 3)) {
      console.log(`      ${node.html}`)
    }
  }
  return { ok: false, violations: failing }
}

async function selfTest() {
  const fixturePath = join(HERE, 'fixtures', 'known-bad-a11y', 'violation.html')
  const html = readFileSync(fixturePath, 'utf8')
  console.log('axe self-test: known-bad-a11y/violation.html')
  const { violations } = await checkHtml(html, 'fixture')
  if (violations.length === 0) {
    console.error('SELF-TEST FAILED: known-bad-a11y fixture produced no violations.')
    console.error('Either axe-core regressed, the fixture lost its violation, or')
    console.error('the harness wiring is broken. Investigate before trusting --html runs.')
    process.exit(1)
  }
  console.log(`self-test ok: ${violations.length} violation(s) detected as expected`)
}

async function checkFiles(paths) {
  let anyFail = false
  for (const p of paths) {
    const html = readFileSync(p, 'utf8')
    const result = await checkHtml(html, p)
    if (!result.ok) anyFail = true
  }
  if (anyFail) {
    console.error('axe check failed.')
    process.exit(1)
  }
  console.log(`axe check ok: ${paths.length} file(s) clean`)
}

const argv = process.argv.slice(2)

if (argv[0] === '--self-test') {
  await selfTest()
} else if (argv[0] === '--html') {
  const files = argv.slice(1)
  if (files.length === 0) {
    console.error('Usage: run_axe.mjs --html <file>...')
    process.exit(2)
  }
  await checkFiles(files)
} else {
  console.error('Usage: run_axe.mjs --self-test')
  console.error('       run_axe.mjs --html <file>...')
  process.exit(2)
}
