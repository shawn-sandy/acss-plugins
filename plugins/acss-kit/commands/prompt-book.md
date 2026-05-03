---
description: Display the acss-kit prompt book — copy-paste prompts for every shipped slash command
argument-hint: [section-number]
allowed-tools: Read
---

# /prompt-book

Display the acss-kit + acss-utilities prompt book — a catalogue of copy-paste prompts mapped to every shipped slash command.

Follow the workflow in `${CLAUDE_PLUGIN_ROOT}/skills/prompt-book/SKILL.md`.

## Usage

```text
/prompt-book
/prompt-book <section-number>
```

**Examples:**

```text
/prompt-book
/prompt-book 5
```

**Arguments:**

- `<section-number>` — *optional*. Print only the section whose heading begins with `## <number>.`. Invalid numbers fall back to a table of contents.

**Quick steps:**

1. Read prompt-book — load `${CLAUDE_PLUGIN_ROOT}/docs/prompt-book.md`.
2. Print full book — when no argument is supplied, emit the file verbatim.
3. Print section by number — when `<section-number>` matches a `## <n>.` heading, emit that section through the next `---` separator.
4. Show TOC on invalid number — list every `## <n>. <title>` and prompt the user to re-run.

## Notes

- This command is read-only. It never edits files.
- The book is bundled at `plugins/acss-kit/docs/prompt-book.md` and ships with every plugin install. Update it there and bump `plugin.json` per the repo's pre-submit checklist.
