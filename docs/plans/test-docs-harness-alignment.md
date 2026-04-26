# Test documentation review — align orientation-layer docs with the Phase 1 harness

## Context

The Phase 1 structural validation harness landed in commit [`71ffe6c`](https://github.com/shawn-sandy/acss-plugins) — `tests/run.sh` is now the default pre-PR check (extract+TSC, SCSS contract, WCAG contrast, manifest replication, known-bad self-tests; ~30s, no browser). A Phase 2 Storybook deep-check (`tests/storybook.sh`) is also in place. Most documentation was updated when the harness landed.

Two top-level orientation files were missed and still describe the **pre-harness** workflow (sandbox-only) as the primary testing path. The design plan at [`docs/plans/test-infrastructure-rewrite.md`](docs/plans/test-infrastructure-rewrite.md) Phase 3 explicitly called for demoting the sandbox in any README that asserts it's the testing entrypoint, but the plan only enumerated `plugins/acss-kit/README.md` — root `README.md` and `CONTRIBUTING.md` were not on the list, so they were inherited as gaps.

Goal: align `README.md` and `CONTRIBUTING.md` with the harness-first messaging already in `tests/README.md`, root `CLAUDE.md`, `plugins/acss-kit/README.md`, and `plugins/acss-kit/.harness/README.md`. Documentation-only change; no scripts touched.

## Current state of test documentation

| File | State | Notes |
|------|-------|-------|
| [`tests/README.md`](tests/README.md) | Current | Comprehensive, accurate. Documents `run.sh`/`storybook.sh`/`setup.sh` with correct one-time-setup, stage breakdown, escape hatch, troubleshooting. |
| [`CLAUDE.md`](CLAUDE.md) (root, "Testing locally") | Current | Names `tests/run.sh` first (~30s), one-time-setup line, `tests/storybook.sh` ~3–4 min, `tests/setup.sh` for end-to-end. |
| [`plugins/acss-kit/README.md`](plugins/acss-kit/README.md) | Current | Contributor recipe Step 5 references `tests/run.sh`; `tests/setup.sh` mentioned only as the end-to-end smoke path. |
| [`plugins/acss-kit/.harness/README.md`](plugins/acss-kit/.harness/README.md) | Current | Phase 2 deep-check correctly framed as opt-in, supplementary to `tests/run.sh`. |
| [`plugins/acss-kit/CHANGELOG.md`](plugins/acss-kit/CHANGELOG.md) | N/A | Plugin-level CHANGELOG; the test harness is repo-level under `tests/`, not a plugin change. No entry needed here. |
| [`README.md`](README.md) (root, "Testing locally") | **Stale** | Names `tests/setup.sh` as the sole testing path. No mention of `tests/run.sh`, one-time setup, or Storybook deep check. |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) ("Testing locally" + "Before submitting a change") | **Stale** | "Testing locally" only mentions `tests/setup.sh`. "Before submitting a change" checklist has no test-run step. |

## Steps

### 1. Update `README.md` "Testing locally" section ([`README.md`](README.md), lines 24–33)

**Why:** This is the first doc a contributor lands on. Telling them `tests/setup.sh` is "testing locally" sends them through 5+ minutes of Vite scaffolding when the contract regression they actually need to catch is detected by `tests/run.sh` in 30 seconds.

Replace the current section with a two-tier shape mirroring [`CLAUDE.md`](CLAUDE.md) lines 82–88:

- Primary: `tests/run.sh` as the default automated check (~30s, no browser). Include the one-time setup line: `npm --prefix tests ci && pip3 install --user tinycss2`.
- Optional: `tests/storybook.sh` (~3–4 min) for render-sensitive changes.
- End-to-end smoke: `tests/setup.sh` for slash-command verification (sandbox is gitignored).
- Link to [`tests/README.md`](tests/README.md) for the full workflow, troubleshooting, escape hatch.

Keep the section concise — root README should orient, not duplicate `tests/README.md`.

### 2. Update `CONTRIBUTING.md` "Testing locally" section ([`CONTRIBUTING.md`](CONTRIBUTING.md), lines 48–64)

