#!/usr/bin/env python3
"""Tests for the Esperanto translation override files."""

import json
import os
import re
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENG_DIR = os.path.join(BASE_DIR, "eng")
ORIGINAL_DIR = os.path.join(BASE_DIR, "extracted", "localization", "eng")

failures = []


def fail(msg):
    failures.append(msg)
    print(f"  FAIL: {msg}")


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def has_originals():
    return os.path.isdir(ORIGINAL_DIR)


def test_all_json_valid():
    """Every file in eng/ must be valid JSON."""
    print("test_all_json_valid")
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        try:
            load_json(os.path.join(ENG_DIR, f))
        except json.JSONDecodeError as e:
            fail(f"{f}: invalid JSON - {e}")


def test_no_sts1_markup():
    """No STS1 markup (!D!, !M!, !B!, NL, [G], [R], [B]) anywhere."""
    print("test_no_sts1_markup")
    sts1_pattern = re.compile(r"!\w+!|\bNL\b|\[G\]|\[R\]|\[B\]")
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        data = load_json(os.path.join(ENG_DIR, f))
        for k, v in data.items():
            if not isinstance(v, str):
                continue
            matches = sts1_pattern.findall(v)
            if matches:
                fail(f"{f} -> {k}: STS1 markup {matches}")


def test_valid_placeholders():
    """All {placeholders} must have matched braces."""
    print("test_valid_placeholders")
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        data = load_json(os.path.join(ENG_DIR, f))
        for k, v in data.items():
            if not isinstance(v, str):
                continue
            depth = 0
            for ch in v:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth < 0:
                        fail(f"{f} -> {k}: unmatched closing brace")
                        break
            else:
                if depth != 0:
                    fail(f"{f} -> {k}: unmatched opening brace")


def test_valid_color_tags():
    """Closing [/tag] tags must have a matching opening [tag]."""
    print("test_valid_color_tags")
    # Matches [tag], [tag=param], [tag param]
    open_re = re.compile(r"\[(\w+)[\s=\]]")
    close_re = re.compile(r"\[/(\w+)\]")
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        data = load_json(os.path.join(ENG_DIR, f))
        for k, v in data.items():
            if not isinstance(v, str):
                continue
            opens = open_re.findall(v)
            closes = close_re.findall(v)
            for tag in closes:
                if tag not in opens:
                    fail(f"{f} -> {k}: [/{tag}] without [{tag}]")


def test_no_empty_values():
    """No value should be empty unless the original is also empty."""
    print("test_no_empty_values")
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        data = load_json(os.path.join(ENG_DIR, f))
        original = None
        if has_originals():
            orig_path = os.path.join(ORIGINAL_DIR, f)
            if os.path.exists(orig_path):
                original = load_json(orig_path)
        for k, v in data.items():
            if v == "":
                if original and original.get(k, "") == "":
                    continue  # original is also empty, fine
                elif original:
                    fail(f"{f} -> {k}: empty but original is not")
                # without originals, can't tell — skip


# --- Tests that require extracted/ (local only, skipped in CI) ---

def test_keys_match_original():
    """Override files must have exactly the same keys as the originals."""
    print("test_keys_match_original")
    if not has_originals():
        print("  SKIP: extracted/ not present")
        return
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        orig_path = os.path.join(ORIGINAL_DIR, f)
        if not os.path.exists(orig_path):
            continue
        override = load_json(os.path.join(ENG_DIR, f))
        original = load_json(orig_path)
        missing = set(original.keys()) - set(override.keys())
        extra = set(override.keys()) - set(original.keys())
        if missing:
            fail(f"{f}: missing {len(missing)} keys: {list(missing)[:3]}...")
        if extra:
            fail(f"{f}: extra {len(extra)} keys: {list(extra)[:3]}...")


def test_placeholders_match_original():
    """Translated descriptions must have the same {placeholders} as the English original."""
    print("test_placeholders_match_original")
    if not has_originals():
        print("  SKIP: extracted/ not present")
        return
    placeholder_re = re.compile(r"\{[^}]+\}")
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        override = load_json(os.path.join(ENG_DIR, f))
        original = load_json(os.path.join(ORIGINAL_DIR, f))
        for k, v in override.items():
            if not isinstance(v, str) or v == original.get(k):
                continue
            if not k.endswith(".description"):
                continue
            orig_val = original.get(k, "")
            if sorted(placeholder_re.findall(v)) != sorted(placeholder_re.findall(orig_val)):
                fail(f"{f} -> {k}: placeholders differ\n"
                     f"    original:  {sorted(placeholder_re.findall(orig_val))}\n"
                     f"    override:  {sorted(placeholder_re.findall(v))}")


def test_duplicate_names_consistent():
    """If one variant of a shared name is translated, all must be."""
    print("test_duplicate_names_consistent")
    if not has_originals():
        print("  SKIP: extracted/ not present")
        return
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        override = load_json(os.path.join(ENG_DIR, f))
        original = load_json(os.path.join(ORIGINAL_DIR, f))
        groups = defaultdict(list)
        for k, v in original.items():
            if k.endswith(".title") or k.endswith(".name"):
                groups[v].append(k)
        for eng_name, keys in groups.items():
            if len(keys) < 2:
                continue
            translated = [k for k in keys if override.get(k) != original.get(k)]
            untranslated = [k for k in keys if override.get(k) == original.get(k)]
            if translated and untranslated:
                fail(f"{f}: '{eng_name}' partially translated - "
                     f"done: {translated}, missing: {untranslated}")


if __name__ == "__main__":
    # These always run (including CI)
    test_all_json_valid()
    test_no_sts1_markup()
    test_valid_placeholders()
    test_valid_color_tags()
    test_no_empty_values()

    # These need extracted/ (local only)
    test_keys_match_original()
    test_placeholders_match_original()
    test_duplicate_names_consistent()

    print(f"\n{'='*50}")
    if failures:
        print(f"{len(failures)} FAILURES")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)
