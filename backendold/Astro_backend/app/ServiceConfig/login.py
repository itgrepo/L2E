#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ServiceConfig import *
import uuid
import random
import string
import smtplib
import hmac
import hashlib
import requests
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEText import MIMEText

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#import socks

#SERVER = '203.150.212.13'  #DEVEVELOP
# SERVER = '10.252.3.157'   #PRODUCTION
# SERVER = 'outgoing.mail.go.th'  # PRODUCTION (old, unreachable from Docker)
SERVER = os.environ.get('MAIL_SERVER', 'outgoing.workd.go.th')

# LINK = 'http://localhost:8080'  #DEVEVELOP
LINK = os.environ.get('FRONTEND_URL', 'http://10.20.11.91')  #PRODUCTION
# LINK = ''  # PRODUCTION
### User And Password Mail ###
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() == 'true'
username_mail = os.environ.get('MAIL_USERNAME', 'learn2earn@bde.go.th')
password_mail = os.environ.get('MAIL_PASSWORD', 'L2E@Start2026!')
MAIL_FROM = os.environ.get('MAIL_FROM', 'DEX Data Exchange <learn2earn@bde.go.th>')
MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
###############################
#socks.setdefaultproxy(TYPE, ADDR, PORT)
#socks.setdefaultproxy(socks.HTTP, 'proxy.customs.net', 3128)
#socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, 'proxy.customs.net', 3128,False,"920181","zxcvbnm")
#socks.wrapmodule(smtplib)
#socks.create_connection()
# ####################################

def triggerLoginFailureAlert(username, is_invalid_username=False, user_id=0):
    from datetime import datetime
    try:
        ip = request.headers.get('X-FORWARDED-FOR', None)
        ip_addr = ip.split(',')[0].strip() if ip else request.remote_addr
    except Exception:
        ip_addr = request.remote_addr or 'unknown'

    msg_detail = f"ALERT: Unauthorized login attempt for username: {username} from IP: {ip_addr}"
    if is_invalid_username:
        msg_detail += " (Invalid Username)"
    else:
        msg_detail += " (Incorrect Password)"

    # Log warning alert
    logAction(user_id, '/login', msg_detail, 'alert')

    # Optionally attempt to send mail to admin if we can
    try:
        fromaddr = "Department Operation Center Team <adminbd@customs.go.th>"
        toaddr = "adminbd@customs.go.th"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = f"Security Alert: Failed Login Attempt ({username})"
        body = f"""
        <h3>Security Alert: Failed Login Attempt</h3>
        <p>A failed login attempt was detected on the system.</p>
        <ul>
            <li><b>Username:</b> {username}</li>
            <li><b>IP Address:</b> {ip_addr}</li>
            <li><b>Attempt Type:</b> {'Invalid Username' if is_invalid_username else 'Incorrect Password'}</li>
            <li><b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
        </ul>
        """
        msg.attach(MIMEText(body, 'html', "utf-8"))
        server = smtplib.SMTP_SSL(SERVER, 465, timeout=3)
        server.login(username_mail, password_mail)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
    except Exception as e:
        current_app.logger.error(f"Could not send login failure alert email: {e}")

