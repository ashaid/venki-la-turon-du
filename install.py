#!/usr/bin/env python3
"""Copy translation files to the game's localization_override folder.

Detects the platform and copies eng/*.json to the right place.
"""

import os
import shutil
import sys

ENG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eng")

POSSIBLE_PATHS = [
    # Linux Flatpak Steam
    os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/SlayTheSpire2"),
    # Linux native Steam
    os.path.expanduser("~/.local/share/SlayTheSpire2"),
    # Windows
    os.path.join(os.environ.get("APPDATA", ""), "SlayTheSpire2"),
    # macOS
    os.path.expanduser("~/Library/Application Support/SlayTheSpire2"),
]

def main():
    user_data = None
    for p in POSSIBLE_PATHS:
        if os.path.isdir(p):
            user_data = p
            break

    if not user_data:
        print("Could not find SlayTheSpire2 user data folder.")
        print("Pass the path manually:")
        print("  python3 install.py /path/to/SlayTheSpire2")
        return

    if len(sys.argv) > 1:
        user_data = sys.argv[1]

    override_dir = os.path.join(user_data, "localization_override", "eng")
    os.makedirs(override_dir, exist_ok=True)

    count = 0
    for f in os.listdir(ENG_DIR):
        if f.endswith(".json"):
            shutil.copy2(os.path.join(ENG_DIR, f), os.path.join(override_dir, f))
            count += 1

    print(f"Installed {count} files to {override_dir}")
    print("Restart the game to see changes.")

if __name__ == "__main__":
    main()
