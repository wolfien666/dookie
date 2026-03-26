# dookie

Google Dork Builder for OSINT — internet-wide open directory and file-type hunting.

## Install

```bash
git clone https://github.com/wolfien666/dookie
cd dookie
pip install -r requirements.txt
```

## Usage

```bash
# Interactive Rich CLI menu (default)
python dookie.py

# Textual TUI — tabbed wizard interface (recommended)
python dookie.py --tui

# Jump directly to a mode
python dookie.py build      # keyword + operator builder
python dookie.py dirs       # open-directory finder
python dookie.py files      # file-type finder
python dookie.py presets    # preset browser
```

## Structure

```
dookie.py          ← entry point
assembler.py       ← dork engine (shared by CLI + TUI)
operators.json     ← all Google operators
presets.json       ← preset dork templates
cli/
  display.py       ← Rich helpers (banner, tables, input)
  menu.py          ← interactive main menu
  builder.py       ← keyword + operator builder
  dirfinder.py     ← open-directory finder
  filefinder.py    ← file-type finder
  presets_cli.py   ← preset browser
gui/
  tui.py           ← Textual TUI (4 tabs + wizard)
```

## Modes

| Mode    | Description |
|---------|-------------|
| Basic   | Pick a preset, get your dork instantly |
| Advanced | Preset + custom keywords, operators, exclusions |

Both modes share `assembler.py` — identical output.
