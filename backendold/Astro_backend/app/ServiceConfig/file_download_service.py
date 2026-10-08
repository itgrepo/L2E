from flask import Flask, request, jsonify, send_from_directory, abort
import os
import json
from . import app, mysql

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

def get_original_filename(file_name, service_id=None):
    if not file_name:
        return ''
    clean_name = file_name
    if service_id:
        for p in [f"ds_{service_id}_", f"dict_{service_id}_", f"samp_{service_id}_", f"excel_{service_id}_"]:
            if clean_name.startswith(p):
                return clean_name[len(p):]
    for p in ['ds_', 'dict_', 'samp_', 'excel_']:
        if clean_name.startswith(p):
            parts = clean_name.split('_', 2)
            if len(parts) >= 3:
                return parts[2]
            elif len(parts) == 2:
                return parts[1]
    return clean_name

@app.route('/downloadFile/<int:service_id>', methods=['GET'])
def downloadFile(service_id):
    try:
        # Default to main data file
        file_type = request.args.get('type', 'data')
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "SELECT file_path, excel_file_path, data_dictionary_path, data_sampling_path FROM service WHERE service_id = %s"
        cursor.execute(sql, (service_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            file_path_val, excel_path_val, dict_path_val, samp_path_val = result
            file_name = None
            if file_type == 'dictionary':
                file_name = dict_path_val or file_path_val or excel_path_val
            elif file_type == 'sampling':
                file_name = samp_path_val
            elif file_type == 'excel':
                file_name = excel_path_val or file_path_val or dict_path_val
            else:
                file_name = file_path_val or excel_path_val or dict_path_val

            if file_name and os.path.exists(os.path.join(UPLOAD_FOLDER, file_name)):
                orig_name = get_original_filename(file_name, service_id)
                try:
                    return send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True, download_name=orig_name)
                except TypeError:
                    return send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True, attachment_filename=orig_name)
            elif file_name:
                return jsonify({"status": "File not found on server"}), 404
            else:
                return jsonify({"status": "No file associated with this dataset"}), 404
        else:
            return jsonify({"status": "Dataset not found"}), 404
            
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)}), 500


@app.route('/previewDatasetFile/<int:service_id>', methods=['GET'])
def previewDatasetFile(service_id):
    try:
        file_type = request.args.get('type', 'data').lower()
        
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT file_path, excel_file_path, data_dictionary_path, data_sampling_path, api_response_fields FROM service WHERE service_id = %s"
        cursor.execute(sql, (service_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            return jsonify({"status": "error", "message": "Dataset not found"}), 404
            
        file_path_val, excel_path_val, dict_path_val, samp_path_val, resp_fields = result
        file_name = None
        if file_type in ['dictionary', 'dict']:
            file_name = dict_path_val or file_path_val or excel_path_val
        elif file_type == 'sampling':
            file_name = samp_path_val
        elif file_type in ['excel', 'xls', 'xlsx']:
            file_name = excel_path_val or file_path_val or dict_path_val
        else: # 'data' or 'csv'
            file_name = file_path_val or excel_path_val or dict_path_val
            
        if not file_name or not os.path.exists(os.path.join(UPLOAD_FOLDER, file_name)):
            cols = []
            if resp_fields:
                try:
                    cols = json.loads(resp_fields) if isinstance(resp_fields, str) else resp_fields
                except Exception:
                    cols = []
            return jsonify({
                "status": "success",
                "filename": get_original_filename(file_name, service_id) if file_name else '',
                "columns": cols if cols else ["ไม่มีไฟล์ข้อมูล"],
                "rows": [],
                "total_rows": 0
            })
            
        full_path = os.path.join(UPLOAD_FOLDER, file_name)
        ext = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
        
        import pandas as pd
        df = None
        if ext == 'csv':
            try:
                df = pd.read_csv(full_path, nrows=10, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(full_path, nrows=10, encoding='cp874')
            except Exception:
                df = pd.read_csv(full_path, nrows=10, encoding='latin1')
        elif ext in ['xls', 'xlsx']:
            df = pd.read_excel(full_path, nrows=10)
        elif ext == 'json':
            df = pd.read_json(full_path)
            df = df.head(10)
            
        if df is not None:
            df = df.fillna('')
            columns = [str(c).strip() for c in df.columns if str(c).strip() and not str(c).startswith('Unnamed:')]
            if not columns:
                columns = [str(c) for c in df.columns]
            rows = df[columns].values.tolist()
            clean_rows = []
            for row in rows:
                clean_rows.append([str(val) if val is not None else '' for val in row])
                
            return jsonify({
                "status": "success",
                "filename": get_original_filename(file_name, service_id),
                "columns": columns,
                "rows": clean_rows,
                "total_rows": len(clean_rows)
            })
        else:
            return jsonify({
                "status": "success",
                "filename": get_original_filename(file_name, service_id),
                "columns": ["ไฟล์ข้อมูล"],
                "rows": [[get_original_filename(file_name, service_id)]],
                "total_rows": 1
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/downloadRequestMou/<int:request_id>', methods=['GET'])
def downloadRequestMou(request_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT mou_file_path, mou_filename FROM dataset_permission_requests WHERE request_id = %s"
        cursor.execute(sql, (request_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0]:
            file_name = result[0]
            if os.path.exists(os.path.join(UPLOAD_FOLDER, file_name)):
                # If attachment filename is provided, pass download_name / attachment_filename
                try:
                    return send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True, download_name=result[1] or file_name)
                except TypeError:
                    return send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True, attachment_filename=result[1] or file_name)
            else:
                return jsonify({"status": "File not found on server"}), 404
        else:
            return jsonify({"status": "No attached file found for this request"}), 404
            
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)}), 500

