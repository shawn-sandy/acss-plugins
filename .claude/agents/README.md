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
