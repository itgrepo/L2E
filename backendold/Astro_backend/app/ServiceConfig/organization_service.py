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
        
        sql = "SELECT org_id, org_name, org_description, contact_name, contact_email, contact_phone, is_active, create_at FROM organization ORDER BY create_at DESC"
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
        # Get roles mapping
        cursor.execute("SELECT organization_id, role_id FROM organization_role_mapping")
        role_mappings = cursor.fetchall()
        org_roles = {}
        for row in role_mappings:
            org_id = row[0]
            if org_id not in org_roles:
                org_roles[org_id] = []
            org_roles[org_id].append(row[1])

        # Convert datetime to string and attach roles
        for row in result:
            if row.get('create_at'):
                row['create_at'] = str(row['create_at'])
            row['role_ids'] = org_roles.get(row['org_id'], [])
            row['is_active'] = bool(row.get('is_active', True))

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
        contact_name = dataInput.get('contact_name', '')
        contact_email = dataInput.get('contact_email', '')
        contact_phone = dataInput.get('contact_phone', '')
        is_active = 1 if dataInput.get('is_active', True) else 0
        role_ids = dataInput.get('role_ids', [])

        if not org_name:
            return jsonify({"status": "Organization name is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        try:
            # Deduplicate role_ids
            unique_roles = list(set(role_ids))
            
            # Validate role_ids
            if unique_roles:
                format_strings = ','.join(['%s'] * len(unique_roles))
                cursor.execute(f"SELECT id FROM organization_role_master WHERE id IN ({format_strings})", tuple(unique_roles))
                valid_roles = [row[0] for row in cursor.fetchall()]
                if len(valid_roles) != len(unique_roles):
                    raise ValueError("One or more role_ids are invalid")

            sql = "INSERT INTO organization (org_name, org_description, contact_name, contact_email, contact_phone, is_active) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (org_name, org_description, contact_name, contact_email, contact_phone, is_active))
            org_id = cursor.lastrowid
            
            for role_id in unique_roles:
                cursor.execute("INSERT INTO organization_role_mapping (organization_id, role_id) VALUES (%s, %s)", (org_id, role_id))
                
            conn.commit()
        except Exception as inner_e:
            conn.rollback()
            raise inner_e
        finally:
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
        contact_name = dataInput.get('contact_name', '')
        contact_email = dataInput.get('contact_email', '')
        contact_phone = dataInput.get('contact_phone', '')
        is_active = 1 if dataInput.get('is_active', True) else 0
        role_ids = dataInput.get('role_ids', [])

        if not org_id or not org_name:
            return jsonify({"status": "Organization ID and name are required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        try:
            # Deduplicate role_ids
            unique_roles = list(set(role_ids))
            
            # Validate role_ids
            if unique_roles:
                format_strings = ','.join(['%s'] * len(unique_roles))
                cursor.execute(f"SELECT id FROM organization_role_master WHERE id IN ({format_strings})", tuple(unique_roles))
                valid_roles = [row[0] for row in cursor.fetchall()]
                if len(valid_roles) != len(unique_roles):
                    raise ValueError("One or more role_ids are invalid")

            sql = "UPDATE organization SET org_name = %s, org_description = %s, contact_name = %s, contact_email = %s, contact_phone = %s, is_active = %s WHERE org_id = %s"
            cursor.execute(sql, (org_name, org_description, contact_name, contact_email, contact_phone, is_active, org_id))
            
            cursor.execute("DELETE FROM organization_role_mapping WHERE organization_id = %s", (org_id,))
            for role_id in unique_roles:
                cursor.execute("INSERT INTO organization_role_mapping (organization_id, role_id) VALUES (%s, %s)", (org_id, role_id))
                
            conn.commit()
        except Exception as inner_e:
            conn.rollback()
            raise inner_e
        finally:
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
        
        try:
            # Check if organization is used by any dataset
            cursor.execute("SELECT 1 FROM service WHERE organization = (SELECT org_name FROM organization WHERE org_id = %s) LIMIT 1", (org_id,))
            if cursor.fetchone():
                raise ValueError("Cannot delete Organization because it is being used by one or more datasets")
                
            sql = "DELETE FROM organization WHERE org_id = %s"
            cursor.execute(sql, (org_id,))
            
            conn.commit()
        except Exception as inner_e:
            conn.rollback()
            raise inner_e
        finally:
            cursor.close()
            conn.close()
        return jsonify({'status': 'success', 'message': 'Organization deleted'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})
