# Rewrite test structure: replace Vite sandbox with automated validation

> **Superseded** by the 2026-04 test-harness simplification: the Vite sandbox
> in `tests/setup.sh` was replaced with a minimal `package.json` + `tsconfig.json`
> fixture, and the Storybook + Playwright deep check (`tests/storybook.sh`,
> `plugins/acss-kit/.harness/`) was removed in favour of `tests/e2e.sh`'s
> jsdom + axe-core path. Kept here for historical context only.

## Context

Today there is no automated test suite. `tests/setup.sh` scaffolds a Vite+React+TS sandbox at `tests/sandbox/`; the developer then opens a `claude` session inside it, runs `/kit-add` and `/theme-create` by hand, and visually verifies that files land on disk and `npm run build` succeeds. Vite is not running tests — it is the host project the plugin's output gets imported into.

Two pressures motivate the rewrite:

1. **Manual smoke-testing scales poorly.** The plugin now ships ~18 components plus theme generation and a form skill. A regression in any one of them slips past human review unless the maintainer happens to re-run that exact command.
2. **Markdown-as-source changes the testing options.** Since v0.3.0, the canonical TSX/SCSS for every component lives as fenced code blocks inside `plugins/acss-kit/skills/components/references/<component>.md`. That means the "plugin output" can be extracted and validated *without ever running Claude or booting a React app*. This was not true before the markdown-as-source consolidation.

Goal: design a test harness that catches plugin-output regressions automatically on every PR, with the lowest dep cost that still meaningfully verifies the contract.

## Objective

Replace the manual `tests/setup.sh` workflow with an automated validation harness, after evaluating two candidate approaches and committing to one (or a hybrid).

## Approaches considered

### Approach A — Storybook + test-runner

A Storybook harness at `plugins/acss-kit/.harness/` (gitignored after install). A Node extractor walks `references/components/*.md`, parses ` ```tsx ` / ` ```scss ` blocks, substitutes placeholders, and writes the components plus auto-generated stories from existing `## Usage Examples` blocks. CI runs `build-storybook` then `@storybook/test-runner` with `axe-playwright` for accessibility checks.

**What it verifies well:** live render, runtime DOM a11y, real prop wiring, TS types at build time.
**What it misses:** theme contrast (no story for CSS-only files), SCSS contract violations that render but break the rem-only / `var()`-fallback rules.
**Cost:** ~12 npm devDeps including Playwright browser download (~350–500 MB), CI run ~3–4 minutes, new GitHub Actions workflow.

### Approach B — Static structural & code validation

A Bash entrypoint `tests/run.sh` orchestrates two validators: `plugins/acss-kit/scripts/validate_components.py` (Python stdlib — markdown structure + SCSS contract) and `plugins/acss-kit/scripts/validate_components.mjs` (Node + `typescript` — runs `tsc --noEmit` over extracted TSX). Themes get the existing [`validate_theme.py`](plugins/acss-kit/scripts/validate_theme.py); manifests get the existing `validate-plugin` / `verify-plugins` skills.

**What it verifies well:** TS types, SCSS contract (rem-only, `var()` fallbacks, data-attribute selectors), WCAG contrast, manifest correctness, placeholder substitution, no `@fpkit/acss` imports leaking back in.
**What it misses:** runtime render errors, live a11y bugs (e.g. focus-order regressions), real DOM behavior.
**Cost:** 1 npm devDep (`typescript` ~70 MB), Python stays stdlib-only, CI run ~30 seconds.

### Comparison summary

| Axis | A (Storybook) | B (Static) |
|---|---|---|
| New devDeps | ~12 npm packages, browser download | 1 npm package |
| CI runtime | 3–4 min | ~30 sec |
| Catches theme contrast regressions | No | Yes (existing tool) |
| Catches SCSS contract violations | No | Yes |
| Catches runtime render errors | Yes | No |
| Catches live a11y violations | Yes (axe) | Partial (textual checks only) |
| Catches type errors in extracted TSX | Yes | Yes |
| Catches `@fpkit/acss` import leak | Yes | Yes |
| Fits markdown-as-source architecture | High | High |
| Maintenance per new component | Auto from `## Usage Examples` | Auto from code blocks |

## Decision: hybrid, B-as-default, local-only

