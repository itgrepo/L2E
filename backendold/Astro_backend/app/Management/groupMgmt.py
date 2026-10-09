from ServiceConfig import *
import pandas as pd
import numpy as np
import math

@app.route('/mgmt/getMenu', methods=['POST'])
def getMenu():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user'))
        user_data = safe_json_loads(decoded_user)
        
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()

        # Canonical menus list
        canonical_menus = [
            {'menu_name_id': 1, 'menu_name': 'Dashboard'},
            {'menu_name_id': 2, 'menu_name': 'Data Catalog'},
            {'menu_name_id': 3, 'menu_name': 'API Management'},
            {'menu_name_id': 4, 'menu_name': 'API Monitor'},
            {'menu_name_id': 5, 'menu_name': 'Dataset Approval'},
            {'menu_name_id': 6, 'menu_name': 'Analytics'},
            {'menu_name_id': 8, 'menu_name': 'Group User Management'},
            {'menu_name_id': 9, 'menu_name': 'Dataset Management'},
            {'menu_name_id': 10, 'menu_name': 'Group Dataset Management'},
            {'menu_name_id': 16, 'menu_name': 'User Management'},
            {'menu_name_id': 7, 'menu_name': 'Permission Management'},
            {'menu_name_id': 17, 'menu_name': 'Settings'}
        ]

        cursor.execute("SELECT previlage_id, previlage_name FROM codename_previlage")
        roles = toJson(cursor.fetchall(), [col[0] for col in cursor.description])

        cursor.execute("""
            SELECT mp.previlage_id, mn.menu_name, mp.value 
            FROM menu_permission mp 
            JOIN menu_name mn ON mp.menu_name_id = mn.menu_name_id
        """)
        existing_perms = toJson(cursor.fetchall(), [col[0] for col in cursor.description])
        
        # Build map: (previlage_id, lower_menu_name) -> value
        perm_map = {}
        for ep in existing_perms:
            m_name = ep['menu_name'].lower().strip()
            if m_name == 'catalog':
                m_name = 'data catalog'
            p_id = ep['previlage_id']
            # If any duplicate record for this role is 'Yes', treat as 'Yes'
            if (p_id, m_name) not in perm_map or ep['value'] == 'Yes':
                perm_map[(p_id, m_name)] = ep['value']

        data_previlage = []
        for role in roles:
            for menu in canonical_menus:
                m_name = menu['menu_name'].lower().strip()
                val = perm_map.get((role['previlage_id'], m_name), 'No')
                data_previlage.append({
                    "menu_name": menu['menu_name'],
                    "menu_name_id": menu['menu_name_id'],
                    "previlage_id": role['previlage_id'],
                    "key": role['previlage_name'],
                    "value": val
                })

        cursor.close()
        conn.close()
        return json.dumps({'data': data_previlage})
    except Exception as e:
        print(f"Error in getMenu: {e}")
        return jsonify({"status": "Error: " + str(e)})

@app.route('/mgmt/getRoles', methods=['POST'])
def getRoles():
    try:
        dataInput = request.json
        decoded_user = platform_decode(dataInput.get('user', ''))
        user_data = safe_json_loads(decoded_user)
        
        if user_data and checkUserIsAdmin(user_data) :
            previlage_id = int(user_data.get('previlage_id', 0))
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "SELECT * FROM codename_previlage ORDER BY previlage_id ASC"
            cursor.execute(sql)
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = toJson(data, columns)
            cursor.close()
            conn.close()
            return jsonify(result)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})

@app.route('/mgmt/getPermission', methods=['POST'])
def getPermission():
    conn = mysql.connect()
    cursor = conn.cursor()
    header = [{
            "text": 'Menu Name',
            "align": 'center',
            "sortable": False
            }]
    sql = "SELECT * FROM `codename_previlage`"
    cursor.execute(sql,)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    for i in range(len(result)):
        data = {
                "text": result[i]['previlage_name'],
                "align": 'left',
                "sortable": False
                }
        header.append(data)

    return json.dumps({'result': header})

@app.route('/mgmt/savePermission', methods=['POST'])
def savePermission():
    try: 
        dataInput = request.json
        data = dataInput.get('data', {})
        previlage_id = data.get('previlage_id')
        menu_name_id = data.get('menu_name_id')
        menu_name = data.get('menu_name', '')
        value = data.get('value', 'No')
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if user_data and checkUserIsAdmin(user_data):
            conn = mysql.connect()
            cursor = conn.cursor()
            
            # Find all menu_name_ids with matching menu_name (case-insensitive and aliases)
            names_to_match = [menu_name.lower().strip()]
            if menu_name.lower().strip() in ['catalog', 'data catalog']:
                names_to_match = ['catalog', 'data catalog']
            elif menu_name.lower().strip() == 'settings':
                names_to_match = ['settings', 'organization management', 'category management']
                
            format_strings = ','.join(['%s'] * len(names_to_match))
            cursor.execute(f"SELECT menu_name_id FROM menu_name WHERE LOWER(TRIM(menu_name)) IN ({format_strings})", tuple(names_to_match))
            matching_rows = cursor.fetchall()
            matching_ids = [row[0] for row in matching_rows]
            if menu_name_id and menu_name_id not in matching_ids:
                matching_ids.append(menu_name_id)
                
            for m_id in matching_ids:
                cursor.execute("SELECT menu_permission_id FROM menu_permission WHERE previlage_id = %s AND menu_name_id = %s", (previlage_id, m_id))
                exists = cursor.fetchone()
                if exists:
                    cursor.execute("UPDATE menu_permission SET value = %s WHERE previlage_id = %s AND menu_name_id = %s", (value, previlage_id, m_id))
                else:
                    cursor.execute("INSERT INTO menu_permission (previlage_id, menu_name_id, value, create_at) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)", (previlage_id, m_id, value))
            
            conn.commit()
            cursor.close()
            conn.close()
            return 'success'
        else :
            return 'Permission denied'
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})