#!/usr/bin/env python3
"""Tests for the Esperanto translation override files."""

import json
import os
import re
import sys

ENG_DIR = os.path.join(os.path.dirname(__file__), "eng")
ORIGINAL_DIR = os.path.join(os.path.dirname(__file__), "extracted", "localization", "eng")

failures = []

def fail(msg):
    failures.append(msg)
    print(f"  FAIL: {msg}")

def test_all_json_valid():
    """Every file in eng/ must be valid JSON."""
    print("test_all_json_valid")
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        path = os.path.join(ENG_DIR, f)
        try:
            with open(path, encoding="utf-8") as fh:
                json.load(fh)
        except json.JSONDecodeError as e:
            fail(f"{f}: invalid JSON - {e}")

def test_keys_match_original():
    """Override files must have exactly the same keys as the originals."""
    print("test_keys_match_original")
    if not os.path.isdir(ORIGINAL_DIR):
        print("  SKIP: extracted/ not present (run GDRE extraction first)")
        return
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        orig_path = os.path.join(ORIGINAL_DIR, f)
        if not os.path.exists(orig_path):
            continue
        with open(os.path.join(ENG_DIR, f), encoding="utf-8") as fh:
            override = json.load(fh)
        with open(orig_path, encoding="utf-8") as fh:
            original = json.load(fh)
        missing = set(original.keys()) - set(override.keys())
        extra = set(override.keys()) - set(original.keys())
        if missing:
            fail(f"{f}: missing {len(missing)} keys: {list(missing)[:3]}...")
        if extra:
            fail(f"{f}: extra {len(extra)} keys: {list(extra)[:3]}...")

def test_no_sts1_markup():
    """No STS1 markup (!D!, !M!, !B!, NL, [G], [R], [B]) in translated strings."""
    print("test_no_sts1_markup")
    if not os.path.isdir(ORIGINAL_DIR):
        print("  SKIP: extracted/ not present")
        return
    sts1_pattern = re.compile(r"!\w+!|\bNL\b|\[G\]|\[R\]|\[B\]")
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(ENG_DIR, f), encoding="utf-8") as fh:
            override = json.load(fh)
        orig_path = os.path.join(ORIGINAL_DIR, f)
        if not os.path.exists(orig_path):
            continue
        with open(orig_path, encoding="utf-8") as fh:
            original = json.load(fh)
        for k, v in override.items():
            if not isinstance(v, str) or v == original.get(k):
                continue  # only check translated strings
            matches = sts1_pattern.findall(v)
            if matches:
                fail(f"{f} -> {k}: leftover STS1 markup {matches}")

def test_placeholders_preserved():
    """Translated descriptions must have the same {placeholders} as the English original."""
    print("test_placeholders_preserved")
    if not os.path.isdir(ORIGINAL_DIR):
        print("  SKIP: extracted/ not present")
        return
    placeholder_re = re.compile(r"\{[^}]+\}")
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(ENG_DIR, f), encoding="utf-8") as fh:
            override = json.load(fh)
        with open(os.path.join(ORIGINAL_DIR, f), encoding="utf-8") as fh:
            original = json.load(fh)
        for k, v in override.items():
            if not isinstance(v, str) or v == original.get(k):
                continue
            if not k.endswith(".description"):
                continue
            orig_val = original.get(k, "")
            override_placeholders = sorted(placeholder_re.findall(v))
            original_placeholders = sorted(placeholder_re.findall(orig_val))
            if override_placeholders != original_placeholders:
                fail(f"{f} -> {k}: placeholders differ\n"
                     f"    original:  {original_placeholders}\n"
                     f"    override:  {override_placeholders}")

def test_no_empty_translations():
    """Translated strings must not be empty (unless the original is also empty)."""
    print("test_no_empty_translations")
    if not os.path.isdir(ORIGINAL_DIR):
        print("  SKIP: extracted/ not present")
        return
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(ENG_DIR, f), encoding="utf-8") as fh:
            override = json.load(fh)
        with open(os.path.join(ORIGINAL_DIR, f), encoding="utf-8") as fh:
            original = json.load(fh)
        for k, v in override.items():
            if v == "" and original.get(k, "") != "":
                fail(f"{f} -> {k}: translated to empty string but original is not empty")

def test_duplicate_names_all_translated():
    """If one variant of a shared name is translated, all must be."""
    print("test_duplicate_names_all_translated")
    if not os.path.isdir(ORIGINAL_DIR):
        print("  SKIP: extracted/ not present")
        return
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(ENG_DIR, f), encoding="utf-8") as fh:
            override = json.load(fh)
        with open(os.path.join(ORIGINAL_DIR, f), encoding="utf-8") as fh:
            original = json.load(fh)
        # Group title/name keys by their English value
        from collections import defaultdict
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
    test_keys_match_original()
    test_no_sts1_markup()
    test_placeholders_preserved()
    test_no_empty_translations()
    test_duplicate_names_all_translated()

    print(f"\n{'='*50}")
    if failures:
        print(f"{len(failures)} FAILURES")
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)
