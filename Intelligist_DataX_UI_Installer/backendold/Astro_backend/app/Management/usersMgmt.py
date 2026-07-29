from ServiceConfig import *
import uuid

@app.route('/mgmt/menuName', methods=['POST'])
def menuName():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT * FROM menu_name"
        cursor.execute(sql,)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"result": "Error"})
        # return jsonify({"result": "Error: " + str(e)})

@app.route('/mgmt/mgmtgetUser', methods=['POST'])
def mgmtgetUser():
    conn = mysql.connect()
    cursor = conn.cursor()
    #sql = "SELECT user.user_id, user.username, user.firstname, user.lastname, user.email, user.last_update, user.previlage_id, cs.status_name, cs.status_id ,user.email_news FROM user JOIN codename_status as cs ON user.status_id = cs.status_id "
    # sql = '''SELECT user.user_id, user.username, user.firstname, user.lastname, user.email, ua.login_respond, user.previlage_id, cs.status_name, cs.status_id ,user.email_news ,"" AS send_QR FROM user JOIN codename_status as cs ON user.status_id = cs.status_id JOIN user_activity as ua ON user.user_id = ua.user_id'''
    sql = '''SELECT user.user_id, user.username, user.firstname, 
    user.lastname, user.email,user.usage_objective,user.other_object, 
    ua.login_respond, user.previlage_id,user.two_factor_authen, 
    cs.status_name, cs.status_id ,user.email_news,user.create_at,"" AS send_QR 
        FROM user 
    JOIN codename_status as cs 
        ON user.status_id = cs.status_id 
    JOIN user_activity as ua 
        ON user.user_id = ua.user_id 
    WHERE user.status_id != 7
    ORDER BY user.user_id DESC''' # เพิ่ม column user.two_factor_authen
    cursor.execute(sql, ())
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    for i in range(len(result)):
        result[i]['login_respond'] = datetime.utcfromtimestamp(int(result[i]['login_respond'])+25200).strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(result)

@app.route('/mgmt/permission', methods=['POST'])
def permission():
    try:
        dataInput = request.json
        previlage_id = dataInput['previlage_id']
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT * FROM menu_permission WHERE previlage_id = %s"
        cursor.execute(sql, (previlage_id))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"result": "Error"})
        # return jsonify({"result": "Error: " + str(e)})


@app.route('/mgmt/getPrevilage', methods=['POST'])
def getPrevilage():
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT previlage_id, previlage_name FROM codename_previlage"
    cursor.execute(sql,)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    conn.commit()
    cursor.close()
    conn.close()
    return json.dumps({'result': result})

@app.route('/mgmt/codenameStatus', methods=['GET'])
def codenameStatus():
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT * FROM codename_status"
    cursor.execute(sql, ())
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    return jsonify(result)

@app.route('/mgmt/mgmtUpdateStatusUser', methods=['POST'])
def mgmtUpdateStatusUser():
    try :
        dataInput = request.json
        status_id = dataInput['data']['status_id']
        user_id = dataInput['data']['user_id']
        firstname = dataInput['data']['firstname']
        lastname = dataInput['data']['lastname']
        email = dataInput['data']['email']
        #------Cookie------#
        # cookie_information = request.cookies.get('information')
        # url_decode_cookie_information = urllib.parse.unquote(cookie_information) # URL Decode
        # dict_cookie_information = json.loads(decode(url_decode_cookie_information)) # Decode cookie['information'] (byte to dict)
        # user_id_cookie = dict_cookie_information['user_id']
        user_data = json.loads(decode(dataInput['user'])) #Data user
        #--------------------#
        if checkUserIsAdmin(user_data) :
        # a=0
        # if (a==0):
            conn = mysql.connect()
            cursor = conn.cursor()
            if status_id != 7:
                sql = "UPDATE user SET status_id = %s WHERE user_id = %s"
                cursor.execute(sql, (status_id, user_id))
                sql_update_status_secret_key = "UPDATE user_secret_key SET secret_key_status = 'active' WHERE user_id =%s"
                cursor.execute(sql_update_status_secret_key, user_id)
            else:
                sql = "UPDATE user SET status_id = %s WHERE user_id = %s"
                cursor.execute(sql, (status_id, user_id))
                sql_update_status_secret_key = "UPDATE user_secret_key SET secret_key_status = 'inactive' WHERE user_id =%s"
                cursor.execute(sql_update_status_secret_key, user_id)
                #if check_email_format(email):
                    #sendMailStatusDelete(email, firstname, lastname) # Have E-mail #
            conn.commit()
            cursor.close()
            conn.close()
            logAction(user_data['user_id'], '/mgmt/mgmtUpdateStatusUser', 'admin has been update status user : '+str(user_id)+' to status id : '+str(status_id)+' success', 'info')
            return 'success'
        else :
            logAction( user_id =user_id_cookie , path = "/mgmt/mgmtUpdateStatusUser" , log = "Permission denied" , type = "warning" )
            return "Permission denied"
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return "Error"

