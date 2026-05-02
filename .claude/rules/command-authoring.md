---
paths:
  - "plugins/*/commands/*.md"
---

# Command File Conventions

- Body must delegate to the master SKILL.md — never re-implement logic inline
- Front-matter shape:
  ```yaml
  ---
  description: <one-line description>
  argument-hint: [--option] [--force]
  allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
  ---
  ```
