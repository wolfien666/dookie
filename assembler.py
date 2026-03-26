#!/usr/bin/env python3
"""
Core dork assembly engine.
Matches actual operators.json (categories[].operators[]) and
presets.json (presets[].dork) schemas.
"""
import json
import os
from typing import Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def load_operators() -> List[Dict]:
    """Return flat list of all operators from operators.json."""
    path = os.path.join(SCRIPT_DIR, 'operators.json')
    with open(path, 'r') as f:
        data = json.load(f)
    ops = []
    for cat in data.get('categories', []):
        for op in cat.get('operators', []):
            op['category'] = cat['id']        # attach category slug
            op['category_label'] = cat['label']
            op['color'] = cat.get('color', 'white')
            op['name'] = op['id']             # alias so old code still works
            op['syntax_clean'] = op['syntax'].rstrip(':')
            ops.append(op)
    return ops


def load_presets() -> List[Dict]:
    """Return list of presets from presets.json."""
    path = os.path.join(SCRIPT_DIR, 'presets.json')
    with open(path, 'r') as f:
        data = json.load(f)
    presets = data.get('presets', [])
    # Normalise: expose 'template' as alias for 'dork'
    for p in presets:
        p.setdefault('template', p.get('dork', ''))
        # Normalise category to slug for filtering
        p['category_label'] = p.get('category', '')
        p['category'] = p['category_label'].lower().replace(' ', '_').replace('&', 'and')
    return presets


def _quote_if_spaced(value: str) -> str:
    value = value.strip()
    if ' ' in value and not (value.startswith('"') and value.endswith('"')):
        return f'"{value}"'
    return value


def assemble_dork(
    keywords: Optional[List[str]] = None,
    operators: Optional[Dict[str, str]] = None,
    preset_id: Optional[str] = None,
) -> str:
    """
    Build a Google dork string.

    operators keys: operator id (e.g. 'site', 'intitle', 'filetype', 'exclude', 'exact')
    """
    if operators is None:
        operators = {}
    if keywords is None:
        keywords = []

    parts = []

    # Start from preset dork if given
    if preset_id:
        presets = load_presets()
        preset = next((p for p in presets if p['id'] == preset_id), None)
        if preset:
            parts.append(preset['template'])

    # Build syntax lookup
    op_list = load_operators()
    syntax_map = {op['id']: op['syntax'] for op in op_list}

    for opname, value in operators.items():
        if not value or not value.strip():
            continue
        value = value.strip()

        if opname in ('exclude', 'minus'):
            for term in [t.strip() for t in value.split(',') if t.strip()]:
                parts.append(f'-{_quote_if_spaced(term)}')
        elif opname == 'exact':
            parts.append(f'"{value}"')
        elif opname == 'wildcard':
            parts.append('*')
        elif opname in ('or', 'and'):
            parts.append(value)
        else:
            syntax = syntax_map.get(opname, f'{opname}:')
            parts.append(f'{syntax}{_quote_if_spaced(value)}')

    for kw in keywords:
        kw = kw.strip()
        if kw:
            parts.append(_quote_if_spaced(kw))

    return ' '.join(parts)


if __name__ == '__main__':
    print(assemble_dork(
        keywords=['login'],
        operators={'intitle': 'index of', 'filetype': 'sql'},
    ))
    print(assemble_dork(preset_id='open_dir_generic'))
