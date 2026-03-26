#!/usr/bin/env python3
"""
dookie - Google dork builder

Usage:
  python dookie.py               # interactive CLI menu
  python dookie.py --gui         # launch web GUI at http://127.0.0.1:5000
  python dookie.py build         # CLI keyword+operator builder
  python dookie.py dirs          # CLI open-directory finder
  python dookie.py files         # CLI file-type finder
  python dookie.py presets       # CLI preset browser
"""
import argparse
import sys
import os

from rich.console import Console
console = Console()

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def launch_gui():
    import threading
    import webbrowser
    from gui.app import app

    def run():
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    console.print('')
    console.print('[bold green]Dookie GUI[/bold green] running at [underline]http://127.0.0.1:5000[/underline]')
    console.print('Press [bold]Ctrl+C[/bold] to stop.')
    webbrowser.open('http://127.0.0.1:5000')
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        console.print('[yellow]Server stopped.[/yellow]')
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        prog='dookie',
        description='Google dork builder'
    )
    parser.add_argument('--gui', action='store_true', help='Launch web GUI')
    parser.add_argument('mode', nargs='?', choices=['build', 'dirs', 'files', 'presets'],
                        help='CLI mode to launch directly')
    args = parser.parse_args()

    if args.gui:
        launch_gui()
        return

    # Import CLI router
    from cli.display import print_banner
    print_banner()

    if args.mode == 'build':
        from cli.builder import run as run_builder
        run_builder()
    elif args.mode == 'dirs':
        from cli.dirfinder import run as run_dirs
        run_dirs()
    elif args.mode == 'files':
        from cli.filefinder import run as run_files
        run_files()
    elif args.mode == 'presets':
        from cli.presets_cli import run as run_presets
        run_presets()
    else:
        # Interactive main menu
        from cli.menu import run as run_menu
        run_menu()


if __name__ == '__main__':
    main()
