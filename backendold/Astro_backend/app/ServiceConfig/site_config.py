#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Site Config API - stores theme/site configuration as a JSON file

from ServiceConfig import *
import json
import os

CONFIG_PATH = '/app/uploads/site_config.json'


@app.route('/site-config', methods=['GET'])
def get_site_config():
    """Return the saved site configuration (theme, logo, colors, etc.)"""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return jsonify({"status": "success", "data": config})
        else:
            return jsonify({"status": "success", "data": {}})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/site-config', methods=['POST'])
def save_site_config():
    """Save site configuration to a persistent JSON file"""
    try:
        data = request.json
        # Ensure uploads directory exists
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


LAYOUT_PATH = '/app/uploads/page_layout.json'


@app.route('/page-layout', methods=['GET'])
def get_page_layout():
    """Return the saved page layout configuration"""
    try:
        if os.path.exists(LAYOUT_PATH):
            with open(LAYOUT_PATH, 'r', encoding='utf-8') as f:
                layout = json.load(f)
            return jsonify({"status": "success", "data": layout})
        else:
            return jsonify({"status": "success", "data": []})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/page-layout', methods=['POST'])
def save_page_layout():
    """Save page layout configuration to a persistent JSON file"""
    try:
        data = request.json
        os.makedirs(os.path.dirname(LAYOUT_PATH), exist_ok=True)
        with open(LAYOUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
