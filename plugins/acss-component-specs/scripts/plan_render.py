#!/usr/bin/env python3
"""
plan_render.py — Given a spec and render target, output the dependency tree and file manifest.

The LLM reads this JSON to know which files to emit and in what bottom-up order.

Usage:
    python plan_render.py specs/button.md --target=react
    python plan_render.py specs/dialog.md --target=all
    python plan_render.py specs/card.md   --target=html

Output: JSON to stdout.
  {
    "ok": true,
    "data": {
      "component": "button",
      "targets": ["react"],
      "dependency_order": ["button"],
      "manifest": {
        "react": [
          {"file": "button/button.tsx", "type": "component"},
          {"file": "button/button.scss", "type": "style"}
        ]
      },
      "staging_base": ".acss-staging"
    },
    "reasons": []
  }
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from parse_spec import parse_spec_file

ALL_TARGETS = ['react', 'html', 'astro']

# Component dependency graph — which components must be generated before each one.
# Used for bottom-up ordering.
DEPENDENCY_GRAPH = {
    'button': [],
    'card': [],
    'card-title': ['card'],
    'card-content': ['card'],
    'card-footer': ['card'],
    'dialog': ['button'],
    'alert': [],
    'stack': [],
    'nav': [],
    'nav-link': ['nav'],
}

# File manifest templates per framework.
# Keys: component name → list of {file, type} dicts.
def _react_manifest(component, is_compound_part=False):
    """React render manifest for a component."""
    if is_compound_part:
        # Compound sub-parts are emitted inside the parent component file
        return []
    name = component.replace('-', '_').lower()
    slug = component.lower()
    return [
        {"file": f"{slug}/{slug}.tsx", "type": "component"},
        {"file": f"{slug}/{slug}.scss", "type": "style"},
    ]


def _html_manifest(component, is_compound_part=False):
    """HTML render manifest for a component."""
    if is_compound_part:
        return []
    slug = component.lower()
    return [
        {"file": f"{slug}/{slug}.html", "type": "component"},
        {"file": f"{slug}/{slug}.css", "type": "style"},
    ]


def _astro_manifest(component, is_compound_part=False):
    """Astro render manifest for a component."""
    if is_compound_part:
        return []
    slug = component.lower()
    display = ''.join(w.capitalize() for w in slug.split('-'))
    return [
        {"file": f"{slug}/{display}.astro", "type": "component"},
        {"file": f"{slug}/{slug}.scss", "type": "style"},
    ]


COMPOUND_PARTS = {'card-title', 'card-content', 'card-footer', 'nav-link'}


def _resolve_targets(target_arg):
    """Resolve --target= argument to a list of framework names."""
    if not target_arg or target_arg == 'all':
        return ALL_TARGETS
    targets = [t.strip() for t in target_arg.split(',')]
    invalid = [t for t in targets if t not in ALL_TARGETS]
    if invalid:
        return None, [f"Unknown target(s): {invalid}. Valid: {ALL_TARGETS}"]
    return targets, []


def _topological_order(component, graph):
    """Return components in bottom-up (dependency-first) order."""
    visited = []
    def visit(c):
        for dep in graph.get(c, []):
            if dep not in visited:
                visit(dep)
        if c not in visited:
            visited.append(c)
    visit(component)
    return visited


def _fail(reasons):
    print(json.dumps({"ok": False, "data": None, "reasons": reasons}))
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if not args:
        _fail(["Usage: plan_render.py <spec-file> [--target=react|html|astro|all]"])

    spec_path = args[0]
    target_arg = 'all'
    for a in args[1:]:
        if a.startswith('--target='):
            target_arg = a.split('=', 1)[1]

    # Parse spec to get component name
    data, reasons = parse_spec_file(spec_path)
    if data is None:
        _fail(reasons)

    fm = data['frontmatter']
    component = fm.get('name', Path(spec_path).stem)

    targets, errs = _resolve_targets(target_arg)
    if errs:
        _fail(errs)

    # Also read .acss-target.json if present, to set default target
    target_json = Path('.acss-target.json')
    if target_json.exists() and target_arg == 'all':
        try:
            import json as _json
            tj = _json.loads(target_json.read_text())
            fw = tj.get('framework')
            if fw and fw in ALL_TARGETS:
                targets = [fw]
        except Exception:
            pass

    is_part = component in COMPOUND_PARTS
    dep_order = _topological_order(component, DEPENDENCY_GRAPH)

    manifest = {}
    for target in targets:
        files = []
        for comp in dep_order:
            is_comp_part = comp in COMPOUND_PARTS
            if target == 'react':
                files.extend(_react_manifest(comp, is_comp_part))
            elif target == 'html':
                files.extend(_html_manifest(comp, is_comp_part))
            elif target == 'astro':
                files.extend(_astro_manifest(comp, is_comp_part))
        manifest[target] = files

    result = {
        "component": component,
        "targets": targets,
        "dependency_order": dep_order,
        "manifest": manifest,
        "staging_base": ".acss-staging",
        "is_compound_part": is_part,
    }

    print(json.dumps({"ok": True, "data": result, "reasons": []}, indent=2))
    sys.exit(0)


if __name__ == '__main__':
    main()
