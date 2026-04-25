#!/usr/bin/env python3
"""
validate_spec.py — Validate acss-component-specs spec files against the schema.

Checks:
  - Required top-level fields present
  - format_version == 1
  - a11y block present for interactive components (or a11y.layout_only: true)
  - WCAG SC values valid against WCAG 2.2 list
  - props entries have required sub-fields
  - maps_to values are from the 7-kind discriminator set
  - --stale: scan project files for outdated generated stamps

Usage:
    python validate_spec.py specs/button.md
    python validate_spec.py                       # validates all specs/*.md
    python validate_spec.py --stale               # also scans project files
    python validate_spec.py specs/button.md --stale

Output: JSON to stdout.
Exit 0 = all valid. Exit 1 = one or more errors.
"""

import glob
import json
import re
import sys
from pathlib import Path

# Import parse_spec from same directory
sys.path.insert(0, str(Path(__file__).parent))
from parse_spec import parse_spec_file

REQUIRED_TOP_LEVEL = [
    'format_version', 'name', 'display_name', 'description',
    'fpkit_source', 'fpkit_version', 'a11y',
]

VALID_MAPS_TO = {'data-attr', 'data-attr-token', 'aria', 'prop', 'class', 'element', 'css-var'}

# WCAG 2.2 success criterion identifiers (A, AA, AAA)
VALID_WCAG_SCS = {
    '1.1.1', '1.2.1', '1.2.2', '1.2.3', '1.2.4', '1.2.5', '1.2.6', '1.2.7', '1.2.8', '1.2.9',
    '1.3.1', '1.3.2', '1.3.3', '1.3.4', '1.3.5', '1.3.6',
    '1.4.1', '1.4.2', '1.4.3', '1.4.4', '1.4.5', '1.4.6', '1.4.7', '1.4.8', '1.4.9',
    '1.4.10', '1.4.11', '1.4.12', '1.4.13',
    '2.1.1', '2.1.2', '2.1.3', '2.1.4',
    '2.2.1', '2.2.2', '2.2.3', '2.2.4', '2.2.5', '2.2.6',
    '2.3.1', '2.3.2', '2.3.3',
    '2.4.1', '2.4.2', '2.4.3', '2.4.4', '2.4.5', '2.4.6', '2.4.7', '2.4.8', '2.4.9', '2.4.10',
    '2.4.11', '2.4.12', '2.4.13',
    '2.5.1', '2.5.2', '2.5.3', '2.5.4', '2.5.5', '2.5.6', '2.5.7', '2.5.8',
    '3.1.1', '3.1.2', '3.1.3', '3.1.4', '3.1.5', '3.1.6',
    '3.2.1', '3.2.2', '3.2.3', '3.2.4', '3.2.5', '3.2.6',
    '3.3.1', '3.3.2', '3.3.3', '3.3.4', '3.3.5', '3.3.6', '3.3.7', '3.3.8', '3.3.9',
    '4.1.1', '4.1.2', '4.1.3',
}

# Pattern for generated-file stamps: // generated from <component>.md@<version>
STAMP_RE = re.compile(r'//\s*generated from\s+(\S+\.md)@(\S+)')


def _fail(reasons):
    print(json.dumps({"ok": False, "data": None, "reasons": reasons}))
    sys.exit(1)


