from ServiceConfig import *
from ServiceConfig.email_service import notify_verification_email

@app.route('/mgmt/addUser', methods=['POST'])
def addUser():
    try:
        dataInput = request.json
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT user.status_id, user.user_id, user.national_id, user.national_id_book, user.email, 
                        user.firstname, user.lastname, user.usage_objective,
                        cp.previlage_name, cp.previlage_id, user.username, user.create_at, user.org_id, 
                        org.org_name, (user.apikey IS NOT NULL AND user.apikey != '') AS has_api_key 
                 FROM `user`
                 LEFT JOIN codename_previlage as cp ON cp.previlage_id = user.previlage_id
                 LEFT JOIN organization org ON user.org_id = org.org_id
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
        org_id = dataInput.get('org_id')
        status_id = dataInput.get('status_id')
        target_user_id = dataInput.get('target_user_id') # New field for clarity
        link = dataInput.get('link', 'http://learn2earndatax.bde.go.th')
        
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if user_data and checkUserIsAdmin(user_data) :
            conn = mysql.connect()
            cursor = conn.cursor()
            
            if target_user_id:
                # Check target user's current status
                cursor.execute("SELECT status_id FROM user WHERE user_id = %s", (target_user_id,))
                curr_user = cursor.fetchone()
                if curr_user:
                    curr_status = str(curr_user[0])
                    if curr_status == '4' and status_id is not None and str(status_id) != '4':
                        cursor.close()
                        conn.close()
                        return jsonify({"status": "error", "message": "ผู้ใช้ยังไม่ได้ยืนยันอีเมล ไม่สามารถเปลี่ยนสถานะได้จนกว่าจะยืนยันอีเมลสำเร็จ"}), 400
                    if curr_status == '8' and status_id is not None and str(status_id) != '8':
                        cursor.close()
                        conn.close()
                        return jsonify({"status": "error", "message": "ผู้ใช้อยู่ในสถานะรออนุมัติ กรุณากดปุ่มอนุมัติ R2 เพื่อเปิดใช้งานบัญชี"}), 400
                    if curr_status == '6' and status_id is not None and str(status_id) != '6':
                        cursor.close()
                        conn.close()
                        return jsonify({"status": "error", "message": "บัญชีถูกล็อค กรุณาใช้ปุ่ม Unlock เพื่อปลดล็อคบัญชี"}), 400

                updates = []
                params = []
                if previlage_id is not None:
                    updates.append("previlage_id = %s")
                    params.append(previlage_id)
                if org_id is not None:
                    updates.append("org_id = %s")
                    params.append(org_id)
                if status_id is not None:
                    updates.append("status_id = %s")
                    params.append(status_id)
                    if str(status_id) in ['1', '2']:
                        updates.append("status_account = 'active'")
                        updates.append("count_login = 0")
                        cursor.execute("UPDATE user_activity SET status_account = '1' WHERE user_id = %s", (target_user_id,))
                    elif str(status_id) == '3':
                        updates.append("status_account = 'suspend'")
                        cursor.execute("UPDATE user_activity SET status_account = '0' WHERE user_id = %s", (target_user_id,))
                    elif str(status_id) == '4':
                        updates.append("status_account = 'pending_verification'")
                        cursor.execute("UPDATE user_activity SET status_account = '0' WHERE user_id = %s", (target_user_id,))
                        # Generate verification token and send verification email
                        cursor.execute("SELECT username, email FROM user WHERE user_id = %s", (target_user_id,))
                        u_row = cursor.fetchone()
                        if u_row:
                            u_name, u_email = u_row[0], u_row[1]
                            import uuid
                            token = (str(uuid.uuid4()) + str(uuid.uuid1())).replace('-', '')
                            cursor.execute("DELETE FROM token_register WHERE username = %s OR email = %s", (u_name, u_email))
                            cursor.execute("INSERT INTO token_register VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)", (token, u_name, u_email, 'active'))
                            try:
                                verify_url = f"{link}/verify/{token}"
                                notify_verification_email(u_name, '', verify_url, u_email)
                                print(f"DEBUG: Sent verification email for user {u_name} on status change to 4. URL: {verify_url}")
                            except Exception as m_err:
                                print(f"Error sending verification email: {m_err}")
                
                if updates:
                    sql = f"UPDATE user SET {', '.join(updates)} WHERE user_id = %s"
                    params.append(target_user_id)
                    cursor.execute(sql, tuple(params))

                logAction( user_id =user_data.get('user_id') , path = "/mgmt/updateUserById" , log = f"Update user: {target_user_id} previlage_id: {previlage_id} org_id: {org_id} status_id: {status_id} success" , type = "info" )

            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"status": "success"})
        else :
            logAction( user_id =user_data.get('user_id') , path = "/mgmt/updateUserById" , log = "Permission denied" , type = "warning" )
            return jsonify({"status": "Permission Denied"})
    except Exception as e:
        print("Error in updateUserById: " + str(e))
        return jsonify({"status": "error", "message": str(e)})


