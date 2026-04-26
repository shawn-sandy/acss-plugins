---
description: Review the acss-kit theme references for cross-source parity (role-catalogue, palette-algorithm, theme-schema, brand-presets) against the Python scripts and JSON schema.
allowed-tools: Agent
---

Invoke the `theme-reference-reviewer` agent to audit the theme references and bundled brand presets. The agent reads `plugins/acss-kit/skills/styles/references/*`, `plugins/acss-kit/assets/theme.schema.json`, the theme-related Python scripts, and any bundled brand presets, then reports cross-source parity findings.

Run the agent in the background so the user can continue working. When the agent completes, report its findings.