def validate_single(spec_path):
    """Validate one spec file. Returns list of error strings (empty = valid)."""
    errors = []

    data, reasons = parse_spec_file(spec_path)
    if data is None:
        return reasons

    if reasons:
        errors.extend(reasons)

    fm = data.get('frontmatter', {})

    # Required top-level fields
    for field in REQUIRED_TOP_LEVEL:
        if field not in fm:
            errors.append(f"Missing required field: {field}")

    # format_version must be 1
    if 'format_version' in fm:
        fv = fm['format_version']
        if fv != 1 and fv != '1':
            errors.append(f"format_version must be 1, got: {fv!r}")

    # a11y block validation
    a11y = fm.get('a11y', {})
    if not isinstance(a11y, dict):
        errors.append("a11y must be a mapping with wcag/layout_only keys.")
    else:
        layout_only = a11y.get('layout_only', False)
        if layout_only is True or layout_only == 'true':
            # layout_only: true — exempt from WCAG requirement
            pass
        else:
            wcag = a11y.get('wcag', [])
            if not wcag:
                errors.append("a11y.wcag must be a non-empty list for interactive components. "
                               "Use a11y.layout_only: true to exempt layout-only components.")
            elif isinstance(wcag, list):
                for sc in wcag:
                    sc_str = str(sc)
                    if sc_str not in VALID_WCAG_SCS:
                        errors.append(f"a11y.wcag contains invalid WCAG 2.2 SC: {sc_str!r}. "
                                       "Check https://www.w3.org/TR/WCAG22/ for valid identifiers.")
            else:
                errors.append("a11y.wcag must be a list of WCAG SC strings.")

    # props validation
    props = fm.get('props', [])
    if isinstance(props, list):
        for idx, prop in enumerate(props):
            if not isinstance(prop, dict):
                errors.append(f"props[{idx}] must be a mapping.")
                continue
            if 'name' not in prop:
                errors.append(f"props[{idx}] missing required field: name")
            if 'maps_to' not in prop:
                errors.append(f"props[{idx}] ({prop.get('name', '?')}) missing required field: maps_to")
            elif prop['maps_to'] not in VALID_MAPS_TO:
                errors.append(f"props[{idx}] ({prop.get('name', '?')}) invalid maps_to: {prop['maps_to']!r}. "
                               f"Must be one of: {sorted(VALID_MAPS_TO)}")

    # fpkit_source must look like a URL
    source = fm.get('fpkit_source', '')
    if source and not str(source).startswith('https://'):
        errors.append(f"fpkit_source must be a full HTTPS URL, got: {source!r}")

    return errors


def find_stale_stamps(project_root='.'):
    """
    Scan project files for // generated from <component>.md@<version> stamps.
    Compare stamp version against current spec version.
    Returns list of {file, stamp_spec, stamp_version, current_version, stale} dicts.
    """
    results = []
    specs_dir = Path('specs')

    # Build a map of spec name → current version
    spec_versions = {}
    if specs_dir.exists():
        for spec_file in specs_dir.glob('*.md'):
            data, _ = parse_spec_file(str(spec_file))
            if data:
                fm = data.get('frontmatter', {})
                spec_name = fm.get('name', spec_file.stem)
                # Look for a version field — not standard yet, use format_version as proxy
                version = str(fm.get('version', fm.get('format_version', '1')))
                spec_versions[spec_file.name] = version

    # Scan project source files for stamps
    project = Path(project_root)
    for ext in ('*.tsx', '*.ts', '*.jsx', '*.js', '*.astro', '*.html', '*.css', '*.scss'):
        for src_file in project.rglob(ext):
            # Skip node_modules and .acss-staging
            parts = src_file.parts
            if 'node_modules' in parts or '.acss-staging' in parts:
                continue
            try:
                text = src_file.read_text(encoding='utf-8', errors='ignore')
                for m in STAMP_RE.finditer(text):
                    spec_filename = m.group(1)
                    stamp_ver = m.group(2)
                    current_ver = spec_versions.get(spec_filename)
                    is_stale = current_ver is not None and stamp_ver != current_ver
                    results.append({
                        "file": str(src_file),
                        "stamp_spec": spec_filename,
                        "stamp_version": stamp_ver,
                        "current_version": current_ver,
                        "stale": is_stale,
                    })
            except Exception:
                continue

    return results


def main():
    args = sys.argv[1:]
    do_stale = '--stale' in args
    spec_args = [a for a in args if not a.startswith('--')]

    if spec_args:
        spec_files = spec_args
    else:
        # Validate all specs
        spec_files = sorted(glob.glob('specs/*.md'))
        if not spec_files:
            print(json.dumps({
                "ok": True,
                "data": {"validated": 0, "errors": {}, "stale": []},
                "reasons": ["No spec files found in specs/."]
            }))
            sys.exit(0)

    all_errors = {}
    for spec_path in spec_files:
        errs = validate_single(spec_path)
        if errs:
            all_errors[spec_path] = errs

    stale_results = []
    if do_stale:
        stale_results = find_stale_stamps()

    ok = len(all_errors) == 0
    reasons = []
    for path, errs in all_errors.items():
        for e in errs:
            reasons.append(f"{path}: {e}")

    stale_list = [r for r in stale_results if r.get('stale')]
    for s in stale_list:
        reasons.append(f"STALE: {s['file']} references {s['stamp_spec']}@{s['stamp_version']} "
                       f"(current: {s['current_version']})")

    if stale_list:
        ok = False

    data = {
        "validated": len(spec_files),
        "errors": all_errors,
        "stale": stale_results,
    }
    print(json.dumps({"ok": ok, "data": data, "reasons": reasons}, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
