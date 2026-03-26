#!/usr/bin/env python3
"""Preset browser."""
from assembler import assemble_dork, load_presets
from cli.display import (
    console, print_section, numbered_table,
    ask, ask_choice, live_preview
)
from rich.table import Table
from rich import box


def run():
    print_section('Preset Browser')
    presets = load_presets()
    if not presets:
        console.print('[red]No presets found.[/red]')
        return

    # Show full table with category + name
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style='bold cyan')
    table.add_column('#', style='dim', width=4)
    table.add_column('Category', style='yellow', width=18)
    table.add_column('Name', style='white')
    for i, p in enumerate(presets, 1):
        table.add_row(str(i), p['category'].replace('_', ' ').title(), p['name'])
    console.print(table)

    idx = ask_choice('Choose preset to generate', presets)
    if idx < 0:
        return
    preset = presets[idx]

    dork = assemble_dork(preset_id=preset['id'])
    live_preview(dork)

    try:
        import pyperclip
        raw = console.input('  Copy to clipboard? [y/N]: ').strip().lower()
        if raw == 'y':
            pyperclip.copy(dork)
            console.print('  [green]Copied![/green]')
    except ImportError:
        pass