@app.route('/login', methods=['POST'])
def login():
    try:

        dataInput = request.json
        username = dataInput['username']
        password = dataInput['password']
        link = dataInput['link']
        conn = mysql.connect()
        cursor = conn.cursor()
        # sql = """SELECT user_id, username, email, firstname, lastname, national_id, national_id_book, national_id_mode, policy_id,
        #        usage_objective, other_object, status_id, previlage_id, count_login, status_account FROM user WHERE username=%s AND password=%s AND status_account='active'"""
        # M&M DB_1
        sql = """SELECT user.*,DataField.sublevel_id ,sublevel_master.Level_Master_id FROM user
JOIN user_activity ON user.user_id = user_activity.user_id
LEFT JOIN DataField ON user.national_id_book = DataField.national_id_book and user.national_id =  DataField.national_id
LEFT JOIN sublevel_master ON DataField.sublevel_id = sublevel_master.sublevel_id
WHERE user.username = %s AND user_activity.password = %s
and DataField.sublevel_id =   (select max(aa.sublevel_id)  from DataField aa where  user.national_id_book = aa.national_id_book and user.national_id =  aa.national_id and aa.expiration >= CURRENT_DATE  )
and  expiration  >=  CURRENT_DATE and user.user_id = (select Max(bb.user_id) from user bb where bb.username = user.username)"""
        # /M&M DB_1
        cursor.execute(sql, (username, password))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        if len(result) > 0 and "password" in result[0]:
            del result[0]["password"]
        conn.commit()
        cursor.close()
        conn.close()
        #----Get E-mail user by username----#
        conn = mysql.connect()
        cursor = conn.cursor()
        sql_email = "SELECT email FROM user WHERE username=%s AND status_account='active' ORDER BY user_id DESC LIMIT 1"
        cursor.execute(sql_email, (username))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_email = toJson(data, columns)
        if len(result_email) > 0:
            email = result_email[0]['email']
        else:
            email = None
        conn.commit()
        cursor.close()
        conn.close()
        #-----------------------------------#
        conn = mysql.connect()
        cursor = conn.cursor()
        sql_time_ac = "SELECT duration FROM timetable_activity  WHERE activity_desc = 'ForceChangePassword'"
        cursor.execute(sql_time_ac)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_time_activity = toJson(data, columns)
        conn.commit()
        cursor.close()
        conn.close()
        # return jsonify({"status": 'result_email : ' + str(result_email) +' len(result_email) : '+str(len(result_email))})
        #----Check E-mail user by username----# ##!!!??? Check E-mail ??? user ???? ????????? user ????????????????? E-mail ???!!!##
        # if len(result_email) == 0:
        #     cursor.close()
        #     conn.close()
        #     # logAction(result[0]['user_id'], '/login', 'username is incorrect', 'warning')
        #     return jsonify({"status": 'username is incorrect'})
        # else:
        #------------------------------------#
        if len(result) == 0:
            conn = mysql.connect()
            cursor = conn.cursor()
            sql_username = "SELECT count_login, user_id, status_id FROM user WHERE username=%s AND status_account='active' ORDER BY user_id DESC LIMIT 1"
            cursor.execute(sql_username, (username))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result_username = toJson(data, columns)
            conn.commit()
            cursor.close()
            conn.close()
            if len(result_username) == 0:
                logAction(0, '/login', f'Failed login attempt: invalid username "{username}"', 'warning')
                triggerLoginFailureAlert(username, is_invalid_username=True, user_id=0)
                return jsonify({"status": 'username is incorrect'})
            else:
                if str(result_username[0]['status_id']) == '6':
                    return jsonify({"status": 'Please check in your email confirmation for unlock account'})
                
                count_login = result_username[0]['count_login'] + 1
                conn = mysql.connect()
                cursor = conn.cursor()
                if count_login >= 5:
                    sql = "UPDATE user SET count_login = %s, status_id = 6, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status_id != '7' AND status_account='active'"
                    msg = f"Account locked due to 5 failed login attempts for user \"{username}\""
                else:
                    sql = "UPDATE user SET count_login = %s, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status_id != '7' AND status_account='active'"
                    msg = f"Failed login attempt: incorrect password for user \"{username}\" (attempt {count_login})"
                cursor.execute(sql, (count_login, username))
                conn.commit()
                cursor.close()
                conn.close()
                logAction(result_username[0]['user_id'], '/login', msg, 'warning')
                triggerLoginFailureAlert(username, is_invalid_username=False, user_id=result_username[0]['user_id'])
                if count_login >= 5:
                    return jsonify({"status": 'Your account is locked'})
                else:
                    return jsonify({"status": 'not found', "attempts": count_login})
        else:
            if str(result[0]['status_id']) == '3':
                logAction(result[0]['user_id'], '/login', 'Your account is suspended', 'info')
                return jsonify({"status": 'Your account is suspended'})

            elif str(result[0]['status_id']) == '4':
                logAction(result[0]['user_id'], '/login', 'Login blocked: Email verification pending (status 4)', 'info')
                return jsonify({"status": 'Please check in your email confirmation'})

            elif str(result[0]['status_id']) == '5':
                logAction(result[0]['user_id'], '/login', 'You are guest member', 'info')
                return jsonify(
                    {"status": 'You are guest member.\nPlease contact administrator for more information'})

            elif str(result[0]['status_id']) == '6':
                ##--Check Email--##
                if check_email_format(email):
                    #-Have E-mail-#
                    # logAction(result[0]['user_id'], '/login','Please check in your email confirmation for unlock account', 'info')
                    return jsonify({"status": 'Please check in your email confirmation for unlock account'})
                else:
                    #-Not have E-mail-#
                    # logAction(result[0]['user_id'], '/login','Please contact Administrator for unlock account', 'info')
                    return jsonify({"status": 'Please contact Administrator for unlock account'})
                ##---------------##
            elif str(result[0]['status_id']) == '7':
                # logAction(result[0]['user_id'], '/login','Please contack Tel: +66', 'info')
                return jsonify({"status": 'Please contact Administrator  Tel: +66'})

            elif str(result[0]['status_id']) == '8':
                logAction(result[0]['user_id'], '/login', 'Account pending admin approval', 'info')
                return jsonify({"status": 'pending_approval'})

            # /////////////////////////////////////////////////////////////////////////////////

            conn = mysql.connect()
            cursor = conn.cursor()
            sql = """SELECT * FROM user_activity JOIN user ON user_activity.user_id = user.user_id WHERE user.username = %s AND user_activity.password=%s AND user.status_id != '7'"""
            cursor.execute(sql, (username, password))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result1 = toJson(data, columns)
            if len(result1) == 0:
                return jsonify({"status": 'password is incorrect'})
            user_id = result1[0]['user_id']
            # print(user_id)
            conn.commit()
            cursor.close()
            conn.close()
            # check_policy_id = result[0]['policy_id']
            # check_policy = checkPolicy(check_policy_id)

            # M&M ????1_1
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = """SELECT consent_agreement.version
                        FROM consent_agreement 
                    LEFT JOIN user_agreement 
                        ON user_agreement.consent_agreement_id = consent_agreement.consent_agreement_id 
                    WHERE user_agreement.user_id = %s AND 
                    user_agreement.date_time = (SELECT MAX(date_time) FROM user_agreement WHERE user_id = %s)"""
            # sql = """SELECT version FROM consent_agreement LEFT JOIN user_agreement ON user_agreement.consent_agreement_id = consent_agreement.consent_agreement_id WHERE user_agreement.user_id = %s AND consent_agreement.status = 'active'"""
            cursor.execute(sql, (result1[0]['user_id'],result1[0]['user_id']))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result_version = toJson(data, columns)
            #print(result_version)
            if len(result_version) > 0:
                check_version = result_version[0]['version']
            else:
                check_version = 1 # Default version
            check_policy = checkPolicy(check_version)
            conn.commit()
            cursor.close()
            conn.close()
            # /M&M ????1_1
            if str(result1[0]['login_status']) != '2':
                # /////////////////////////////////////////////////////////////////////////////////
                # print(check_policy)
                # if check_policy == "success":
                # print(user_id)
                # print(result)

                if str(result[0]['previlage_id']) not in ['3', '4']:  # Normal Users
                    result[0]['isAdmin'] = 'false'
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = """UPDATE user SET status_id = 2, count_login = 0, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status_id != '7' AND status_account='active'"""  # Update Status is Online
                    cursor.execute(sql, username)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    logAction(result[0]['user_id'], '/login','login success', 'info')

                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = """UPDATE user_activity SET login_respond = UNIX_TIMESTAMP(),login_status = 1 WHERE user_id = %s"""
                    cursor.execute(sql, user_id)
                    conn.commit()
                    cursor.close()
                    conn.close()

                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = """SELECT login_respond,create_date ,status_account FROM user_activity WHERE user_id = %s"""
                    cursor.execute(sql, user_id)
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result2 = toJson(data, columns)
                    cursor.close()
                    conn.close()
                    if len(result2) > 0 and len(result_time_activity) > 0:
                        if int(result2[0]['login_respond']) - int(result2[0]['create_date']) >= result_time_activity[0]['duration']:  # 7776000
                            return jsonify({"status": "change password", "data": result[0]})
                        else:
                            # M&M ??1_3
                            if check_policy == "success":
                                return jsonify({"status": "success", "data": result[0]})
                            else:
                                logAction(result[0]['user_id'],
                                          '/login', 'policy is update', 'info')
                                return jsonify({"status": "policy is update", "data": result[0]})
                    else:
                         return jsonify({"status": "success", "data": result[0]})
                else:  # Admin or Root
                    result[0]['isAdmin'] = 'true'
                    # print(user_id)
                    # M&M ????1_2
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = """UPDATE user SET status_id = 2, count_login = 0, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status_id != '7' AND status_account='active'"""  # Update Status is Online
                    cursor.execute(sql, username)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    # /M&M ????1_2
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = """UPDATE user_activity SET status_account = '1', login_respond = UNIX_TIMESTAMP(),login_status = 1 WHERE user_id = %s"""
                    cursor.execute(sql, user_id)
                    conn.commit()
                    cursor.close()
                    conn.close()

                    # print('===UPDATE user_activity')
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = """SELECT login_respond,create_date,status_account FROM user_activity WHERE user_id = %s"""
                    cursor.execute(sql, user_id)
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result2 = toJson(data, columns)
                    # print(result2)
                    conn.commit()
                    cursor.close()
                    conn.close()

                    if len(result2) > 0 and len(result_time_activity) > 0:
                        if int(result2[0]['login_respond']) - int(result2[0]['create_date']) >= result_time_activity[0]['duration']:
                            # print('===change password')
                            logAction(result[0]['user_id'], '/login',
                                      'change password admin', 'info')
                            return jsonify({"status": "change password admin", "data": result[0]})
                        else:
                            # print('===success')
                            logAction(result[0]['user_id'],
                                      '/login', 'user is admin', 'info')
                            return jsonify({"status": "user is admin", "data": result[0], "status2": check_policy})
                    else:
                         return jsonify({"status": "user is admin", "data": result[0], "status2": check_policy})

                        # /M&M ??1_3
            elif str(result1[0]['login_status']) == '2':
                conn = mysql.connect()
                cursor = conn.cursor()
                sql = "UPDATE user_activity SET login_status = %s WHERE user_id = %s"
                cursor.execute(sql, ('1', user_id))
                conn.commit()
                cursor.close()
                conn.close()
                if str(result[0]['previlage_id']) in ['3', '4']:  # Admin or Department Admin
                    result[0]['isAdmin'] = 'true'
                    return jsonify({"status": "user is admin", "data": result[0]})
                else:  # Normal Users
                    result[0]['isAdmin'] = 'false'
                    return jsonify({"status": "success", "data": result[0], "status2": check_policy})
                # return jsonify({"status": "User already to use", "data": result[0]['user_id']})
            # else:
            #     return jsonify({"status": "User already to use", "data": result[0]['user_id']})
    except Exception as e:
        import traceback
        traceback.print_exc()
        # DB_2 /
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT user.user_id FROM user JOIN user_activity ON user.user_id = user_activity.user_id WHERE user.username=%s AND user_activity.password=%s AND user.status_id != '7' AND user.status_account='active'"""
        cursor.execute(sql, (username, password))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_err = toJson(data, columns)
        cursor.close()
        conn.close()
        
        if len(result_err) > 0:
            logAction(result_err[0]['user_id'], '/login', str(e), 'error')
        
        current_app.logger.info(e)
        #---------------#
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e), "Line number": line_number})
        # return jsonify({"status": "Error"})

@app.route('/auth', methods=['POST', 'OPTIONS'])
def auth():
    try:
        dataInput = request.json
        username = dataInput['usr']
        OTP = dataInput['mfa']
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT user_secret_key.secret_key FROM user_secret_key 
        INNER JOIN user ON user_secret_key.user_id = user.user_id WHERE user.username = %s 
        AND user_secret_key.secret_key_status = 'active'"""
        cursor.execute(sql,(username))
        secret_key = cursor.fetchone()
        cursor.close()
        conn.close()
        totp = pyotp.TOTP(secret_key[0])
        totp2 = totp.now()
        otp_verify = totp.verify(OTP)
        if (otp_verify == True):
            # return 'success'
            return jsonify({"status": "Success"})
        else :
            # return 'failure'
            return jsonify({"status": "Error"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e), "Line number": line_number})

