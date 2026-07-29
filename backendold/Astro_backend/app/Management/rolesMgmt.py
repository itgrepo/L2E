from ServiceConfig import *

@app.route('/mgmt/addUser', methods=['POST'])
def addUser():
    try:
        dataInput = request.json
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT user.user_id, user.national_id, user.national_id_book, user.email, cp.previlage_name, cp.previlage_id, user.username, user.create_at FROM `user`
                        LEFT JOIN codename_previlage as cp ON cp.previlage_id = user.previlage_id
                            WHERE user.status_id != '7'"""
        cursor.execute(sql,)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        conn.commit()
        cursor.close()
        
        # Format dates
        for item in result:
            item['create_at'] = str(item['create_at']) if item.get('create_at') else None

        return jsonify(result)
    except Exception as e:
        print("Error in addUser: ",str(e))
        return jsonify({"status": "error", "message": str(e)})



@app.route('/mgmt/addUserById', methods=['POST'])
def addUserById():
    try:
        dataInput = request.json
        previlage_id = dataInput['previlage_id']
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT user.user_id, user.national_id, user.national_id_book, user.email, cp.previlage_name, cp.previlage_id, user.username FROM `user`
                        JOIN codename_previlage as cp ON cp.previlage_id = user.previlage_id
                            WHERE user.previlage_id != %s AND user.status_id != '7'"""
        cursor.execute(sql, (previlage_id))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        conn.commit()
        cursor.close()
        return jsonify(result)
    except Exception as e:
        current_app.logger.info(e)
        print("Error: ",str(e))
        return jsonify({"result": "Error"})
        # return jsonify({"result": "Error: " + str(e)})