**Approach B becomes the default check** (`tests/run.sh`, ~30 sec, catches the silent regressions). **Approach A becomes opt-in local verification** invoked as `tests/run.sh --with-storybook` (developers run it before merging anything render-sensitive). The Vite sandbox at `tests/sandbox/` survives as the user-facing demo path documented in `RECIPE.md` — it stops being "the tests."

No GitHub Actions workflow ships with this work. Validation runs locally; documenting `tests/run.sh` as a pre-PR ritual is the contract. CI is a future follow-up if the harness proves useful in practice.

Why split this way: the silent regressions (missing rem unit, missing `var()` fallback, theme contrast drift, manifest/version desync) are cheap to detect statically and slip past human review reliably. The loud regressions (a `Dialog` that fails to mount) surface immediately when any developer first imports the component, so they do not need an automated gate to catch them — they need a local check on demand. Optimizing the default check for sensitivity-per-second favours Approach B; optimizing the local "deep check" for coverage favours Approach A.

Pure-A would burn ~3–4 minutes per run on a browser download and miss theme/SCSS regressions entirely. Pure-B would miss the occasional runtime regression. The hybrid uses each tool where its yield is highest.

## Steps

### Phase 1 — Approach B: structural + code validation (CI gate)

1. **Create the shared extractor** at `plugins/acss-kit/scripts/lib/extract.mjs` (Node, ESM). Walks a passed reference markdown file, parses ` ```tsx ` and ` ```scss ` fenced blocks under `## TSX Template` / `## SCSS Template`, substitutes `{{IMPORT_SOURCE:...}}` / `{{NAME}}` / `{{FIELDS}}` against a passed-in vars object, returns `{ tsx, scss }`. Used by all subsequent validators (and, if Phase 2 lands, by the Storybook harness too). *Why a single extractor:* tests assert the same generation logic that `/kit-add` performs at runtime — divergence between the two would defeat the test.

2. **Create [`tests/validate_components.mjs`](tests/validate_components.mjs)** (Node). For every reference doc under `skills/components/references/components/`:
   - Extracts `foundation.md`'s `## TSX Template` block first, writes to `tests/.tmp/ui.tsx` so component imports resolve. *No vendored TSX file* — extractor processes `foundation.md` as a first-class component.
   - Calls the extractor with default fixture vars from `tests/fixtures/component-vars.json`.
   - Writes outputs to `tests/.tmp/extracted/<component>/<component>.{tsx,scss}` (gitignored).
   - Runs `tsc --noEmit --jsx react-jsx --strict` over the directory; fails if any diagnostic.
   - Asserts: every `import` resolves to either `react` or a relative path; no `@fpkit/acss` imports.
   - **Hard fails** (with the file path and the missing element in the error message) when a reference has a `## TSX Template` heading but no `tsx` fenced code block, or fences without a language. No skip-on-malformed mode.
   *Why Node + `tsc`:* the only dependency that gives meaningful "does this TSX type-check" answers. Python regex cannot resolve module imports. *Why under `tests/` and not `plugins/acss-kit/scripts/`:* this is test infrastructure, not a runtime plugin script — it sits outside the plugin's stdlib-only contract.

