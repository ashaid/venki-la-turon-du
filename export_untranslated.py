#!/usr/bin/env python3
"""Export untranslated strings to a TSV file for easy editing.

Usage:
    python export_untranslated.py                  # export all
    python export_untranslated.py cards.json       # export one file
    python export_untranslated.py --titles-only    # just names/titles (good starting point)

Open the TSV in any spreadsheet app (Google Sheets, LibreOffice Calc, Excel).
Fill in column C (Esperanto), then run import_translations.py to apply.
"""

import csv
import hashlib
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENG_DIR = os.path.join(BASE_DIR, "eng")
ORIGINAL_DIR = os.path.join(BASE_DIR, "extracted", "localization", "eng")
HASHES_PATH = os.path.join(BASE_DIR, "original_hashes.json")
OUTPUT = os.path.join(BASE_DIR, "untranslated.tsv")


def hash_value(v):
    return hashlib.sha256(v.encode("utf-8")).hexdigest()[:12]


def is_untranslated(f, k, v, originals, hashes):
    """Check if a string is still the original English."""
    if originals and f in originals:
        return v == originals[f].get(k)
    if hashes and f in hashes:
        if not isinstance(v, str):
            return True
        return hash_value(v) == hashes[f].get(k)
    return False


def main():
    # Load reference data (prefer extracted originals, fall back to hashes)
    originals = {}
    hashes = {}

    if os.path.isdir(ORIGINAL_DIR):
        for f in os.listdir(ORIGINAL_DIR):
            if f.endswith(".json"):
                with open(os.path.join(ORIGINAL_DIR, f), encoding="utf-8") as fh:
                    originals[f] = json.load(fh)
    elif os.path.exists(HASHES_PATH):
        with open(HASHES_PATH, encoding="utf-8") as fh:
            hashes = json.load(fh)
    else:
        print("Error: no reference data found.")
        print("Need either extracted/ (from GDRE) or original_hashes.json")
        return

    filter_file = None
    titles_only = False
    for arg in sys.argv[1:]:
        if arg == "--titles-only":
            titles_only = True
        elif arg.endswith(".json"):
            filter_file = arg
        else:
            print(f"Unknown argument: {arg}")
            return

    rows = []
    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        if filter_file and f != filter_file:
            continue
        with open(os.path.join(ENG_DIR, f), encoding="utf-8") as fh:
            override = json.load(fh)

        for k, v in override.items():
            if not isinstance(v, str) or not v:
                continue
            if not is_untranslated(f, k, v, originals, hashes):
                continue  # already translated
            if titles_only and not (k.endswith(".title") or k.endswith(".name")):
                continue
            rows.append((f, k, v))

    with open(OUTPUT, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["file", "key", "english", "esperanto"])
        for f, k, eng in rows:
            writer.writerow([f, k, eng, ""])

    print(f"Exported {len(rows)} untranslated strings to {OUTPUT}")
    print(f"Open in a spreadsheet, fill in the 'esperanto' column, then run:")
    print(f"  python import_translations.py")

if __name__ == "__main__":
    main()