def checkPolicy(check_version):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT version FROM consent_agreement WHERE status = 'active' "
    cursor.execute(sql)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    cursor.close()
    conn.close()
    if check_version != result[0]['version']:
        return "policy is update"
    else:
        return "success"

@app.route('/logout', methods=['POST'])
def logout():
    try:
        dataInput = request.json
        #user_id = dataInput['user_id']
        user_id = decode(dataInput['user_id'])
        conn = mysql.connect()
        cursor = conn.cursor()
        # Update Status is Offline
        sql = "UPDATE user SET status_id = 1, create_at = CURRENT_TIMESTAMP WHERE user_id = %s  AND status_id= 2"
        cursor.execute(sql, (user_id))
        conn.commit()
        cursor.close()
        conn.close()

        conn = mysql.connect()
        cursor = conn.cursor()
        # Update Status is Offline
        sql = "UPDATE user_activity SET login_status = 0 WHERE user_id = %s  "
        cursor.execute(sql, (user_id))
        conn.commit()
        cursor.close()
        conn.close()
        logAction(user_id, '/logout', 'log out', 'info')
        return jsonify({"status": "success"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e), "Line number": line_number})
        # return jsonify({"status": "Error"})


@app.route('/forgotPassword', methods=['POST'])
def forgotPassword():
    try:
        dataInput = request.json
        username = dataInput['username']
        #national_id = dataInput['national_id']
        #national_id_book = dataInput['national_id_book']
        #id_mode = dataInput['id_mode']
        link = dataInput['link']

        conn = mysql.connect()
        cursor = conn.cursor()
        #-----------------------------#
        # if id_mode == 1:
        #     sql = "SELECT user_id, username, email, firstname, lastname, status_id FROM user WHERE username = %s AND status_id != '7'"
        #     cursor.execute(sql, (username))
        #     data = cursor.fetchall()
        #     columns = [column[0] for column in cursor.description]
        #     result = toJson(data, columns)
        # elif id_mode == 2:
        #     sql = "SELECT user_id, username, email, firstname, lastname, status_id FROM user WHERE national_id = %s AND status_id != '7'"
        #     cursor.execute(sql, (national_id))
        #     data = cursor.fetchall()
        #     columns = [column[0] for column in cursor.description]
        #     result = toJson(data, columns)
        # elif id_mode == 3:
        #     sql = "SELECT user_id, username, email, firstname, lastname, status_id FROM user WHERE national_id_book = %s AND status_id != '7'"
        #     cursor.execute(sql, (national_id_book))
        #     data = cursor.fetchall()
        #     columns = [column[0] for column in cursor.description]
        #     result = toJson(data, columns)
        #-----------------------------#
        sql = "SELECT user_id, username, email, firstname, lastname, status_id FROM user WHERE username = %s AND status_id != '7'"
        cursor.execute(sql, (username))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        cursor.close()
        conn.close()
        if len(result) == 0:
            return 'not found'
        else:
            if str(result[0]['status_id']) == '3':
                return 'Your account is suspended'
            # elif str(result[0]['status_id']) == '6':
            #     return 'Your account is lock'
            else:
                #--reset count_login---#
                conn = mysql.connect()
                cursor = conn.cursor()
                sql = "UPDATE user SET count_login = 0 , status_id = 1 WHERE username = %s AND status_id != '7'"
                cursor.execute(sql, username)
                conn.commit()
                cursor.close()
                conn.close()
                #---------------------#
                token = (str(uuid.uuid4()) +
                         str(uuid.uuid1())).replace('-', '')
                conn = mysql.connect()
                cursor = conn.cursor()
                sql = "INSERT INTO token_forgotpassword VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
                cursor.execute(
                    sql, (token, username, result[0]['email'], 'active'))
                conn.commit()
                cursor.close()
                conn.close()
                ##--Check Email--##
                if check_email_format(result[0]['email']):
                    #-Have E-mail-#
                    sendMailResetPassword(
                        token, result[0]['email'], link, result[0]['user_id'])
                    logAction(result[0]['user_id'],
                              '/forgotPassword', 'forgot password', 'info')
                    # return 'success'
                    return jsonify({"status": "success"})
                else:  # -Not have E-mail
                    updatePassword(randomStringDigits(), result[0]['user_id'])
                    logAction(result[0]['user_id'], '/forgotPassword',
                              'forgot password (not have email)', 'info')
                    # return 'success (not have email)'
                    return jsonify({"status": "success (not have email)"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e), "Line number": line_number})
        # return jsonify({"status": "Error"})

