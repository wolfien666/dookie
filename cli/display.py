#!/usr/bin/env python3
"""Shared Rich display helpers — banner, tables, panels."""
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

try:
    import art
    _HAS_ART = True
except ImportError:
    _HAS_ART = False

console = Console()

GRADIENT = ['bright_magenta', 'magenta', 'cyan', 'bright_cyan']


def _gradient_text(text: str) -> Text:
    colors = GRADIENT
    t = Text()
    for i, ch in enumerate(text):
        t.append(ch, style=f'bold {colors[i % len(colors)]}')
    return t


def print_banner():
    console.print()
    if _HAS_ART:
        raw = art.text2art('dookie', font='tarty1')
    else:
        raw = '  dookie'
    for line in raw.split('\n'):
        console.print(_gradient_text(line))
    console.print()
    console.print('  [dim]Google dork builder — internet-wide OSINT[/dim]')
    console.print()


def print_section(title: str):
    console.rule(f'[bold yellow]{title}[/bold yellow]')
    console.print()


def numbered_table(items: list, title: str = '', col: str = 'Option') -> Table:
    table = Table(title=title, box=box.SIMPLE_HEAD, show_header=True,
                  header_style='bold cyan')
    table.add_column('#', style='dim', width=4)
    table.add_column(col, style='white')
    for i, item in enumerate(items, 1):
        table.add_row(str(i), item)
    return table


def live_preview(dork: str):
    console.print()
    console.print(Panel(
        f'[bold green]{dork}[/bold green]',
        title='[bold]Dork Preview[/bold]',
        border_style='green',
        expand=False
    ))
    console.print()


def ask(prompt: str, default: str = '') -> str:
    suffix = f' [dim](leave blank to skip)[/dim]' if default == '' else f' [dim](default: {default})[/dim]'
    return console.input(f'  [bold cyan]{prompt}[/bold cyan]{suffix}: ').strip() or default


def ask_choice(prompt: str, choices: list) -> int:
    """Ask user to pick from 1..N, return 0-based index or -1 on cancel."""
    while True:
        raw = console.input(f'  [bold]{prompt}[/bold] (1-{len(choices)}, or 0 to cancel): ').strip()
        if raw == '0':
            return -1
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return idx
        except ValueError:
            pass
        console.print('  [red]Invalid choice, try again.[/red]')


def mode_toggle() -> str:
    """Ask user for Basic or Advanced mode. Returns 'basic' or 'advanced'."""
    console.print()
    console.print('  [bold]Select mode:[/bold]')
    console.print('  [green]1[/green]  Basic     — choose a preset and go')
    console.print('  [yellow]2[/yellow]  Advanced  — preset + custom keywords & operators')
    console.print()
    while True:
        raw = ask_choice('Mode', ['Basic', 'Advanced'])
        if raw == 0:
            return 'basic'
        elif raw == 1:
            return 'advanced'
