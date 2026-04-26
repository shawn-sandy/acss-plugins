# Maintainer Commands

Slash commands at the repo root that delegate to one of the [review agents](agents/README.md). All four are **read-only** — they spawn a background agent that reports findings and writes nothing.

| Command | Argument | Description | Dispatches to |
|---|---|---|---|
| [`/review-component`](commands/review-component.md) | `<path/to/references/components/<name>.md>` | Verify a component reference doc against the canonical embedded-markdown shape and catalog parity table. | [`component-reference-reviewer`](agents/README.md#component-reference-reviewer) |
| [`/review-script`](commands/review-script.md) | `<path/to/script.py>` | Audit a single Python script against the project contract (stdlib only, JSON to stdout, exit codes, reasons array). | [`python-script-reviewer`](agents/README.md#python-script-reviewer) |
| [`/review-scripts`](commands/review-scripts.md) | _(none)_ | Audit every `plugins/*/scripts/*.py` in parallel and report a summary table. | [`python-script-reviewer`](agents/README.md#python-script-reviewer) (one per script) |
| [`/review-themes`](commands/review-themes.md) | _(none)_ | Cross-source parity audit of the acss-kit theme references — role catalogue, palette algorithm, theme schema, bundled brand presets — against the Python scripts. | [`theme-reference-reviewer`](agents/README.md#theme-reference-reviewer) |

## How invocation works

Each command file is a thin wrapper: front-matter declares `allowed-tools: Agent`, and the body asks Claude to invoke the named agent in the background. The agent reads the target file(s), runs its checks, and reports findings — no edits.

If you want the agent to *also* fix what it finds, run the corresponding **authoring/updating skill** instead (see [`skills/README.md`](skills/README.md)). For example, `/component-update` runs the same review and surfaces drift; `/review-component` only reports.

## Adding a new command

The repo's [`/add-command`](skills/add-command/SKILL.md) skill scaffolds a new command in a plugin (`plugins/<name>/commands/`). For a repo-root maintainer command like the ones above, write the `.md` file directly:

1. Create `.claude/commands/<command-name>.md`.
2. Front-matter: `description:`, `argument-hint:` (if it takes an argument), `allowed-tools:` (usually just `Agent`).
3. Body: one paragraph instructing Claude to dispatch to the named agent in the background.
4. Add a row to the table above.
