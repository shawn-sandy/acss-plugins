---
description: Review all Python scripts across all plugins against the project contract. Spawns one background agent per script and reports all findings when complete.
allowed-tools: Agent, Bash, Glob
---

1. Use Glob to find all files matching `plugins/*/scripts/*.py`.
2. For each script found, spawn a separate `python-script-reviewer` agent in the background — all agents run in parallel.
3. When all agents complete, consolidate the results and report a summary table: one row per script showing PASS/FAIL per check and total issues found.
