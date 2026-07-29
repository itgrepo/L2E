from ServiceConfig import app, mysql, toJson, platform_decode, safe_json_loads, checkUserIsAdmin
from flask import request, jsonify
import json

@app.route('/getOrganizations', methods=['POST'])
def getOrganizations():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "SELECT org_id, org_name, org_description, create_at FROM organization ORDER BY create_at DESC"
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
        # Convert datetime to string
        for row in result:
            if row.get('create_at'):
                row['create_at'] = str(row['create_at'])

        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/addOrganization', methods=['POST'])
def addOrganization():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        org_name = dataInput.get('org_name')
        org_description = dataInput.get('org_description', '')

        if not org_name:
            return jsonify({"status": "Organization name is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "INSERT INTO organization (org_name, org_description) VALUES (%s, %s)"
        cursor.execute(sql, (org_name, org_description))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Organization created'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/updateOrganization', methods=['POST'])
def updateOrganization():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        org_id = dataInput.get('org_id')
        org_name = dataInput.get('org_name')
        org_description = dataInput.get('org_description')

        if not org_id or not org_name:
            return jsonify({"status": "Organization ID and name are required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "UPDATE organization SET org_name = %s, org_description = %s WHERE org_id = %s"
        cursor.execute(sql, (org_name, org_description, org_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Organization updated'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/deleteOrganization', methods=['POST'])
def deleteOrganization():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        org_id = dataInput.get('org_id')

        if not org_id:
            return jsonify({"status": "Organization ID is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "DELETE FROM organization WHERE org_id = %s"
        cursor.execute(sql, (org_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Organization deleted'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})
