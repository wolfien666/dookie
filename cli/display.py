#!/usr/bin/env python3
"""Shared Rich display helpers."""
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
    t = Text()
    for i, ch in enumerate(text):
        t.append(ch, style=f'bold {GRADIENT[i % len(GRADIENT)]}')
    return t


def print_banner():
    console.print()
    if _HAS_ART:
        raw = art.text2art('dookie', font='tarty1')
    else:
        raw = '  dookie'
    for line in raw.split('\n'):
        if line.strip():
            console.print(_gradient_text(line))
    console.print()
    console.print('  [dim]Google Dork Builder — internet-wide OSINT[/dim]')
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
    suffix = ' [dim](leave blank to skip)[/dim]' if default == '' else f' [dim](default: {default})[/dim]'
    return console.input(f'  [bold cyan]{prompt}[/bold cyan]{suffix}: ').strip() or default


def ask_choice(prompt: str, choices: list) -> int:
    """Prompt user to pick 1..N. Returns 0-based index, or -1 on cancel/0."""
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
    """Return 'basic' or 'advanced'."""
    console.print()
    console.print('  [bold]Select mode:[/bold]')
    console.print('  [green]1[/green]  Basic     — choose a preset and go')
    console.print('  [yellow]2[/yellow]  Advanced  — preset + custom keywords & operators')
    console.print()
    idx = ask_choice('Mode', ['Basic', 'Advanced'])
    return 'advanced' if idx == 1 else 'basic'


def copy_offer(dork: str):
    try:
        import pyperclip
        raw = console.input('  Copy to clipboard? [y/N]: ').strip().lower()
        if raw == 'y':
            pyperclip.copy(dork)
            console.print('  [green]Copied![/green]')
    except ImportError:
        console.print('  [dim](install pyperclip to enable clipboard copy)[/dim]')