# @app.route('/testSendMail', methods=['GET'])


def sendMailResetPassword(token, email, link, user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT firstname, lastname FROM user WHERE email=%s AND status_id != '7'"
    cursor.execute(sql, email)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    firstname = result[0]['firstname']
    lastname = result[0]['lastname']
    conn.commit()
    cursor.close()
    conn.close()
    fromaddr = MAIL_FROM
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Data Exchange - Reset Password"
    reset_link = str(link) + "/resetpassword/" + str(token)
    footer = "<br><br><br>Data Exchange Team<br>Email: " + username_mail
    body = """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #1e293b;">Reset Password</h2>
        <p>Hi {firstname} {lastname},</p>
        <p>คุณได้ส่งคำขอรีเซ็ตรหัสผ่านเข้ามาในระบบ กรุณาคลิกปุ่มด้านล่างเพื่อตั้งรหัสผ่านใหม่:</p>
        <a href="{link}" style="display: inline-block; padding: 14px 28px; margin: 20px 0; background-color: #db2777; color: #ffffff; border-radius: 8px; text-decoration: none; font-weight: bold;">ตั้งรหัสผ่านใหม่</a>
        <p style="color: #64748b; font-size: 0.875rem;">หากคุณไม่ได้ร้องขอ สามารถเพิกเฉยอีเมลนี้ได้ ลิงก์จะหมดอายุโดยอัตโนมัติ</p>
        {footer}
    </div>""".format(firstname=firstname, lastname=lastname, link=reset_link, footer=footer)
    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(SERVER, MAIL_PORT, timeout=10)
        else:
            server = smtplib.SMTP(SERVER, MAIL_PORT, timeout=10)
        if username_mail and password_mail:
            server.login(username_mail, password_mail)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return "success"
    except Exception as e:
        print(f"SMTP Error: {e}")
        return "error"


@app.route('/verifyResetToken', methods=['POST'])
def verifyResetToken():
    try:
        dataInput = request.json
        token = dataInput.get('token')
        if not token:
            return jsonify({"status": "invalid"})

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT username, email FROM token_forgotpassword WHERE token = %s AND status = 'active'"
        cursor.execute(sql, (token,))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        cursor.close()
        conn.close()

        if len(result) == 0:
            return jsonify({"status": "invalid"})
        return jsonify({"status": "valid", "username": result[0]['username']})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})


