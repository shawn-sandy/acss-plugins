#!/usr/bin/env python3
"""
parse_spec.py — Parse an acss-component-specs spec file into JSON.

Reads the YAML frontmatter and section index from a spec .md file.
Auto-derives theme_dependencies by scanning body text for var(--color-*, ...) patterns.

Usage:
    python parse_spec.py specs/button.md

Output: JSON to stdout
  {
    "ok": true,
    "data": {
      "frontmatter": { ...parsed fields... },
      "sections": ["SCSS", "Usage"],
      "theme_dependencies": ["--color-primary", "--color-text-inverse"]
    },
    "reasons": []
  }

Exit 0 on success, 1 on failure.
"""

import json
import re
import sys
from pathlib import Path


# Supported YAML scalar types — no anchors, aliases, or multiline flow.
_WCAG_SC_RE = re.compile(r'\b\d+\.\d+\.\d+\b')
_COLOR_VAR_RE = re.compile(r'var\(\s*(--color-[a-z0-9-]+)')
_SECTION_RE = re.compile(r'^##\s+(.+)$', re.MULTILINE)
_FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)


def _fail(reasons):
    print(json.dumps({"ok": False, "data": None, "reasons": reasons}))
    sys.exit(1)


def _parse_yaml_frontmatter(text):
    """
    Minimal YAML parser — handles only the shapes used in spec frontmatter.
    Supports: scalars, lists, nested mappings (2-level), quoted strings.
    Rejects: anchors (&), aliases (*), multiline flow ({...} spanning lines).
    """
    reasons = []
    result = {}

    # Reject anchors and aliases
    if re.search(r'^\s*&\w|^\s*\*\w', text, re.MULTILINE):
        reasons.append("YAML anchors and aliases are not supported in spec frontmatter.")
        return None, reasons

    lines = text.split('\n')
    i = 0
    current_key = None
    current_list = None
    current_mapping_key = None
    current_mapping = None
    indent_stack = []

    def flush_list():
        nonlocal current_key, current_list
        if current_key and current_list is not None:
            result[current_key] = current_list
            current_key = None
            current_list = None

    def flush_mapping():
        nonlocal current_mapping_key, current_mapping
        if current_mapping_key and current_mapping is not None:
            result[current_mapping_key] = current_mapping
            current_mapping_key = None
            current_mapping = None

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # Skip blank lines
        if not stripped:
            i += 1
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level key: value
        if indent == 0:
            flush_list()
            flush_mapping()

            # key: value or key:
            m = re.match(r'^([a-z_][a-z0-9_-]*):\s*(.*)', stripped)
            if not m:
                i += 1
                continue

            key = m.group(1)
            val = m.group(2).strip()

            if val == '' or val is None:
                # Could be a mapping or list block
                current_key = key
                current_list = None
                current_mapping = None
                i += 1
                # Peek ahead to see if next non-empty line is a list item or mapping
                j = i
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    next_stripped = lines[j].strip()
                    if next_stripped.startswith('- ') or next_stripped == '-':
                        current_list = []
                    elif re.match(r'^[a-z_][a-z0-9_-]*:', next_stripped):
                        current_mapping = {}
                        current_mapping_key = key
                continue
            else:
                # Scalar value
                val = _unquote(val)
                result[key] = val

        elif indent == 2:
            # List item under current_key
            m_item = re.match(r'^\s{2}-\s+(.*)', stripped if False else line)
            m_item = re.match(r'^  -\s*(.*)', line)
            if m_item and current_list is not None:
                item_val = m_item.group(1).strip()
                if item_val.startswith('{'):
                    # Inline mapping — parse it
                    obj = _parse_inline_mapping(item_val, reasons)
                    current_list.append(obj)
                elif item_val == '' or item_val is None:
                    # Block mapping item — collect sub-lines
                    obj = {}
                    i += 1
                    while i < len(lines):
                        sub_line = lines[i]
                        sub_indent = len(sub_line) - len(sub_line.lstrip())
                        if sub_indent < 4 and sub_line.strip():
                            break
                        sub_m = re.match(r'^\s{4}([a-z_][a-z0-9_-]*):\s*(.*)', sub_line)
                        if sub_m:
                            obj[sub_m.group(1)] = _unquote(sub_m.group(2).strip())
                        i += 1
                    current_list.append(obj)
                    continue
                else:
                    current_list.append(_unquote(item_val))
            elif current_mapping is not None:
                # Nested key: value inside a mapping block
                sub_m = re.match(r'^  ([a-z_][a-z0-9_-]*):\s*(.*)', line)
                if sub_m:
                    current_mapping[sub_m.group(1)] = _unquote(sub_m.group(2).strip())

        elif indent == 4:
            # Nested sub-mapping (e.g. framework_notes.react.strategy)
            if current_mapping is not None:
                sub_m = re.match(r'^    ([a-z_][a-z0-9_-]*):\s*(.*)', line)
                if sub_m:
                    sub_key = sub_m.group(1)
                    sub_val = _unquote(sub_m.group(2).strip())
                    # The parent key is current_mapping_key; nest under last sub-mapping
                    # For framework_notes, we need 3-level nesting
                    # Check if current_mapping has a pending sub-dict
                    if '_current_sub' in current_mapping:
                        current_mapping['_current_sub'][sub_key] = sub_val
                    else:
                        current_mapping[sub_key] = sub_val

        elif indent == 6:
            # 3-level nesting: framework_notes.react.{strategy,dependencies,caveats}
            if current_mapping is not None and '_current_sub' in current_mapping:
                sub_m = re.match(r'^      ([a-z_][a-z0-9_-]*):\s*(.*)', line)
                if sub_m:
                    current_mapping['_current_sub'][sub_m.group(1)] = _unquote(sub_m.group(2).strip())

        i += 1

    flush_list()
    flush_mapping()

    # Clean up internal tracking keys
    for k in list(result.keys()):
        if k.startswith('_'):
            del result[k]

    return result, reasons


