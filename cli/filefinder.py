#!/usr/bin/env python3
"""File-type finder — Basic and Advanced modes."""
from assembler import assemble_dork, load_presets
from cli.display import (
    console, print_section, numbered_table,
    ask, ask_choice, live_preview, mode_toggle
)


def run():
    print_section('File Finder')
    mode = mode_toggle()
    if mode == 'basic':
        _basic()
    else:
        _advanced()


def _basic():
    presets = [p for p in load_presets() if p['category'] == 'files']
    if not presets:
        console.print('[red]No file presets found.[/red]')
        return

    print_section('File Finder Presets')
    labels = [p['name'] for p in presets]
    console.print(numbered_table(labels, col='Preset'))
    idx = ask_choice('Choose preset', labels)
    if idx < 0:
        return

    dork = presets[idx]['template']
    live_preview(dork)
    _copy_offer(dork)


def _advanced():
    presets = [p for p in load_presets() if p['category'] == 'files']
    if not presets:
        console.print('[red]No file presets found.[/red]')
        return

    # Step 1
    print_section('Step 1 — Choose preset')
    labels = [p['name'] for p in presets]
    console.print(numbered_table(labels, col='Preset'))
    idx = ask_choice('Choose preset', labels)
    if idx < 0:
        return
    preset = presets[idx]

    # Step 2 — keywords
    print_section('Step 2 — Keywords')
    kw_raw = ask('Add keywords (space-separated)')
    keywords = [k for k in kw_raw.split() if k]

    # Step 3 — operators
    print_section('Step 3 — Optional operators')
    console.print('  [dim]Available: site, intext, intitle, inurl, filetype, minus[/dim]')
    console.print()
    op_choices = ['site', 'intext', 'intitle', 'inurl', 'filetype', 'minus']
    operators = {}
    for op in op_choices:
        val = ask(f'{op}:')
        if val:
            operators[op] = val

    dork = assemble_dork(
        keywords=keywords,
        operators=operators,
        preset_id=preset['id']
    )
    live_preview(dork)
    _copy_offer(dork)


def _copy_offer(dork: str):
    try:
        import pyperclip
        raw = console.input('  Copy to clipboard? [y/N]: ').strip().lower()
        if raw == 'y':
            pyperclip.copy(dork)
            console.print('  [green]Copied![/green]')
    except ImportError:
        pass
