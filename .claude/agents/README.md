# Subagents

Specialized review agents for the acss-plugins repo. Each agent is read-only — it reports findings but never modifies files.

Claude can invoke these automatically when context matches the agent's `description`. You can also invoke them explicitly by asking Claude to delegate to a named agent.

---

## skill-quality-reviewer

**File:** `skill-quality-reviewer.md`

Reviews a `SKILL.md` or `commands/*.md` file against plugin authoring conventions before you commit.

### Checks

| Check | What it verifies |
|---|---|
| Front-matter fields | `name` and `description` are present and non-empty |
| Step structure | Each numbered step is a single, testable action |
| GitHub URL hygiene | All fpkit/acss source references use full `github.com` URLs |
| No inline knowledge | Long reference material is delegated to `references/` docs |
| Delegation pattern | Command files call the master `SKILL.md`, not re-implement it |

### When Claude invokes it automatically

When you write or significantly edit a `SKILL.md` or `commands/*.md` file.

### Manual invocation

```
Review plugins/acss-app-builder/skills/acss-app-builder/SKILL.md using the skill-quality-reviewer agent
```

### Sample output

```
Reviewing: plugins/acss-app-builder/skills/acss-app-builder/SKILL.md

  [PASS] Front-matter fields (name, description)
  [FAIL] Step structure — step 3 bundles two unrelated actions
  [PASS] GitHub URL hygiene
  [PASS] No inline knowledge re-implementation
  [SKIP] Delegation pattern (not a command file)

1 issue found.
```

---

## python-script-reviewer

**File:** `python-script-reviewer.md`

Reviews a Python script under `plugins/*/scripts/` against the project contract defined in `CLAUDE.md`.

### Contract

All scripts in this repo must:

- Use Python 3 standard library only (no `pip install` dependencies)
- Write JSON to stdout
- Exit `0` on success, `1` on failure
- Include a `"reasons"` array in the JSON output

### Checks

| Check | What it verifies |
|---|---|
| Standard library only | No third-party imports |
| JSON output to stdout | Results serialized as JSON, not plain text |
| Exit codes | `0` success / `1` failure, differentiated |
| Reasons array | `"reasons"` key present in output dict |
| No hardcoded paths | All paths come from arguments or environment |

### When Claude invokes it automatically

When you add or significantly modify a script under `plugins/*/scripts/`.

### Manual invocation

```
Review plugins/acss-theme-builder/scripts/generate_palette.py using the python-script-reviewer agent
```

### Sample output

```
Reviewing: plugins/acss-theme-builder/scripts/generate_palette.py

  [PASS] Standard library only
  [PASS] JSON output to stdout
  [PASS] Exit codes
  [FAIL] Reasons array — "reasons" key not present in output dict
  [PASS] No hardcoded paths

1 issue found.
```

---

## component-reference-reviewer

**File:** `component-reference-reviewer.md`

Reviews a single component reference doc under `plugins/acss-kit/skills/components/references/components/<name>.md` against the canonical embedded-markdown shape and the catalog parity table. Pairs with the `/component-author` and `/component-update` skills.

### Checks

| Check | What it verifies |
|---|---|
| Verification banner | Top-of-file blockquote with `**Verified against fpkit source:**` and an `@fpkit/acss@<version>` reference |
| Canonical sections | All nine sections present and in order (Overview → Generation Contract → Props Interface → TSX Template → CSS Variables → SCSS Template → Accessibility → Usage Examples) |
| Generation Contract fields | `export_name`, `file`, `scss`, `imports`, `dependencies` all present |
| fpkit URL hygiene | All `github.com/shawn-sandy/acss` URLs pin to a tag/SHA, never `blob/main` |
| Catalog entry | Component appears in `catalog.md` "Verification Status" table |
| TSX Template imports | Only `react`, `'../ui'`, and relative paths to vendored components — never `@fpkit/acss` |

### How it gets invoked

Three triggers, none of them via a `settings.json` hook (no PostToolUse hook for component reference docs is currently wired):

- **Model-invocation** — Claude routes to the agent when the request matches its `description` (e.g. authoring or editing a `references/components/<name>.md` file in a maintenance conversation).
- **From the `/component-update` skill** — that skill explicitly delegates to this agent on every run.
- **Manually via slash command** — `/review-component <path>` (see below).

### Manual invocation

```
/review-component plugins/acss-kit/skills/components/references/components/button.md
```

### Sample output

```
Reviewing: plugins/acss-kit/skills/components/references/components/button.md

  [PASS] Verification banner
  [PASS] Canonical sections
  [PASS] Generation Contract fields
  [PASS] fpkit URL hygiene
  [PASS] Catalog entry
  [PASS] TSX Template imports

All checks passed — reference doc follows the canonical shape.
```

---

## theme-reference-reviewer

**File:** `theme-reference-reviewer.md`

Reviews the acss-kit theme references and bundled brand presets for cross-source parity. Cross-checks role names, contrast pair definitions, and OKLCH algorithm constants between markdown documentation, the JSON schema, and the Python scripts. Pairs with the `/style-author`, `/style-update`, and `/plugin-health` skills.

### Checks

| Check | What it verifies |
|---|---|
| Role parity | Roles in `role-catalogue.md`, `theme.schema.json` `$defs.palette`, and `tokens_to_css.py:ROLE_GROUPS` are identical sets |
| Required vs optional | Required-role annotations in markdown match the `required` array in `theme.schema.json` |
| WCAG contrast pair parity | Contrast pair table in `styles/SKILL.md` matches `validate_theme.py:PAIRS` |
| OKLCH algorithm parity | Lightness anchors and hue offsets in `palette-algorithm.md` match constants in `generate_palette.py` |
| Bundled brand preset validation | Every `assets/brand-presets/*.css` passes `validate_theme.py` (SKIP if directory absent) |

### How it gets invoked

Three triggers, none of them via a `settings.json` hook (no PostToolUse hook for theme references is currently wired):

- **Model-invocation** — Claude routes to the agent when the request matches its `description` (e.g. authoring or editing a file under `skills/styles/references/` or `assets/theme.schema.json` in a maintenance conversation).
- **From the `/style-author`, `/style-update`, and `/plugin-health` skills** — each of those calls this agent during their own workflow.
- **Manually via slash command** — `/review-themes` (no arguments).

### Manual invocation

```
/review-themes
```

### Sample output

```
Reviewing: theme references

  [PASS] Role parity
  [PASS] Required vs optional consistency
  [PASS] WCAG contrast pair parity
  [PASS] OKLCH algorithm parity
  [PASS] Bundled brand preset validation

All checks passed — theme references are internally consistent.
```

---

## Adding a new agent

1. Create `.claude/agents/<name>.md` with a YAML front-matter block:

```yaml
---
name: <name>
description: <one-line description — Claude uses this to decide when to invoke automatically>
---
```

2. Write the agent body as instructions addressed to Claude.
3. End with "Do not modify any files. Report only." if the agent is review-only.
4. Add an entry to this README.