@app.route('/mgmt/resendQRcode', methods=['POST'])
def resendQRcode():
    try :
        input_data = request.json
        # print("update description text is : ",input_data)
        user_data = json.loads(decode(input_data['user']))
        # a=0
        # if(a==0):
        if checkUserIsAdmin(user_data) :
            normal_user_data = input_data['data']
            username = normal_user_data['username']
            email = normal_user_data['email']
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "SELECT firstname,lastname,email FROM user WHERE username = %s AND status_id != '7' "
            cursor.execute(sql, (username))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = toJson(data, columns)
            conn.commit()
            cursor.close()
            conn.close()
            # print(result[0]['email'])
            if len(result) != 0:
                QRstr = createSecretKeyTwoFactor(username,1)
                # print(QRstr,"This is QR string")
                if(QRstr != "" and result[0]['email'] not in [None,'None']):
                    # print("start send qr")
                    #send_email = sendMailQrOTP(result[0]['email'],result[0]['firstname'],result[0]['lastname'],QRstr)
                    # print(("Alreader sent qr : ",a))
                        # logAction(user_data['user_id'], '/mgmt/resendQRcode', 'Resend QRCode for user : '+username+' and send to email : '+result[0]['email']+' success', 'info')
                    return(jsonify({"status": "Success"}))
                else :
                    # logAction(user_data['user_id'], '/mgmt/resendQRcode', 'user : '+username+' not have email for resend QRcode', 'warning')
                    return(jsonify({"status": "Error"}))
            else :
                # logAction(user_data['user_id'], '/mgmt/resendQRcode', 'Cannot find username : '+username, 'warning')
                return(jsonify({"status": "user not found"}))
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error"})


@app.route('/updateTwoFactorAuthen' ,methods=['POST'])
def updateTwoFactorAuthen():
    dataInput = request.json
    two_factor_authen_status = dataInput['two_factor_authen_status'] # status = on,off
    user_id = decode(dataInput['user_id']) # user_id ที่ต้องการจะ update status ของ 2FA
    user_data = json.loads(decode(dataInput['user'])) #Data user
    try:
        ##--Check User Permission--##
        # a=0
        # if(a==0):
        if checkUserIsAdmin(user_data) :
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "UPDATE user SET two_factor_authen = %s WHERE user_id = %s"
            cursor.execute(sql,(two_factor_authen_status,user_id))
            conn.commit()
            cursor.close()
            conn.close()
            logAction(user_data['user_id'], '/updateTwoFactorAuthen', 'Change status of user_id : '+user_id.decode('utf-8')+' to '+two_factor_authen_status, 'info')
            return jsonify({"status": "success"})
        else:
            logAction(user_data['user_id'], '/updateTwoFactorAuthen', 'Permission denied', 'warning')
            return jsonify({"status": "Permission denied"})     
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"status": "Error"})


