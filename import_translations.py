#!/usr/bin/env python3
"""Import translations from the TSV file back into the JSON override files.

Usage:
    python3 import_translations.py                  # import from untranslated.tsv
    python3 import_translations.py my_file.tsv      # import from a specific file

Only rows with a non-empty 'esperanto' column are applied.
Runs validation after importing.
"""

import csv
import json
import os
import re
import sys

ENG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eng")
ORIGINAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted", "localization", "eng")

def main():
    tsv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "untranslated.tsv")

    if not os.path.exists(tsv_path):
        print(f"Error: {tsv_path} not found. Run export_untranslated.py first.")
        return

    # Read TSV
    translations = {}
    with open(tsv_path, encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            eo = row.get("esperanto", "").strip()
            if not eo:
                continue
            f = row["file"]
            k = row["key"]
            if f not in translations:
                translations[f] = {}
            translations[f][k] = eo

    if not translations:
        print("No translations found in TSV. Fill in the 'esperanto' column first.")
        return

    # Apply
    applied = 0
    warnings = []
    placeholder_re = re.compile(r"\{[^}]+\}")
    sts1_re = re.compile(r"!\w+!|\bNL\b|\[G\]|\[R\]|\[B\]")

    for f, entries in sorted(translations.items()):
        override_path = os.path.join(ENG_DIR, f)
        orig_path = os.path.join(ORIGINAL_DIR, f)
        if not os.path.exists(override_path):
            warnings.append(f"File not found: {f}")
            continue

        with open(override_path, encoding="utf-8") as fh:
            override = json.load(fh)
        with open(orig_path, encoding="utf-8") as fh:
            original = json.load(fh)

        for k, eo in entries.items():
            if k not in override:
                warnings.append(f"{f} -> {k}: key not found, skipping")
                continue

            # Validate: check for STS1 markup
            if sts1_re.search(eo):
                warnings.append(f"{f} -> {k}: contains STS1 markup (NL, !D!, etc.) - use STS2 format instead")
                continue

            # Validate: check placeholders match original
            if k.endswith(".description"):
                orig_placeholders = sorted(placeholder_re.findall(original.get(k, "")))
                new_placeholders = sorted(placeholder_re.findall(eo))
                if orig_placeholders != new_placeholders:
                    warnings.append(f"{f} -> {k}: placeholder mismatch\n"
                                    f"  expected: {orig_placeholders}\n"
                                    f"  got:      {new_placeholders}")
                    continue

            override[k] = eo
            applied += 1

        with open(override_path, "w", encoding="utf-8") as fh:
            json.dump(override, fh, indent=2, ensure_ascii=False)

    print(f"Applied {applied} translations")

    if warnings:
        print(f"\n{len(warnings)} warnings:")
        for w in warnings:
            print(f"  {w}")

    # Sync to override folder
    print(f"\nDon't forget to copy eng/ to your localization_override folder!")
    print(f"Run: python3 install.py")

if __name__ == "__main__":
    main()
