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

def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'none'; style-src 'unsafe-inline'"
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.route('/downloadFile/<int:service_id>', methods=['GET'])
def downloadFile(service_id):
    try:
        file_type = request.args.get('type', 'data')
        user_param = request.args.get('user') or request.headers.get('x-user')
        
        # Parse user info early for permissions and audit logging
        user_data = {}
        user_id = 0
        u_email = None
        if user_param:
            try:
                from ServiceConfig import platform_decode, safe_json_loads
                user_data = safe_json_loads(platform_decode(user_param)) if user_param else {}
                user_id = user_data.get('user_id') or 0
                u_email = user_data.get('email')
            except Exception:
                pass

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "SELECT file_path, excel_file_path, data_dictionary_path, data_sampling_path, access_type, organization, created_by, contact_email, service_name, dataset_id FROM service WHERE service_id = %s"
        cursor.execute(sql, (service_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({"status": "Dataset not found"}), 404
            
        file_path_val, excel_path_val, dict_path_val, samp_path_val, access_type, org_name, created_by_val, contact_email_val, service_name_val, dataset_id_val = result
        access_type_lower = (access_type or 'public').lower()
        
        # Private (PII) datasets are strictly owner-only
        if access_type_lower == 'pii':
            is_owner = False
            if created_by_val is not None and user_id is not None and str(created_by_val) == str(user_id):
                is_owner = True
            elif not created_by_val and contact_email_val and u_email and contact_email_val.strip().lower() == u_email.strip().lower():
                is_owner = True
            if not is_owner:
                cursor.close()
                conn.close()
                return jsonify({"status": "error", "message": "Permission denied: only the dataset owner can access this private dataset"}), 403
        elif file_type != 'dictionary' and access_type_lower in ['internal', 'restricted']:
            previlage_id = str(user_data.get('previlage_id', '2'))
            user_org_id = user_data.get('org_id')
            user_org_name = ''
            if user_org_id:
                cursor.execute("SELECT org_name FROM organization WHERE org_id = %s", (user_org_id,))
                orow = cursor.fetchone()
                if orow:
                    user_org_name = orow[0]
                    
            has_perm = False
            if previlage_id == '4':
                has_perm = True
            elif access_type_lower == 'internal' and previlage_id in ['3', '5'] and user_org_name and user_org_name == org_name:
                has_perm = True
            elif previlage_id == '3' and user_org_name and user_org_name == org_name:
                has_perm = True
            elif user_id:
                cursor.execute("SELECT 1 FROM service_user_access WHERE service_id = %s AND user_id = %s", (service_id, user_id))
                if cursor.fetchone():
                    has_perm = True
                elif access_type_lower == 'internal':
                    cursor.execute("""
                        SELECT 1 FROM group_user_detail gud
                        WHERE gud.user_id = %s AND (
                            EXISTS (SELECT 1 FROM service WHERE service_id = %s AND l2e_group_id = gud.group_id)
                            OR EXISTS (SELECT 1 FROM service_group_access sga WHERE sga.service_id = %s AND sga.group_id = gud.group_id)
                        )
                    """, (user_id, service_id, service_id))
                    if cursor.fetchone():
                        has_perm = True
                        
            if not has_perm:
                cursor.close()
                conn.close()
                return jsonify({"status": "error", "message": "Permission denied: access required for this internal/restricted dataset"}), 403

        cursor.close()
        conn.close()
        
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
            
            # Record download log into MySQL log table
            try:
                ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
                if ip_addr and ',' in ip_addr:
                    ip_addr = ip_addr.split(',')[0].strip()
                user_agent = request.headers.get('User-Agent', 'Unknown')
                
                log_conn = mysql.connect()
                log_cursor = log_conn.cursor()
                ds_title = service_name_val or dataset_id_val or f"ID {service_id}"
                log_sql = """INSERT INTO log (user_id, ip, path, log_detail, type, device) 
                             VALUES (%s, %s, %s, %s, 'Download', %s)"""
                log_cursor.execute(log_sql, (
                    user_id or 0, 
                    ip_addr, 
                    f"/downloadFile/{service_id}?type={file_type}", 
                    f"Downloaded Dataset: {ds_title}", 
                    user_agent
                ))
                log_conn.commit()
                log_cursor.close()
                log_conn.close()
            except Exception as log_ex:
                print("Failed to record download log in file_download_service:", log_ex)

            # Notify Dataset Creator & Super Admin about file download
            try:
                from ServiceConfig.notification_util import notify_dataset_access
                notify_dataset_access(service_id, 'download', actor_user_id=user_id, detail=file_type)
            except Exception as notif_ex:
                print("Failed to notify download access:", notif_ex)

            try:
                resp = send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True, download_name=orig_name)
            except TypeError:
                resp = send_from_directory(UPLOAD_FOLDER, file_name, as_attachment=True, attachment_filename=orig_name)
            return add_security_headers(resp)
        elif file_name:
            return jsonify({"status": "File not found on server"}), 404
        else:
            return jsonify({"status": "No file associated with this dataset"}), 404
            
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)}), 500


