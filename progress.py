#!/usr/bin/env python3
"""Show translation progress per file and overall."""

import hashlib
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENG_DIR = os.path.join(BASE_DIR, "eng")
ORIGINAL_DIR = os.path.join(BASE_DIR, "extracted", "localization", "eng")
HASHES_PATH = os.path.join(BASE_DIR, "original_hashes.json")


def hash_value(v):
    return hashlib.sha256(v.encode("utf-8")).hexdigest()[:12]


def bar(pct, width=20):
    filled = int(pct / 100 * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def main():
    # Load reference data
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

    rows = []
    total_done = 0
    total_all = 0

    for f in sorted(os.listdir(ENG_DIR)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(ENG_DIR, f), encoding="utf-8") as fh:
            override = json.load(fh)

        total = len(override)
        done = 0
        for k, v in override.items():
            if not isinstance(v, str):
                continue
            if originals and f in originals:
                if v != originals[f].get(k):
                    done += 1
            elif hashes and f in hashes:
                if hash_value(v) != hashes[f].get(k):
                    done += 1

        total_done += done
        total_all += total
        rows.append((f, done, total))

    print(f"\n  Venki la Turon du \u2014 Translation Progress\n")
    print(f"  {'File':<30} {'Done':>5} / {'Total':<5}  {'%':>5}  Progress")
    print(f"  {'\u2500'*30} {'\u2500'*5}   {'\u2500'*5}  {'\u2500'*5}  {'\u2500'*20}")

    for f, done, total in rows:
        pct = done * 100 // total if total else 0
        if done > 0:
            print(f"  {f:<30} {done:>5} / {total:<5}  {pct:>4}%  {bar(pct)}")

    print(f"  {'\u2500'*30} {'\u2500'*5}   {'\u2500'*5}  {'\u2500'*5}  {'\u2500'*20}")

    untouched = [(f, t) for f, d, t in rows if d == 0]
    if untouched:
        print(f"\n  Untouched files ({len(untouched)}):")
        for f, t in untouched:
            print(f"    {f:<30} {t:>5} strings")

    pct = total_done * 100 // total_all if total_all else 0
    print(f"\n  OVERALL: {total_done}/{total_all} strings ({pct}%)  {bar(pct)}")
    print(f"  Remaining: {total_all - total_done} strings\n")

if __name__ == "__main__":
    main()
