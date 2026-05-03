---
description: Display the acss-kit prompt book — copy-paste prompts for every shipped slash command
argument-hint: [section-number]
allowed-tools: Read
---

# /prompt-book

Display the acss-kit + acss-utilities prompt book — a catalogue of copy-paste prompts mapped to every shipped slash command.

## Usage

```
/prompt-book
/prompt-book <section-number>
```

**Examples:**

```
/prompt-book
/prompt-book 5
```

## Workflow

### `/prompt-book` (no arguments)

1. Read `${CLAUDE_PLUGIN_ROOT}/docs/prompt-book.md`.
2. Print the file verbatim so the user can copy any prompt directly out of the transcript.
3. Do not edit, summarise, or paraphrase. The book is the source of truth.

### `/prompt-book <section-number>`

1. Read `${CLAUDE_PLUGIN_ROOT}/docs/prompt-book.md`.
2. Locate the section heading that begins with `## <number>.` (e.g. `## 5. Generate a theme from a brand color`).
3. Print only that section — heading through the next `---` separator.
4. If the number does not match a section, print the full table of contents (top-level `##` headings) so the user can pick a valid one.

## Notes

- This command is read-only. It never edits files.
- The book lives at `plugins/acss-kit/docs/prompt-book.md` in the repo and is bundled with the plugin install — every user gets it automatically.
- To update the book, edit that file and bump `plugin.json` per the repo's pre-submit checklist.
