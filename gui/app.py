#!/usr/bin/env python3
"""Flask GUI for dookie."""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from flask import Flask, render_template, request, jsonify
from assembler import assemble_dork, load_operators, load_presets

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), 'static'),
    template_folder=os.path.join(os.path.dirname(__file__), 'templates')
)


@app.route('/')
def index():
    operators = load_operators()
    presets = load_presets()
    # Group presets by category for template
    categories = {}
    for p in presets:
        categories.setdefault(p['category'], []).append(p)
    return render_template('index.html', operators=operators,
                           presets=presets, categories=categories)


@app.route('/api/presets')
def api_presets():
    return jsonify(load_presets())


@app.route('/api/operators')
def api_operators():
    return jsonify(load_operators())


@app.route('/api/dork', methods=['POST'])
def api_dork():
    data = request.get_json(force=True)
    keywords = data.get('keywords', [])
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split() if k.strip()]
    operators = data.get('operators', {})
    preset_id = data.get('preset_id') or None
    dork = assemble_dork(keywords=keywords, operators=operators,
                         preset_id=preset_id)
    return jsonify({'dork': dork})


if __name__ == '__main__':
    app.run(debug=True)
