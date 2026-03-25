#!/usr/bin/env python3
"""Export untranslated strings to a TSV file for easy editing.

Usage:
    python3 export_untranslated.py                  # export all
    python3 export_untranslated.py cards.json       # export one file
    python3 export_untranslated.py --titles-only    # just names/titles (good starting point)

Open the TSV in any spreadsheet app (Google Sheets, LibreOffice Calc, Excel).
Fill in column C (Esperanto), then run import_translations.py to apply.
"""

import csv
import json
import os
import sys

ENG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eng")
ORIGINAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted", "localization", "eng")
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "untranslated.tsv")

def main():
    if not os.path.isdir(ORIGINAL_DIR):
        print("Error: extracted/ not found. Run GDRE extraction first.")
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
        orig_path = os.path.join(ORIGINAL_DIR, f)
        if not os.path.exists(orig_path):
            continue
        with open(orig_path, encoding="utf-8") as fh:
            original = json.load(fh)

        for k in override:
            if override[k] != original.get(k):
                continue  # already translated
            eng_val = original.get(k, "")
            if not eng_val:
                continue  # skip empty
            if titles_only and not (k.endswith(".title") or k.endswith(".name")):
                continue
            rows.append((f, k, eng_val))

    with open(OUTPUT, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["file", "key", "english", "esperanto"])
        for f, k, eng in rows:
            writer.writerow([f, k, eng, ""])

    print(f"Exported {len(rows)} untranslated strings to {OUTPUT}")
    print(f"Open in a spreadsheet, fill in the 'esperanto' column, then run:")
    print(f"  python3 import_translations.py")

if __name__ == "__main__":
    main()