@app.route('/resetPasswordByToken', methods=['POST'])
def resetPasswordByToken():
    try:
        dataInput = request.json
        token = dataInput.get('token')
        new_password = dataInput.get('password')

        if not token or not new_password:
            return jsonify({"status": "Missing token or password"})

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT username, email FROM token_forgotpassword WHERE token = %s AND status = 'active'"
        cursor.execute(sql, (token,))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)

        if len(result) == 0:
            cursor.close()
            conn.close()
            return jsonify({"status": "invalid_token"})

        username = result[0]['username']

        # Get user_id
        sql_user = "SELECT user_id FROM user WHERE username = %s AND status_account = 'active' ORDER BY user_id DESC LIMIT 1"
        cursor.execute(sql_user, (username,))
        user_data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        user_result = toJson(user_data, columns)

        if len(user_result) == 0:
            cursor.close()
            conn.close()
            return jsonify({"status": "user_not_found"})

        user_id = user_result[0]['user_id']

        # Update password without hashing (matching system's plaintext storage)
        sql_update_pass = "UPDATE user_activity SET create_date = UNIX_TIMESTAMP(), password = %s , emailnews = %s WHERE user_id = %s"
        cursor.execute(sql_update_pass, (new_password, "-", user_id))
        
        # Update user password history using the correct column 'password_rank'
        sql_max = "SELECT MAX(password_rank) FROM user_password_history WHERE user_id = %s "
        cursor.execute(sql_max, user_id)
        data_max = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_max = toJson(data_max, columns)
        max_seq = int(result_max[0]['MAX(password_rank)']) if result_max[0]['MAX(password_rank)'] is not None else 0
        
        sql_history = "INSERT INTO user_password_history VALUES(NULL, %s,%s,%s,UNIX_TIMESTAMP())"
        cursor.execute(sql_history, (user_id, max_seq + 1, new_password))

        # Mark token as used
        sql_update = "UPDATE token_forgotpassword SET status = 'used' WHERE token = %s"
        cursor.execute(sql_update, (token,))
        conn.commit()
        cursor.close()
        conn.close()

        logAction(user_id, '/resetPasswordByToken', 'Password reset via token', 'info')
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "Error: " + str(e)})


def randomStringDigits(stringLength=8):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


