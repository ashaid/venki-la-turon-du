#!/usr/bin/env python3
"""Tests for the Esperanto translation override files."""

import hashlib
import json
import os
import re
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENG_DIR = os.path.join(BASE_DIR, "eng")
ORIGINAL_DIR = os.path.join(BASE_DIR, "extracted", "localization", "eng")
HASHES_PATH = os.path.join(BASE_DIR, "original_hashes.json")

failures = []


def fail(msg):
    failures.append(msg)
    print(f"  FAIL: {msg}")


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def hash_value(v):
    return hashlib.sha256(v.encode("utf-8")).hexdigest()[:12]


def has_originals():
    return os.path.isdir(ORIGINAL_DIR)


def has_hashes():
    return os.path.exists(HASHES_PATH)


def load_hashes():
    if has_hashes():
        return load_json(HASHES_PATH)
    return {}


def is_translated(f, k, v, originals, hashes):
    """Check if a string has been translated (differs from original)."""
    if not isinstance(v, str):
        return False
    if originals and f in originals:
        return v != originals[f].get(k)
    if hashes and f in hashes:
        return hash_value(v) != hashes[f].get(k)
    return False


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
    hashes = load_hashes()
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
                    continue
                elif original:
                    fail(f"{f} -> {k}: empty but original is not")
                elif hashes and f in hashes:
                    orig_hash = hashes[f].get(k)
                    empty_hash = hash_value("")
                    if orig_hash != empty_hash:
                        fail(f"{f} -> {k}: empty but original is not")


def test_keys_match_original():
    """Override files must have exactly the same keys as the originals."""
    print("test_keys_match_original")
    hashes = load_hashes()
    if not has_originals() and not hashes:
        print("  SKIP: no reference data")
        return
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        override = load_json(os.path.join(ENG_DIR, f))
        if has_originals():
            orig_path = os.path.join(ORIGINAL_DIR, f)
            if not os.path.exists(orig_path):
                continue
            original_keys = set(load_json(orig_path).keys())
        elif f in hashes:
            original_keys = set(hashes[f].keys())
        else:
            continue
        missing = original_keys - set(override.keys())
        extra = set(override.keys()) - original_keys
        if missing:
            fail(f"{f}: missing {len(missing)} keys: {list(missing)[:3]}...")
        if extra:
            fail(f"{f}: extra {len(extra)} keys: {list(extra)[:3]}...")


def test_placeholders_match_original():
    """Translated descriptions must have the same {placeholders} as the English original."""
    print("test_placeholders_match_original")
    if not has_originals():
        print("  SKIP: extracted/ not present (need full text to compare placeholders)")
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
    hashes_data = load_hashes()
    if not has_originals() and not hashes_data:
        print("  SKIP: no reference data")
        return
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        override = load_json(os.path.join(ENG_DIR, f))
        if has_originals():
            orig_path = os.path.join(ORIGINAL_DIR, f)
            if not os.path.exists(orig_path):
                continue
            original = load_json(orig_path)
        elif f in hashes_data:
            # Without full text we can't group by English name
            # but we can detect if same-hash keys are partially translated
            file_hashes = hashes_data[f]
            hash_groups = defaultdict(list)
            for k, h in file_hashes.items():
                if k.endswith(".title") or k.endswith(".name"):
                    hash_groups[h].append(k)
            for h, keys in hash_groups.items():
                if len(keys) < 2:
                    continue
                translated = [k for k in keys if is_translated(f, k, override.get(k, ""), {}, hashes_data)]
                untranslated = [k for k in keys if not is_translated(f, k, override.get(k, ""), {}, hashes_data)]
                if translated and untranslated:
                    fail(f"{f}: shared name partially translated - "
                         f"done: {translated}, missing: {untranslated}")
            continue
        else:
            continue

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
    test_all_json_valid()
    test_no_sts1_markup()
    test_valid_placeholders()
    test_valid_color_tags()
    test_no_empty_values()
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
