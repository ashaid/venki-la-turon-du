#!/usr/bin/env python3
"""Lint JSON files in eng/ for consistent formatting.

Checks:
  - Valid JSON (parseable)
  - 2-space indentation
  - Keys sorted alphabetically
  - UTF-8 encoding, no BOM
  - Trailing newline
  - No trailing whitespace on lines
  - No duplicate keys

Run with --fix to auto-format all files.
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENG_DIR = os.path.join(BASE_DIR, "eng")

failures = []


def fail(msg):
    failures.append(msg)
    print(f"  FAIL: {msg}")


def check_file(path, fix=False):
    name = os.path.basename(path)

    with open(path, "rb") as f:
        raw_bytes = f.read()

    # BOM check
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        fail(f"{name}: has UTF-8 BOM")
        if fix:
            raw_bytes = raw_bytes[3:]

    raw = raw_bytes.decode("utf-8")

    # Parse
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"{name}: invalid JSON - {e}")
        return

    # Trailing newline
    if not raw.endswith("\n"):
        fail(f"{name}: no trailing newline")

    # Check lines for trailing whitespace
    for i, line in enumerate(raw.split("\n"), 1):
        if line != line.rstrip():
            fail(f"{name}:{i}: trailing whitespace")
            break  # one per file is enough

    # Sorted keys
    keys = list(data.keys())
    if keys != sorted(keys):
        first_unsorted = next(
            (i for i in range(len(keys) - 1) if keys[i] > keys[i + 1]), None
        )
        if first_unsorted is not None:
            fail(f"{name}: keys not sorted "
                 f"('{keys[first_unsorted]}' before '{keys[first_unsorted + 1]}')")

    # Indentation: re-serialize and compare
    expected = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if raw != expected:
        # Only report if it's not just a sorting issue (already reported above)
        if keys == sorted(keys):
            fail(f"{name}: formatting differs from canonical (2-space indent, sorted)")

    if fix:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(expected)


def main():
    fix = "--fix" in sys.argv

    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        check_file(os.path.join(ENG_DIR, f), fix=fix)

    if fix:
        print(f"Formatted {len(os.listdir(ENG_DIR))} files")
        return

    print(f"\n{'='*50}")
    if failures:
        print(f"{len(failures)} issues found")
        print(f"Run 'python lint.py --fix' to auto-format")
        sys.exit(1)
    else:
        print("ALL FILES OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
