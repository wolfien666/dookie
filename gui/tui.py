#!/usr/bin/env python3
"""
Textual TUI for dookie — tabbed interface with step-by-step wizard.
Run standalone:  python gui/tui.py
Or via:          python dookie.py --tui
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

try:
    from textual.app import App, ComposeResult
    from textual.widgets import (
        Header, Footer, TabbedContent, TabPane,
        Input, Button, Select, Label, Static, RadioButton, RadioSet
    )
    from textual.containers import Vertical, Horizontal, Container
    from textual.reactive import reactive
    from textual import on
    _HAS_TEXTUAL = True
except ImportError:
    _HAS_TEXTUAL = False

from assembler import assemble_dork, load_operators, load_presets


# ---- Fallback: rich-based TUI when textual is not installed -----------------
def _rich_tui():
    """Minimal Rich fallback when Textual is not available."""
    from cli.menu import run
    from rich.console import Console
    console = Console()
    console.print('[yellow]Textual not installed — falling back to Rich CLI menu.[/yellow]')
    console.print('[dim]Install with: pip install textual[/dim]\n')
    run()


if not _HAS_TEXTUAL:
    def run():
        _rich_tui()
else:
    # ---- Helpers ----------------------------------------------------------------
    def _preset_options(category_substring: str):
        presets = load_presets()
        matches = [p for p in presets
                   if category_substring.lower() in p['category'].lower()
                   or category_substring.lower() in p['category_label'].lower()]
        return [(p['name'], p['id']) for p in matches]

    def _all_preset_options():
        return [(p['name'], p['id']) for p in load_presets()]

    CSS = """
    Screen { background: #0d0d0d; }
    Header { background: #1a0030; color: #b44fff; }
    Footer { background: #0d0d0d; }
    TabbedContent { background: #0d0d0d; }
    TabPane { padding: 1 2; }
    .wizard-box { border: solid #2a2a2a; padding: 1 2; margin-bottom: 1; }
    .preview-box { border: solid #39ff14; background: #0a1a0a;
                   padding: 1 2; margin-top: 1; color: #39ff14;
                   min-height: 4; }
    .step-label { color: #00d4ff; text-style: bold; margin-bottom: 1; }
    .hint { color: #555; margin-bottom: 1; }
    .section-title { color: #ffd600; text-style: bold; margin: 1 0; }
    Input { background: #1e1e1e; border: solid #2a2a2a; color: #e0e0e0; }
    Input:focus { border: solid #b44fff; }
    Button { background: #b44fff; color: #000; border: none; margin-top: 1; }
    Button:hover { background: #00d4ff; }
    Button.secondary { background: #1e1e1e; border: solid #2a2a2a; color: #888; }
    Button.copy { background: #1e1e1e; border: solid #00d4ff; color: #00d4ff; }
    Select { background: #1e1e1e; border: solid #2a2a2a; color: #e0e0e0; }
    RadioButton { color: #e0e0e0; }
    .mode-row { height: 3; }
    .hidden { display: none; }
    """

    class DorkPreview(Static):
        """Live dork preview widget."""
        dork = reactive('')

        def render(self):
            return self.dork if self.dork else '(your dork will appear here)'


    class WizardStep(Container):
        """A single wizard step panel."""
        pass


    # ---- Builder Tab ------------------------------------------------------------
    class BuilderTab(TabPane):
        STEP = reactive(1)
        _keywords: str = ''
        _mode: str = 'basic'
        _ops: dict = {}

        def compose(self) -> ComposeResult:
            yield Label('\u2731 Keyword + Operator Builder', classes='section-title')
            with Vertical(classes='wizard-box', id='bld-s1'):
                yield Label('Step 1 \u2014 Keywords', classes='step-label')
                yield Label('What are you hunting for?', classes='hint')
                yield Input(placeholder='e.g. admin login database', id='bld-kw')
                yield Button('Next \u2192', id='bld-s1-next')
            with Vertical(classes='wizard-box hidden', id='bld-s2'):
                yield Label('Step 2 \u2014 Mode', classes='step-label')
                with RadioSet(id='bld-mode'):
                    yield RadioButton('Basic  \u2014 site, intitle, filetype, intext', value=True, id='bld-basic')
                    yield RadioButton('Advanced \u2014 full operator picker', id='bld-adv')
                yield Horizontal(
                    Button('\u2190 Back', id='bld-s2-back', classes='secondary'),
                    Button('Next \u2192', id='bld-s2-next'),
                )
            with Vertical(classes='wizard-box hidden', id='bld-s3'):
                yield Label('Step 3 \u2014 Operators', classes='step-label')
                yield Label('site:', classes='hint')
                yield Input(placeholder='example.com', id='bop-site')
                yield Label('intitle:', classes='hint')
                yield Input(placeholder='index of', id='bop-intitle')
                yield Label('filetype:', classes='hint')
                yield Input(placeholder='pdf', id='bop-filetype')
                yield Label('intext:', classes='hint')
                yield Input(placeholder='password', id='bop-intext')
                yield Label('Exclude (-term):', classes='hint')
                yield Input(placeholder='login,admin', id='bop-minus')
                yield Horizontal(
                    Button('\u2190 Back', id='bld-s3-back', classes='secondary'),
                    Button('\u26a1 Generate', id='bld-generate'),
                )
            yield Label('\U0001f50d Dork Preview', classes='section-title')
            yield DorkPreview(id='preview-builder', classes='preview-box')
            yield Button('\U0001f4cb Copy', id='bld-copy', classes='copy')

        @on(Button.Pressed, '#bld-s1-next')
        def step1_next(self): self._go(2)

        @on(Button.Pressed, '#bld-s2-back')
        def step2_back(self): self._go(1)

        @on(Button.Pressed, '#bld-s2-next')
        def step2_next(self): self._go(3)

        @on(Button.Pressed, '#bld-s3-back')
        def step3_back(self): self._go(2)

        @on(Button.Pressed, '#bld-generate')
        def do_generate(self):
            kw = [k for k in self.query_one('#bld-kw', Input).value.split() if k]
            ops = {}
            for oid in ['site','intitle','filetype','intext']:
                v = self.query_one(f'#bop-{oid}', Input).value.strip()
                if v: ops[oid] = v
            minus = self.query_one('#bop-minus', Input).value.strip()
            if minus: ops['exclude'] = minus
            dork = assemble_dork(keywords=kw, operators=ops)
            self.query_one('#preview-builder', DorkPreview).dork = dork

        @on(Button.Pressed, '#bld-copy')
        def do_copy(self):
            dork = self.query_one('#preview-builder', DorkPreview).dork
            if dork:
                try:
                    import pyperclip; pyperclip.copy(dork)
                    self.app.notify('Copied!')
                except ImportError:
                    self.app.notify('pip install pyperclip to enable copy')

        def _go(self, step: int):
            for s in [1, 2, 3]:
                w = self.query_one(f'#bld-s{s}')
                if s == step:
                    w.remove_class('hidden')
                else:
                    w.add_class('hidden')


    # ---- Dirs Tab ---------------------------------------------------------------
    class DirsTab(TabPane):
        def compose(self) -> ComposeResult:
            opts = _preset_options('open_director') or _preset_options('director')
            if not opts:
                opts = [('(no open-directory presets found)', '')]
            yield Label('\U0001f4c2 Open Directory Finder', classes='section-title')
            with Vertical(classes='wizard-box', id='dir-s1'):
                yield Label('Step 1 \u2014 Mode', classes='step-label')
                with RadioSet(id='dir-mode'):
                    yield RadioButton('Basic  \u2014 one-click preset', value=True)
                    yield RadioButton('Advanced \u2014 preset + filters')
                yield Button('Next \u2192', id='dir-s1-next')
            with Vertical(classes='wizard-box hidden', id='dir-s2'):
                yield Label('Step 2 \u2014 Pick Preset', classes='step-label')
                yield Select(opts, id='dir-preset')
                yield Horizontal(
                    Button('\u2190 Back', id='dir-s2-back', classes='secondary'),
                    Button('Next \u2192', id='dir-s2-next'),
                )
            with Vertical(classes='wizard-box hidden', id='dir-s3'):
                yield Label('Step 3 \u2014 Filters (Advanced)', classes='step-label')
                yield Label('Keywords:', classes='hint')
                yield Input(placeholder='mp4 movies 2024', id='dir-kw')
                yield Label('intitle:', classes='hint')
                yield Input(id='dir-intitle')
                yield Label('intext:', classes='hint')
                yield Input(id='dir-intext')
                yield Label('filetype:', classes='hint')
                yield Input(id='dir-filetype')
                yield Label('Exclude:', classes='hint')
                yield Input(id='dir-minus')
                yield Horizontal(
                    Button('\u2190 Back', id='dir-s3-back', classes='secondary'),
                    Button('\u26a1 Generate', id='dir-generate'),
                )
            yield Label('\U0001f50d Dork Preview', classes='section-title')
            yield DorkPreview(id='preview-dirs', classes='preview-box')
            yield Button('\U0001f4cb Copy', id='dir-copy', classes='copy')

        def _mode(self) -> str:
            rs = self.query_one('#dir-mode', RadioSet)
            return 'advanced' if rs.pressed_index == 1 else 'basic'

        @on(Button.Pressed, '#dir-s1-next')
        def s1_next(self):
            self._go(2)

        @on(Button.Pressed, '#dir-s2-back')
        def s2_back(self): self._go(1)

        @on(Button.Pressed, '#dir-s2-next')
        def s2_next(self):
            if self._mode() == 'basic':
                self._generate()
            else:
                self._go(3)

        @on(Button.Pressed, '#dir-s3-back')
        def s3_back(self): self._go(2)

        @on(Button.Pressed, '#dir-generate')
        def do_generate(self): self._generate()

        def _generate(self):
            pid = self.query_one('#dir-preset', Select).value
            ops = {}
            kw = []
            if self._mode() == 'advanced':
                raw = self.query_one('#dir-kw', Input).value.strip()
                kw = [k for k in raw.split() if k]
                for oid in ['intitle','intext','filetype']:
                    v = self.query_one(f'#dir-{oid}', Input).value.strip()
                    if v: ops[oid] = v
                minus = self.query_one('#dir-minus', Input).value.strip()
                if minus: ops['exclude'] = minus
            dork = assemble_dork(keywords=kw, operators=ops, preset_id=pid if pid else None)
            self.query_one('#preview-dirs', DorkPreview).dork = dork

        @on(Button.Pressed, '#dir-copy')
        def do_copy(self):
            dork = self.query_one('#preview-dirs', DorkPreview).dork
            if dork:
                try:
                    import pyperclip; pyperclip.copy(dork)
                    self.app.notify('Copied!')
                except ImportError:
                    self.app.notify('pip install pyperclip to enable copy')

        def _go(self, step: int):
            for s in [1, 2, 3]:
                w = self.query_one(f'#dir-s{s}')
                if s == step:
                    w.remove_class('hidden')
                else:
                    w.add_class('hidden')


    # ---- Files Tab --------------------------------------------------------------
    class FilesTab(TabPane):
        def compose(self) -> ComposeResult:
            opts = _preset_options('exposed_file') or _preset_options('file')
            if not opts:
                opts = [('(no file presets found)', '')]
            yield Label('\U0001f4c4 File Finder', classes='section-title')
            with Vertical(classes='wizard-box', id='ff-s1'):
                yield Label('Step 1 \u2014 Mode', classes='step-label')
                with RadioSet(id='ff-mode'):
                    yield RadioButton('Basic  \u2014 one-click preset', value=True)
                    yield RadioButton('Advanced \u2014 preset + filters')
                yield Button('Next \u2192', id='ff-s1-next')
            with Vertical(classes='wizard-box hidden', id='ff-s2'):
                yield Label('Step 2 \u2014 Pick File Type', classes='step-label')
                yield Select(opts, id='ff-preset')
                yield Horizontal(
                    Button('\u2190 Back', id='ff-s2-back', classes='secondary'),
                    Button('Next \u2192', id='ff-s2-next'),
                )
            with Vertical(classes='wizard-box hidden', id='ff-s3'):
                yield Label('Step 3 \u2014 Filters (Advanced)', classes='step-label')
                yield Label('Keywords:', classes='hint')
                yield Input(placeholder='password username', id='ff-kw')
                yield Label('intext:', classes='hint')
                yield Input(id='ff-intext')
                yield Label('inurl:', classes='hint')
                yield Input(id='ff-inurl')
                yield Label('filetype override:', classes='hint')
                yield Input(id='ff-filetype')
                yield Label('Exclude:', classes='hint')
                yield Input(id='ff-minus')
                yield Horizontal(
                    Button('\u2190 Back', id='ff-s3-back', classes='secondary'),
                    Button('\u26a1 Generate', id='ff-generate'),
                )
            yield Label('\U0001f50d Dork Preview', classes='section-title')
            yield DorkPreview(id='preview-files', classes='preview-box')
            yield Button('\U0001f4cb Copy', id='ff-copy', classes='copy')

        def _mode(self) -> str:
            rs = self.query_one('#ff-mode', RadioSet)
            return 'advanced' if rs.pressed_index == 1 else 'basic'

        @on(Button.Pressed, '#ff-s1-next')
        def s1_next(self): self._go(2)

        @on(Button.Pressed, '#ff-s2-back')
        def s2_back(self): self._go(1)

        @on(Button.Pressed, '#ff-s2-next')
        def s2_next(self):
            if self._mode() == 'basic':
                self._generate()
            else:
                self._go(3)

        @on(Button.Pressed, '#ff-s3-back')
        def s3_back(self): self._go(2)

        @on(Button.Pressed, '#ff-generate')
        def do_generate(self): self._generate()

        def _generate(self):
            pid = self.query_one('#ff-preset', Select).value
            ops = {}
            kw = []
            if self._mode() == 'advanced':
                raw = self.query_one('#ff-kw', Input).value.strip()
                kw = [k for k in raw.split() if k]
                for oid in ['intext','inurl','filetype']:
                    v = self.query_one(f'#ff-{oid}', Input).value.strip()
                    if v: ops[oid] = v
                minus = self.query_one('#ff-minus', Input).value.strip()
                if minus: ops['exclude'] = minus
            dork = assemble_dork(keywords=kw, operators=ops, preset_id=pid if pid else None)
            self.query_one('#preview-files', DorkPreview).dork = dork

        @on(Button.Pressed, '#ff-copy')
        def do_copy(self):
            dork = self.query_one('#preview-files', DorkPreview).dork
            if dork:
                try:
                    import pyperclip; pyperclip.copy(dork)
                    self.app.notify('Copied!')
                except ImportError:
                    self.app.notify('pip install pyperclip to enable copy')

        def _go(self, step: int):
            for s in [1, 2, 3]:
                w = self.query_one(f'#ff-s{s}')
                if s == step:
                    w.remove_class('hidden')
                else:
                    w.add_class('hidden')


    # ---- Presets Tab ------------------------------------------------------------
    class PresetsTab(TabPane):
        def compose(self) -> ComposeResult:
            presets = load_presets()
            yield Label('\u2b50 Preset Browser', classes='section-title')
            yield Label('Select a preset to load it into the preview.', classes='hint')
            opts = [(f"{p['category_label']} \u2014 {p['name']}", p['id']) for p in presets]
            yield Select(opts, id='all-preset')
            yield Button('\u26a1 Load Preset', id='preset-load')
            yield Label('\U0001f50d Dork Preview', classes='section-title')
            yield DorkPreview(id='preview-presets', classes='preview-box')
            yield Button('\U0001f4cb Copy', id='preset-copy', classes='copy')

        @on(Button.Pressed, '#preset-load')
        def load_preset(self):
            pid = self.query_one('#all-preset', Select).value
            presets = load_presets()
            preset = next((p for p in presets if p['id'] == pid), None)
            if preset:
                dork = preset['template']
                if preset.get('requires_target'):
                    self.app.notify('This preset needs a TARGET — edit the dork manually.')
                self.query_one('#preview-presets', DorkPreview).dork = dork

        @on(Button.Pressed, '#preset-copy')
        def do_copy(self):
            dork = self.query_one('#preview-presets', DorkPreview).dork
            if dork:
                try:
                    import pyperclip; pyperclip.copy(dork)
                    self.app.notify('Copied!')
                except ImportError:
                    self.app.notify('pip install pyperclip to enable copy')


    # ---- Main App ---------------------------------------------------------------
    class DookieApp(App):
        CSS = CSS
        TITLE = 'dookie'
        SUB_TITLE = 'Google Dork Builder'
        BINDINGS = [('q', 'quit', 'Quit'), ('ctrl+c', 'quit', 'Quit')]

        def compose(self) -> ComposeResult:
            yield Header()
            with TabbedContent():
                with BuilderTab('\U0001f527 Builder'):
                    pass
                with DirsTab('\U0001f4c2 Open Dirs'):
                    pass
                with FilesTab('\U0001f4c4 File Finder'):
                    pass
                with PresetsTab('\u2b50 Presets'):
                    pass
            yield Footer()


    def run():
        DookieApp().run()


if __name__ == '__main__':
    run()
