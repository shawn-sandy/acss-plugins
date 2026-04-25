---
description: Scaffold a new component spec by fetching its fpkit source
argument-hint: <component> [--refresh]
allowed-tools: WebFetch, Write, Read, Bash
---

Scaffolds `specs/<component>.md` from live fpkit source.

1. Run `python scripts/fetch_fpkit_source.py <component> [--refresh]` to populate `assets/fpkit-cache/`.
2. Read the cached source; extract props, CSS vars, data attributes, and events.
3. Write `specs/<component>.md` using the frontmatter shape from `references/spec-format.md`.
4. Cite the returned SHA in `fpkit_version`; set `format_version: 1`.
5. Confirm the spec validates cleanly with `python scripts/validate_spec.py specs/<component>.md`.

`--refresh` forces a re-fetch even if a cached version exists.

Follow SKILL.md § /spec-add for the full authoring workflow.
