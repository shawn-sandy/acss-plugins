---
description: Review a component reference doc against the canonical embedded-markdown shape and catalog parity. Runs in the background.
argument-hint: <path/to/references/components/file.md>
allowed-tools: Agent
---

Review the component reference doc at `$ARGUMENTS` using the `component-reference-reviewer` agent. Run the agent in the background so the user can continue working. When the agent completes, report its findings.

If no argument is provided, ask the user which reference doc to review. The expected location is `plugins/acss-kit/skills/components/references/components/<name>.md`.
