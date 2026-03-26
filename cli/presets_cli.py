#!/usr/bin/env python3
"""Preset browser."""
from assembler import load_presets, assemble_dork
from cli.display import console, print_section, ask_choice, live_preview, copy_offer
from rich.table import Table
from rich import box


def run():
    print_section('Preset Browser')
    presets = load_presets()
    if not presets:
        console.print('[red]No presets found.[/red]')
        return

    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style='bold cyan')
    table.add_column('#', style='dim', width=4)
    table.add_column('Category', style='yellow', width=22)
    table.add_column('Name', style='white')
    for i, p in enumerate(presets, 1):
        table.add_row(str(i), p['category_label'], p['name'])
    console.print(table)

    idx = ask_choice('Choose preset to use', presets)
    if idx < 0:
        return

    preset = presets[idx]
    # If preset requires a target, prompt for it
    if preset.get('requires_target'):
        target = console.input('  [bold cyan]Enter target domain (e.g. example.com): [/bold cyan]').strip()
        dork = preset['template'].replace('TARGET', target) if target else preset['template']
    else:
        dork = preset['template']

    live_preview(dork)
    copy_offer(dork)
