---
name: prompt-book
description: Display the bundled prompt book — a copy-paste catalogue of natural-language prompts mapped to every shipped slash command across acss-kit and acss-utilities. Use when the user runs /prompt-book or asks to see example prompts, prompt templates, or what they can ask Claude Code to do with these plugins.
---

# Prompt Book

Read-only display skill. Backs the `/prompt-book` slash command. The skill never edits files — it only reads `${CLAUDE_PLUGIN_ROOT}/docs/prompt-book.md` and prints content into the transcript.

## Source of truth

The prompt book itself lives at `${CLAUDE_PLUGIN_ROOT}/docs/prompt-book.md`. Treat it as authoritative: never paraphrase, summarise, or reformat the content when displaying it. To update the book, edit that file directly and bump `plugin.json` per the repo's pre-submit checklist.

## Workflow

### Mode 1 — full book (no argument)

1. Read `${CLAUDE_PLUGIN_ROOT}/docs/prompt-book.md`.
2. Print the file verbatim into the transcript so the user can copy any prompt directly.

### Mode 2 — single section (`<section-number>` argument)

1. Read `${CLAUDE_PLUGIN_ROOT}/docs/prompt-book.md`.
2. Locate the section heading that begins with `## <number>.` (e.g. `## 5. Generate a theme from a brand color`).
3. Print only that section — from the matched heading through the next `---` separator (or end of file if no separator follows).
4. If `<number>` does not match any section heading, fall back to Mode 3.

### Mode 3 — table of contents (invalid argument fallback)

1. Read `${CLAUDE_PLUGIN_ROOT}/docs/prompt-book.md`.
2. Extract every top-level `## <number>. <title>` heading.
3. Print the list as a numbered table of contents and prompt the user to re-run with a valid number.

## Constraints

- Read-only: never call Write, Edit, or Bash that mutates state.
- Verbatim output: do not collapse whitespace, change wording, or strip formatting.
- The book's section numbers are stable identifiers — match `## <n>.` exactly (digit then period). Do not invent fuzzy matches.
