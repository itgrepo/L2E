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