3. **Create [`tests/validate_components.py`](tests/validate_components.py)** (Python, may use `tinycss2` — test infra is exempt from the plugin's stdlib-only rule). Follows the existing detector contract: JSON to stdout, `reasons` array. For every extracted `.scss`:
   - Parses each file with `tinycss2` (or libsass via subprocess) into compiled CSS, *then* runs regex assertions over the compiled output. *Why parse first:* SCSS nesting, `@if`/`@each`, and `#{$var}` interpolation produce false positives when scanned raw with regex; the parser flattens to AST-correct CSS.
   - Asserts every `var(--color-*, ...)` and `var(--font-*, ...)` reference includes a fallback.
   - Asserts every numeric value uses `rem`, `%`, `fr`, `vh|vw`, `calc()`, or `0` — bare `px` fails except in an allowlist (e.g. `1px solid` borders).
   - Asserts no class-name conflicts across components (each `.<name>` declared at most once across the directory).
   - Hard fails on malformed `## SCSS Template` sections, same contract as the TSX validator.

4. **Create [`tests/validate_manifest.py`](tests/validate_manifest.py)** (Python). Replicates the manifest/structure checks currently performed by the `verify-plugins` skill: required `plugin.json` fields, no `version` key in `marketplace.json` plugin entries, required files present (`README.md`, `CHANGELOG.md`, `commands/*.md`, at least one `SKILL.md`). *Why replicate instead of invoke:* the `verify-plugins` skill is invoked from inside Claude sessions; there is no documented CLI bridge, so the harness needs its own copy to run standalone.

5. **Create [`tests/run.sh`](tests/run.sh)** (Bash) as the single entrypoint. In order:
   1. `rm -rf tests/.tmp && mkdir -p tests/.tmp` — wipe stale state. *Documented as serial-only:* concurrent runs in the same checkout are unsupported.
   2. `node tests/validate_components.mjs` — extract + tsc.
   3. `python3 tests/validate_components.py tests/.tmp/extracted` — SCSS contract.
   4. `python3 plugins/acss-kit/scripts/validate_theme.py plugins/acss-kit/assets/theme/*.css` — existing WCAG validator (still lives under the plugin since it's a runtime script).
   5. `python3 tests/validate_manifest.py` — manifest/structure replication.
   6. Run the known-bad self-tests (step 7 below).
   Exit non-zero if any step fails; print a summary line per step regardless of outcome. *Why Bash orchestrator:* matches the existing `setup.sh` location convention and keeps language polyglot without a Node-vs-Python build step.

6. **Add `tests/fixtures/component-vars.json`** with realistic placeholder values (`NAME: "Button"`, `componentsDir: "src/components/fpkit"`, `IMPORT_SOURCE: "../ui"`, etc.). *Form fixture deferred:* `tests/fixtures/form-vars.json` is out of scope until the `component-form` skill enters validation scope (see step 11).

7. **Add `tests/fixtures/known-bad/`** with two files: `known-bad.tsx` (banned `@fpkit/acss` import + missing `aria-disabled`) and `known-bad.scss` (missing `var()` fallback, bare `px` value). The harness runs both validators against this dir as a final step in `tests/run.sh` and **expects failure** — exits non-zero if either passes. *Why:* without this, a regex regression in either validator silently passes everything. Cheap insurance for the test-the-tests gap.

8. **Add devDependency** `typescript` to a minimal `tests/package.json` (Node-only, no React imports). *Why a separate `tests/package.json`:* keeps the harness's lockfile out of the plugin's user-facing surface and avoids confusing `/plugin install` consumers who never need it.

9. **Add `.gitignore` entries** for `tests/.tmp/`, `tests/node_modules/`. **Commit `tests/package-lock.json`** for reproducibility (one devDep, churn is minimal).

10. **Update [`tests/README.md`](tests/README.md)** to document `tests/run.sh` as the primary path. Include:
    - The serial-only constraint on `tests/.tmp/`.
    - A "Component Form gap" callout: `skills/component-form/SKILL.md` is not yet covered by the harness; manual smoke-test via the demo sandbox is the current verification path.
    - A literal escape-hatch instruction for harness regressions: *"If a bug in the validator itself is blocking your PR, comment out the failing step in `tests/run.sh` in your branch and link the bug report in the PR description."* Honest about reality without compromising the no-bypass default.
    - One-line note explaining the `.mjs` extension (ESM by default, no `type: "module"` needed in `package.json`).
    - The manual sandbox flow demoted to "User-facing demo (run before opening a PR that touches a slash command's prose)."

11. **Update [`CLAUDE.md`](CLAUDE.md) "Testing locally" section** to point to `tests/run.sh` first, sandbox second.

### Phase 2 — Approach A: optional Storybook deep check

12. **Audit `## Usage Examples` blocks** before scaffolding anything. Run `grep -l "## Usage Examples" plugins/acss-kit/skills/components/references/components/*.md` and read 3 docs to confirm the section exists across the catalog and contains renderable JSX (not prose-only or wrapped in non-renderable contexts). If the assumption breaks, redesign the story-generation step before continuing. *Why first:* Phase 2's whole design depends on this assumption; better to confirm in 5 minutes than discover it after scaffolding.

13. **Create the Storybook harness scaffold** at `plugins/acss-kit/.harness/` with `package.json`, `vite.config.ts`, `.storybook/main.ts`, `.storybook/preview.ts`. Add to `.gitignore` so installed deps never commit. *Why under the plugin and not under `tests/`:* the harness is plugin-internal; version-locking it to the plugin's references is a feature.

14. **Create the story generator** `plugins/acss-kit/scripts/generate_stories.mjs`. Reuses Phase 1's `extract.mjs` to extract TSX, then walks `## Usage Examples` blocks in the same reference doc and emits one `<component>.stories.tsx` per component, one story per top-level JSX expression. Writes to `.harness/src/generated/`. *Why `## Usage Examples` and not a new `## Story` block:* every reference doc already has usage examples; adding a new required section would be migration cost without a coverage win.

15. **Create [`tests/storybook.sh`](tests/storybook.sh)** as a separate entrypoint (not a flag on `run.sh`). Runs `npm --prefix plugins/acss-kit/.harness ci`, `node plugins/acss-kit/scripts/generate_stories.mjs`, `npm --prefix plugins/acss-kit/.harness run build-storybook`, `npm --prefix plugins/acss-kit/.harness run test-storybook`. *Why a separate script:* two single-purpose scripts beat one branch-heavy script when the second path is rarely run; keeps `tests/run.sh` simple.

16. **Document the deep check** in `tests/README.md`: when to run it (before merging anything render-sensitive), what failure modes it catches that Phase 1 does not, and the local prerequisite of `npx playwright install`.

### Phase 3 — Demote the manual workflow

17. **Update [`tests/setup.sh`](tests/setup.sh)** to print a banner: "This scaffolds a demo sandbox; for automated tests run `tests/run.sh`." The script keeps working — it just stops being the documented testing path.

18. **Remove the "Testing locally" section's claim that `tests/setup.sh` is the testing entrypoint** from any plugin-level README that asserts it.

19. **Stop referencing the sandbox in PR review checklists** (if any exist in the repo or in `release-check`); replace with `tests/run.sh`.

## Verification

End-to-end checks after Phase 1 lands:

1. Clean checkout: `cd plugins/acss-kit && find . -name "*.md"` → ensure references exist as expected. Then run `tests/run.sh` from the repo root. Expect exit 0, all four steps green.
2. Inject a regression: edit one component reference doc to remove a `var()` fallback (e.g. `var(--color-primary, #4f46e5)` → `var(--color-primary)`). Re-run `tests/run.sh`. Expect exit 1 and the SCSS validator's `reasons` array calls out the file and the offending var.
3. Inject a TS regression: edit a reference's TSX block to add `import x from '@fpkit/acss'`. Re-run. Expect exit 1 from the Node validator with a clear "import not allowed" message.
4. Inject a theme regression: edit `assets/theme/light.css` to set `--color-text` to a low-contrast value against `--color-background`. Re-run. Expect exit 1 from `validate_theme.py`.
5. Inject a manifest regression: bump `plugin.json` `version` without touching `CHANGELOG.md`. Re-run. Expect `release-check` (invoked indirectly) to flag the missing changelog entry.

After Phase 2 lands:

6. `tests/storybook.sh` on a clean checkout: expect Storybook to build, then test-runner to run all stories with no axe violations. (`tests/run.sh` should also still pass independently.)
7. Inject a runtime regression in a `## TSX Template` block (e.g. throw inside a component on mount). Re-run `tests/storybook.sh`. Expect `tests/run.sh` to still pass (textual checks don't catch it) but Storybook test-runner to fail on that component's story.

Self-tests (verify the harness catches its own contract violations):

8. Run `tests/run.sh` on a clean checkout: the known-bad fixtures in `tests/fixtures/known-bad/` are intentionally malformed; the harness should treat them as **expected failures** and exit 0 only if both fail validation. If known-bad files start passing, the validator regex has regressed.

## Critical files to create or modify

**Phase 1:**
- [`plugins/acss-kit/scripts/lib/extract.mjs`](plugins/acss-kit/scripts/lib/extract.mjs) — new, shared markdown-block extractor + placeholder substitution. Header comment documents the substitution contract and reminds maintainers to mirror changes in `/kit-add` prose.
- [`tests/validate_components.mjs`](tests/validate_components.mjs) — new, Node + `tsc`. Test infra, not a runtime plugin script.
- [`tests/validate_components.py`](tests/validate_components.py) — new, Python (may use `tinycss2`). Follows detector contract.
- [`tests/validate_manifest.py`](tests/validate_manifest.py) — new, replicates `verify-plugins` skill's checks.
- [`tests/run.sh`](tests/run.sh) — new, Bash orchestrator with `rm -rf tests/.tmp` as the first action.
- [`tests/fixtures/component-vars.json`](tests/fixtures/component-vars.json) — new.
- [`tests/fixtures/known-bad/`](tests/fixtures/known-bad/) — new, intentional-failure smoke test for the validators themselves.
- [`tests/package.json`](tests/package.json) + [`tests/package-lock.json`](tests/package-lock.json) — new, single devDep `typescript`. Lockfile committed.
- [`tests/README.md`](tests/README.md) — updated; primary path is `tests/run.sh`, includes Component Form gap callout, escape-hatch note, `.mjs` rationale.
- [`.gitignore`](.gitignore) — add `tests/.tmp/` and `tests/node_modules/`.

**Phase 2 (optional):**
- `plugins/acss-kit/.harness/` (gitignored) — Storybook scaffold.
- [`plugins/acss-kit/scripts/generate_stories.mjs`](plugins/acss-kit/scripts/generate_stories.mjs) — new, story generator that reuses `extract.mjs`.
- [`tests/storybook.sh`](tests/storybook.sh) — new, separate entrypoint for the deep check.

**Phase 3:**
- [`tests/setup.sh`](tests/setup.sh) — updated banner only, otherwise unchanged.
- [`CLAUDE.md`](CLAUDE.md) — updated Testing locally section.
- [`plugins/acss-kit/README.md`](plugins/acss-kit/README.md) — remove any "Testing locally" claim that names `tests/setup.sh` as the entrypoint.

## Existing utilities to reuse

- [`plugins/acss-kit/scripts/validate_theme.py`](plugins/acss-kit/scripts/validate_theme.py) — WCAG 2.2 AA contrast pairings (already exists, just gets wrapped by `tests/run.sh`).
- `validate-plugin`, `verify-plugins`, `release-check` skills at the repo root — manifest and structure validation.
- The detector and generator script contracts documented in [`CLAUDE.md`](CLAUDE.md) — new Python validator follows the detector contract (JSON to stdout, `reasons` array).
- The `{{IMPORT_SOURCE:...}}` / `{{NAME}}` / `{{FIELDS}}` placeholder convention used by `/kit-add` at runtime — the extractor in step 1 is a deterministic re-implementation of that same logic.

## Next steps (out of scope)

- Add `.github/workflows/validate.yml` to run `tests/run.sh` on every PR once the harness has proven useful in local practice.
- Extend the harness to cover `skills/component-form/SKILL.md` once `{{FIELDS}}` substitution stabilizes. Add `tests/fixtures/form-vars.json` at that point.
- A `/kit-test <component>` slash command that runs `tests/run.sh` scoped to one component for fast iteration during reference-doc edits.
- A pre-commit hook in `.claude/hooks/` that runs `tests/run.sh` on edits to `references/**/*.md`.
- Visual regression snapshots in the Storybook harness (Chromatic or `@storybook/test-runner`'s screenshot mode) — only worth it if the team wants pixel-level review.
- Promoting Storybook from opt-in to a second CI job once the team has paid the browser-download cost ergonomically (caching Playwright in GHA).

---

## Interview Summary

This section captures decisions and open risks surfaced during `/plan-interview` before implementation.

### Key Decisions Confirmed

**Extractor drift mitigation (Round 1):** Document the substitution contract in `extract.mjs` with a "mirror this in /kit-add" comment header. Cheapest path; relies on humans noticing when `/kit-add` prose changes. Acceptable while the placeholder rules stay simple (`{{NAME}}`, `{{IMPORT_SOURCE:...}}`, `{{FIELDS}}`).

**SCSS parsing strategy (Round 1):** Use Python's `tinycss2` (or libsass via subprocess) to parse SCSS into compiled CSS first, then run regex assertions over the compiled output. AST-correct without stylelint's Node-deps cost. The validator lives under `tests/`, not `plugins/acss-kit/scripts/`, so the project's stdlib-only contract stays intact.

**Skill invocation (Round 1):** Skip invoking `verify-plugins` from `tests/run.sh`. Replicate the manifest/structure checks as a dedicated `tests/validate_manifest.py` so the harness stays decoupled from any Claude runtime. Some logic duplication accepted as the cost of standalone-runnability.

**Foundation handling (Round 1):** Extractor treats `foundation.md` as a first-class component — extracts its `## TSX Template` block into `tests/.tmp/ui.tsx` before processing any component. No fallback to a vendored `.tsx` file.

**Form skill scope (Round 3):** `skills/component-form/SKILL.md` is excluded from this rewrite. Validator only walks `skills/components/references/components/`. Documented as a gap in `tests/README.md`.

**Malformed reference handling (Round 3):** Hard fail with a clear error message identifying the file and the missing element (e.g. *"references/components/dialog.md has `## TSX Template` heading but no `tsx` fenced code block"*). No skip/warn modes.

**Temp dir contract (Round 3):** `tests/run.sh` wipes `tests/.tmp/` (`rm -rf` then `mkdir`) at the start of every run. Documented as serial-only — concurrent runs in the same checkout are unsupported.

**Bypass policy (Round 3):** No environment variable bypass, no skip flag. If `tests/run.sh` cannot run, the contributor cannot ship. The `tests/README.md` documents a literal escape hatch (comment out the failing step + link bug report) for harness regressions only.

### Plan Naming

| Element | Current | Issue | Suggested | User decision |
|---------|---------|-------|-----------|---------------|
| Filename | `i-want-to-rewrite-calm-hammock.md` | Random pattern (`calm-hammock`) unrelated to content | `test-infrastructure-rewrite.md` | Accepted — file renamed and moved to `docs/plans/` |
| H1 Heading | `# Rewrite test structure: replace Vite sandbox with automated validation` | Pass — descriptive | _(no change)_ | n/a |

### Open Risks & Concerns

1. **Extractor↔runtime drift is accepted, not eliminated.** If `/kit-add` evolves its substitution rules and the comment in `extract.mjs` is missed during review, validator success becomes meaningless. Re-evaluate if a real divergence ever bites.
2. **`tinycss2` is third-party.** It is permitted under `tests/` but introduces a new Python dependency for the test suite. Document the install step in `tests/README.md`. If `tinycss2` proves brittle, the libsass-via-subprocess fallback is a known-good alternative.
3. **The harness has no automated rollback path.** With "no bypass" + "hard fail on malformed", a regression in the validator itself blocks every PR. Mitigation: the literal escape hatch documented in `tests/README.md`. Honest acknowledgement of reality.
4. **Phase 2's `## Usage Examples` assumption is unverified.** Step 12 audits this before scaffolding; if it breaks, Phase 2's design must change.
5. **Manifest replication can drift from `verify-plugins`.** Two implementations of the same contract diverge over time. If both are ever found out of sync, pick one as canonical and have the other invoke it.

### Recommended Next Steps

The following amendments from the interview have been integrated into the plan body above:

1. Step 2 tightened to lock the foundation extraction path (no vendored TSX hedge).
2. Step 3 declares `tinycss2` parsing strategy; validators moved from `plugins/acss-kit/scripts/` to `tests/` to honor the stdlib-only contract.
3. New step 4 for `tests/validate_manifest.py` replacing the `verify-plugins` skill invocation.
4. Step 5 adds `rm -rf tests/.tmp` as the first action; documents serial-only constraint.
5. Step 6 drops `tests/fixtures/form-vars.json`; deferred until form is in scope.
6. New step 7 adds `tests/fixtures/known-bad/` for harness self-tests.
7. Step 9 commits `tests/package-lock.json` for reproducibility.
8. Step 10 expands `tests/README.md` content with gap callout, escape hatch, and `.mjs` rationale.
9. New step 12 audits `## Usage Examples` blocks before Phase 2 scaffolding.
10. Step 15 replaces `tests/run.sh --with-storybook` flag with a separate `tests/storybook.sh` script.

### Simplification Opportunities Applied

- Replaced `--with-storybook` flag with a separate `tests/storybook.sh` script. Two single-purpose scripts beat one branch-heavy script.
- Dropped `tests/fixtures/form-vars.json` from Phase 1. Form skill is out of scope; the second fixture is dead surface until that changes.
