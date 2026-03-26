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
    from textual.containers import Vertical, Horizontal, Container, VerticalScroll
    from textual.reactive import reactive
    from textual import on
    _HAS_TEXTUAL = True
except ImportError:
    _HAS_TEXTUAL = False

from assembler import assemble_dork, load_operators, load_presets


def _rich_tui():
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
    def _preset_options(category_substring: str):
        presets = load_presets()
        matches = [p for p in presets
                   if category_substring.lower() in p['category'].lower()
                   or category_substring.lower() in p['category_label'].lower()]
        return [(p['name'], p['id']) for p in matches]

    CSS = """
    Screen { background: #0d0d0d; }
    Header { background: #1a0030; color: #b44fff; }
    Footer { background: #0d0d0d; }
    TabbedContent { height: 1fr; background: #0d0d0d; }
    TabPane { height: 1fr; padding: 0; }
    VerticalScroll { height: 1fr; padding: 1 2; }
    .wizard-box { border: solid #2a2a2a; padding: 1 2; margin-bottom: 1; height: auto; }
    .preview-box { border: solid #39ff14; background: #0a1a0a;
                   padding: 1 2; margin-top: 1; color: #39ff14;
                   min-height: 4; height: auto; }
    .step-label { color: #00d4ff; text-style: bold; margin-bottom: 1; }
    .hint { color: #555; margin-bottom: 1; }
    .section-title { color: #ffd600; text-style: bold; margin: 1 0; }
    Input { background: #1e1e1e; border: solid #2a2a2a; color: #e0e0e0; height: 3; }
    Input:focus { border: solid #b44fff; }
    Button { background: #b44fff; color: #000; border: none; margin-top: 1; height: 3; }
    Button:hover { background: #00d4ff; }
    Button.secondary { background: #1e1e1e; border: solid #2a2a2a; color: #888; }
    Button.copy { background: #1e1e1e; border: solid #00d4ff; color: #00d4ff; }
    Select { background: #1e1e1e; border: solid #2a2a2a; color: #e0e0e0; }
    RadioButton { color: #e0e0e0; }
    Horizontal { height: auto; }
    """

    class DorkPreview(Static):
        dork = reactive('')
        def render(self):
            return self.dork if self.dork else '(your dork will appear here)'


    # ---- Builder Tab ------------------------------------------------------------
    class BuilderTab(TabPane):
        BINDINGS = [
            ('j', 'scroll_dn', 'Scroll ▼'),
            ('k', 'scroll_up', 'Scroll ▲'),
            ('pagedown', 'page_dn', 'PgDn'),
            ('pageup',   'page_up', 'PgUp'),
        ]
        _step: int = 1
        _mode: str = 'basic'

        def compose(self) -> ComposeResult:
            with VerticalScroll(id='bld-scroll'):
                yield Label('\u2731 Keyword + Operator Builder', classes='section-title')
                yield self._render_step()
                yield Label('\U0001f50d Dork Preview', classes='section-title')
                yield DorkPreview(id='preview-builder', classes='preview-box')
                yield Button('\U0001f4cb Copy', id='bld-copy', classes='copy')

        def _render_step(self):
            if self._step == 1:
                return self._step1()
            elif self._step == 2:
                return self._step2()
            else:
                return self._step3()

        def _step1(self):
            box = Vertical(classes='wizard-box', id='bld-box')
            box.compose_add_child(Label('Step 1 \u2014 Keywords', classes='step-label'))
            box.compose_add_child(Label('What are you hunting for?', classes='hint'))
            box.compose_add_child(Input(placeholder='e.g. admin login database', id='bld-kw'))
            box.compose_add_child(Button('Next \u2192', id='bld-next'))
            return box

        def _step2(self):
            box = Vertical(classes='wizard-box', id='bld-box')
            box.compose_add_child(Label('Step 2 \u2014 Mode', classes='step-label'))
            rs = RadioSet(id='bld-mode')
            rs.compose_add_child(RadioButton('Basic  \u2014 site, intitle, filetype, intext', value=True, id='bld-basic'))
            rs.compose_add_child(RadioButton('Advanced \u2014 full operator picker', id='bld-adv'))
            box.compose_add_child(rs)
            row = Horizontal()
            row.compose_add_child(Button('\u2190 Back', id='bld-back', classes='secondary'))
            row.compose_add_child(Button('Next \u2192', id='bld-next'))
            box.compose_add_child(row)
            return box

        def _step3(self):
            box = Vertical(classes='wizard-box', id='bld-box')
            box.compose_add_child(Label('Step 3 \u2014 Operators', classes='step-label'))
            for lbl, pid, ph in [
                ('site:',          'bop-site',    'example.com  (optional)'),
                ('intitle:',       'bop-intitle', 'index of  (optional)'),
                ('filetype:',      'bop-filetype','pdf  (optional)'),
                ('intext:',        'bop-intext',  'password  (optional)'),
                ('Exclude (-term):','bop-minus',  'login,admin  (optional)'),
            ]:
                box.compose_add_child(Label(lbl, classes='hint'))
                box.compose_add_child(Input(placeholder=ph, id=pid))
            row = Horizontal()
            row.compose_add_child(Button('\u2190 Back', id='bld-back', classes='secondary'))
            row.compose_add_child(Button('\u26a1 Generate', id='bld-generate'))
            box.compose_add_child(row)
            return box

        def _refresh(self):
            scroll = self.query_one('#bld-scroll', VerticalScroll)
            try:
                old = self.query_one('#bld-box')
                old.remove()
            except Exception:
                pass
            title = self.query_one('.section-title')
            scroll.mount(self._render_step(), before=title)
            scroll.scroll_home(animate=False)

        @on(Button.Pressed, '#bld-next')
        def _next(self):
            if self._step == 1:
                self._step = 2
            elif self._step == 2:
                self._step = 3
            self._refresh()

        @on(Button.Pressed, '#bld-back')
        def _back(self):
            if self._step > 1:
                self._step -= 1
            self._refresh()

        @on(Button.Pressed, '#bld-generate')
        def do_generate(self):
            try:
                kw = [k for k in self.query_one('#bld-kw', Input).value.split() if k]
            except Exception:
                kw = []
            ops = {}
            for oid in ['site','intitle','filetype','intext']:
                try:
                    v = self.query_one(f'#bop-{oid}', Input).value.strip()
                    if v: ops[oid] = v
                except Exception:
                    pass
            try:
                minus = self.query_one('#bop-minus', Input).value.strip()
                if minus: ops['exclude'] = minus
            except Exception:
                pass
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

        def action_scroll_dn(self): self.query_one('#bld-scroll', VerticalScroll).scroll_down()
        def action_scroll_up(self): self.query_one('#bld-scroll', VerticalScroll).scroll_up()
        def action_page_dn(self):   self.query_one('#bld-scroll', VerticalScroll).scroll_page_down()
        def action_page_up(self):   self.query_one('#bld-scroll', VerticalScroll).scroll_page_up()


    # ---- Dirs Tab ---------------------------------------------------------------
    class DirsTab(TabPane):
        BINDINGS = [
            ('j', 'scroll_dn', 'Scroll ▼'),
            ('k', 'scroll_up', 'Scroll ▲'),
            ('pagedown', 'page_dn', 'PgDn'),
            ('pageup',   'page_up', 'PgUp'),
        ]
        _step: int = 1
        _mode: str = 'basic'
        _opts: list = []

        def compose(self) -> ComposeResult:
            self._opts = _preset_options('open_director') or _preset_options('director')
            if not self._opts:
                self._opts = [('(no open-directory presets found)', '')]
            with VerticalScroll(id='dir-scroll'):
                yield Label('\U0001f4c2 Open Directory Finder', classes='section-title')
                yield self._render_step()
                yield Label('\U0001f50d Dork Preview', classes='section-title')
                yield DorkPreview(id='preview-dirs', classes='preview-box')
                yield Button('\U0001f4cb Copy', id='dir-copy', classes='copy')

        def _render_step(self):
            if self._step == 1: return self._step1()
            if self._step == 2: return self._step2()
            return self._step3()

        def _step1(self):
            box = Vertical(classes='wizard-box', id='dir-box')
            box.compose_add_child(Label('Step 1 \u2014 Mode', classes='step-label'))
            rs = RadioSet(id='dir-mode')
            rs.compose_add_child(RadioButton('Basic  \u2014 one-click preset', value=True))
            rs.compose_add_child(RadioButton('Advanced \u2014 preset + filters'))
            box.compose_add_child(rs)
            box.compose_add_child(Button('Next \u2192', id='dir-next'))
            return box

        def _step2(self):
            box = Vertical(classes='wizard-box', id='dir-box')
            box.compose_add_child(Label('Step 2 \u2014 Pick Preset', classes='step-label'))
            box.compose_add_child(Select(self._opts, id='dir-preset'))
            row = Horizontal()
            row.compose_add_child(Button('\u2190 Back', id='dir-back', classes='secondary'))
            row.compose_add_child(Button('Next \u2192', id='dir-next'))
            box.compose_add_child(row)
            return box

        def _step3(self):
            box = Vertical(classes='wizard-box', id='dir-box')
            box.compose_add_child(Label('Step 3 \u2014 Filters (Advanced)', classes='step-label'))
            for lbl, pid, ph in [
                ('Keywords:',  'dir-kw',      'mp4 movies 2024  (optional)'),
                ('intitle:',   'dir-intitle', 'index of  (optional)'),
                ('intext:',    'dir-intext',  'password  (optional)'),
                ('filetype:',  'dir-filetype','pdf  (optional)'),
                ('Exclude:',   'dir-minus',   '-login -admin  (optional)'),
            ]:
                box.compose_add_child(Label(lbl, classes='hint'))
                box.compose_add_child(Input(placeholder=ph, id=pid))
            row = Horizontal()
            row.compose_add_child(Button('\u2190 Back', id='dir-back', classes='secondary'))
            row.compose_add_child(Button('\u26a1 Generate', id='dir-generate'))
            box.compose_add_child(row)
            return box

        def _get_mode(self):
            try:
                rs = self.query_one('#dir-mode', RadioSet)
                return 'advanced' if rs.pressed_index == 1 else 'basic'
            except Exception:
                return 'basic'

        def _refresh(self):
            scroll = self.query_one('#dir-scroll', VerticalScroll)
            try:
                self.query_one('#dir-box').remove()
            except Exception:
                pass
            title = self.query_one('.section-title')
            scroll.mount(self._render_step(), before=title)
            scroll.scroll_home(animate=False)

        @on(Button.Pressed, '#dir-next')
        def _next(self):
            if self._step == 1:
                if self._get_mode() == 'basic':
                    self._step = 2
                    self._refresh()
                    self._generate()
                    return
                self._step = 2
            elif self._step == 2:
                self._step = 3
            self._refresh()

        @on(Button.Pressed, '#dir-back')
        def _back(self):
            if self._step > 1: self._step -= 1
            self._refresh()

        @on(Button.Pressed, '#dir-generate')
        def do_generate(self): self._generate()

        def _generate(self):
            try:
                pid = self.query_one('#dir-preset', Select).value
            except Exception:
                pid = None
            ops, kw = {}, []
            if self._get_mode() == 'advanced':
                try:
                    raw = self.query_one('#dir-kw', Input).value.strip()
                    kw = [k for k in raw.split() if k]
                except Exception:
                    pass
                for oid in ['intitle','intext','filetype']:
                    try:
                        v = self.query_one(f'#dir-{oid}', Input).value.strip()
                        if v: ops[oid] = v
                    except Exception:
                        pass
                try:
                    minus = self.query_one('#dir-minus', Input).value.strip()
                    if minus: ops['exclude'] = minus
                except Exception:
                    pass
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

        def action_scroll_dn(self): self.query_one('#dir-scroll', VerticalScroll).scroll_down()
        def action_scroll_up(self): self.query_one('#dir-scroll', VerticalScroll).scroll_up()
        def action_page_dn(self):   self.query_one('#dir-scroll', VerticalScroll).scroll_page_down()
        def action_page_up(self):   self.query_one('#dir-scroll', VerticalScroll).scroll_page_up()


    # ---- Files Tab --------------------------------------------------------------
    class FilesTab(TabPane):
        BINDINGS = [
            ('j', 'scroll_dn', 'Scroll ▼'),
            ('k', 'scroll_up', 'Scroll ▲'),
            ('pagedown', 'page_dn', 'PgDn'),
            ('pageup',   'page_up', 'PgUp'),
        ]
        _step: int = 1
        _mode: str = 'basic'
        _opts: list = []

        def compose(self) -> ComposeResult:
            self._opts = _preset_options('exposed_file') or _preset_options('file')
            if not self._opts:
                self._opts = [('(no file presets found)', '')]
            with VerticalScroll(id='ff-scroll'):
                yield Label('\U0001f4c4 File Finder', classes='section-title')
                yield self._render_step()
                yield Label('\U0001f50d Dork Preview', classes='section-title')
                yield DorkPreview(id='preview-files', classes='preview-box')
                yield Button('\U0001f4cb Copy', id='ff-copy', classes='copy')

        def _render_step(self):
            if self._step == 1: return self._step1()
            if self._step == 2: return self._step2()
            return self._step3()

        def _step1(self):
            box = Vertical(classes='wizard-box', id='ff-box')
            box.compose_add_child(Label('Step 1 \u2014 Mode', classes='step-label'))
            rs = RadioSet(id='ff-mode')
            rs.compose_add_child(RadioButton('Basic  \u2014 one-click preset', value=True))
            rs.compose_add_child(RadioButton('Advanced \u2014 preset + filters'))
            box.compose_add_child(rs)
            box.compose_add_child(Button('Next \u2192', id='ff-next'))
            return box

        def _step2(self):
            box = Vertical(classes='wizard-box', id='ff-box')
            box.compose_add_child(Label('Step 2 \u2014 Pick File Type', classes='step-label'))
            box.compose_add_child(Select(self._opts, id='ff-preset'))
            row = Horizontal()
            row.compose_add_child(Button('\u2190 Back', id='ff-back', classes='secondary'))
            row.compose_add_child(Button('Next \u2192', id='ff-next'))
            box.compose_add_child(row)
            return box

        def _step3(self):
            box = Vertical(classes='wizard-box', id='ff-box')
            box.compose_add_child(Label('Step 3 \u2014 Filters (Advanced)', classes='step-label'))
            for lbl, pid, ph in [
                ('Keywords:',         'ff-kw',      'password username  (optional)'),
                ('intext:',           'ff-intext',  'confidential  (optional)'),
                ('inurl:',            'ff-inurl',   'admin  (optional)'),
                ('filetype override:','ff-filetype','xls pdf  (optional)'),
                ('Exclude:',          'ff-minus',   '-login -signup  (optional)'),
            ]:
                box.compose_add_child(Label(lbl, classes='hint'))
                box.compose_add_child(Input(placeholder=ph, id=pid))
            row = Horizontal()
            row.compose_add_child(Button('\u2190 Back', id='ff-back', classes='secondary'))
            row.compose_add_child(Button('\u26a1 Generate', id='ff-generate'))
            box.compose_add_child(row)
            return box

        def _get_mode(self):
            try:
                rs = self.query_one('#ff-mode', RadioSet)
                return 'advanced' if rs.pressed_index == 1 else 'basic'
            except Exception:
                return 'basic'

        def _refresh(self):
            scroll = self.query_one('#ff-scroll', VerticalScroll)
            try:
                self.query_one('#ff-box').remove()
            except Exception:
                pass
            title = self.query_one('.section-title')
            scroll.mount(self._render_step(), before=title)
            scroll.scroll_home(animate=False)

        @on(Button.Pressed, '#ff-next')
        def _next(self):
            if self._step == 1:
                if self._get_mode() == 'basic':
                    self._step = 2
                    self._refresh()
                    self._generate()
                    return
                self._step = 2
            elif self._step == 2:
                self._step = 3
            self._refresh()

        @on(Button.Pressed, '#ff-back')
        def _back(self):
            if self._step > 1: self._step -= 1
            self._refresh()

        @on(Button.Pressed, '#ff-generate')
        def do_generate(self): self._generate()

        def _generate(self):
            try:
                pid = self.query_one('#ff-preset', Select).value
            except Exception:
                pid = None
            ops, kw = {}, []
            if self._get_mode() == 'advanced':
                try:
                    raw = self.query_one('#ff-kw', Input).value.strip()
                    kw = [k for k in raw.split() if k]
                except Exception:
                    pass
                for oid in ['intext','inurl','filetype']:
                    try:
                        v = self.query_one(f'#ff-{oid}', Input).value.strip()
                        if v: ops[oid] = v
                    except Exception:
                        pass
                try:
                    minus = self.query_one('#ff-minus', Input).value.strip()
                    if minus: ops['exclude'] = minus
                except Exception:
                    pass
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

        def action_scroll_dn(self): self.query_one('#ff-scroll', VerticalScroll).scroll_down()
        def action_scroll_up(self): self.query_one('#ff-scroll', VerticalScroll).scroll_up()
        def action_page_dn(self):   self.query_one('#ff-scroll', VerticalScroll).scroll_page_down()
        def action_page_up(self):   self.query_one('#ff-scroll', VerticalScroll).scroll_page_up()


    # ---- Presets Tab ------------------------------------------------------------
    class PresetsTab(TabPane):
        BINDINGS = [
            ('j', 'scroll_dn', 'Scroll ▼'),
            ('k', 'scroll_up', 'Scroll ▲'),
            ('pagedown', 'page_dn', 'PgDn'),
            ('pageup',   'page_up', 'PgUp'),
        ]

        def compose(self) -> ComposeResult:
            with VerticalScroll(id='pre-scroll'):
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
                    self.app.notify('This preset needs a TARGET \u2014 edit the dork manually.')
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

        def action_scroll_dn(self): self.query_one('#pre-scroll', VerticalScroll).scroll_down()
        def action_scroll_up(self): self.query_one('#pre-scroll', VerticalScroll).scroll_up()
        def action_page_dn(self):   self.query_one('#pre-scroll', VerticalScroll).scroll_page_down()
        def action_page_up(self):   self.query_one('#pre-scroll', VerticalScroll).scroll_page_up()


    # ---- Main App ---------------------------------------------------------------
    class DookieApp(App):
        CSS = CSS
        TITLE = 'dookie'
        SUB_TITLE = 'Google Dork Builder'
        BINDINGS = [
            ('q', 'quit', 'Quit'),
            ('ctrl+c', 'quit', 'Quit'),
        ]

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