def updatePassword(password, user_id):
    key = 'e9NHdT3GU6wBdWlw3RTqvrShGzyerRl4BaMhFeUI3v4j6U0opW5a19HQHDAHHCrhYXq8oG6D'.encode(
        "utf-8")
    msg = password.encode("utf-8")
    passwordEncrypt = hmac.new(key, msg, hashlib.sha256).hexdigest()
    # conn = mysql.connect()
    # cursor = conn.cursor()
    # sql = "UPDATE user SET password = %s, create_at = CURRENT_TIMESTAMP WHERE user_id = %s"
    # cursor.execute(sql, (passwordEncrypt, user_id))
    # conn.commit()
    # cursor.close()

    conn = mysql.connect()
    cursor = conn.cursor()
    # DB_4 /
    sql = "UPDATE user_activity SET create_date = UNIX_TIMESTAMP(), password = %s,emailnews = %s WHERE user_id = %s"
    cursor.execute(sql, (passwordEncrypt, password, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return 'success'


@app.route('/resetPassword', methods=['POST'])
def resetPassword():
    try:
        dataInput = request.json
        # username = dataInput['username']
        password = dataInput['password']
        currentPassword = dataInput['currentPassword']
        #cpassword = dataInput['cpassword']
        user_id = decode(dataInput['user_id'])
        # conn = mysql.connect()
        # cursor = conn.cursor()
        # sql = "SELECT username, email FROM token_forgotpassword WHERE token = %s"
        # cursor.execute(sql,(token))
        # data = cursor.fetchall()
        # columns = [column[0] for column in cursor.description]
        # result = toJson(data,columns)
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT user.user_id, user_activity.password, email, firstname, lastname FROM user JOIN user_activity ON user.user_id = user_activity.user_id WHERE user.user_id = %s"
        cursor.execute(sql, user_id)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        # M&M ????1_5
        sql_pass = "SELECT password FROM (SELECT history_id , password FROM user_password_history WHERE user_id = %s ORDER BY history_id DESC LIMIT 3) AS new WHERE password = %s "
        cursor.execute(sql_pass, (user_id, password))
        data_pass = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_pass = toJson(data_pass, columns)
        sql_max = "SELECT MAX(history_id) FROM user_password_history WHERE user_id = %s "
        cursor.execute(sql_max, user_id)
        data_max = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_max = toJson(data_max, columns)
        cursor.close()
        conn.close()
        # /M&M ????1_5
        # return jsonify({"status": str(result_pass)})
        if currentPassword == result[0]['password']:
            # if str(result_pass) == '[]':
            if len(result_pass) == 0:
                # conn = mysql.connect()
                # cursor = conn.cursor()
                # sql = "UPDATE user SET password = %s, create_at = CURRENT_TIMESTAMP WHERE user_id = %s AND status_account = 'active'"
                # cursor.execute(sql, (password, user_id))
                # conn.commit()
                # cursor.close()

                conn = mysql.connect()
                cursor = conn.cursor()
                # DB_5 /
                sql = "UPDATE user_activity SET create_date = UNIX_TIMESTAMP(), password = %s , emailnews = %s   WHERE user_id = %s"
                cursor.execute(sql, (password, '-', user_id))
                conn.commit()
                cursor.close()
                conn.close()
                # logAction(result[0]['user_id'], '/resetPassword', 'resetPassword success', 'info')
                sendMailResetPasswordSuccess(result[0]['email'])
                # M&M ????1_6
                conn = mysql.connect()
                cursor = conn.cursor()
                max_seq = int(result_max[0]['MAX(password_rank)']) if result_max[0]['MAX(password_rank)'] is not None else 0
                sql = "INSERT INTO user_password_history VALUES(NULL, %s,%s,%s,UNIX_TIMESTAMP())"
                cursor.execute(
                    sql, (user_id, max_seq + 1, password))
                conn.commit()
                cursor.close()
                conn.close()
                # /M&M ????1_6
                return jsonify({"status": "success"})
            else:
                return jsonify({"status": "same password"})
        else:
            return jsonify({"status": str(result[0]['password'])})

    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"status": "Error: " + str(e)})


@app.route('/changePassword', methods=['POST'])
def changePassword():
    return jsonify({"status": "error", "message": "Direct password change is disabled. Please use email reset link."})
    
    try:
        dataInput = request.json
        # username = dataInput['username']
        password = dataInput['password']
        currentPassword = dataInput['currentPassword']
        #cpassword = dataInput['cpassword']
        user_id = decode(dataInput['user_id'])
        # conn = mysql.connect()
        # cursor = conn.cursor()
        # sql = "SELECT username, email FROM token_forgotpassword WHERE token = %s"
        # cursor.execute(sql,(token))
        # data = cursor.fetchall()
        # columns = [column[0] for column in cursor.description]
        # result = toJson(data,columns)
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT user.user_id, user_activity.password, email, firstname, lastname FROM user JOIN user_activity ON user.user_id = user_activity.user_id WHERE user.user_id = %s"
        cursor.execute(sql, user_id)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        # M&M ????1_5
        sql_pass = "SELECT password FROM (SELECT history_id , password FROM user_password_history WHERE user_id = %s ORDER BY history_id DESC LIMIT 3) AS new WHERE password = %s "
        cursor.execute(sql_pass, (user_id, password))
        data_pass = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_pass = toJson(data_pass, columns)
        sql_max = "SELECT MAX(password_rank) as max_rank FROM user_password_history WHERE user_id = %s "
        cursor.execute(sql_max, user_id)
        data_max = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_max = toJson(data_max, columns)
        # /M&M ????1_5
        # return jsonify({"status": str(result_pass)})
        cursor.close()
        conn.close()
        if currentPassword == result[0]['password']:
            # if str(result_pass) == '[]':
            if len(result_pass) == 0:
                # conn = mysql.connect()
                # cursor = conn.cursor()
                # sql = "UPDATE user SET password = %s, create_at = CURRENT_TIMESTAMP WHERE user_id = %s AND status_account = 'active'"
                # cursor.execute(sql, (password, user_id))
                # conn.commit()
                # cursor.close()

                conn = mysql.connect()
                cursor = conn.cursor()
                # DB_5 /
                sql = "UPDATE user_activity SET create_date = UNIX_TIMESTAMP(), password = %s , emailnews = %s   WHERE user_id = %s"
                cursor.execute(sql, (password, "-", user_id))
                conn.commit()
                cursor.close()
                conn.close()
                logAction(result[0]['user_id'], '/resetPassword',
                          'resetPassword success', 'info')
                sendMailEditPassword(
                    result[0]['email'], result[0]['firstname'], result[0]['lastname'])
                # M&M ????1_6
                conn = mysql.connect()
                cursor = conn.cursor()
                
                max_seq = int(result_max[0]['max_rank']) if result_max[0]['max_rank'] is not None else 0
                
                sql = "INSERT INTO user_password_history VALUES(NULL, %s,%s,%s,UNIX_TIMESTAMP())"
                cursor.execute(
                    sql, (user_id, max_seq + 1, password))
                conn.commit()
                cursor.close()
                conn.close()
                # /M&M ????1_6
                return jsonify({"status": "success"})
            else:
                return jsonify({"status": "same password"})
        else:
            return jsonify({"status": str(currentPassword)})

    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"status": "Error"})


