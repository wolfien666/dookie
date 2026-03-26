# dookie

A Google dork builder for OSINT — internet-wide open directory and file-type hunting.

## Features

- **CLI mode** (Rich TUI): keyword builder, open-directory finder, file finder, preset browser
- **GUI mode** (`--gui` flag): tabbed web interface with step-by-step wizard, live preview, copy button
- Both modes share the same `assembler.py` engine and `presets.json` / `operators.json` data

## Getting started

```bash
pip install -r requirements.txt

# CLI mode
python dookie.py build
python dookie.py dirs
python dookie.py files
python dookie.py presets

# GUI mode (opens browser at http://127.0.0.1:5000)
python dookie.py --gui
```

## Project structure

```
dookie.py          ← entrypoint with --gui switch
assembler.py       ← core dork string builder (shared by CLI + GUI)
operators.json     ← all Google operators with metadata
presets.json       ← internet-wide preset templates
cli/
  display.py       ← Rich banner, tables, live preview helpers
  builder.py       ← basic keyword+operator builder
  dirfinder.py     ← open-directory finder (basic + advanced)
  filefinder.py    ← file-type finder
  presets_cli.py   ← preset browser
gui/
  app.py           ← Flask server
  templates/
    index.html     ← tabbed wizard UI
  static/
    style.css      ← dark terminal theme
    script.js      ← live preview + copy
```
