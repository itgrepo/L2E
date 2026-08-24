from flask import request, jsonify
from ServiceConfig import *
import json
import base64

def platform_decode(data):
    if not data:
        return ""
    try:
        # Standard decode pattern used in this project
        decoded = base64.b64decode(data[:-5][::-1]).decode('utf-8')
        return decoded
    except Exception as e:
        print(f"Decode error: {e}")
        return ""

def safe_json_loads(data):
    if not data:
        return {}
    try:
        return json.loads(data)
    except:
        return {}

@app.route('/getDatasetAccessGroups', methods=['POST'])
def getDatasetAccessGroups():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        service_id = dataInput.get('service_id')

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})
            
        if not service_id:
             return jsonify({"status": "Service ID is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # 1. Get currently assigned groups
        sql_assigned = """
            SELECT gu.group_id, gu.group_name
            FROM service_group_access sga
            JOIN group_user gu ON sga.group_id = gu.group_id
            WHERE sga.service_id = %s
        """
        cursor.execute(sql_assigned, (service_id,))
        assigned_data = cursor.fetchall()
        assigned_cols = [col[0] for col in cursor.description]
        assigned_groups = toJson(assigned_data, assigned_cols)
        
        # 2. Get available groups (not assigned to this service)
        sql_available = """
            SELECT group_id, group_name
            FROM group_user
            WHERE group_id NOT IN (
                SELECT group_id FROM service_group_access WHERE service_id = %s
            )
        """
        cursor.execute(sql_available, (service_id,))
        available_data = cursor.fetchall()
        available_cols = [col[0] for col in cursor.description]
        available_groups = toJson(available_data, available_cols)
        
        conn.close()
        return jsonify({
            'status': 'success', 
            'assigned': assigned_groups, 
            'available': available_groups
        })
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/updateDatasetAccessGroups', methods=['POST'])
def updateDatasetAccessGroups():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        service_id = dataInput.get('service_id')
        group_ids = dataInput.get('group_ids', []) # List of group IDs

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Clear existing mappings
        sql_clear = "DELETE FROM service_group_access WHERE service_id = %s"
        cursor.execute(sql_clear, (service_id,))
        
        # Insert new mappings
        if group_ids:
            sql_insert = "INSERT INTO service_group_access (service_id, group_id) VALUES (%s, %s)"
            for gid in group_ids:
                cursor.execute(sql_insert, (service_id, gid))
        
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Dataset group access updated'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/getDatasetAccessUsers', methods=['POST'])
def getDatasetAccessUsers():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        service_id = dataInput.get('service_id')

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})
            
        if not service_id:
             return jsonify({"status": "Service ID is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # 1. Get currently assigned users
        sql_assigned = """
            SELECT u.user_id, u.username, u.firstname, u.lastname, u.email
            FROM service_user_access sua
            JOIN user u ON sua.user_id = u.user_id
            WHERE sua.service_id = %s AND u.status_id != '7'
        """
        cursor.execute(sql_assigned, (service_id,))
        assigned_data = cursor.fetchall()
        assigned_cols = [col[0] for col in cursor.description]
        assigned_users = toJson(assigned_data, assigned_cols)
        
        # 2. Get available users (not assigned to this service)
        # Limiting to 500 for performance
        sql_available = """
            SELECT user_id, username, firstname, lastname, email
            FROM user
            WHERE status_id != '7' AND user_id NOT IN (
                SELECT user_id FROM service_user_access WHERE service_id = %s
            )
            LIMIT 500
        """
        cursor.execute(sql_available, (service_id,))
        available_data = cursor.fetchall()
        available_cols = [col[0] for col in cursor.description]
        available_users = toJson(available_data, available_cols)
        
        conn.close()
        return jsonify({
            'status': 'success', 
            'assigned': assigned_users, 
            'available': available_users
        })
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/updateDatasetAccessUsers', methods=['POST'])
def updateDatasetAccessUsers():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        service_id = dataInput.get('service_id')
        user_ids = dataInput.get('user_ids', []) # List of user IDs

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Clear existing mappings
        sql_clear = "DELETE FROM service_user_access WHERE service_id = %s"
        cursor.execute(sql_clear, (service_id,))
        
        # Insert new mappings
        if user_ids:
            sql_insert = "INSERT INTO service_user_access (service_id, user_id) VALUES (%s, %s)"
            for uid in user_ids:
                cursor.execute(sql_insert, (service_id, uid))
        
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Dataset user access updated'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/getGroupDatasetAccess', methods=['POST'])
def getGroupDatasetAccess():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        group_id = dataInput.get('group_id')

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})
            
        if not group_id:
             return jsonify({"status": "Group ID is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # 1. Get datasets currently assigned to this group
        sql_assigned = """
            SELECT s.service_id, s.service_name, s.organization
            FROM service_group_access sga
            JOIN service s ON sga.service_id = s.service_id
            WHERE sga.group_id = %s AND s.status != 'Deleted'
        """
        cursor.execute(sql_assigned, (group_id,))
        assigned_data = cursor.fetchall()
        assigned_cols = [col[0] for col in cursor.description]
        assigned_datasets = toJson(assigned_data, assigned_cols)
        
        # 2. Get available datasets (not assigned to this group)
        sql_available = """
            SELECT service_id, service_name, organization
            FROM service
            WHERE status != 'Deleted' AND service_id NOT IN (
                SELECT service_id FROM service_group_access WHERE group_id = %s
            )
        """
        cursor.execute(sql_available, (group_id,))
        available_data = cursor.fetchall()
        available_cols = [col[0] for col in cursor.description]
        available_datasets = toJson(available_data, available_cols)
        
        conn.close()
        return jsonify({
            'status': 'success', 
            'assigned': assigned_datasets, 
            'available': available_datasets
        })
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/updateGroupDatasetAccess', methods=['POST'])
def updateGroupDatasetAccess():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        group_id = dataInput.get('group_id')
        service_ids = dataInput.get('service_ids', []) # List of service IDs

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Clear existing mappings for this GROUP
        sql_clear = "DELETE FROM service_group_access WHERE group_id = %s"
        cursor.execute(sql_clear, (group_id,))
        
        # Insert new mappings
        if service_ids:
            sql_insert = "INSERT INTO service_group_access (group_id, service_id) VALUES (%s, %s)"
            for sid in service_ids:
                cursor.execute(sql_insert, (group_id, sid))
        
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Group dataset access updated'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})
