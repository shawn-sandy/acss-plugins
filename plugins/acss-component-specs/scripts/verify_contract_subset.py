#!/usr/bin/env python3
"""
verify_contract_subset.py — Assert that every field in kit-builder Generation
Contract blocks appears in the acss-component-specs spec frontmatter shape.

Reads kit-builder reference docs, extracts ## Generation Contract sections,
and checks each declared field against the spec-format.md schema fields.

Run as part of /release-check for acss-component-specs.

Usage:
    python verify_contract_subset.py

Output: JSON to stdout.
Exit 0 = all contract fields present in spec shape. Exit 1 = missing fields.
"""

import json
import re
import sys
from pathlib import Path


# Kit-builder component reference files to check
KIT_BUILDER_REFS_PATH = (
    Path(__file__).parent.parent.parent /
    'acss-kit-builder/skills/acss-kit-builder/references/components'
)

# Known spec frontmatter field names (from references/spec-format.md schema)
SPEC_FRONTMATTER_FIELDS = {
    'format_version',
    'name',
    'display_name',
    'description',
    'fpkit_source',
    'fpkit_version',
    'component_type',
    'a11y',
    'props',
    'events',
    'framework_notes',
    'css_vars',
    'theme_dependencies',
}

# Mapping from kit-builder Generation Contract field names to spec field names
# (fields that exist under a different name in the spec)
CONTRACT_TO_SPEC_FIELD = {
    'export_name': 'display_name',
    'file': 'name',           # file: button.tsx → name: button
    'scss': 'name',           # scss: button.scss → name: button
    'imports': 'framework_notes',  # imports are framework-specific
    'dependencies': 'framework_notes',  # dependencies are in framework_notes
}

# Generation Contract block pattern
CONTRACT_BLOCK_RE = re.compile(
    r'## Generation Contract\s*```[^\n]*\n(.*?)```',
    re.DOTALL
)
CONTRACT_FIELD_RE = re.compile(r'^([a-z_]+):\s*(.+)$', re.MULTILINE)


def _fail(reasons):
    print(json.dumps({"ok": False, "data": None, "reasons": reasons}))
    sys.exit(1)


def extract_contract_fields(ref_text):
    """Extract all field names from ## Generation Contract blocks."""
    fields = set()
    for m in CONTRACT_BLOCK_RE.finditer(ref_text):
        block = m.group(1)
        for fm in CONTRACT_FIELD_RE.finditer(block):
            fields.add(fm.group(1).strip())
    return fields


def check_field_in_spec(field):
    """Return True if a contract field is covered by the spec shape."""
    # Direct match
    if field in SPEC_FRONTMATTER_FIELDS:
        return True
    # Mapped field
    if field in CONTRACT_TO_SPEC_FIELD:
        mapped = CONTRACT_TO_SPEC_FIELD[field]
        return mapped in SPEC_FRONTMATTER_FIELDS
    return False


def main():
    if not KIT_BUILDER_REFS_PATH.exists():
        _fail([f"Kit-builder references directory not found: {KIT_BUILDER_REFS_PATH}"])

    ref_files = list(KIT_BUILDER_REFS_PATH.glob('*.md'))
    if not ref_files:
        _fail([f"No .md files found in {KIT_BUILDER_REFS_PATH}"])

    missing = {}
    all_fields_seen = set()

    for ref_file in sorted(ref_files):
        text = ref_file.read_text(encoding='utf-8')
        fields = extract_contract_fields(text)
        if not fields:
            continue
        all_fields_seen.update(fields)
        missing_for_file = [f for f in fields if not check_field_in_spec(f)]
        if missing_for_file:
            missing[ref_file.name] = missing_for_file

    ok = len(missing) == 0
    reasons = []
    for fname, fields in missing.items():
        for f in fields:
            reasons.append(
                f"{fname}: contract field '{f}' has no corresponding spec frontmatter field. "
                f"Add it to SPEC_FRONTMATTER_FIELDS or CONTRACT_TO_SPEC_FIELD mapping."
            )

    print(json.dumps({
        "ok": ok,
        "data": {
            "ref_files_checked": len(ref_files),
            "contract_fields_seen": sorted(all_fields_seen),
            "missing": missing,
        },
        "reasons": reasons,
    }, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