def sendMailEditPassword(dataInput, firstname, lastname):
    # token, email, link
    link = LINK
    # token = 'klsakdfjlksdjflkj'
    # email = 'sirawit14@gmail.com'
    fromaddr = MAIL_FROM
    toaddr = dataInput
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Edit your profile for Department Operation Center"
    footer = "<br><br><br>Department Operation Center" + \
        "<br>Call Center: +66" + "<br>Email: adminbd@customs.go.th"
    body = "<p style='font-size: 14px'>Hi&nbsp;&nbsp;" + firstname + "&nbsp;" + lastname + \
        "<br>Your member profile was changed on the Department Operation Center account.<br>If this was your action, then you can safely ignore this email.<br>If this was not yours, a malicious user may have your password.Please review your profile at  <br>and change your password.If you need any help, please contact Contact Center at /contactcenter Tel: +66.</p>" + footer

    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        server = smtplib.SMTP_SSL(SERVER, 465)
        text = msg.as_string()
        ##Login Mail server##
        server.login(username_mail, password_mail)
        #-------------------#
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return 'success'
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"status": "Error: " + str(e)})


def sendMailResetPasswordSuccess(email):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT firstname, lastname FROM user WHERE email=%s AND status_id != '7'"
    cursor.execute(sql, email)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    firstname = result[0]['firstname']
    lastname = result[0]['lastname']
    conn.commit()
    cursor.close()
    conn.close()
    #print(email)
    fromaddr = MAIL_FROM
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Reset Password Department Operation Center Successful"
    footer = "<br><br><br>Department Operation Center Team" + \
        "<br>Call Center: +662 009 9999" + "<br>Email: adminbd@customs.go.th"
    # body = "<br/><p style='text-indent:40px;padding-right:40px;font-size: 14px;'>Reset password Department Operation Center is successful, <br>You can log in with your Email and your new password." + footer
    body = "<p style='font-size: 14px;'>Hi&nbsp;&nbsp;" + firstname + "&nbsp;" + lastname + \
        "<br>You are successfully unlock your account at Department Operation Center. <br>You can log-in with your Username and Password to explore. " + footer
    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(SERVER, MAIL_PORT, timeout=10)
        else:
            server = smtplib.SMTP(SERVER, MAIL_PORT, timeout=10)
        text = msg.as_string()
        ##Login Mail server##
        if username_mail and password_mail:
            server.login(username_mail, password_mail)
        #-------------------#
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return "success"
    except Exception as e:
        current_app.logger.info(e)
        return "error"
        # return jsonify({"status": "Error: " + str(e)})


def sendMailUnlockAccountSuccess(email):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT firstname, lastname FROM user WHERE email=%s AND status_id != '7'"
    cursor.execute(sql, email)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    firstname = result[0]['firstname']
    lastname = result[0]['lastname']
    conn.commit()
    cursor.close()
    conn.close()
    fromaddr = MAIL_FROM
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Reset Password Department Operation Center Successful"
    footer = "<br><br><br>Department Operation Center Team" + \
        "<br>Call Center: +66" + "<br>Email: adminbd@customs.go.th"
    # body = "<br/><p style='text-indent:40px;padding-right:40px;font-size: 14px;'>Unlock account Department Operation Center is successful, <br>You can log in with your Account." + footer
    body = "<p style=font-size: 14px;'>Hi&nbsp;&nbsp;" + firstname + "&nbsp;" + lastname + \
        "<br>Unlock account Department Operation Center is successful, <br>You can log in with your Account." + footer
    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        server = smtplib.SMTP_SSL(SERVER, 465)
        text = msg.as_string()
        ##Login Mail server##
        server.login(username_mail, password_mail)
        #-------------------#
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return "success"
    except Exception as e:
        current_app.logger.info(e)
        return "error"
        # return jsonify({"status": "Error: " + str(e)})


@app.route('/validateEmail', methods=['POST'])
def validateEmail():
    # expect {email, firstname, lastname}
    dataInput = request.json

    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT firstname, lastname FROM user WHERE email=%s AND status_id != '7'"
    cursor.execute(sql, (dataInput['email']))
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    conn.commit()
    cursor.close()
    conn.close()

    if len(result) != 0:
        if (dataInput['firstname'] == result[0]['firstname'] and dataInput['lastname'] == result[0]['lastname']):
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "not found"})
    else:
        return jsonify({"status": "not found"})


