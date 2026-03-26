#!/usr/bin/env python3
"""Keyword + operator builder."""
from assembler import assemble_dork, load_operators
from cli.display import (
    console, print_section, numbered_table,
    ask, ask_choice, live_preview, copy_offer, mode_toggle
)


def run():
    print_section('Basic Builder')

    # Keywords first
    kw_raw = ask('Enter keywords (space-separated)')
    keywords = [k for k in kw_raw.split() if k]

    mode = mode_toggle()
    ops = load_operators()
    chosen_ops = {}

    if mode == 'basic':
        # Only show the most useful 4 operators
        basic_ids = ['site', 'intitle', 'filetype', 'intext']
        basic_ops = [op for op in ops if op['id'] in basic_ids]
        print_section('Quick Operators')
        for op in basic_ops:
            val = ask(f'{op["syntax"]}  [dim]{op["description"]}[/dim]')
            if val:
                chosen_ops[op['id']] = val
        # Exclusions
        excl = ask('Exclude terms (comma-separated, e.g. login,admin)')
        if excl:
            chosen_ops['exclude'] = excl
    else:
        # Full operator picker by category
        categories = {}
        for op in ops:
            categories.setdefault(op['category'], {'label': op['category_label'], 'ops': []})
            categories[op['category']]['ops'].append(op)

        for cat_id, cat in categories.items():
            print_section(f'Operators — {cat["label"]}')
            labels = [f"{op['syntax']:22s} {op['description']}" for op in cat['ops']]
            console.print(numbered_table(labels, col='Operator'))
            console.print('  [dim]Enter numbers separated by commas, or Enter to skip.[/dim]')
            raw = ask('Select')
            if not raw:
                continue
            try:
                indices = [int(x.strip()) - 1 for x in raw.split(',') if x.strip()]
            except ValueError:
                continue
            for i in indices:
                if 0 <= i < len(cat['ops']):
                    op = cat['ops'][i]
                    val = ask(f'Value for {op["syntax"]}')
                    if val:
                        chosen_ops[op['id']] = val

    dork = assemble_dork(keywords=keywords, operators=chosen_ops)
    live_preview(dork)
    copy_offer(dork)
