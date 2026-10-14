from ServiceConfig import app, mysql, platform_decode, safe_json_loads, checkUserIsAdmin
from flask import request, jsonify

@app.route('/getDatasetGroups', methods=['POST'])
def getDatasetGroups():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"}), 403

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "SELECT id, code, name_th, name_en, prefix FROM l2e_dataset_group WHERE active = 1 ORDER BY display_order ASC"
        cursor.execute(sql)
        data = cursor.fetchall()

        result = []
        for row in data:
            result.append({
                "id": row[0],
                "code": row[1],
                "name_th": row[2],
                "name_en": row[3],
                "prefix": row[4]
            })

        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"}), 500

@app.route('/addDatasetGroup', methods=['POST'])
def addDatasetGroup():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"}), 403

        name_th = dataInput.get('name_th', '').strip()
        name_en = dataInput.get('name_en', '').strip() or name_th
        prefix = dataInput.get('prefix', '').strip().upper()
        code = dataInput.get('code', '').strip().lower()

        if not name_th:
            return jsonify({"status": "ชื่อกลุ่มข้อมูลย่อยจำเป็นต้องระบุ"}), 400

        if not prefix:
            return jsonify({"status": "รหัส Prefix จำเป็นต้องระบุ"}), 400

        if not prefix.endswith('-'):
            prefix += '-'

        if not code:
            import re
            code = re.sub(r'[^a-zA-Z0-9_]', '_', name_en.lower())
            if not code or code == '_':
                code = prefix.replace('-', '').lower()

        conn = mysql.connect()
        cursor = conn.cursor()

        # Check existing prefix or code
        cursor.execute("SELECT 1 FROM l2e_dataset_group WHERE prefix = %s OR code = %s", (prefix, code))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"status": "รหัส Prefix หรือ Code นี้มีอยู่แล้วในระบบ"}), 400

        cursor.execute("""
            INSERT INTO l2e_dataset_group (code, name_th, name_en, prefix, active, display_order)
            VALUES (%s, %s, %s, %s, 1, (SELECT COALESCE(MAX(d.display_order), 0) + 1 FROM l2e_dataset_group d))
        """, (code, name_th, name_en, prefix))
        new_id = cursor.lastrowid
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "data": {
                "id": new_id,
                "code": code,
                "name_th": name_th,
                "name_en": name_en,
                "prefix": prefix
            }
        })
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"}), 500

@app.route('/getSourceSystems', methods=['POST'])
def getSourceSystems():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"}), 403

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "SELECT id, code, name_th, name_en FROM source_system WHERE active = 1"
        cursor.execute(sql)
        data = cursor.fetchall()

        result = []
        for row in data:
            result.append({
                "id": row[0],
                "code": row[1],
                "name_th": row[2],
                "name_en": row[3]
            })

        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"}), 500

@app.route('/getOrganizationRoles', methods=['POST'])
def getOrganizationRoles():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"}), 403

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "SELECT id, code, name_th, name_en FROM organization_role_master WHERE active = 1"
        cursor.execute(sql)
        data = cursor.fetchall()

        result = []
        for row in data:
            result.append({
                "id": row[0],
                "code": row[1],
                "name_th": row[2],
                "name_en": row[3]
            })

        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": f"Error: {str(e)}"}), 500
