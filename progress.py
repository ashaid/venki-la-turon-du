#!/usr/bin/env python3
"""Show translation progress per file and overall."""

import json
import os

ENG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eng")
ORIGINAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted", "localization", "eng")

def bar(pct, width=20):
    filled = int(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)

def main():
    if not os.path.isdir(ORIGINAL_DIR):
        print("Error: extracted/ not found. Run GDRE extraction first.")
        return

    rows = []
    total_done = 0
    total_all = 0

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

        done = sum(1 for k in override if override[k] != original.get(k))
        total = len(override)
        total_done += done
        total_all += total
        rows.append((f, done, total))

    print(f"\n  Venki la Turon du — Translation Progress\n")
    print(f"  {'File':<30} {'Done':>5} / {'Total':<5}  {'%':>5}  Progress")
    print(f"  {'─'*30} {'─'*5}   {'─'*5}  {'─'*5}  {'─'*20}")

    for f, done, total in rows:
        pct = done * 100 // total if total else 0
        if done > 0:
            print(f"  {f:<30} {done:>5} / {total:<5}  {pct:>4}%  {bar(pct)}")

    print(f"  {'─'*30} {'─'*5}   {'─'*5}  {'─'*5}  {'─'*20}")

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