#========== GET QRString API =====================#
@app.route('/getQRString' ,methods=['POST'])
def getQRString():
    try:
        dataInput = request.json
        # print(dataInput)
        if len(dataInput) != 0:
            username = dataInput['username']
            #========= get username to find user_id ================
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = """SELECT user_id FROM user WHERE username = %s AND status_id != 7"""
            cursor.execute(sql,(username))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = toJson(data,columns)
            conn.commit()
            print(result[0]['user_id'])
            #========= Use id for get QRString =====================
            if len(result) != 0 :
                sql = """SELECT secret_key FROM user_secret_key WHERE user_id = %s"""
                cursor.execute(sql,(result[0]['user_id']))
                data = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                secret_key = toJson(data,columns)
                print(secret_key)
                conn.commit()
                cursor.close()
                conn.close()
                if len(secret_key) != 0:
                    stringToQR = pyotp.totp.TOTP(secret_key[0]['secret_key']).provisioning_uri(username, issuer_name="bigdataplatform.customs.net")
                    return jsonify({"status":"Success","data": stringToQR})
                else:
                    return jsonify({"status": "Error! This user not have QRCode."})
            else :
                return jsonify({"status": "Error! This user is invalid."})

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        # return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        return jsonify({"status": "Error"})
#----------------------------------------------------------------------------------------------------#
@app.route('/getMenuByPermission', methods=['POST'])
def getMenuByPermission():
    try:
        dataInput = request.json
        #------Cookie------#
        # cookie_information = request.cookies.get('information')
        # print(cookie_information)
        # url_decode_cookie_information = urllib.parse.unquote(cookie_information) # URL Decode
        # print(url_decode_cookie_information)
        # dict_cookie_information = json.loads(decode(url_decode_cookie_information)) # Decode cookie['information'] (byte to dict)
        # print(dict_cookie_information)
        #------------------#
        # username = dict_cookie_information['username']
        user_data = json.loads(decode(dataInput['user'])) #Data user
        #------------------#
        if checkUserIsAdmin(user_data) :
            ##--Get menu--#
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = """SELECT menu_name.menu_name,menu_name.icon 
                        FROM `menu_permission` 
                    LEFT JOIN menu_name 
                        ON menu_permission.menu_name_id = menu_name.menu_name_id 
                    WHERE menu_permission.previlage_id = 
                        (SELECT previlage_id FROM user WHERE username = %s AND status_id != '7') 
                        AND menu_permission.value = 'Yes' AND menu_name IS NOT NULL"""
            cursor.execute(sql,(user_data['username']))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = toJson(data,columns)
            conn.commit()
            cursor.close()
            conn.close()
            #--------------#
            return jsonify({"status":"Success","data":result})
        else:
            logAction(user_data['user_id'], '/getMenuByPermission', 'Permission denied', 'warning')
            return jsonify({"status": "Permission denied"})    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error"})
        
