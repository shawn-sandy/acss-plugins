# acss-utilities — Architecture

This guide is for maintainers extending the plugin (adding a family, tightening the validator, swapping the generator). Consumers should start with [tutorial.md](tutorial.md) instead.

## Plugin layout

```text
plugins/acss-utilities/
├── .claude-plugin/
│   └── plugin.json                      # name, version (authoritative), description, license
├── README.md                            # user-facing install + command summary
├── CHANGELOG.md                         # Keep-a-Changelog 1.1.0
├── ATTRIBUTION.md                       # fpkit/acss upstream pin + mirrored-vs-extended scope
├── docs/                                # this developer guide (you are here)
├── commands/
│   ├── utility-add.md                   # YAML front-matter + delegation to skills/utilities/SKILL.md
│   ├── utility-list.md
│   ├── utility-tune.md
│   └── utility-bridge.md
├── skills/utilities/
│   ├── SKILL.md                         # canonical per-command workflow
│   └── references/
│       ├── utility-catalogue.md         # every family, every class, the property each one references
│       ├── naming-convention.md         # selector grammar + !important policy
│       ├── breakpoints.md               # responsive prefix + media-query syntax
│       └── token-bridge.md              # alias mapping + dark-mode parity contract
├── scripts/
│   ├── generate_utilities.py            # tokens JSON → utilities.css + per-family partials
│   ├── validate_utilities.py            # selector grammar, var() fallbacks, parity, budget
│   └── detect_utility_target.py         # find React root + drop directory
└── assets/
    ├── utilities.tokens.json            # source-of-truth (committed)
    ├── utilities.css                    # generated bundle (committed; regeneratable)
    ├── utilities/                       # per-family partials (committed; regeneratable)
    │   ├── color-bg.css
    │   ├── color-text.css
    │   └── …
    └── token-bridge.css                 # acss-kit ↔ fpkit alias layer (committed)
```

The committed bundle (`utilities.css`) and per-family partials are **canonical artifacts**. `tests/run.sh` enforces idempotency: regenerating from `utilities.tokens.json` must produce byte-identical output to what's checked in. Edits go through the tokens file and the generator, not by hand.

## Command → SKILL delegation

Every command file follows the same pattern:

```yaml
---
description: <one line>
argument-hint: [--option] [--flag]
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

Body delegates to `${CLAUDE_PLUGIN_ROOT}/skills/utilities/SKILL.md`.
```

The body is intentionally thin — three to five sentences plus a "Quick steps" outline. The full per-command workflow lives in [`skills/utilities/SKILL.md`](../skills/utilities/SKILL.md), which the slash command tells Claude to follow. Every section in `SKILL.md` lists the references it should load (`references/utility-catalogue.md`, etc.) so Claude pulls only what's needed.

**Never re-implement command logic inline in the command file.** The contract is: command file = entry point + arguments doc, SKILL.md = the workflow.

## Generator/validator contract

Both scripts follow the project's [generator/validator contract](../../../.claude/rules/python-scripts.md) — Python 3 stdlib only (`generate_utilities.py`) or stdlib + `tinycss2` (`validate_utilities.py`).

| Script | Output | Exit codes |
|---|---|---|
| `generate_utilities.py` | CSS (bundle to stdout, or per-family files via `--out-dir`); errors on stderr | 0 success, 1 logical (unknown family), 2 usage/IO |
| `validate_utilities.py` | JSON to stdout with `ok` and `reasons` | 0 success, 1 contract violation, 2 usage/IO |
| `detect_utility_target.py` | JSON to stdout with `source`, `projectRoot`, `utilitiesDir`, `reasons` | 0 success (configured / default), 1 no React root |

The detector is the only script that follows the **detector** contract (machine-callable, structured); the other two are generator/validator (data + reasons).

## How to add a new family

Concrete walkthrough — say you want to add a `border-width` family (`.border-0`, `.border-1`, `.border-2`).

| Step | What to touch |
|---|---|
| 1 | `assets/utilities.tokens.json#families` → add `"border-width": { "enabled": true, "responsive": false }`. Add the scale (e.g. `"borderWidth": [0, 1, 2, 4, 8]`) at the top level of the tokens file. |
| 2 | `scripts/generate_utilities.py` → write an `emit_border_width(tokens)` function returning `_section("border-width utilities", body)`. Register it in the `EMITTERS` dict and append `"border-width"` to `FAMILY_ORDER` in canonical position (after `color-border`). |
| 3 | Run the generator: `python3 plugins/acss-utilities/scripts/generate_utilities.py --tokens plugins/acss-utilities/assets/utilities.tokens.json --out-dir plugins/acss-utilities/assets/`. Inspect `assets/utilities/border-width.css` and the regenerated bundle. |
| 4 | Run the validator: `python3 plugins/acss-utilities/scripts/validate_utilities.py plugins/acss-utilities/assets/`. Should be `ok: true`. |
| 5 | `skills/utilities/references/utility-catalogue.md` → add a section listing the new family's classes and the `border-width` value each one sets. Update the family-inventory table at the top with the class count. |
| 6 | `commands/utility-list.md` and `commands/utility-add.md` → add `border-width` to any explicit family lists. |
| 7 | Bump `CHANGELOG.md` under `[Unreleased]` → `### Added`. |

