#!/usr/bin/env python3
"""Core dork string assembly engine.
Used by both CLI and GUI — single source of truth.
"""
import json
import os
import re
from typing import Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def load_operators() -> List[Dict]:
    path = os.path.join(SCRIPT_DIR, 'operators.json')
    with open(path, 'r') as f:
        return json.load(f)['operators']


def load_presets() -> List[Dict]:
    path = os.path.join(SCRIPT_DIR, 'presets.json')
    with open(path, 'r') as f:
        return json.load(f)['presets']


def _quote_if_spaced(value: str) -> str:
    """Wrap value in quotes if it contains spaces and isn't already quoted."""
    value = value.strip()
    if ' ' in value and not (value.startswith('"') and value.endswith('"')):
        return f'"{value}"'
    return value


def assemble_dork(
    keywords: Optional[List[str]] = None,
    operators: Optional[Dict[str, str]] = None,
    preset_id: Optional[str] = None,
    base_template: Optional[str] = None
) -> str:
    """
    Assemble a Google dork string.

    Args:
        keywords:      plain keywords / phrases
        operators:     dict of operator name -> value
                       e.g. {"site": "example.com", "intitle": "index of"}
        preset_id:     load template from presets.json by id
        base_template: raw template string to start from

    Returns:
        Ready-to-paste Google search string.
    """
    if operators is None:
        operators = {}
    if keywords is None:
        keywords = []

    parts = []

    # Start from preset template if requested
    if preset_id:
        presets = load_presets()
        preset = next((p for p in presets if p['id'] == preset_id), None)
        if preset:
            parts.append(preset['template'])
    elif base_template:
        parts.append(base_template)

    # Build operator lookup
    op_list = load_operators()
    opdict = {op['name']: op['syntax'] for op in op_list}

    # Append operators
    for opname, value in operators.items():
        if not value or not value.strip():
            continue
        value = value.strip()
        syntax = opdict.get(opname)
        if not syntax:
            continue

        if opname == 'quotes':
            parts.append(f'"{value}"')
        elif opname == 'minus':
            # Support multiple exclusions separated by commas
            for term in [t.strip() for t in value.split(',') if t.strip()]:
                parts.append(f'-{_quote_if_spaced(term)}')
        elif opname in ('or', 'pipe'):
            # value like "pdf|doc|xls" → already formatted
            parts.append(value)
        elif opname == 'wildcard':
            parts.append('*')
        else:
            parts.append(f'{syntax}{_quote_if_spaced(value)}')

    # Append plain keywords
    for kw in keywords:
        kw = kw.strip()
        if not kw:
            continue
        parts.append(_quote_if_spaced(kw))

    return ' '.join(parts)


if __name__ == '__main__':
    # Quick smoke test
    print(assemble_dork(
        keywords=['login'],
        operators={'intitle': 'index of', 'filetype': 'sql'},
    ))