@app.route('/EditUserProfileByAdmin' ,methods=['POST'])
def EditUserProfileByAdmin():
    try:
        dataInput = request.json
        data_user = json.loads(decode(dataInput['user'])) #Data user
        if checkUserIsAdmin(data_user) :
            link = dataInput['link']
            username = dataInput['username']
            firstname = dataInput['firstname']
            lastname = dataInput['lastname']
            usage_objective = dataInput['usage_objective']
            other_object = dataInput['other_object']
            email = dataInput['email']
            if other_object in [None,"Null","None"]:
              other_object = "-"
            conn = mysql.connect()
            cursor = conn.cursor()

            sql_get = """SELECT * FROM user WHERE username = %s AND status_id != 7"""
            cursor.execute(sql_get, (username))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = toJson(data, columns)
            # print(result)
            if result[0]['email'] not in ["None",None]:# Check email is not null
                # Check email is not change
                if result[0]['email'] == email:
                    sql = "UPDATE user SET firstname = %s , lastname = %s ,usage_objective = %s , other_object = %s WHERE user_id = %s"
                    cursor.execute(sql, (firstname, lastname, usage_objective, other_object, result[0]['user_id']))

                    sql_getdata = "SELECT * FROM user WHERE user_id = %s AND status_id != 7 "
                    cursor.execute(sql_getdata, result[0]['user_id'])
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result_data = toJson(data, columns)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    # sendMailEditProfile(dataInput, link, result_data[0]['firstname'], result_data[0]['lastname'])
                    #return json.dumps({'status': 'success', 'data': result})
                    logAction(data_user['user_id'], '/EditUserProfileByAdmin', 'user : '+username+' has been change profile by admin', 'info')
                    return jsonify({'status': 'success', 'data': result_data})
                # ========================== email is change ==========================
                else:
                    sql_get2 = """SELECT email FROM user WHERE email = %s AND status_id != 7"""
                    cursor.execute(sql_get2, (email,))
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result_check_email2= toJson(data, columns)
                    # print(result_check_email2)
                    if len(result_check_email2) == 0:
                        if email in [None,"None",""]:
                            sql = "INSERT INTO temp_user VALUES (NULL, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
                            cursor.execute(sql, (result[0]['user_id'], firstname, lastname, email, usage_objective, other_object))

                            sql = "UPDATE user SET firstname = %s , lastname = %s ,usage_objective = %s , other_object = %s  ,email = NULL WHERE user_id = %s"
                            cursor.execute(sql, (firstname, lastname, usage_objective, other_object, result[0]['user_id']))

                            sql_get = """SELECT * FROM user WHERE user_id = %s AND status_id != 7"""
                            cursor.execute(sql_get, (result[0]['user_id']))
                            data = cursor.fetchall()
                            columns = [column[0] for column in cursor.description]
                            result_data = toJson(data, columns)
                            conn.commit()
                            cursor.close()
                            conn.close()

                            # sendMailEditProfileOld(result_data)
                            # sendMailEditProfile(dataInput, link, result_data[0]['firstname'], result_data[0]['lastname'])
                            logAction(data_user['user_id'], '/EditUserProfileByAdmin', 'user : '+username+' has been change profile and email not changed by admin', 'info')
                            return jsonify({'status': 'email success', 'data': 'Please verify email'})
                        else:
                            sql = "INSERT INTO temp_user VALUES (NULL, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
                            cursor.execute(sql, (result[0]['user_id'], firstname, lastname, email, usage_objective, other_object))

                            sql = "UPDATE user SET firstname = %s , lastname = %s ,usage_objective = %s , other_object = %s  ,email = %s WHERE user_id = %s"
                            cursor.execute(sql, (firstname, lastname, usage_objective, other_object, email, result[0]['user_id']))

                            sql_get = """SELECT * FROM user WHERE user_id = %s"""
                            cursor.execute(sql_get, (result[0]['user_id']))
                            data = cursor.fetchall()
                            columns = [column[0] for column in cursor.description]
                            result_data = toJson(data, columns)
                            conn.commit()
                            cursor.close()
                            conn.close()

                            # sendMailEditProfileOld(result_data)
                            # sendMailEditProfile(dataInput, link, result_data[0]['firstname'], result_data[0]['lastname'])
                            logAction(data_user['user_id'], '/EditUserProfileByAdmin', 'user : '+username+' has been change profile and email has changed to : '+email+' by admin', 'info')
                            return jsonify({'status': 'email success', 'data': result_data})
                    else:
                        cursor.close()
                        conn.close()
                        logAction(data_user['user_id'], '/EditUserProfileByAdmin', 'user : '+username+' email is duplicate', 'warning')
                        return jsonify({'status': 'email is duplicate'})
            elif result[0]['email'] in ["None",None]:
                # Check email is not change
                if result[0]['email'] == email:
                    sql = "UPDATE user SET firstname = %s , lastname = %s ,usage_objective = %s , other_object = %s WHERE user_id = %s"
                    cursor.execute(sql, (firstname, lastname, usage_objective, other_object, result[0]['user_id']))

                    sql_getdata = "SELECT * FROM user WHERE user_id = %s"
                    cursor.execute(sql_getdata, result[0]['user_id'])
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result_data = toJson(data, columns)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    logAction(data_user['user_id'], '/EditUserProfileByAdmin', 'user : '+username+' has been change profile and email not changed by admin', 'info')
                    return jsonify({'status': 'success', 'data': result_data})
                else:
                    sql_get3 = """SELECT email FROM user where email = %s AND status_id != 7"""
                    cursor.execute(sql_get3, (email))
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result_check_email3 = toJson(data, columns)
                    if len(result_check_email3) == 0:
                        sql = "INSERT INTO temp_user VALUES (NULL, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
                        cursor.execute(sql, (result[0]['user_id'], firstname, lastname, email, usage_objective, other_object))

                        sql = "UPDATE user SET firstname = %s , lastname = %s ,usage_objective = %s , other_object = %s  ,email = %s WHERE user_id = %s"
                        cursor.execute(sql, (firstname, lastname, usage_objective, other_object, email, result[0]['user_id']))

                        sql_get = """SELECT * FROM user WHERE user_id = %s"""
                        cursor.execute(sql_get, (result[0]['user_id']))
                        data = cursor.fetchall()
                        columns = [column[0] for column in cursor.description]
                        result_data = toJson(data, columns)
                        conn.commit()
                        cursor.close()
                        conn.close()
                        # sendMailEditProfileOld(result_data)
                        # sendMailEditProfile(dataInput, link, result_data[0]['firstname'], result_data[0]['lastname'])
                        logAction(data_user['user_id'], '/EditUserProfileByAdmin', 'user : '+username+' has been change profile and email has changed to : '+email+' by admin', 'info')
                        return jsonify({'status': 'email success', 'data': result_data})
                    else:
                        cursor.close()
                        conn.close()
                        logAction(data_user['user_id'], '/EditUserProfileByAdmin', 'user : '+username+' email is duplicate', 'warning')
                        return jsonify({'status': 'email is duplicate'})
        else:
            return jsonify({"status": "Permission denied"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error"})

#========== Change Password By Admin API =====================#
@app.route('/ChangePasswordByAdmin' ,methods=['POST'])
def ChangePasswordByAdmin():
    try:
        dataInput = request.json
        data_user = json.loads(decode(dataInput['user'])) #Data user
        if checkUserIsAdmin(data_user) :
            new_password = dataInput['new_password']
            username = dataInput['username']
            # username = decode(dataInput['username'])
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "SELECT user.user_id, user_activity.password, email, firstname, lastname FROM user JOIN user_activity ON user.user_id = user_activity.user_id WHERE user.username = %s AND status_id != 7"
            cursor.execute(sql, username)
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = toJson(data, columns)
            if len(result) != 0 :
                sql_current_password = "SELECT password FROM (SELECT sequence_no , password FROM user_password_history WHERE user_id = %s ORDER BY sequence_no DESC LIMIT 3) AS new WHERE password = %s "
                cursor.execute(sql_current_password, (result[0]['user_id'], new_password))
                data_pass = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result_current_password = toJson(data_pass, columns)
                sql_max = "SELECT MAX(sequence_no) FROM user_password_history WHERE user_id = %s "
                cursor.execute(sql_max, result[0]['user_id'])
                data_max = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result_max = toJson(data_max, columns)
                cursor.close()
                conn.close()
                if len(result_current_password) == 0:
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = "UPDATE user_activity SET create_date = UNIX_TIMESTAMP(), password = %s , emailnews = %s   WHERE user_id = %s"
                    cursor.execute(sql, (new_password, "-",result[0]['user_id']))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = "INSERT INTO user_password_history VALUES(NULL, %s,%s,%s,UNIX_TIMESTAMP())"
                    cursor.execute(sql, (result[0]['user_id'], int(result_max[0]['MAX(sequence_no)']) + 1, new_password))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    logAction(data_user['user_id'], '/ChangePasswordByAdmin', 'admin has been changed password user : '+username+' success', 'info')
                    return jsonify({"status": "Success"})
                elif len(result_current_password)!= 0:
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = "UPDATE user_activity SET create_date = UNIX_TIMESTAMP(), password = %s , emailnews = %s   WHERE user_id = %s"
                    cursor.execute(sql, (new_password, "-",result[0]['user_id']))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    logAction(data_user['user_id'], '/ChangePasswordByAdmin', 'admin has been changed password user : '+username+' success', 'info')
                    # sendMailEditPassword(result[0]['email'],result[0]['firstname'],result[0]['lastname'] )
                return jsonify({"status":"Success"})
            else: 
                logAction(data_user['user_id'], '/ChangePasswordByAdmin', 'user : '+username+' not found', 'warning')
                return jsonify({"status":"Error user not found"})
        else:
            logAction(data_user['user_id'], '/ChangePasswordByAdmin', 'Permission denied', 'warning')
            return jsonify({"status": "Permission denied"})

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error"})

  #========== Change Password By Admin API =====================#
@app.route('/AddUserByAdmin' ,methods=['POST'])
def AddUserByAdmin():
    try:
        dataInput = request.json
        data_user = json.loads(decode(dataInput['user'])) #Data user
        if checkUserIsAdmin(data_user) :
            #================ get input data ===========================#
            username = dataInput['username']
            password = dataInput['password']
            firstname = dataInput['firstname']
            lastname = dataInput['lastname']
            usage_objective = dataInput['usage_objective']
            other_object = dataInput['other_object']
            email = dataInput['email']
            if email not in [None,"None",""]:
                if email.isspace():
                    email = email.strip()
            elif email in [None,"None",""]:
                email = None
            # link = dataInput['link']
            national_id = username
            national_id_book = ''
            national_id_mode = 1
            # ================= Check user has been already exist ========#
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "SELECT * FROM user WHERE (username = %s AND status_id != '7') OR (national_id = %s AND national_id_book = %s AND status_id != '7' ) OR (email = %s AND status_id != '7') AND status_account = 'active'"
            cursor.execute(sql, (username, national_id, national_id_book, email))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = toJson(data, columns)
            conn.close()
            # current_app.logger.info(len(data))
            if len(data):
                if result[0]['username'] == username:
                    logAction(data_user['user_id'], '/AddUserByAdmin', 'Username is duplicate','warning')
                    return jsonify({'status': 'Error Username is duplicate'})
                elif result[0]['email'] == email:
                    logAction(data_user['user_id'], '/AddUserByAdmin', 'Email is duplicate','warning')
                    return jsonify({'status': 'Error Email is duplicate'})
                elif result[0]['national_id'] == national_id and national_id_mode == 1:
                    logAction(data_user['user_id'], '/AddUserByAdmin', 'National ID is duplicate','warning')
                    return jsonify({'status': 'Error National ID is duplicate'})
                elif result[0]['national_id_book'] == national_id_book and national_id_mode == 2:
                    logAction(data_user['user_id'], '/AddUserByAdmin', 'Passport is duplicate','warning')
                    return jsonify({'status': 'Error Passport is duplicate'})
            # ================= Check user has been already exist ========#
            if len(data) != 0:
                if str(result[0]['status_id']) == '4':
                    logAction(data_user['user_id'], '/AddUserByAdmin', 'This user has been duplicate','warning')
                    return jsonify({'status': 'Error user has been duplicate'})
            # ================= Check user has been already exist ========#
            elif len(data) == 0:
                token = (str(uuid.uuid4()) + str(uuid.uuid1())).replace('-', '')
                conn = mysql.connect()
                cursor = conn.cursor()
                sql_token_register = "INSERT INTO token_register VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
                cursor.execute(sql_token_register, (token, username, email, 'active'))
                conn.commit()
                cursor.close()
                conn.close()
                conn = mysql.connect()
                cursor = conn.cursor()
                sql_codename_policy = "SELECT MAX(policy_id) FROM codename_policy "
                cursor.execute(sql_codename_policy)
                data = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                resultCheckPolicy = toJson(data, columns)
                default_level = 3  # user level
                status = 4  # Status = Pending
                status_account = "active"
                count_login = 0
                policy_id = resultCheckPolicy[0]['MAX(policy_id)']  # policy_id is present
                # print(default_level+"\n"+status+"\n"+status_account+"\n"+count_login+"\n"+policy_id)

                sql_user = "INSERT INTO user VALUES (NULL,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, CURRENT_TIMESTAMP, 1,'off')" # off -> 2FA status off  , DataX -> type_user
                cursor.execute(sql_user,(username, email, firstname, lastname, national_id, national_id_book, national_id_mode, policy_id,usage_objective, other_object, default_level, count_login, status, status_account))
                conn.commit()
                cursor.close()
                conn.close()
                #/M&M DB_1
                id = cursor.lastrowid
                conn = mysql.connect()
                cursor = conn.cursor()
                sql_user_activity = "INSERT INTO user_activity(user_id,login_status,login_respond,create_date,status_account,password,emailnews) VALUES(%s,%s,UNIX_TIMESTAMP(),UNIX_TIMESTAMP(),%s,%s,%s)"
                value = (id, '0', '0',password,'-')
                cursor.execute(sql_user_activity, value)
                conn.commit()
                cursor.close()
                conn.close()
                # M&M ?????1_1
                conn = mysql.connect()
                cursor = conn.cursor()
                sql_pass = """INSERT INTO user_password_history VALUES(NULL, %s,%s,%s,UNIX_TIMESTAMP())"""
                cursor.execute(sql_pass, (id, '1', password))

                if national_id:
                    sql_data = """INSERT INTO DataField VALUES(NULL, %s,'',%s,'9999-01-01')"""
                    cursor.execute(sql_data, (national_id, 1.1))
                    sql_data = """INSERT INTO DataField VALUES(NULL, %s,'',%s,'9999-01-01')"""
                    cursor.execute(sql_data, (national_id, 1.2))
                else:
                    sql_data = """INSERT INTO DataField VALUES(NULL, '',%s,%s,'9999-01-01')"""
                    cursor.execute(sql_data, (national_id_book, 1.1))
                    sql_data = """INSERT INTO DataField VALUES(NULL, '',%s,%s,'9999-01-01')"""
                    cursor.execute(sql_data, (national_id_book, 1.2))
                # sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,CURRENT_DATE())"""
                # cursor.execute(sql_data, (national_id, national_id_book,1.1))
                conn.commit()
                cursor.close()
                conn.close()
                # /M&M ?????1_1
                # M&M ?????1_1 6/8/19 10.27
                conn = mysql.connect()
                cursor = conn.cursor()
                sql_max_consent_agreement = "SELECT MAX(version) FROM consent_agreement WHERE status = 'active'"
                cursor.execute(sql_max_consent_agreement)
                data = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result_max = toJson(data, columns)
                sql_id_consent_agreement = "SELECT consent_agreement_id FROM consent_agreement WHERE status = 'active' AND version = %s"
                cursor.execute(sql_id_consent_agreement, (result_max[0]['MAX(version)']))
                data = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result_id = toJson(data, columns)

                ip = request.headers.get('X-FORWARDED-FOR',None)
                # ip = "192.168.2.36"
                conn = mysql.connect()
                cursor = conn.cursor()
                sql_user_agreement = "INSERT INTO user_agreement VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())"
                cursor.execute(sql_user_agreement, (ip, id, result_id[0]['consent_agreement_id']))
                # cursor.execute(sql, (request.remote_addr, id, result_id[0]['consent_agreement_id']))
                conn.commit()
                # /M&M ?????1_1 6/8/19 10.27
                # sendMailConfirmRegister(id, token, email, link, firstname, lastname)
                sql_fetch_token_register = "SELECT username, email FROM token_register WHERE username = %s"
                cursor.execute(sql_fetch_token_register,username)
                data = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result_fetch_token_register = toJson(data, columns)

                sql_password = "SELECT user_activity.password , user.* FROM user JOIN user_activity ON user.user_id = user_activity.user_id WHERE user.username = %s AND user.status_id != '7'"
                cursor.execute(sql_password, str(result_fetch_token_register[0]['username']))
                data_password = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result_password = toJson(data_password, columns)
                sql_account = "SELECT create_date FROM user_activity WHERE user_id = %s"
                cursor.execute(sql_account, (result_password[0]['user_id']))
                data_account = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result_account = toJson(data_account, columns)

                sql_time = "SELECT UNIX_TIMESTAMP()"
                cursor.execute(sql_time)
                data_time = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result_time = toJson(data_time, columns)

                sql_timetable_activity = "SELECT duration FROM timetable_activity  WHERE activity_desc = 'LinkExpire' "
                cursor.execute(sql_timetable_activity)
                data = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                result_linkEx = toJson(data, columns)
                conn.commit()
                cursor.close()
                conn.close()
                national = result_password[0]['national_id']
                if len(data) == 0:
                    logAction(data_user['user_id'],'/AddUserByAdmin', 'not found','warning')
                    return jsonify({'status': 'not found'})
                elif int(result_time[0]['UNIX_TIMESTAMP()']) - int(result_account[0]['create_date']) >= result_linkEx[0]['duration']: #259200
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql_D1 = """DELETE FROM user WHERE user_id = %s"""
                    # return jsonify({'status': str(result_password[0]['user_id'])})
                    cursor.execute(sql_D1,(result_password[0]['user_id']))

                    sql_D2 = """DELETE FROM user_activity WHERE user_id = %s"""
                    # return jsonify({'status': str(result_password[0]['user_id'])})
                    cursor.execute(sql_D2,(result_password[0]['user_id']))
                    # M&M ?????1_1 6/8/19 10.27
                    sql_D3 = """DELETE FROM user_agreement WHERE user_id = %s"""
                    # return jsonify({'status': str(result_password[0]['user_id'])})
                    cursor.execute(sql_D3,(result_password[0]['user_id']))

                    sql_D4 = """DELETE FROM user_password_history WHERE user_id = %s"""
                    # return jsonify({'status': str(result_password[0]['user_id'])})
                    cursor.execute(sql_D4,(result_password[0]['user_id']))

                    sql_D5 = """DELETE FROM DataField WHERE national_id = %s"""
                    # return jsonify({'status': str(result_password[0]['user_id'])})
                    cursor.execute(sql_D5,(national))

                    # sql = """DELETE FROM token_register WHERE token = %s;"""
                    # cursor.execute(sql,(dataInput['token']))
                    # conn.commit()
                    # cursor.close()
                    # conn.close()
                    logAction(data_user['user_id'],'/AddUserByAdmin', 'link expire','warning')
                    return jsonify({'status': 'link expire'})
                else:
                    # M&M ?????1_1 6/8/19 10.27
                    # sql_max = "SELECT MAX(version) FROM consent_agreement WHERE status = 'active'"
                    # cursor.execute(sql_max)
                    # data = cursor.fetchall()
                    # columns = [column[0] for column in cursor.description]
                    # result_max = toJson(data, columns)
                    # sql_id = "SELECT consent_agreement_id FROM consent_agreement WHERE status = 'active' AND version = %s"
                    # cursor.execute(sql_id, (result_max[0]['MAX(version)']))
                    # data = cursor.fetchall()
                    # columns = [column[0] for column in cursor.description]
                    # result_id = toJson(data, columns)
                    #
                    # conn = mysql.connect()
                    # cursor = conn.cursor()
                    # sql = "INSERT INTO user_agreement VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())"
                    # cursor.execute(sql, (request.remote_addr, result_password[0]['user_id'], result_id[0]['consent_agreement_id']))
                    # conn.commit()
                    # cursor.close()

                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = "UPDATE user_activity SET status_account = '1' WHERE user_id = %s "
                    cursor.execute(sql, (result_password[0]['user_id']))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    # /M&M ?????1_8
                    # M&M 6/8/62 (1)
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    # sql = """DELETE FROM token_register WHERE token = %s ;"""
                    # cursor.execute(sql,(dataInput['token']))
                    # conn.commit()
                    # cursor.close()
                    # conn.close()
                    sql = "SELECT * FROM user WHERE username = %s AND status_id != '7' AND status_account='active'"
                    cursor.execute(sql, username)
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result = toJson(data, columns)
                    conn.commit()
                    cursor.close()
                    conn.close()
                if str(result[0]['status_id']) == '4':  # check status is pending
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    status = 1  # Status = Offline

                    # user_id, email, password, firstname, lastname, create_at, privilege_level, job_title, status, last_updated
                    sql = "UPDATE user SET status_id = %s, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status_id != '7' AND status_account='active'"
                    cursor.execute(sql, (status, username))

                    sql = "UPDATE token_register SET status = %s, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status = 'active'"
                    cursor.execute(sql, ('inactive', username))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    # user = { 'firstname': dataInput['firstname'], 'lastname': dataInput['lastname'], 'email': dataInput['email'] }
                    # addPreRoles(user)
                    # addPreGroups(user)
                    # addPreOwnerUser(user)
                    # removeOldPreAddOwner(dataInput['email'])
                    #================================== Generate Secret key ============================================================
                    QRcode = createSecretKeyTwoFactor(username,2)
                    #==============================================================================================
                    if(QRcode != "Error"):
                        if email not in [None]:
                            #sendMailWelcomeForRegister(result[0]['user_id'],email, result[0]['firstname'], result[0]['lastname'],QRcode)
                            logAction(data_user['user_id'],'/AddUserByAdmin', 'User : '+str(result[0]['user_id'])+' has been create success','info')
                        elif email in [None]:
                            logAction(data_user['user_id'],'/AddUserByAdmin', 'User : '+str(result[0]['user_id'])+' has been create without email success','info')
                    return(jsonify({"status": "Success"}))
                else :
                    logAction(data_user['user_id'],'/AddUserByAdmin', 'add new user has not complete','warning')
                    return(jsonify({"status": "Error"}))
            else:
                logAction(data_user['user_id'],'/AddUserByAdmin', 'add new user has not complete','warning')
                return(jsonify({"status": "Error"}))
        else:
            logAction(data_user['user_id'],'/AddUserByAdmin', 'Permission denied','warning')
            return jsonify({"status": "Permission denied"})            
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error"})