def _parse_inline_mapping(text, reasons):
    """Parse a simple YAML inline mapping: {key: value, key2: value2}"""
    text = text.strip()
    if text.startswith('{') and text.endswith('}'):
        text = text[1:-1]
    obj = {}
    for part in text.split(','):
        part = part.strip()
        if ':' in part:
            k, _, v = part.partition(':')
            obj[k.strip()] = _unquote(v.strip())
    return obj


def _unquote(val):
    """Strip surrounding quotes from a YAML scalar value."""
    if not val:
        return val
    if (val.startswith('"') and val.endswith('"')) or \
       (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    # Booleans
    if val.lower() == 'true':
        return True
    if val.lower() == 'false':
        return False
    # Try integer
    try:
        return int(val)
    except ValueError:
        pass
    return val


def parse_spec_file(path):
    """Parse a spec .md file. Returns (data_dict, reasons_list)."""
    try:
        content = Path(path).read_text(encoding='utf-8')
    except FileNotFoundError:
        return None, [f"File not found: {path}"]
    except Exception as e:
        return None, [f"Could not read {path}: {e}"]

    m = _FRONTMATTER_RE.match(content)
    if not m:
        return None, ["No YAML frontmatter block found (expected --- ... --- at top of file)."]

    fm_text = m.group(1)
    body = content[m.end():]

    frontmatter, fm_reasons = _parse_yaml_frontmatter(fm_text)
    if frontmatter is None:
        return None, fm_reasons

    # Extract section headings from body
    sections = _SECTION_RE.findall(body)

    # Auto-derive theme_dependencies from var(--color-*) in body
    color_vars = list(dict.fromkeys(_COLOR_VAR_RE.findall(body)))  # unique, ordered

    # Also scan css_vars defaults in frontmatter for color references
    if isinstance(frontmatter.get('css_vars'), list):
        for cv in frontmatter['css_vars']:
            if isinstance(cv, dict):
                default_val = str(cv.get('default', ''))
                for match in _COLOR_VAR_RE.findall(default_val):
                    if match not in color_vars:
                        color_vars.append(match)

    data = {
        "frontmatter": frontmatter,
        "sections": sections,
        "theme_dependencies": color_vars,
    }
    return data, fm_reasons


def main():
    if len(sys.argv) < 2:
        _fail(["Usage: parse_spec.py <spec-file>"])

    path = sys.argv[1]
    data, reasons = parse_spec_file(path)

    if data is None:
        _fail(reasons)

    output = {"ok": True, "data": data, "reasons": reasons}
    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == '__main__':
    main()