@app.route('/mgmt/approveUserRegistration', methods=['POST'])
def approveUserRegistration():
    """Approve user onboarding request: grant R2 (previlage_id=2) and activate account (status_id=1)."""
    try:
        dataInput = request.json or {}
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})
            
        target_user_id = dataInput.get('target_user_id')
        if not target_user_id:
            return jsonify({"status": "error", "message": "Target user ID is required"}), 400
            
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Update user to R2 (General User) and Active (1) with 2FA enabled for initial setup
        sql = """UPDATE user 
                 SET previlage_id = 2, status_id = 1, status_account = 'active', 2fa_status = 'on'
                 WHERE user_id = %s"""
        cursor.execute(sql, (target_user_id,))
        cursor.execute("UPDATE user_activity SET status_account = '1' WHERE user_id = %s", (target_user_id,))
        
        # Notify user
        try:
            from ServiceConfig.notification_util import notify_user
            notify_user(target_user_id, 'account_approved', 'บัญชีของคุณได้รับการอนุมัติแล้ว คุณได้รับสิทธิ์ระดับ R2 (ผู้ใช้งานทั่วไป) และสามารถเข้าใช้งานระบบได้ทันที')
        except Exception as notif_err:
            print(f"Could not notify approved user: {notif_err}")
            
        conn.commit()
        cursor.close()
        conn.close()
        
        logAction(user_data.get('user_id'), '/mgmt/approveUserRegistration', f'Approved user {target_user_id} as R2 Active', 'info')
        return jsonify({"status": "success", "message": "อนุมัติผู้ใช้งานเป็นสิทธิ์ระดับ R2 สำเร็จ"})
    except Exception as e:
        print("Error in approveUserRegistration: " + str(e))
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
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
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
        status_id = dataInput.get('status_id', 4)
        previlage_id = dataInput.get('previlage_id', 2)
        org_id = dataInput.get('org_id')
        groups = dataInput.get('groups', [])
        
        if not username or not email or not password:
            return jsonify({"status": "error", "message": "Missing required fields"})

        is_user_valid, user_err = validate_username_rules(username)
        if not is_user_valid:
            return jsonify({"status": "error", "message": user_err})

        import re
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) or re.search(r'[<>"\'/;`%&]', email):
            return jsonify({"status": "error", "message": "Invalid email format"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check duplicate (case-insensitive for username)
        cursor.execute("SELECT user_id, username, email FROM user WHERE (LOWER(username) = LOWER(%s) OR email = %s) AND status_id != '7'", (username, email))
        data_dup = cursor.fetchall()
        if data_dup:
            for row in data_dup:
                if row[1] and row[1].lower() == username.lower():
                    cursor.close()
                    conn.close()
                    return jsonify({"status": "error", "message": "ชื่อผู้ใช้นี้ถูกใช้แล้ว (ไม่อนุญาตให้ซ้ำแม้ต่างกันแค่ตัวพิมพ์ใหญ่-เล็ก)"})
                if row[2] and row[2].lower() == email.lower():
                    cursor.close()
                    conn.close()
                    return jsonify({"status": "error", "message": "อีเมลนี้ถูกใช้แล้ว"})
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Username or Email already exists"})

        status_account_val = 'active' if str(status_id) in ['1', '2'] else ('suspend' if str(status_id) == '3' else 'pending_verification')

        # Insert user with admin_created tag
        sql_user = """
            INSERT INTO user (username, password, email, firstname, lastname,
                              national_id, national_id_book, national_id_mode,
                              status_id, status_account, previlage_id, org_id, job_title,
                              policy_id, usage_objective, create_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """
        cursor.execute(sql_user, (
            username, password, email, '', '',
            username, '', 1,
            status_id, status_account_val, previlage_id, org_id, '',
            1, 'admin_created'
        ))
        user_id = cursor.lastrowid
        
        # If pending verification (4), generate token and send verification email
        if int(status_id) == 4:
            import uuid
            token = (str(uuid.uuid4()) + str(uuid.uuid1())).replace('-', '')
            cursor.execute("DELETE FROM token_register WHERE username = %s OR email = %s", (username, email))
            sql_token = "INSERT INTO token_register VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
            cursor.execute(sql_token, (token, username, email, 'active'))
            
            try:
                fallback_link = "http://learn2earndatax.bde.go.th"
                link = dataInput.get('link', fallback_link)
                verify_url = f"{link}/verify/{token}"
                notify_verification_email(username, '', verify_url, email)
                print(f"DEBUG: Admin AddUser Verification Email sent to {email}. URL: {verify_url}")
            except Exception as mail_err:
                print("Could not send verification email in Admin AddUser: " + str(mail_err))

        
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
                cursor.execute("INSERT INTO group_user_detail (user_id, group_id) VALUES (%s, %s)", (user_id, group_id))
                
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
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        #------------------#
        # a = 0
        # if (a==0):
        if checkUserIsAdmin(user_data) :
            conn = mysql.connect()
            cursor = conn.cursor()
            
            sql1 = """UPDATE user SET previlage_id = 2 WHERE user_id in (SELECT * FROM (SELECT user_id from user WHERE previlage_id = %s) as a )"""
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

@app.route('/mgmt/unlockUserByAdmin', methods=['POST'])
def unlockUserByAdmin():
    try:
        dataInput = request.json
        user_data = safe_json_loads(platform_decode(dataInput.get('user', '')))
        
        if not user_data or not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        target_user_id = dataInput.get('target_user_id')
        if not target_user_id:
             return jsonify({"status": "Missing target_user_id"})

        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "UPDATE user SET status_id = 1, count_login = 0 WHERE user_id = %s"
        cursor.execute(sql, (target_user_id,))
        

        
        conn.commit()
        cursor.close()
        conn.close()

        logAction(user_data.get('user_id'), '/mgmt/unlockUserByAdmin', f'Admin unlocked user_id {target_user_id}', 'info')

        return jsonify({"status": "success"})
    except Exception as e:
        import traceback
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()})
