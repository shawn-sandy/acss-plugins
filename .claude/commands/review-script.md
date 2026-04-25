---
description: Review a Python script against the project contract (stdlib only, JSON stdout, exit codes, reasons array). Runs in the background.
argument-hint: <path/to/script.py>
allowed-tools: Agent
---

Review the script at `$ARGUMENTS` using the `python-script-reviewer` agent. Run the agent in the background so the user can continue working. When the agent completes, report its findings.

If no argument is provided, ask the user which script to review.
