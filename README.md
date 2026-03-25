# Venki la Turon du

[![Tests](https://github.com/tonyolag/venki-la-turon-du/actions/workflows/tests.yml/badge.svg)](https://github.com/tonyolag/venki-la-turon-du/actions/workflows/tests.yml)

Esperanto translation for Slay the Spire 2.

This is a work in progress. About 10% of the game's text has been translated so far, mostly carried over from the first game's official Esperanto translation. Everything else still shows in English until someone translates it.

No mods needed. The game has a built-in override system — you just drop files in a folder.

## Installing

1. Find your SlayTheSpire2 user data folder:

   | Platform | Path |
   |----------|------|
   | Linux (Flatpak Steam) | `~/.var/app/com.valvesoftware.Steam/.local/share/SlayTheSpire2/` |
   | Linux (native Steam) | `~/.local/share/SlayTheSpire2/` |
   | Windows | `%APPDATA%\SlayTheSpire2\` |
   | macOS | `~/Library/Application Support/SlayTheSpire2/` |

2. Copy the `eng/` folder into `localization_override/` inside that directory:

   ```
   SlayTheSpire2/
     localization_override/
       eng/          <-- put the files here
         cards.json
         relics.json
         ...
   ```

3. Set your game language to **English** (in Steam or in-game settings).

4. Start the game. Translated text shows in Esperanto, everything else stays in English.

Or if you have Python installed, just run:

```bash
python3 install.py
```

It finds the right folder automatically.

## Updating

Pull the latest version and run `python3 install.py` again, or copy `eng/` over the old files. Your game settings won't be affected.

## Helping with translation

You don't need to know how to code or use git from the command line.

### Getting started with GitHub

If you've never used GitHub before:

1. **Fork the project** — click the "Fork" button in the top right of this repo's page. This makes your own copy.
2. **Edit files in the browser** — navigate to any file in `eng/` (like `cards.json`), click the pencil icon to edit, make your changes, then click "Commit changes" at the bottom.
3. **Send your changes back** — go to your fork's page, click "Contribute" then "Open pull request". Add a short description of what you translated and submit it.

That's it. You can do everything from the browser without installing anything.

### What to translate

The `eng/` folder has JSON files — one per category (cards, relics, potions, etc.). Each file looks like this:

```json
{
  "STRIKE_IRONCLAD.title": "Bato",
  "STRIKE_IRONCLAD.description": "Faru {Damage:diff()} da damaĝo."
}
```

Each line has a **key** (left side, like `STRIKE_IRONCLAD.title`) and a **value** (right side, like `"Bato"`). Only change the values. Don't touch the keys.

Strings that are already in Esperanto have been translated. Strings still in English need translating.

### If you prefer spreadsheets

If you'd rather work in a spreadsheet than edit JSON:

1. Run `python3 export_untranslated.py` to get an `untranslated.tsv` file
2. Open it in Google Sheets, LibreOffice Calc, or Excel
3. You'll see columns: **file**, **key**, **english**, **esperanto**
4. Fill in the **esperanto** column for any rows you want to translate
5. Save as TSV (tab-separated)
6. Run `python3 import_translations.py` to apply your translations

You can also export just names (`--titles-only`) or a single file:

```bash
python3 export_untranslated.py --titles-only
python3 export_untranslated.py cards.json
```

### Things to preserve

When translating descriptions, keep these exactly as they are:

- **Placeholders** like `{Damage:diff()}`, `{Block:diff()}`, `{Energy:energyIcons()}` — the game fills these in with numbers/icons
- **Color tags** like `[gold]Vulnerable[/gold]` or `[blue]3[/blue]` — translate the word inside, but keep the tags
- **Newlines** — use actual line breaks where the English has them

### Checking your work

```bash
python3 tests.py      # validate files (markup, placeholders, JSON)
python3 progress.py   # see translation progress
```

## Progress

Run `python3 progress.py` for the latest numbers. As of the initial release:

```
  cards     286 / 1233   23%  ████░░░░░░░░░░░░░░░░
  relics    224 / 963    23%  ████░░░░░░░░░░░░░░░░
  powers    115 / 832    13%  ██░░░░░░░░░░░░░░░░░░
  potions    41 / 133    30%  ██████░░░░░░░░░░░░░░
  orbs        6 / 17     35%  ███████░░░░░░░░░░░░░
  ────────────────────────────────────────────────
  overall   674 / 6714   10%  ██░░░░░░░░░░░░░░░░░░
```

38 files are completely untouched (UI, events, achievements, etc.).

## How it works

Slay the Spire 2 checks for a `localization_override/` folder in user data at startup. Files in a language subfolder (like `eng/`) replace the matching strings from the game's built-in text. Since the files live outside the game install directory, they survive game updates.

We're overriding the English slot, so the game thinks it's loading English but gets Esperanto instead.

## Stargazers

[![Star History Chart](https://api.star-history.com/svg?repos=tonyolag/venki-la-turon-du&type=Date)](https://star-history.com/#tonyolag/venki-la-turon-du&Date)
