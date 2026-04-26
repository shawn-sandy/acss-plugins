---
name: add-command
description: Scaffold a new slash command for a plugin — creates the command .md with front-matter and adds a stub section to SKILL.md.
disable-model-invocation: false
---

# /add-command

Usage: `/add-command <plugin-name> <command-name>`

Example: `/add-command acss-kit theme-export`

## Steps

1. **Validate inputs** — confirm `<plugin-name>` is one of the existing plugin directories. If `<command-name>` already exists in `commands/`, stop and warn.

2. **Ask the user** (via AskUserQuestion):
   - One-line description of what the command does
   - Argument hint (e.g., `<name> [--force]`) — leave empty if none
   - Which tools the command needs (default: `Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion`)
   - Which skill owns the workflow (for `acss-kit`, usually `components` or `styles`)

3. **Create `<plugin>/commands/<command-name>.md`**:

```markdown
---
description: <user's description>
argument-hint: <argument-hint>
allowed-tools: <tools>
---

<One sentence summary of what this command does.>

Follow the `/<command-name>` workflow in the owning skill:
`plugins/<plugin>/skills/<skill>/SKILL.md`

**Quick checklist:**

1. TODO — fill in steps
2. ...

**Safety:** refuse on dirty git tree and on any existing non-empty target file unless `--force`.
```

4. **Add a stub section to `plugins/<plugin>/skills/<skill>/SKILL.md`** at the end of the file:

```markdown
## /<command-name>

> TODO: implement this workflow

### Steps

1. ...
```

5. **Print a summary**:
   - Files created/modified
   - Reminder: "Fill in the SKILL.md stub and the command checklist before testing."

Do not implement the command logic. The user fills in the SKILL.md stub.
