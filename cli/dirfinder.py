#!/usr/bin/env python3
"""Open-directory finder — Basic and Advanced modes."""
from assembler import assemble_dork, load_presets
from cli.display import (
    console, print_section, numbered_table,
    ask, ask_choice, live_preview, copy_offer, mode_toggle
)

CAT_SLUG = 'open_directories'


def run():
    print_section('Open Directory Finder')
    mode = mode_toggle()
    if mode == 'basic':
        _basic()
    else:
        _advanced()


def _get_presets():
    all_presets = load_presets()
    # Try exact slug first, then partial match on label
    presets = [p for p in all_presets if p['category'] == CAT_SLUG]
    if not presets:
        presets = [p for p in all_presets
                   if 'director' in p['category_label'].lower()
                   or 'open' in p['category_label'].lower()]
    return presets


def _basic():
    presets = _get_presets()
    if not presets:
        console.print('[red]No open-directory presets found.[/red]')
        return
    print_section('Pick a Preset')
    labels = [p['name'] for p in presets]
    console.print(numbered_table(labels, col='Preset'))
    idx = ask_choice('Choose preset', labels)
    if idx < 0:
        return
    dork = presets[idx]['template']
    live_preview(dork)
    copy_offer(dork)


def _advanced():
    presets = _get_presets()
    if not presets:
        console.print('[red]No open-directory presets found.[/red]')
        return

    print_section('Step 1 — Choose Preset')
    labels = [p['name'] for p in presets]
    console.print(numbered_table(labels, col='Preset'))
    idx = ask_choice('Choose preset', labels)
    if idx < 0:
        return
    preset = presets[idx]

    print_section('Step 2 — Keywords')
    kw_raw = ask('Add keywords (space-separated)')
    keywords = [k for k in kw_raw.split() if k]

    print_section('Step 3 — Optional Operators')
    console.print('  [dim]Leave blank to skip any operator.[/dim]\n')
    ops = {}
    for opname in ['site', 'intitle', 'intext', 'filetype', 'inurl']:
        val = ask(f'{opname}:')
        if val:
            ops[opname] = val
    excl = ask('Exclude terms (comma-separated)')
    if excl:
        ops['exclude'] = excl

    dork = assemble_dork(keywords=keywords, operators=ops, preset_id=preset['id'])
    live_preview(dork)
    copy_offer(dork)