@app.route('/mgmt/getUserById', methods=['POST'])
def getUserById():
    try:
        dataInput = request.json
        previlage_id = dataInput['previlage_id']
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT user.user_id, user.national_id, user.national_id_book, user.email, cp.previlage_name, cp.previlage_id ,user.username FROM `user`
                        JOIN codename_previlage as cp ON cp.previlage_id = user.previlage_id
                            WHERE user.previlage_id = %s AND user.status_id != '7'"""
        cursor.execute(sql, (previlage_id))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        conn.commit()
        cursor.close()
        return jsonify(result)
    except Exception as e:
        current_app.logger.info(e)
        print("Error: ",str(e))
        return jsonify({"result": "Error"})
        # return jsonify({"result": "Error: " + str(e)})

@app.route('/mgmt/updateUserById', methods=['POST'])
def updateUserById():
    try:
        dataInput = request.json
        previlage_id = dataInput.get('previlage_id')
        target_user_id = dataInput.get('target_user_id') # New field for clarity
        
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if user_data and checkUserIsAdmin(user_data) :
            conn = mysql.connect()
            cursor = conn.cursor()
            
            if target_user_id and previlage_id:
                sql = """UPDATE user SET previlage_id = %s WHERE user_id = %s"""
                cursor.execute(sql, (previlage_id, target_user_id))
                logAction( user_id =user_data['user_id'] , path = "/mgmt/updateUserById" , log = "Update user: "+str(target_user_id)+" To previlage_id: "+str(previlage_id)+" success" , type = "info" )

            conn.commit()
            cursor.close()
            return jsonify({"status": "success"})
        else :
            logAction( user_id =user_data.get('user_id') , path = "/mgmt/updateUserById" , log = "Permission denied" , type = "warning" )
            return jsonify({"status": "Permission Denied"})
    except Exception as e:
        print("Error in updateUserById: " + str(e))
        return jsonify({"status": "error", "message": str(e)})


@app.route('/upadteStatusPrevilage', methods=['POST'])
def upadteStatusPrevilage():
    try:
        dataInput = request.json
        dataUser = dataInput['data']
        rolesName = dataInput['rolesName']
        #------Cookie------#
        # cookie_information = request.cookies.get('information')
        # url_decode_cookie_information = urllib.parse.unquote(cookie_information) # URL Decode
        # dict_cookie_information = json.loads(decode(url_decode_cookie_information)) # Decode cookie['information'] (byte to dict)
        # user_id = dict_cookie_information['user_id']
        user_data = json.loads(decode(dataInput['user']))
        #------------------#
        # a = 0
        # if (a==0):
        if checkUserIsAdmin(user_data) :
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "INSERT INTO codename_previlage VALUES (NULL,%s, CURRENT_TIMESTAMP)"
            cursor.execute(sql, (rolesName))

            sql = "SELECT * FROM codename_previlage WHERE previlage_name = %s"
            cursor.execute(sql, (rolesName))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = toJson(data, columns)

            if len(dataUser) > 0:
                for i in range(len(dataUser)):
                    sql = "UPDATE user SET previlage_id = %s WHERE email = %s"
                    cursor.execute(sql, (result[0]['previlage_id'], dataUser[i]['email']))

            conn.commit()
            cursor.close()
            # return 'success'
            logAction( user_id =user_data['user_id'] , path = "/upadteStatusPrevilage" , log = "Add New Role: "+rolesName+" success" , type = "info" )
            return jsonify({"status": "success"})
        else :
            logAction( user_id =user_data['user_id'] , path = "/upadteStatusPrevilage" , log = "Permission denied" , type = "warning" )
            return jsonify({"status": "Permission denied"})
    except Exception as e:
        current_app.logger.info(e)
        print("Error: ",str(e))
        return jsonify({"status": "Error"})
        # return jsonify({"result": "Error: " + str(e)})

@app.route('/mgmt/addRole', methods=['POST'])
def addRole():
    try:
        dataInput = request.json
        role_name = dataInput.get('role_name')
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        if not role_name:
            return jsonify({"status": "error", "message": "Role name is required"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # 1. Insert into codename_previlage
        sql = "INSERT INTO codename_previlage (previlage_name) VALUES (%s)"
        cursor.execute(sql, (role_name))
        new_role_id = cursor.lastrowid
        
        # 2. Initialize menu_permission for this new role
        sql_menus = "SELECT menu_name_id FROM menu_name"
        cursor.execute(sql_menus)
        menus = cursor.fetchall()
        
        for menu in menus:
            sql_perm = "INSERT INTO menu_permission (previlage_id, menu_name_id, value) VALUES (%s, %s, 'No')"
            cursor.execute(sql_perm, (new_role_id, menu[0]))

        conn.commit()
        cursor.close()
        
        logAction(user_id=user_data.get('user_id'), path="/mgmt/addRole", log="Add New Role: "+str(role_name)+" success", type="info")
        return jsonify({"status": "success", "new_role_id": new_role_id})
    except Exception as e:
        print(f"Error in addRole: {e}")
        return jsonify({"status": "error", "message": str(e)})


@app.route('/mgmt/createUser', methods=['POST'])
def createUser():
    try:
        dataInput = request.json
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "error", "message": "Permission Denied"})

        username = dataInput.get('username')
        email = dataInput.get('email')
        password = dataInput.get('password')
        status_id = dataInput.get('status_id', 1)
        previlage_id = dataInput.get('previlage_id', 3)
        groups = dataInput.get('groups', [])
        
        if not username or not email or not password:
            return jsonify({"status": "error", "message": "Missing required fields"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check duplicate
        cursor.execute("SELECT user_id FROM user WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            cursor.close()
            return jsonify({"status": "error", "message": "Username or Email already exists"})

        # Insert user
        sql_user = """
            INSERT INTO user (username, password, email, firstname, lastname,
                              national_id, national_id_book, national_id_mode,
                              status_id, status_account, previlage_id, job_title,
                              policy_id, usage_objective, create_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        cursor.execute(sql_user, (
            username, password, email, '', '',
            username, '', 1,        
            status_id, 'active', previlage_id, '',     
            1, '' 
        ))
        user_id = cursor.lastrowid
        
        # Insert user_activity
        sql_activity = """
            INSERT INTO user_activity (user_id, login_status, login_respond, create_date,
                                       status_account, password, emailnews)
            VALUES (%s, %s, %s, UNIX_TIMESTAMP(), %s, %s, %s)
        """
        cursor.execute(sql_activity, (user_id, 0, 0, '0', password, '-'))

        # Insert password history
        sql_pass = "INSERT INTO user_password_history VALUES(NULL, %s, '1', %s, UNIX_TIMESTAMP())"
        cursor.execute(sql_pass, (user_id, password))

        # Insert DataField placeholder
        sql_datafield = "INSERT INTO DataField (national_id, national_id_book, sublevel_id, expiration) VALUES (%s, %s, %s, '9999-01-01')"
        cursor.execute(sql_datafield, (username, '', 1.1))
        cursor.execute(sql_datafield, (username, '', 1.2))

        # Handle groups
        if groups and len(groups) > 0:
            for group_id in groups:
                cursor.execute("INSERT INTO user_groups_relation (user_id, group_id) VALUES (%s, %s)", (user_id, group_id))
                
        conn.commit()
        cursor.close()

        logAction(user_id=user_data.get('user_id'), path="/mgmt/createUser", log=f"Admin created user: {username}", type="info")
        return jsonify({"status": "success", "user_id": user_id})
    except Exception as e:
        print("Error in createUser: ", str(e))
        return jsonify({"status": "error", "message": str(e)})

@app.route('/mgmt/deleteUser', methods=['POST'])
def deleteUser():
    try:
        dataInput = request.json
        target_user_id = dataInput.get('target_user_id')
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if user_data and checkUserIsAdmin(user_data) :
            if target_user_id:
                conn = mysql.connect()
                cursor = conn.cursor()
                # Status 7 is the platform's standard for Deleted/Hidden
                sql = "UPDATE user SET status_id = '7' WHERE user_id = %s"
                cursor.execute(sql, (target_user_id))
                conn.commit()
                cursor.close()
                logAction(user_id=user_data.get('user_id'), path="/mgmt/deleteUser", log="Deleted user ID: "+str(target_user_id), type="info")
                return jsonify({"status": "success"})
            else:
                return jsonify({"status": "error", "message": "Target user ID is missing"})
        else:
            return jsonify({"status": "Permission Denied"})
    except Exception as e:
        print(f"Error in deleteUser: {e}")
        return jsonify({"status": "error", "message": str(e)})
    
@app.route('/mgmt/deleteRoles', methods=['POST'])
def deleteRoles():
    try:
        dataInput = request.json
        previlage_id = dataInput['data']['previlage_id']
        #------Cookie------#
        # cookie_information = request.cookies.get('information')
        # url_decode_cookie_information = urllib.parse.unquote(cookie_information) # URL Decode
        # dict_cookie_information = json.loads(decode(url_decode_cookie_information)) # Decode cookie['information'] (byte to dict)
        # user_id = dict_cookie_information['user_id']
        user_data = json.loads(decode(dataInput['user']))
        #------------------#
        # a = 0
        # if (a==0):
        if checkUserIsAdmin(user_data) :
            conn = mysql.connect()
            cursor = conn.cursor()
            
            sql1 = """UPDATE user SET previlage_id = 3 WHERE user_id in (SELECT * FROM (SELECT user_id from user WHERE previlage_id = %s) as a )"""
            cursor.execute(sql1, (previlage_id))
            sql2 = """DELETE FROM `codename_previlage` WHERE previlage_id = %s"""
            cursor.execute(sql2, (previlage_id))
            conn.commit()
            cursor.close()
            logAction( user_id =user_data['user_id'] , path = "/mgmt/deleteRoles" , log = "Delete Role previlage_id: "+str(previlage_id)+" success" , type = "info" )
            # return 'success'
            return jsonify({"status": "success"})
        else :
            logAction( user_id =user_data['user_id'] , path = "/mgmt/deleteRoles" , log = "Permission denied" , type = "warning" )
            return jsonify({"status": "Permission denied"})
    except Exception as e:
        current_app.logger.info(e)
        print("Error: ",str(e))
        return jsonify({"status": "Error"})
        # return jsonify({"result": "Error: " + str(e)})