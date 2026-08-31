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
        dataInput = request.json
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "error", "message": "Permission Denied"}), 403
            
        data = dataInput.get('data', {})
        # Ensure uploads directory exists
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        try:
            logAction(user_id=user_data.get('user_id'), path="/site-config", log="Admin updated site configuration", type="info")
        except:
            pass
            
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


import html

def sanitize_html(text):
    if not isinstance(text, str):
        return text
    # Basic sanitization to prevent XSS (encode < and >)
    return text.replace('<script', '&lt;script').replace('javascript:', 'javascript&#58;').replace('onerror=', 'onerror&#61;')

def sanitize_block(block):
    if isinstance(block, dict):
        for k, v in block.items():
            if isinstance(v, str):
                block[k] = sanitize_html(v)
            elif isinstance(v, dict):
                sanitize_block(v)
            elif isinstance(v, list):
                for item in v:
                    sanitize_block(item)

@app.route('/page-layout', methods=['POST'])
def save_page_layout():
    """Save page layout configuration to a persistent JSON file"""
    try:
        dataInput = request.json
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "error", "message": "Permission Denied"}), 403
            
        data = dataInput.get('data', [])
        
        # Sanitize HTML to prevent XSS
        if isinstance(data, list):
            for block in data:
                sanitize_block(block)
                
        os.makedirs(os.path.dirname(LAYOUT_PATH), exist_ok=True)
        with open(LAYOUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        try:
            logAction(user_id=user_data.get('user_id'), path="/page-layout", log="Admin updated page layout", type="info")
        except:
            pass
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
