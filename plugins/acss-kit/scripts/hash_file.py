#!/usr/bin/env python3
"""
Hash a file or stdin content using sha256, after applying the kit-sync
normalization rules (LF line endings, strip trailing whitespace per line,
collapse trailing blank lines to one).

Normalization is identical for written content and on-disk content during
drift detection — otherwise a Prettier run would flip every file to
"modified" the next day.

Usage:
    python3 hash_file.py --path <abs-or-rel-path>
    cat content | python3 hash_file.py --stdin

Output (JSON to stdout):

    {
      "path": "/abs/path/to/file" | null,
      "sha256": "<hex>",
      "normalizedBytes": <int>,
      "reasons": []
    }

Exit codes:
    0 — hashed successfully
    1 — logical failure (file not found via --path)
    2 — usage / IO error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


_TRAILING_WS_RE = re.compile(rb"[ \t]+(?=\n)")


def normalize(raw: bytes) -> bytes:
    # Normalize CRLF / CR to LF
    text = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    # Strip trailing whitespace on every line
    text = _TRAILING_WS_RE.sub(b"", text)
    # Collapse 2+ trailing newlines to a single trailing newline
    text = re.sub(rb"\n+\Z", b"\n", text)
    if text and not text.endswith(b"\n"):
        text = text + b"\n"
    return text


def hash_bytes(raw: bytes) -> tuple[str, int]:
    norm = normalize(raw)
    return hashlib.sha256(norm).hexdigest(), len(norm)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--path", type=str, help="path to file to hash")
    g.add_argument("--stdin", action="store_true", help="read content from stdin")
    args = parser.parse_args()

    try:
        if args.path:
            p = Path(args.path)
            if not p.is_file():
                print(json.dumps({
                    "path": str(p),
                    "sha256": None,
                    "normalizedBytes": 0,
                    "reasons": [f"File not found: {p}"],
                }))
                return 1
            raw = p.read_bytes()
            label = str(p.resolve())
        else:
            raw = sys.stdin.buffer.read()
            label = None
    except OSError as e:
        print(f"hash_file: {e}", file=sys.stderr)
        return 2

    sha, n = hash_bytes(raw)
    print(json.dumps({
        "path": label,
        "sha256": sha,
        "normalizedBytes": n,
        "reasons": [],
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
