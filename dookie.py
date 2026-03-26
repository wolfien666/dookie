#!/usr/bin/env python3
"""
dookie — Google Dork Builder

Usage:
  python dookie.py              # interactive Rich CLI menu
  python dookie.py --tui        # Textual TUI (tabbed wizard)
  python dookie.py build        # jump to builder
  python dookie.py dirs         # jump to open-directory finder
  python dookie.py files        # jump to file finder
  python dookie.py presets      # jump to preset browser
"""
import argparse
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from rich.console import Console
console = Console()


def main():
    parser = argparse.ArgumentParser(prog='dookie', description='Google dork builder')
    parser.add_argument('--tui', action='store_true', help='Launch Textual TUI')
    parser.add_argument('mode', nargs='?',
                        choices=['build', 'dirs', 'files', 'presets'],
                        help='Jump directly to a CLI mode')
    args = parser.parse_args()

    if args.tui:
        from gui.tui import run
        run()
        return

    from cli.display import print_banner
    print_banner()

    if args.mode == 'build':
        from cli.builder import run; run()
    elif args.mode == 'dirs':
        from cli.dirfinder import run; run()
    elif args.mode == 'files':
        from cli.filefinder import run; run()
    elif args.mode == 'presets':
        from cli.presets_cli import run; run()
    else:
        from cli.menu import run; run()


if __name__ == '__main__':
    main()
