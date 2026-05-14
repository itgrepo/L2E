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
        data_previlage = []
        # sql = "SELECT * FROM `menu_name`"
        ##-Filter some menu_name-##
        sql = "SELECT * FROM `menu_name` WHERE menu_name NOT IN ('User Management','Permission Management','Service Configuration')"
        cursor.execute(sql,)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)

        sql = "SELECT * FROM `codename_previlage`"
        cursor.execute(sql,)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_previlage = toJson(data, columns)

        sql = "SELECT * FROM menu_permission"
        cursor.execute(sql,)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_menu = toJson(data, columns)

        for i in range(len(result)):
            for j in range(len(result_previlage)):
                data = {
                        "menu_name": result[i]['menu_name'],
                        "menu_name_id": result[i]['menu_name_id'],
                        "previlage_id": result_previlage[j]["previlage_id"],
                        "key": result_previlage[j]["previlage_name"],
                        "value": "No"
                        }
                data_previlage.append(data)
        for k in range(len(result_menu)):
            for m in range(len(data_previlage)):
                if data_previlage[m]['previlage_id'] == result_menu[k]['previlage_id'] and data_previlage[m]['menu_name_id'] == result_menu[k]['menu_name_id']:
                    data = {
                            "menu_name": data_previlage[m]['menu_name'],
                            "menu_name_id": data_previlage[m]['menu_name_id'],
                            "previlage_id": data_previlage[m]['previlage_id'],
                            "key": data_previlage[m]['key'],
                            "value": result_menu[k]['value']
                            }
                    data_previlage[m] = data
        conn.commit()
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
            # In this DB: 1=RootAdmin, 2=Admin, 3=User
            if(previlage_id == 1):
                conn = mysql.connect()
                cursor = conn.cursor()
                sql = "SELECT * FROM codename_previlage"
                cursor.execute(sql,)
                data = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result = toJson(data, columns)
                conn.commit()
                cursor.close()
                return jsonify(result)
            else:
                conn = mysql.connect()
                cursor = conn.cursor()
                sql = "SELECT * FROM codename_previlage WHERE previlage_id != 1"
                cursor.execute(sql,)
                data = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result = toJson(data, columns)
                conn.commit()
                cursor.close()
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
    try : 
        dataInput = request.json
        previlage_name = dataInput['data']['key']
        previlage_id = dataInput['data']['previlage_id']
        menu_name_id = dataInput['data']['menu_name_id']
        menu_name = dataInput['data']['menu_name']
        value = dataInput['data']['value']
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if user_data and checkUserIsAdmin(user_data) :
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "SELECT * FROM menu_permission WHERE previlage_id = %s AND menu_name_id = %s"
            cursor.execute(sql, (previlage_id, menu_name_id))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = toJson(data, columns)
            # print(result)
            if len(result) > 0:
                sql = "UPDATE menu_permission SET value = %s WHERE previlage_id = %s AND menu_name_id = %s"
                cursor.execute(sql, (value, previlage_id, menu_name_id))
                logAction( user_id =user_data['user_id'] , path = "/mgmt/savePermission" , log = "Updatemenu_permission : value= "+str(value)+" ,previlage_id= "+str(previlage_id)+" ,menu_name_id= "+str(menu_name_id)+" success" , type = "info" )
            else:
                sql = "INSERT INTO menu_permission VALUES (NULL, %s, %s, %s, CURRENT_TIMESTAMP)"
                cursor.execute(sql, (previlage_id, menu_name_id, value))
                logAction( user_id =user_data['user_id'] , path = "/mgmt/savePermission" , log = "Add menu_permission : value= "+str(value)+" ,previlage_id= "+str(previlage_id)+" ,menu_name_id= "+str(menu_name_id)+" success" , type = "info" )
            conn.commit()
            cursor.close()
            return 'success'
        else :
            logAction( user_id =user_data['user_id'] , path = "/mgmt/savePermission" , log = "Permission denied" , type = "warning" )
            return 'Permission denied'
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return "Error"