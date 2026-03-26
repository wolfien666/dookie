#!/usr/bin/env python3
"""Interactive main menu."""
from cli.display import console, print_section, numbered_table, ask_choice


def run():
    print_section('Main Menu')
    items = [
        'Basic Builder       — keywords + operator picker',
        'Open Directory Finder — internet-wide open-dir dorks',
        'File Finder         — configs, backups, keys, DB dumps',
        'Preset Browser      — browse all saved templates',
        'Exit',
    ]
    console.print(numbered_table(items, title='What do you want to build?', col='Mode'))
    idx = ask_choice('Choose', items)
    if idx == 0:
        from cli.builder import run as r; r()
    elif idx == 1:
        from cli.dirfinder import run as r; r()
    elif idx == 2:
        from cli.filefinder import run as r; r()
    elif idx == 3:
        from cli.presets_cli import run as r; r()
    else:
        console.print('[dim]Bye.[/dim]')
