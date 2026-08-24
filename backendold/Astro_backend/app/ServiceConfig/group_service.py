from flask import request, jsonify
from ServiceConfig import *
import json
from ServiceConfig.notification_util import notify_user
import os
import sys

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

@app.route('/getGroups', methods=['POST'])
def getGroups():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Select groups with member count and dataset count
        sql = """
            SELECT gu.group_id, gu.group_name, gu.create_at, 
                   COUNT(DISTINCT gud.user_id) as member_count,
                   COUNT(DISTINCT sga.service_id) as dataset_count
            FROM group_user gu
            LEFT JOIN group_user_detail gud ON gu.group_id = gud.group_id
            LEFT JOIN service_group_access sga ON gu.group_id = sga.group_id
            GROUP BY gu.group_id
            ORDER BY gu.create_at DESC
        """
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        results = toJson(data, columns)
        
        conn.close()
        return jsonify({'status': 'success', 'data': results})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/addGroup', methods=['POST'])
def addGroup():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        group_name = dataInput.get('group_name')

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})
        
        if not group_name:
            return jsonify({"status": "Group name is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check duplicate
        sql_check = "SELECT group_id FROM group_user WHERE group_name = %s"
        cursor.execute(sql_check, (group_name,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"status": "Group name already exists"})

        sql_insert = "INSERT INTO group_user (group_name) VALUES (%s)"
        cursor.execute(sql_insert, (group_name,))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Group created successfully'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/deleteGroup', methods=['POST'])
def deleteGroup():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        group_id = dataInput.get('group_id')

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Delete members first
        sql_del_members = "DELETE FROM group_user_detail WHERE group_id = %s"
        cursor.execute(sql_del_members, (group_id,))
        
        # Delete group
        sql_del_group = "DELETE FROM group_user WHERE group_id = %s"
        cursor.execute(sql_del_group, (group_id,))
        
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})

@app.route('/getGroupMembers', methods=['POST'])
def getGroupMembers():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        group_id = dataInput.get('group_id')

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Get assigned users
        sql_assigned = """
            SELECT u.user_id, u.username, u.firstname, u.lastname, u.email
            FROM group_user_detail gud
            JOIN user u ON gud.user_id = u.user_id
            WHERE gud.group_id = %s AND u.status_id != '7'
        """
        cursor.execute(sql_assigned, (group_id,))
        assigned_data = cursor.fetchall()
        assigned_cols = [col[0] for col in cursor.description]
        assigned_users = toJson(assigned_data, assigned_cols)
        
        # Get available users (not in this group)
        sql_available = """
            SELECT user_id, username, firstname, lastname, email
            FROM user
            WHERE status_id != '7' AND user_id NOT IN (
                SELECT user_id FROM group_user_detail WHERE group_id = %s
            )
            LIMIT 500
        """
        cursor.execute(sql_available, (group_id,))
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

@app.route('/updateGroupMembers', methods=['POST'])
def updateGroupMembers():
    try:
        from .email_service import notify_added_to_group
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        group_id = dataInput.get('group_id')
        user_ids = dataInput.get('user_ids', []) # List of user IDs that SHOULD be in the group

        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # 1. Fetch group name
        cursor.execute("SELECT group_name FROM group_user WHERE group_id = %s", (group_id,))
        group_res = cursor.fetchone()
        group_name = group_res[0] if group_res else f"Group {group_id}"
        
        # 2. Fetch existing members to find who is newly added
        cursor.execute("SELECT user_id FROM group_user_detail WHERE group_id = %s", (group_id,))
        existing_users = {row[0] for row in cursor.fetchall()}
        
        new_users = set(user_ids) - existing_users
        
        # Simple approach: Clear and refill
        sql_clear = "DELETE FROM group_user_detail WHERE group_id = %s"
        cursor.execute(sql_clear, (group_id,))
        
        if user_ids:
            sql_insert = "INSERT INTO group_user_detail (group_id, user_id) VALUES (%s, %s)"
            for uid in user_ids:
                cursor.execute(sql_insert, (group_id, uid))
                
        # 3. If there are new users, fetch their emails and notify
        if new_users:
            format_strings = ','.join(['%s'] * len(new_users))
            cursor.execute(f"SELECT email FROM user WHERE user_id IN ({format_strings}) AND status_account = 'active'", tuple(new_users))
            emails = [row[0] for row in cursor.fetchall() if row[0]]
            if emails:
                notify_added_to_group(group_name, emails)
        
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})
