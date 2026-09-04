# coding=utf-8
import codecs
import re

with codecs.open('ServiceConfig/bigdataservice.py', 'r', 'utf-8') as f:
    content = f.read()

old_func = """def request_dataset_permission():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        user_id = user_data.get('user_id')
        
        user_str = dataInput.get('user')
        if user_str and not user_id:
            decoded_user = platform_decode(user_str)
            parsed_user = safe_json_loads(decoded_user)
            user_id = parsed_user.get('user_id')
            
        service_id = dataInput.get('service_id')
        fields = dataInput.get('fields', [])
        reason = dataInput.get('reason', '')
        
        if not user_id or not service_id:
            return jsonify({'status': 'error', 'message': 'Missing user or service ID'}), 400
            
        fields_json = json.dumps(fields)
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check if there is already a Pending request
        sql_check = "SELECT request_id FROM dataset_permission_requests WHERE user_id = %s AND service_id = %s AND status = 'Pending'"
        cursor.execute(sql_check, (user_id, service_id))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'คุณได้ส่งคำขอที่อยู่ระหว่างรอดำเนินการสำหรับชุดข้อมูลนี้แล้ว'}), 400
            
        # Insert
        sql_insert = "INSERT INTO dataset_permission_requests (user_id, service_id, fields_json, reason, status) VALUES (%s, %s, %s, %s, 'Pending')"
        cursor.execute(sql_insert, (user_id, service_id, fields_json, reason))"""

new_func = """def request_dataset_permission():
    try:
        import os, uuid
        from werkzeug.utils import secure_filename
        
        if request.is_json:
            dataInput = request.json
        else:
            dataInput = request.form
            
        user_data = getattr(request, 'current_user', {})
        user_id = user_data.get('user_id')
        
        user_str = dataInput.get('user')
        if user_str and not user_id:
            decoded_user = platform_decode(user_str)
            parsed_user = safe_json_loads(decoded_user)
            user_id = parsed_user.get('user_id')
            
        service_id = dataInput.get('service_id')
        
        fields_str = dataInput.get('fields', '[]')
        fields = fields_str if isinstance(fields_str, list) else safe_json_loads(fields_str)
        reason = dataInput.get('reason', '')
        
        # Handle file upload
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                unique_name = str(uuid.uuid4()) + "_" + filename
                save_path = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), unique_name)
                # Ensure dir exists
                os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
                file.save(save_path)
                file_path = f"/api/uploads/{unique_name}"
        
        if not user_id or not service_id:
            return jsonify({'status': 'error', 'message': 'Missing user or service ID'}), 400
            
        fields_json = json.dumps(fields)
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check if there is already a Pending request
        sql_check = "SELECT request_id FROM dataset_permission_requests WHERE user_id = %s AND service_id = %s AND status = 'Pending'"
        cursor.execute(sql_check, (user_id, service_id))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'คุณได้ส่งคำขอที่อยู่ระหว่างรอดำเนินการสำหรับชุดข้อมูลนี้แล้ว'}), 400
            
        # Insert
        sql_insert = "INSERT INTO dataset_permission_requests (user_id, service_id, fields_json, reason, status, request_file_path) VALUES (%s, %s, %s, %s, 'Pending', %s)"
        cursor.execute(sql_insert, (user_id, service_id, fields_json, reason, file_path))"""

if "def request_dataset_permission():" in content:
    # Safely replace
    content = content.replace(old_func, new_func)
    
with codecs.open('ServiceConfig/bigdataservice.py', 'w', 'utf-8') as f:
    f.write(content)
