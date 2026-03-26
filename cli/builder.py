#!/usr/bin/env python3
"""Basic keyword + operator builder."""
import json
import os
from assembler import assemble_dork, load_operators
from cli.display import (
    console, print_section, numbered_table,
    ask, ask_choice, live_preview, mode_toggle
)


def run():
    print_section('Basic Builder')
    ops = load_operators()
    categories = ['scope', 'url', 'title', 'content', 'file', 'date', 'boolean']

    # Keywords
    kw_raw = ask('Enter keywords (space-separated)')
    keywords = [k for k in kw_raw.split() if k]

    chosen_ops = {}

    for cat in categories:
        cat_ops = [op for op in ops if op['category'] == cat]
        if not cat_ops:
            continue
        print_section(f'Operators — {cat.title()}')
        labels = [f"{op['syntax']:20s} {op['description']}" for op in cat_ops]
        console.print(numbered_table(labels, col='Operator'))
        console.print('  [dim]Enter numbers separated by commas, or press Enter to skip.[/dim]')
        raw = ask('Select operators')
        if not raw:
            continue
        try:
            indices = [int(x.strip()) - 1 for x in raw.split(',') if x.strip()]
        except ValueError:
            continue
        for i in indices:
            if 0 <= i < len(cat_ops):
                op = cat_ops[i]
                val = ask(f'Value for {op["syntax"]}')
                if val:
                    chosen_ops[op['name']] = val

    dork = assemble_dork(keywords=keywords, operators=chosen_ops)
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