**Why:** Contributors land here for the PR workflow. The current text equates "testing locally" with the sandbox demo, omitting the structural validation that's now the contract.

Apply the same two-tier shape as Step 1, but tuned for the contributor angle:

- Lead with `tests/run.sh` as the structural-validation gate, including one-time setup.
- Mention `tests/storybook.sh` as the optional render-sensitive deep check.
- Keep the existing sandbox flow (`tests/setup.sh` → `cd tests/sandbox && claude`) but reframe it as the end-to-end smoke path for slash-command prose changes — not "the testing path."
- Preserve the existing pointer to [`tests/README.md`](tests/README.md) for the full workflow.

### 3. Update `CONTRIBUTING.md` "Before submitting a change" checklist ([`CONTRIBUTING.md`](CONTRIBUTING.md), lines 66–72)

**Why:** Phase 3 Step 19 of the design plan called for adding the harness to PR checklists. The current four-item list covers version, URL hygiene, marketplace description, and README — but not the test-run step itself.

Add a leading item:

- `tests/run.sh` passes from the repo root.

Keep the existing four items in their current order. Five items total.

### 4. Verify the `setup.sh` framing across all updated files

**Why:** Easy to introduce a copy-paste inconsistency. After Steps 1–3, all five user-facing files (root `README.md`, root `CLAUDE.md`, `CONTRIBUTING.md`, `tests/README.md`, `plugins/acss-kit/README.md`) should describe `tests/setup.sh` with the same role: "demo sandbox for end-to-end slash-command smoke testing," not "the testing path."

This is a re-read-and-confirm step, not a separate edit.

## Verification

Run after the doc edits land (they're text-only; the actual harness behavior doesn't change):

1. `tests/run.sh` from the repo root — expect exit 0, all six stages green. Confirms the harness still works (sanity).
2. `grep -n "tests/setup.sh\|tests/run.sh\|tests/storybook.sh" README.md CONTRIBUTING.md` — expect every match in both files to introduce `tests/run.sh` *before* `tests/setup.sh` and to mention `tests/storybook.sh` as optional.
3. `grep -n "npm --prefix tests ci\|tinycss2" README.md CONTRIBUTING.md` — expect at least one match in each file (the one-time setup line).
4. Read `CONTRIBUTING.md` "Before submitting a change" — expect five items, with `tests/run.sh` as item 1.
5. Spot-read each of the five user-facing files end-to-end to confirm the `tests/setup.sh` role is consistent ("demo sandbox / end-to-end smoke," never "the testing path").

## Critical files to modify

- [`README.md`](README.md) — "Testing locally" section (lines 24–33).
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — "Testing locally" section (lines 48–64) and "Before submitting a change" checklist (lines 66–72).

## Existing patterns to reuse

- The two-tier "default automated check + optional deep check + end-to-end demo" framing from [`tests/README.md`](tests/README.md) lines 5–9 (the path table) and [`CLAUDE.md`](CLAUDE.md) "Testing locally" section (lines 82–88).
- The exact one-time-setup string `npm --prefix tests ci && pip3 install --user tinycss2` from [`CLAUDE.md`](CLAUDE.md) line 84 — keep it identical across files for grep-ability.

## Out of scope (next steps)

- Marking the design plan [`docs/plans/test-infrastructure-rewrite.md`](docs/plans/test-infrastructure-rewrite.md) as "completed" with frontmatter (separate plan-status pass).
- Adding a `tests/setup.sh` startup banner pointing at `tests/run.sh` (Phase 3 Step 17 of the design plan — code change, not docs).
- Adding a `.github/workflows/validate.yml` to run `tests/run.sh` on PRs (the design plan defers this until the harness proves useful in local practice).
- Updating [`plugins/acss-kit/CHANGELOG.md`](plugins/acss-kit/CHANGELOG.md) — repo-level test infrastructure is not a plugin change, so the plugin CHANGELOG correctly omits it.
- Reviewing `plugins/acss-kit/docs/*.md` (architecture, troubleshooting, recipes, tutorial) — none of them mention `tests/run.sh`, `tests/setup.sh`, or `tinycss2`, so there's nothing to update.

## Unresolved questions

None. The two-tier framing is established in three other files; this plan replicates it in two more.
