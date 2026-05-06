---
name: audit-subagents
description: Audit subagent definition files against Claude Code best practices — front-matter, tool restrictions, description quality, plugin compatibility, system-prompt structure. Use when reviewing existing subagents, before committing a new agent, or asking what's wrong with our subagents.
disable-model-invocation: false
---

# /audit-subagents

Usage:

- `/audit-subagents` — audit every subagent file in the repo
- `/audit-subagents <path>` — audit a single agent file or a directory of agent files

Reference: https://code.claude.com/docs/en/sub-agents

Read-only. Does NOT modify any files.

## Step 1 — Resolve targets

Build the list of files to audit:

- If an argument is provided and it points to a `.md` file → audit that one file.
- If the argument is a directory → audit every `*.md` under it (non-recursive into `references/` or `commands/`).
- If no argument is provided → audit:
  - `.claude/agents/*.md` (excluding `README.md`)
  - `plugins/*/agents/*.md` (if any plugin ships subagents)

If the resolved list is empty, print `No subagent files found.` and stop.

## Step 2 — Run the checks

For each file, parse the YAML front-matter and the markdown body, then run the eight checks below. Track per-file PASS / WARN / FAIL outcomes; do not stop on the first failure.

Treat any file under `plugins/*/agents/` as a **plugin subagent** — checks 7 and 8 apply differently for those.

### Check 1 — Required front-matter

The docs list `name` and `description` as the only required fields.

- FAIL if either is missing or empty.
- PASS otherwise.

### Check 2 — `name` format

The docs require lowercase letters and hyphens.

- FAIL if `name` does not match `^[a-z][a-z0-9-]*$` (e.g. uppercase, underscores, leading digit).
- WARN if `name` does not match the file basename (sans `.md`) — these should agree so `/agents` and the file system stay aligned.
- PASS otherwise.

### Check 3 — `description` quality

Claude routes to a subagent based on its description, so it must convey **when to delegate**.

- FAIL if `description` is shorter than 40 characters — too vague to drive routing.
- WARN if `description` does not contain at least one trigger phrase. Trigger phrases include: `use when`, `use proactively`, `use immediately`, `use after`, `use before`, `invoke when`, `run when`, or a present-tense verb describing the input (`reviews`, `audits`, `validates`, `scaffolds`, `generates`).
- PASS otherwise.

### Check 4 — Tool restrictions

Subagents inherit every tool unless `tools` or `disallowedTools` is set. For a focused agent — especially a review-only one — that default is too broad.

- FAIL if the description contains any of `review`, `audit`, `validate`, `report`, `read-only`, `research` AND the front-matter has neither a `tools` allowlist excluding write tools nor a `disallowedTools` list containing `Write` and `Edit`.
- WARN if neither `tools` nor `disallowedTools` is set at all (the agent silently inherits everything).
- PASS otherwise.

### Check 5 — Read-only consistency

If the agent body ends with a phrase like "Do not modify any files" or "Report only", the front-matter must back that up.

- FAIL if the body declares read-only but `tools` includes any of `Write`, `Edit`, `NotebookEdit`, or `disallowedTools` does not deny them and `tools` is unset.
- PASS otherwise.

### Check 6 — System-prompt body

The body of the file becomes the agent's entire system prompt (the docs note subagents do not see Claude Code's own system prompt).

- FAIL if the body (everything after the closing `---`) is shorter than 100 characters or has no headings, numbered steps, or bullet checklist.
- WARN if the body has no explicit "Output format" / "Output" / "Report" section — without one the agent's reply shape is unpredictable.
- PASS otherwise.

### Check 7 — Plugin subagent compatibility (plugin agents only)

Per the docs, plugin-distributed subagents silently ignore `hooks`, `mcpServers`, and `permissionMode`.

- Skip this check for files outside `plugins/*/agents/`.
- FAIL if any of `hooks`, `mcpServers`, or `permissionMode` is set in a plugin agent's front-matter.
- PASS otherwise.

### Check 8 — Front-matter field whitelist

Warn on unknown keys so typos (`tool` vs `tools`, `description:` vs `descriptions:`) surface early.

The documented keys are:
`name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`.

- WARN once per unknown key per file.
- PASS if every key is on the list above.

## Step 3 — Render the report

Print one block per file, then a summary line:

```
Auditing: .claude/agents/skill-quality-reviewer.md

  [PASS] Required front-matter
  [PASS] name format
  [PASS] description quality
  [WARN] Tool restrictions — neither `tools` nor `disallowedTools` set; agent inherits everything
  [PASS] Read-only consistency
  [PASS] System-prompt body
  [SKIP] Plugin subagent compatibility (project-scope agent)
  [PASS] Front-matter field whitelist

== Summary ==
4 files audited.
0 FAIL  3 WARN  29 PASS  2 SKIP
```

If a single file is audited, omit the summary line.

If every check is PASS, print `All subagents follow Claude Code best practices.` after the summary.

## Step 4 — Suggested fixes

For each FAIL or WARN, append a one-line remediation hint to the bottom of the report:

- Missing `tools` allowlist on a review agent → `Add tools: Read, Grep, Glob to the front-matter`
- Plugin agent uses `hooks` → `Move the agent to .claude/agents/ or remove the hooks block`
- Body lacks structure → `Add a numbered "When invoked" section and an "Output format" section`
- `name` mismatch with filename → `Rename the file or update the name field so they match`

This skill does not modify any files. The maintainer applies fixes manually or by re-authoring with `/agents`.