The maintainer skill at `.claude/skills/utility-author/SKILL.md` (planned, see plugin-health) automates steps 1–7 for typical families. For now do them by hand.

## Bundle-size budget resolution

When `validate_utilities.py` checks bundle size, it resolves the budget in this order:

1. **Explicit `--max-kb N` flag** wins. Used by `tests/run.sh` and ad-hoc runs.
2. **`bundleSizeBudgetKb` from a co-located `utilities.tokens.json`** — the validator searches `<bundle.parent>/utilities.tokens.json`, then `<bundle.parent.parent>/utilities.tokens.json`, then `<target>/utilities.tokens.json`.
3. **Hard-coded fallback of 80 KB** when neither is found.

This was wired up in commit `2af654e` after a Copilot review noted the field was previously dead.

## `.acss-target.json` schema (utilities-relevant fields)

The detector reads the same `.acss-target.json` that `acss-kit` uses, with one added field:

```json
{
  "componentsDir": "src/components/fpkit",   // acss-kit's
  "utilitiesDir": "src/styles"               // acss-utilities'
}
```

Both fields are optional. The detector requires that `(projectRoot / utilitiesDir)` exists on disk before honoring it — a stale entry pointing at a deleted directory falls through to the default. The same fail-safe lives in `acss-kit/scripts/detect_target.py` for `componentsDir`.

## Hooks the plugin opts into

The repo's `.claude/settings.json` runs validation after every Write/Edit:

| Hook | Matcher | Effect |
|---|---|---|
| Validate utility CSS | `Write\|Edit` on `plugins/acss-utilities/assets/.*\.css$` | Runs `validate_utilities.py` and reports the reasons array if non-empty |

Existing project-wide hooks (JSON-syntax check, `plugin.json` required-fields, command front-matter, SKILL.md front-matter) cover the new plugin automatically — no per-plugin matcher edit is needed.

## Version-bump checklist

When releasing a new `acss-utilities` version:

1. Update `plugins/acss-utilities/.claude-plugin/plugin.json#version` (authoritative).
2. **Do not** add a `version:` key to `.claude-plugin/marketplace.json` — the manifest always wins silently. Update only the `description` field if the user-facing scope changed.
3. Move bullets from `## [Unreleased]` to a new dated section in `plugins/acss-utilities/CHANGELOG.md`.
4. If commands or scripts changed, update `plugins/acss-utilities/README.md` and the docs in this folder.
5. Run `tests/run.sh` to confirm structural validation, idempotency, and the bad-fixture self-tests pass.
6. The maintainer skill `.claude/skills/release-plugin/` automates steps 1–3; `.claude/skills/release-check/` audits the paperwork before a PR.

## Tests

`tests/run.sh` covers (post-`acss-utilities`):

- Manifest validation (every `plugins/<name>/.claude-plugin/plugin.json` has required fields) — Step 5
- **Step 8: utility validator** — runs `validate_utilities.py` over `plugins/acss-utilities/assets/`. Enforces selector grammar, `var()` fallbacks, no duplicate selectors per context, responsive parity, bridge dark-mode parity, and bundle-size budget (against `bundleSizeBudgetKb` from the tokens file).
- **Step 9: idempotency** — regenerates the bundle and per-family partials from `utilities.tokens.json` into a tmp dir and diffs against the committed copy. Any divergence fails the harness with the regenerate-and-commit instruction inline.

What is **not** in the harness yet:

- Bad-fixture self-tests (PascalCase selector, missing `var()` fallback, missing `[data-theme="dark"]` alias, oversize bundle). Each fixture would assert that the validator exits non-zero. Wiring is deferred — the `[Unreleased]` CHANGELOG entry tracks this.

One-time install for the test runner: `npm --prefix tests ci && pip3 install --user tinycss2`.

## Deferred work

- **`docs/visual-guide.md`** — Mermaid + SVG diagram-first portal mirroring `acss-kit/docs/visual-guide.md`. Requires authoring system-overview, command-flow, and class-anatomy diagrams. Deferred to keep the initial docs PR focused.
- **`assets/utilities.tokens.schema.json`** — JSON Schema for the source-of-truth file, for editor autocompletion. The `$schema` pointer was removed in commit `2af654e` rather than shipping a real schema; a future maintainer pass should add the schema and re-introduce the pointer.
- **`utility-author` and `utility-update` maintainer skills** — listed in `.claude/skills/` but not yet authored. Would automate "add a new family" and "re-validate after token-bridge or naming changes" respectively. Until then, follow the manual walkthrough in [How to add a new family](#how-to-add-a-new-family).

## Cross-plugin coordination

`acss-utilities` and `acss-kit` are deliberately decoupled. Pairing happens at the user level:

- `acss-kit` ships components + themes; `acss-utilities` ships the atomic layer.
- The bridge file is the **only** integration point — and it's regeneratable from any acss-kit theme via `/utility-bridge`.
- `/utility-add` does not invoke `acss-kit` flows; `/setup` (acss-kit) does not invoke `/utility-add`. Each plugin is self-contained.

This matters when bumping the upstream `@fpkit/acss` pin in `ATTRIBUTION.md` — the bump should not require coordinated changes to `acss-kit` unless a new fpkit role lands that requires a new alias in the bridge.