@app.route('/previewDatasetFile/<int:service_id>', methods=['GET'])
def previewDatasetFile(service_id):
    try:
        file_type = request.args.get('type', 'data').lower()
        
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT file_path, excel_file_path, data_dictionary_path, data_sampling_path, api_response_fields, access_type, created_by, contact_email FROM service WHERE service_id = %s"
        cursor.execute(sql, (service_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            return jsonify({"status": "error", "message": "Dataset not found"}), 404
            
        file_path_val, excel_path_val, dict_path_val, samp_path_val, resp_fields, access_type_val, created_by_val, contact_email_val = result
        access_type_lower = (access_type_val or 'public').lower()
        if access_type_lower == 'pii':
            user_param = request.args.get('user') or request.headers.get('x-user')
            from ServiceConfig import platform_decode, safe_json_loads
            user_data = safe_json_loads(platform_decode(user_param)) if user_param else {}
            u_id = user_data.get('user_id')
            u_email = user_data.get('email')
            is_owner = False
            if created_by_val is not None and u_id is not None and str(created_by_val) == str(u_id):
                is_owner = True
            elif not created_by_val and contact_email_val and u_email and contact_email_val.strip().lower() == u_email.strip().lower():
                is_owner = True
            if not is_owner:
                return jsonify({"status": "error", "message": "Permission denied: only the dataset owner can access this private dataset"}), 403
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
            display_name = result[1] or file_name
            file_path = os.path.join(UPLOAD_FOLDER, file_name)
            if os.path.exists(file_path):
                force_download = request.args.get('download', '0') == '1'
                
                mimetype = None
                display_lower = display_name.lower()
                file_lower = file_name.lower()
                if display_lower.endswith('.pdf') or file_lower.endswith('.pdf'):
                    mimetype = 'application/pdf'
                elif display_lower.endswith(('.jpg', '.jpeg')) or file_lower.endswith(('.jpg', '.jpeg')):
                    mimetype = 'image/jpeg'
                elif display_lower.endswith('.png') or file_lower.endswith('.png'):
                    mimetype = 'image/png'
                elif display_lower.endswith('.webp') or file_lower.endswith('.webp'):
                    mimetype = 'image/webp'
                else:
                    return jsonify({"status": "error", "message": "File format not supported or restricted"}), 403
                    
                try:
                    resp = send_from_directory(
                        UPLOAD_FOLDER, 
                        file_name, 
                        as_attachment=force_download, 
                        download_name=display_name,
                        mimetype=mimetype
                    )
                except TypeError:
                    resp = send_from_directory(
                        UPLOAD_FOLDER, 
                        file_name, 
                        as_attachment=force_download, 
                        attachment_filename=display_name,
                        mimetype=mimetype
                    )
                return add_security_headers(resp)
            else:
                return jsonify({"status": "File not found on server"}), 404
        else:
            return jsonify({"status": "No attached file found for this request"}), 404
            
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)}), 500