def sendMailUnlockAccount(token, email, link, username, user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT firstname, lastname FROM user WHERE email=%s AND status_id != '7'"
    cursor.execute(sql, email)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    firstname = result[0]['firstname']
    lastname = result[0]['lastname']
    conn.commit()
    cursor.close()
    conn.close()
    fromaddr = "Department Operation Center Team <adminbd@customs.go.th>"
    toaddr = email
    random = randomStringDigits()
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Unlock Account for Department Operation Center Team"
    link = str(link) + "/unlock/" + str(token)
    footer = "<br><br><br>Department Operation Center Team" + \
      "<br>Call Center: +66" + "<br>Email: adminbd@customs.go.th"
    # body = "<br/>Username: " + username + "<br/>Password: " + random + "<br/><p onClick='" + updatePassword(random, user_id) + "' style='text-indent:40px;padding-left:40px;padding-right:40px;font-size: 14px;width: 410px; margin-right: auto; margin-left: auto;'>You login fail more than five time on Department Operation Center Team<br> Before we get started, we just need to confirm that this is you.<br>Click below to unlock your account</p> <a href='" + str(link) + "' style='margin: 0 auto;display: block;width: 160px;height: 60px;margin-top: 30px;background-color: #19b5fe;text-align: center;line-height: 60px;color: #ffffff;border-radius: 4px;text-decoration: none;'>Unlock Account</a>" + footer
    body = "<p onClick='" + updatePassword(random, user_id) + "' style='font-size: 14px;'>Hi&nbsp;&nbsp;" + firstname + "&nbsp;" + lastname + "<br>Your account has been locked after five consecutive failed password attempts.<br>Please click \"" + "Unlock Account" + "\" button below and use the temporary password to access the Department Operation Center<br>Then we recommend you change the password right away to future security purpose.</p><br/><b>Password: </b>" + str(
        random) + " <a href='" + str(link) + "' style='display: block;width: 160px;height: 60px;margin-top: 30px;background-color: #19b5fe;text-align: center;line-height: 60px;color: #ffffff;border-radius: 4px;text-decoration: none;'>Unlock Account</a>" + footer
    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        server = smtplib.SMTP_SSL(SERVER, 465)
        text = msg.as_string()
        ##Login Mail server##
        server.login(username_mail, password_mail)
        #-------------------#
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return "success"
    except Exception as e:
        current_app.logger.info(e)
        return "error"
        # return jsonify({"status": "Error: " + str(e)})


@app.route('/unlockAccount', methods=['POST'])
def unlockAccount():
    dataInput = request.json
    username = dataInput['username']
    email = dataInput['email']

    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT * FROM user WHERE username = %s AND status_id != '7' AND status_account='active'"
    cursor.execute(sql, username)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    conn.commit()
    cursor.close()
    conn.close()

    if len(result) == 0:
        return 'Username not found.'

    if str(result[0]['status_id']) == '6':  # check status is Lock
        conn = mysql.connect()
        cursor = conn.cursor()
        status = 1  # Status = Offline

        # user_id, email, password, firstname, lastname, create_at, privilege_level, job_title, status, last_updated
        sql = "UPDATE user SET status_id = %s, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status_id != '7' AND status_account='active'"
        cursor.execute(sql, (status, username))

        sql = "UPDATE token_unlock_account SET status = %s, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status = 'active'"
        cursor.execute(sql, ('inactive', username))
        conn.commit()
        cursor.close()
        conn.close()
        # sendMailUnlockAccountSuccess(email)
        logAction(result[0]['user_id'], '/unlockAccount',
                  'unlock account success', 'info')
        return 'success'
    else:
        return 'Your Username is duplicated.'


@app.route('/getEmailFromTokenUnlockAccount', methods=['POST'])
def getEmailFromTokenUnlockAccount():
    dataInput = request.json
    conn = mysql.connect()
    cursor = conn.cursor()
    sql = "SELECT username, email FROM token_unlock_account WHERE token = %s"
    cursor.execute(sql, (dataInput['token']))
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = toJson(data, columns)
    conn.commit()
    cursor.close()
    conn.close()
    if len(data) == 0:
        return jsonify({'status': 'not found'})

    return jsonify({'status': 'found', 'email': result[0]['email'], 'username': result[0]['username']})


@app.route('/sendDataSuggestion', methods=['POST'])
def sendDataSuggestion():
    dataInput = request.json
    username = dataInput['username']  # user name
    category_id = dataInput['category_id']
    data_suggestion = dataInput['data_ suggestion']  # body mail
    # return str(data_suggestion)+" "+ str(category_id) + " " + str(username)+""
    sendMailToAdmin(data_suggestion, category_id, username)

    conn = mysql.connect()
    cursor = conn.cursor()

    sql_get = "SELECT user_id FROM user WHERE username = %s AND status_id != '7'"
    cursor.execute(sql_get, (username))
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result_user_id = toJson(data, columns)

    sql = "INSERT INTO user_data_suggestion VALUES (NULL, %s, %s, %s, CURRENT_TIMESTAMP) "
    cursor.execute(
        sql, (result_user_id[0]['user_id'], category_id, data_suggestion))
    conn.commit()
    cursor.close()
    conn.close()

    return 'success'


# M&M ????1_9
@app.route('/confrimPassword', methods=['POST'])
def confrimPassword():
    dataInput = request.json
    user_id = decode(dataInput['user_id'])
    password = dataInput['password']
    conn = mysql.connect()
    cursor = conn.cursor()
    # DB_6 /
    sql = """SELECT user_id , password FROM user JOIN user_activity ON user.user_id = user_activity.user_id WHERE user.user_id = %s AND user_activity.password = %s """
    cursor.execute(sql, (user_id, password))
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result_pass = toJson(data, columns)
    conn.commit()
    cursor.close()
    conn.close()
    if len(result_pass) == 0:
        return jsonify({"status": 'password is wrong'})
    else:
        return jsonify({"status": 'password is correct'})