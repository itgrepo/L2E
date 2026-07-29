#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ServiceConfig import *
import uuid
import os
import smtplib
import json
from ServiceConfig.notification_util import notify_user
import base64
import time

def platform_decode(data):
    if not data:
        return data
    if isinstance(data, str) and data.strip().startswith('{'):
        return data
    try:
        padded_data = data
        missing_padding = len(padded_data) % 4
        if missing_padding:
            padded_data += '=' * (4 - missing_padding)
        return base64.b64decode(padded_data).decode('utf-8')
    except:
        try:
            return decode(data).decode('utf-8')
        except:
            return data

# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEText import MIMEText

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#import socks

# SMTP Configuration (Configurable via Environment Variables)
SERVER = os.environ.get('MAIL_SERVER', 'outgoing.mail.go.th')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
username_mail = os.environ.get('MAIL_USERNAME', 'adminbd@customs.go.th')
password_mail = os.environ.get('MAIL_PASSWORD', 'P@ssw0rd')
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() == 'true'
MAIL_FROM = os.environ.get('MAIL_FROM', "Department Operation Center <adminbd@customs.go.th>")

LINK = os.environ.get('FRONTEND_URL', 'http://110.78.210.128:3001')
LINK_V = '10.20.11.91/api' # Internal API link
###############################
#os.environ['http_proxy'] = "http://920181:zxcvbnm@proxy.customs.net:3128"
#os.environ['https_proxy'] = "http://920181:zxcvbnm@proxy.customs.net:3128"
#s = socks.socksocket()
#socks.setdefaultproxy(TYPE, ADDR, PORT)
#socks.setdefaultproxy(socks.HTTP, 'proxy.customs.net', 3128)
#socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, 'proxy.customs.net', 3128,False,"920181","zxcvbnm")
#socks.wrapmodule(smtplib)
#socks.create_connection()
####################################




def sendMailConfirmRegister(id, token, email, link, firstname, lastname):
    fromaddr = "Department Operation Center <adminbd@customs.go.th>"
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Verify Email Address for Department Operation Center"
    link = str(link) + "/verify/" + str(token)
    footer = "<br><br><br>Department Operation Center" + "<br>Call Center: +66 " + "<br>Email: adminbd@customs.go.th"
    body = "<p style='font-size: 14px;width: 550px;'>Hi&nbsp;&nbsp;" + firstname + "&nbsp;" + lastname + "<br>Thank you for signing up with Department Operation Center.<br> Please click the \"Verify Email\" button below to verify your email address.</p> <a href='" + str(
        link) + "' style='margin: 0 auto;display: block;width: 160px;height: 60px;margin-top: 30px;background-color: #19b5fe;text-align: center;line-height: 60px;color: #ffffff;border-radius: 4px;text-decoration: none;'>Verify Email</a>" + footer

    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(SERVER, MAIL_PORT, timeout=5)
        else:
            server = smtplib.SMTP(SERVER, MAIL_PORT, timeout=5)
        
        if username_mail and password_mail:
            server.login(username_mail, password_mail)
        #-------------------#
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return "success"
    except Exception as e:
        current_app.logger.warning(f"SMTP Error: {e}")
        return "error"


def sendMailWelcomeForRegister(id,email, firstname, lastname,QRstr):
    # email = ''

    fromaddr = "Department Operation Center <adminbd@customs.go.th>"
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Welcome to bigdataPlatform"
    footer = "<br><br><br>Department Operation Center Team" + "<br>Call Center: +66" + "<br>Email: adminbd@customs.go.th"
    body = "<p style='font-size: 14px;'>Hi&nbsp;&nbsp;" + firstname + "&nbsp;" + lastname + "<br>Welcome to BigdataPlatform.<br>Please log-in with your Username and Password to explore our data hub at " +"<br><br>Please use this QRCode with : Putty,Microsoft Authentication,Google Authenticator to get OTP and use them for process 2factor authentication in <br><br><br><img id=barcode src=https://api.qrserver.com/v1/create-qr-code/?data="+ QRstr +"&amp;size=200x200 width='200' height='200' />" + footer#ใส่ domain

    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(SERVER, MAIL_PORT, timeout=5)
        else:
            server = smtplib.SMTP(SERVER, MAIL_PORT, timeout=5)
        
        if username_mail and password_mail:
            server.login(username_mail, password_mail)
        #-------------------#
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return "success"
    except Exception as e:
        current_app.logger.warning(f"SMTP Error in Welcome Mail: {e}")
        return "error"
        server.login(username_mail,password_mail)
        #-------------------#
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        logAction(id, 'sendMailWelcomeForRegister', 'send mail welcome is success', 'info')
        return "success"
    except Exception as e:
        current_app.logger.info(e)
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})


@app.route('/resendEmailConfirmation', methods=['POST'])
def resendEmailConfirmation():
    try:
        dataInput = request.json
        email = dataInput['dataresend']['email']
        user_id = dataInput['dataresend']['user_id']
        link = dataInput['link']
        username = dataInput['dataresend']['username']
        firstname = dataInput['dataresend']['firstname']
        lastname = dataInput['dataresend']['lastname']
        token = (str(uuid.uuid4()) + str(uuid.uuid1())).replace('-', '')
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "INSERT INTO token_register VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
        cursor.execute(sql, (token, username, email, 'active'))
        conn.commit()
        cursor.close()
        conn.close()
        logAction(user_id, '/resendEmailConfirmation', 'send email comfirm success', 'info')
        sendMailConfirmRegister(user_id, token, email, link, firstname, lastname)
        return 'success'
    except Exception as e:
        current_app.logger.info(e)
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})


# @app.route('/firstStepRegister', methods=['POST'])
# def firstStepRegister():
#     try:
#         dataInput = request.json
#         username = dataInput['username']
#         password = dataInput['password']
#         firstname = dataInput['firstname']
#         lastname = dataInput['lastname']
#         national_id = dataInput['national_id']
#         national_id_book = dataInput['national_id_book'].upper()
#         national_id_mode = dataInput['national_id_mode']
#         # policy_id = dataInput['policy_id']
#         usage_objective = dataInput['usage_objective']
#         other_object = dataInput['other_object']
#         email = dataInput['email']
#         link = dataInput['link']

#         conn = mysql.connect()
#         cursor = conn.cursor()
#         sql = "SELECT * FROM user WHERE (username = %s AND status_id != '7') OR (national_id = %s AND national_id_book = %s AND status_id != '7' ) OR (email = %s AND status_id != '7') AND status_account = 'active'"
#         cursor.execute(sql, (username, national_id, national_id_book, email))
#         data = cursor.fetchall()
#         columns = [column[0] for column in cursor.description]
#         result = toJson(data, columns)
#         conn.close()
#         # current_app.logger.info(len(data))
#         if len(data):
#             if result[0]['username'] == username:
#                 # return 'Username is duplicate'
#                 return jsonify({'status': 'Username is duplicate'})
#             elif result[0]['email'] == email:
#                 # return 'email is duplicate'
#                 return jsonify({'status': 'email is duplicate'})
#             elif result[0]['national_id'] == national_id and national_id_mode == 1:
#                 # return 'National ID is duplicate'
#                 return jsonify({'status': 'National ID is duplicate'})
#             elif result[0]['national_id_book'] == national_id_book and national_id_mode == 2:
#                 # return 'Passport is duplicate'
#                 return jsonify({'status': 'Passport is duplicate'})

#         if len(data) != 0:
#             if str(result[0]['status_id']) == '4':
#                 # return 'Please check in your email confirmation'
#                 return jsonify({'status': 'Please check in your email confirmation'})
#         # return jsonify({'data': dataInput, 'status': 'success'})
#     except Exception as e:
#         current_app.logger.info(e)
#         # return "Error: " + str(e)
#         # return "Error"
#         return jsonify({'status': 'Error'})

@app.route('/firstStepRegister', methods=['POST'])
def firstStepRegister():
    try:
        dataInput = request.json
        username = dataInput['username']
        password = dataInput['password']
        firstname = dataInput['firstname']
        lastname = dataInput['lastname']
        national_id = dataInput['national_id']
        national_id_book = dataInput['national_id_book'].upper()
        national_id_mode = dataInput['national_id_mode']
        # policy_id = dataInput['policy_id']
        usage_objective = dataInput['usage_objective']
        other_object = dataInput['other_object']
        email = dataInput['email']
        link = dataInput['link']

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
                # return 'Username is duplicate'
                return jsonify({'status': 'Username is duplicate'})
            elif result[0]['email'] == email:
                # return 'email is duplicate'
                return jsonify({'status': 'email is duplicate'})
            elif result[0]['national_id'] == national_id and national_id_mode == 1:
                # return 'National ID is duplicate'
                return jsonify({'status': 'National ID is duplicate'})
            elif result[0]['national_id_book'] == national_id_book and national_id_mode == 2:
                # return 'Passport is duplicate'
                return jsonify({'status': 'Passport is duplicate'})

        if len(data) != 0:
            if str(result[0]['status_id']) == '4':
                # return 'Please check in your email confirmation'
                return jsonify({'status': 'Please check in your email confirmation'})
        elif len(data) == 0:
            token = (str(uuid.uuid4()) + str(uuid.uuid1())).replace('-', '')
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "INSERT INTO token_register VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
            cursor.execute(sql, (token, username, email, 'active'))
            conn.commit()
            cursor.close()
            conn.close()
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "SELECT MAX(policy_id) FROM codename_policy "
            cursor.execute(sql)
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            resultCheckPolicy = toJson(data, columns)
            cursor.close()
            conn.close()
            default_level = 3  # user level
            status = 4  # Status = Pending
            status_account = "active"
            count_login = 0
            policy_id = resultCheckPolicy[0]['MAX(policy_id)']  # policy_id is present

            conn = mysql.connect()
            cursor = conn.cursor()
            # user_id, username, password, email, firstname, lastname, national_id, national_id_book, national_id_mode, policy_id, usage_objective, other_object, create_at, privilege_id, count_login, status_id, status_account, last_updated
            # sql = "INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
            # cursor.execute(sql, (
            # username, password, email, firstname, lastname, national_id, national_id_book, national_id_mode, policy_id,
            # usage_objective, other_object, default_level, count_login, status, status_account))
            # conn.commit()
            # cursor.close()

            # M&M DB_1

            sql = "INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s,'off')" # off -> 2FA status off  
            cursor.execute(sql, (username, email, firstname, lastname, national_id, national_id_book, national_id_mode, policy_id,usage_objective, other_object, default_level, count_login, status, status_account,1))
            conn.commit()
            cursor.close()
            conn.close()
            #/M&M DB_1
            id = cursor.lastrowid
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "INSERT INTO user_activity(user_id,login_status,login_respond,create_date,status_account,password,emailnews) VALUES(%s,%s,UNIX_TIMESTAMP(),UNIX_TIMESTAMP(),%s,%s,'-')"
            value = (id, '0', '0',password)
            cursor.execute(sql, value)
            conn.commit()
            cursor.close()
            conn.close()
            # M&M ?????1_1
            conn = mysql.connect()
            cursor = conn.cursor()
            sql_pass = """INSERT INTO user_password_history VALUES(NULL, %s,%s,%s,UNIX_TIMESTAMP())"""
            cursor.execute(sql_pass, (id, '1', password))

            if national_id:
                sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,'9999-01-01')"""
                cursor.execute(sql_data, (national_id,'', 1.1))
                sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,'9999-01-01')"""
                cursor.execute(sql_data, (national_id,'', 1.2))
            else:
                sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,'9999-01-01')"""
                cursor.execute(sql_data, ('',national_id_book, 1.1))
                sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,'9999-01-01')"""
                cursor.execute(sql_data, ('',national_id_book, 1.2))
            # sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,CURRENT_DATE())"""
            # cursor.execute(sql_data, (national_id, national_id_book,1.1))
            conn.commit()
            cursor.close()
            conn.close()
            # /M&M ?????1_1
            # M&M ?????1_1 6/8/19 10.27
            conn = mysql.connect()
            cursor = conn.cursor()
            sql_max = "SELECT MAX(version) FROM consent_agreement WHERE status = 'active'"
            cursor.execute(sql_max)
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result_max = toJson(data, columns)
            sql_id = "SELECT consent_agreement_id FROM consent_agreement WHERE status = 'active' AND version = %s"
            cursor.execute(sql_id, (result_max[0]['MAX(version)']))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result_id = toJson(data, columns)

            ip = request.headers.get('X-FORWARDED-FOR',None)

            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "INSERT INTO user_agreement VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())"
            cursor.execute(sql, (ip, id, result_id[0]['consent_agreement_id']))
            # cursor.execute(sql, (request.remote_addr, id, result_id[0]['consent_agreement_id']))
            conn.commit()
            
            sql = "SELECT * FROM user WHERE username = %s AND status_id != '7' AND status_account='active'"
            cursor.execute(sql, username)
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result_authen = toJson(data, columns)
            conn.commit()
            cursor.close()
            conn.close()
            # /M&M ?????1_1 6/8/19 10.27
            #================================== Generate Secret key =======================================
            QRcode = createSecretKeyTwoFactor(username,2)
            #==============================================================================================
            if(QRcode != "Error"):
                sendMailWelcomeForRegister(result_authen[0]['user_id'],email, result_authen[0]['firstname'], result_authen[0]['lastname'],QRcode)
            logAction(id, '/firstStepRegister', 'register success', 'info')
        return jsonify({'status': 'success','data': str(username)})
        # return jsonify({'data': dataInput, 'status': 'success'})
    except Exception as e:
        current_app.logger.info(e)
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})


# @app.route('/afterPolicyRegister', methods=['POST'])
# def afterPolicyRegister():
#     try:
#         dataInput = request.json
#         username = dataInput['username']
#         password = dataInput['password']
#         firstname = dataInput['firstname']
#         lastname = dataInput['lastname']
#         national_id = dataInput['national_id']
#         national_id_book = dataInput['national_id_book'].upper()
#         national_id_mode = dataInput['national_id_mode']
#         # policy_id = dataInput['policy_id']
#         usage_objective = dataInput['usage_objective']
#         other_object = dataInput['other_object']
#         email = dataInput['email']
#         email_news = dataInput['email_news']
#         link = dataInput['link']

#         token = (str(uuid.uuid4()) + str(uuid.uuid1())).replace('-', '')
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         sql = "INSERT INTO token_register VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
#         cursor.execute(sql, (token, username, email, 'active'))
#         conn.commit()
#         cursor.close()
#         conn.close()
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         sql = "SELECT MAX(policy_id) FROM codename_policy "
#         cursor.execute(sql)
#         data = cursor.fetchall()
#         columns = [column[0] for column in cursor.description]
#         resultCheckPolicy = toJson(data, columns)
#         cursor.close()
#         conn.close()
#         default_level = 3  # user level
#         status = 4  # Status = Pending
#         status_account = "active"
#         count_login = 0
#         policy_id = resultCheckPolicy[0]['MAX(policy_id)']  # policy_id is present

#         conn = mysql.connect()
#         cursor = conn.cursor()
#         # user_id, username, password, email, firstname, lastname, national_id, national_id_book, national_id_mode, policy_id, usage_objective, other_object, create_at, privilege_id, count_login, status_id, status_account, last_updated
#         # sql = "INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
#         # cursor.execute(sql, (
#         # username, password, email, firstname, lastname, national_id, national_id_book, national_id_mode, policy_id,
#         # usage_objective, other_object, default_level, count_login, status, status_account))
#         # conn.commit()
#         # cursor.close()

#         # M&M DB_1

#         sql = "INSERT INTO user VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s,'off')" # off -> 2FA status off  
#         cursor.execute(sql, (username, email, firstname, lastname, national_id, national_id_book, national_id_mode, policy_id,usage_objective, other_object, default_level, count_login, status, status_account,email_news))
#         conn.commit()
#         cursor.close()
#         conn.close()
#         #/M&M DB_1
#         id = cursor.lastrowid
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         sql = "INSERT INTO user_activity(user_id,login_status,login_respond,create_date,status_account,password,emailnews) VALUES(%s,%s,UNIX_TIMESTAMP(),UNIX_TIMESTAMP(),%s,%s,%s)"
#         value = (id, '0', '0',password,'-')
#         cursor.execute(sql, value)
#         conn.commit()
#         cursor.close()
#         conn.close()
#         # M&M ?????1_1
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         sql_pass = """INSERT INTO user_password_history VALUES(NULL, %s,%s,%s,UNIX_TIMESTAMP())"""
#         cursor.execute(sql_pass, (id, '1', password))

#         if national_id:
#             sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,'9999-01-01')"""
#             cursor.execute(sql_data, (national_id,'', 1.1))
#             sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,'9999-01-01')"""
#             cursor.execute(sql_data, (national_id,'', 1.2))
#         else:
#             sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,'9999-01-01')"""
#             cursor.execute(sql_data, ('',national_id_book, 1.1))
#             sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,'9999-01-01')"""
#             cursor.execute(sql_data, ('',national_id_book, 1.2))
#         # sql_data = """INSERT INTO DataField VALUES(NULL, %s,%s,%s,CURRENT_DATE())"""
#         # cursor.execute(sql_data, (national_id, national_id_book,1.1))
#         conn.commit()
#         cursor.close()
#         conn.close()
#         # /M&M ?????1_1
# 		# M&M ?????1_1 6/8/19 10.27
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         sql_max = "SELECT MAX(version) FROM consent_agreement WHERE status = 'active'"
#         cursor.execute(sql_max)
#         data = cursor.fetchall()
#         columns = [column[0] for column in cursor.description]
#         result_max = toJson(data, columns)
#         sql_id = "SELECT consent_agreement_id FROM consent_agreement WHERE status = 'active' AND version = %s"
#         cursor.execute(sql_id, (result_max[0]['MAX(version)']))
#         data = cursor.fetchall()
#         columns = [column[0] for column in cursor.description]
#         result_id = toJson(data, columns)

#         ip = request.headers.get('X-FORWARDED-FOR',None)

#         conn = mysql.connect()
#         cursor = conn.cursor()
#         sql = "INSERT INTO user_agreement VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())"
#         cursor.execute(sql, (ip, id, result_id[0]['consent_agreement_id']))
#         # cursor.execute(sql, (request.remote_addr, id, result_id[0]['consent_agreement_id']))
#         conn.commit()
#         cursor.close()
#         conn.close()
#         # /M&M ?????1_1 6/8/19 10.27
#         sendMailConfirmRegister(id, token, email, link, firstname, lastname)
#         logAction(id, '/afterPolicyRegister', 'register success', 'info')
#         return jsonify({'status': 'success','data': str(username)})
#     except Exception as e:
#         logAction(id, '/afterPolicyRegister', str(e), 'error')
#         current_app.logger.info(e)
#         return "Error" 


@app.route('/getEmailFromToken', methods=['POST'])
def getEmailFromToken():
    conn = None
    try:
        dataInput = request.json
        token = dataInput.get('token')
        if not token:
            return jsonify({'status': 'not found', 'message': 'Token is required'})

        conn = mysql.connect()
        cursor = conn.cursor()

        # 1. Look up the token
        sql = "SELECT username, email FROM token_register WHERE token = %s AND status = 'active'"
        cursor.execute(sql, (token,))
        token_data = cursor.fetchall()
        if not token_data:
            cursor.close()
            conn.close()
            return jsonify({'status': 'not found', 'message': 'Token ไม่ถูกต้องหรือถูกใช้ไปแล้ว'})
        
        columns = [column[0] for column in cursor.description]
        token_res = toJson(token_data, columns)[0]
        username = token_res['username']

        # 2. Get user and activity details
        sql_user = """
            SELECT u.user_id, u.username, u.national_id, ua.create_date 
            FROM user u 
            JOIN user_activity ua ON u.user_id = ua.user_id 
            WHERE u.username = %s AND u.status_id != '7'
        """
        cursor.execute(sql_user, (username,))
        user_data = cursor.fetchall()
        if not user_data:
            # If token exists but user doesn't, clean up the ghost token
            cursor.execute("DELETE FROM token_register WHERE token = %s", (token,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'not found', 'message': 'ไม่พบข้อมูลผู้ใช้ กรุณาสมัครสมาชิกใหม่'})

        columns = [column[0] for column in cursor.description]
        user_res = toJson(user_data, columns)[0]
        user_id = user_res['user_id']
        create_date = int(user_res['create_date'])
        national_id = user_res['national_id']

        # 3. Check for link expiration
        cursor.execute("SELECT duration FROM timetable_activity WHERE activity_desc = 'LinkExpire' LIMIT 1")
        link_ex_data = cursor.fetchall()
        duration = 259200 # Default 3 days
        if link_ex_data:
            duration = int(link_ex_data[0][0])

        current_time = int(time.time()) # Use python time to be safe
        if current_time - create_date >= duration:
            # Cleanup expired user
            cursor.execute("DELETE FROM user WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM user_activity WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM user_agreement WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM user_password_history WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM DataField WHERE national_id = %s", (national_id,))
            cursor.execute("DELETE FROM token_register WHERE token = %s", (token,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'link expire', 'message': 'ลิงก์ยืนยันตัวตนหมดอายุแล้ว ระบบได้ลบข้อมูลเดิมเพื่อให้คุณสามารถสมัครใหม่ได้'})

        # 4. Success: Directly activate user account (1)
        # Previously set to 8 (Pending Admin Approval), but now skipping that step
        cursor.execute("UPDATE user SET status_id = 1, status_account = 'active' WHERE user_id = %s", (user_id,))
        cursor.execute("UPDATE user_activity SET status_account = '1' WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM token_register WHERE token = %s", (token,))
        
        # Get user details for welcome email
        cursor.execute("SELECT email, firstname, lastname FROM user WHERE user_id = %s", (user_id,))
        user_info = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()

        # Send welcome email
        if user_info:
            try:
                sendMailWelcomeForRegister(user_id, user_info[0], user_info[1], user_info[2], '-')
            except Exception as mail_err:
                current_app.logger.warning(f"Could not send welcome email: {mail_err}")

        logAction(user_id, '/getEmailFromToken', f'User {username} email verified and activated directly', 'info')

        return jsonify({
            'status': 'found', 
            'email': token_res['email'], 
            'username': username, 
            'pending_approval': False,
            'active': True
        })

    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        current_app.logger.error(f"Error in getEmailFromToken: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/secondStepRegister', methods=['POST'])
def secondStepRegister():
    try:
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
                sendMailWelcomeForRegister(result[0]['user_id'],email, result[0]['firstname'], result[0]['lastname'],QRcode)
                return(jsonify({"status": "Success"}))
        else:
            return(jsonify({"status": "Your Username is duplicated."}))
            # return 'Your Username is duplicated.'
    except Exception as e:
        current_app.logger.info(e)
        return jsonify({"status": "Error"})
        # return "Error: " + str(e)


@app.route('/editProfileUser', methods=['POST']) 
def editProfileUser():
    try :
        data = request.json
        dataInput = json.loads(decode(data['user']))
        link = data['link']
        #-------------#
        user_id = dataInput['user_id']
        firstname = dataInput['firstname']
        lastname = dataInput['lastname']
        usage_objective = dataInput['usage_objective']
        other_object = dataInput['other_object']
        email = dataInput['email']
        #-------------#
        ##-------------##
        conn = mysql.connect()
        cursor = conn.cursor()
        sql_get = """SELECT * FROM user WHERE user_id = %s AND status_id != '7'"""
        cursor.execute(sql_get, (user_id))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_email = toJson(data, columns)
        conn.commit()
        cursor.close()
        conn.close()
        ##-------------##
        if len(result_email) != 0 : 
            #Have User#
            ##--Check Email Input--##
            if check_email_format(email) :
                ###Have Email###
                if result_email[0]['email'] == email:
                    # # user_id, firstname, lastname, email, usage_objective, other_object, last_updated
                    # sql = "INSERT INTO temp_user VALUES (NULL, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
                    # cursor.execute(sql, (user_id, firstname, lastname, email, usage_objective, other_object))
                    #
                    # sql_get = """SELECT * FROM user WHERE user_id = %s"""
                    # cursor.execute(sql_get, (user_id))
                    # data = cursor.fetchall()
                    # columns = [column[0] for column in cursor.description]
                    # result = toJson(data, columns)
                    # conn.commit()
                    # cursor.close()

                    # M&M ��� editProfileUser (1)
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = "UPDATE user SET firstname = %s , lastname = %s ,usage_objective = %s , other_object = %s WHERE user_id = %s"
                    cursor.execute(sql, (firstname, lastname, usage_objective, other_object, user_id))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    #----#
                    conn = mysql.connect()
                    cursor = conn.cursor()                   
                    sql_getdata = "SELECT * FROM user WHERE user_id = %s"
                    cursor.execute(sql_getdata, user_id)
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result = toJson(data, columns)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    #/M&M ��� editProfileUser (1)

                    # sendMailEditProfileOld(result)
                    sendMailEditProfile(dataInput, link, result[0]['firstname'], result[0]['lastname'])
                    #return json.dumps({'status': 'success', 'data': result})
                    return jsonify({'status': 'success', 'data': result})
                else:
                    conn = mysql.connect()
                    cursor = conn.cursor() 
                    sql_get = """SELECT email FROM user where user_id != %s AND status_id != '7'"""
                    cursor.execute(sql_get, (user_id))
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result = toJson(data, columns)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    for j in range(len(result)):
                        if result[j]['email'] != email:
                            check = True
                        else:
                            return json.dumps({'status': 'error', 'data': 'Email is duplicate'})
                    if check == True:
                        conn = mysql.connect()
                        cursor = conn.cursor()            
                        sql = "INSERT INTO temp_user VALUES (NULL, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
                        cursor.execute(sql, (user_id, firstname, lastname, email, usage_objective, other_object))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        #---#
                        conn = mysql.connect()
                        cursor = conn.cursor()    
                        sql_get = """SELECT * FROM user WHERE user_id = %s"""
                        cursor.execute(sql_get, (user_id))
                        data = cursor.fetchall()
                        columns = [column[0] for column in cursor.description]
                        result = toJson(data, columns)
                        conn.commit()
                        cursor.close()
                        conn.close()
                        #---#
                        sendMailEditProfileOld(result)
                        sendMailEditEmail(dataInput, link, result[0]['firstname'], result[0]['lastname'])
                        return json.dumps({'status': 'email success', 'data': 'Please verify email'})
                    else :
                        return 'error'
            else :
                ###Not have Email Input###
                #--Check Email in Table : user--#
                if check_email_format(result_email[0]['email']):
                    #-Have Email-#
                    return 'E-mail is required'
                else :
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    sql = "UPDATE user SET firstname = %s , lastname = %s ,usage_objective = %s , other_object = %s WHERE user_id = %s"
                    cursor.execute(sql, (firstname, lastname, usage_objective, other_object, user_id))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    #----#
                    conn = mysql.connect()
                    cursor = conn.cursor()                   
                    sql_getdata = "SELECT * FROM user WHERE user_id = %s"
                    cursor.execute(sql_getdata, user_id)
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result = toJson(data, columns)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'success', 'data': result})
        else :
            #Not have User#
            return 'error'
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        # return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        return jsonify({"status": "Error"})


def sendMailEditProfileOld(result):
    # token, email, link
    # link = 'http://localhost:8080'
    # token = ''
    # email = ''
    # token = str(result[0]['user_id'])
    fromaddr = "Department Operation Center <adminbd@customs.go.th>"
    toaddr = result[0]['email']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Edit your profile for Department Operation Center"
    footer = "<br><br><br>Team" + "<br>Call Center: +66" + "<br>Email: adminbd@customs.go.th"
    body = "<p style='font-size: 14px;'>Hi&nbsp;&nbsp;" + result[0]['firstname'] + "&nbsp;" + result[0][
        'lastname'] + "<br>Your member profile was changed on the Department Operation Center account.<br/>If this was your action, then you can safely ignore this email.<br/>If this was not yours, a malicious user may have your password.Please review your profile at <br/>and change your password.  If you need any help, please contact Department Operation Center Contact Center at /contactcenter Tel: +66.</p>" + footer #ใส่domain ด้วย

    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        server = smtplib.SMTP_SSL(SERVER, 465)
        ##Login Mail server##
        server.login(username_mail,password_mail)
        #-------------------#
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return 'success'
    except:
        return "error"


def sendMailEditProfile(dataInput, dataInputLink, firstname, lastname):
    # token, email, link
    link = LINK
    # token = ''
    # email = ''
    # token = str(dataInput['user_id'])
    fromaddr = "Department Operation Center <adminbd@customs.go.th>"
    toaddr = dataInput['email']
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Edit your profile for Department Operation Center"
    footer = "<br><br><br>Department Operation Center Team" + "<br>Call Center: +66" + "<br>Email: adminbd@customs.go.th"
    body = "<p style='font-size: 14px'>Hi&nbsp;&nbsp;" + firstname + "&nbsp;" + lastname + "<br>Your member profile was changed on the Department Operation Center account.<br>If this was your action, then you can safely ignore this email.<br>If this was not yours, a malicious user may have your password.Please review your profile at <br>and change your password.If you need any help, please contact Contact Center at /contactcenter Tel: +66.</p>" + footer # ใส่ domain

    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        server = smtplib.SMTP_SSL(SERVER, 465)
        ##Login Mail server##
        server.login(username_mail,password_mail)
        #-------------------#
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return 'success'
    except:
        return "error"

def sendMailEditEmail(dataInput, dataInputLink, firstname, lastname):
    # token, email, link
    # link = ''
    # token = ''
    # email = ''
    token = str(dataInput['user_id'])
    fromaddr = "Department Operation Center <adminbd@customs.go.th>"
    toaddr = dataInput['email']
    link = LINK_V + '/verifyEditProfile/' + token
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Edit your email for Department Operation Center"
    footer = "<br><br><br>Department Operation Center Team" + "<br>Call Center: +66" + "<br>Email: adminbd@customs.go.th"
    body = "<p style='font-size: 14px'>Hi&nbsp;&nbsp;" + firstname + "&nbsp;" + lastname + "<br>Your member profile was changed on the Department Operation Center account.<br>If this was your action, then you can safely ignore this email.<br>If this was not yours, a malicious user may have your password.Please review your profile at <br>and change your password.If you need any help, please contact Contact Center at /contactcenter Tel: +66.</p><a href='" + str(
        link) + "' style='margin: 0 auto;display: block;width: 160px;height: 60px;margin-top: 30px;background-color: #19b5fe;text-align: center;line-height: 60px;color: #ffffff;border-radius: 4px;text-decoration: none;'>Verify Email</a>" + footer

    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        server = smtplib.SMTP_SSL(SERVER, 465)
        ##Login Mail server##
        server.login(username_mail,password_mail)
        #-------------------#
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return 'success'
    except:
        return "error"

def sendMailUnlockAccountByAdmin(email, firstname, lastname):
    fromaddr = "Department Operation Center <adminbd@customs.go.th>"
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Unlock Account Successfully for Department Operation Center"
    footer = "<br><br><br>Department Operation Center" + "<br>Call Center: +66 " + "<br>Email: adminbd@customs.go.th"
    body = "<p style='font-size: 14px;width: 550px;'>Hi&nbsp;&nbsp;" + firstname + "&nbsp;" + lastname + "<br>Now your account has been unlock by system administrator<br> Please contact system administrator for get a default password.</p>" + footer

    msg.attach(MIMEText(body, 'html', "utf-8"))
    try:
        server = smtplib.SMTP_SSL(SERVER, 465)
        ##Login Mail server##
        server.login(username_mail,password_mail)
        #-------------------#
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
        return "success"
    except Exception as e:
        current_app.logger.info(e)
        logAction(id, 'sendMailConfirmRegister', str(e), 'error')
        # return "Error: " + str(e)
        return "Error"


@app.route('/verifyEditProfile/<string:userid>', methods=['GET'])
def verifyEditProfile(userid):
    try:
        user_id = userid
        link = LINK
        conn = mysql.connect()
        cursor = conn.cursor()
        sql_get = """SELECT * FROM temp_user WHERE user_id = %s AND last_update = (SELECT MAX(last_update) FROM temp_user WHERE user_id = %s)"""
        cursor.execute(sql_get, (user_id, user_id))
        data = cursor.fetchall()
        conn.commit()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)

        sql = "UPDATE user SET firstname = %s, lastname = %s, email = %s, usage_objective = %s, other_object = %s, last_update = CURRENT_TIMESTAMP WHERE user_id = %s"
        cursor.execute(sql, (
        result[0]['firstname'], result[0]['lastname'], result[0]['email'], result[0]['usage_objective'],
        result[0]['other_object'], result[0]['user_id']))
        conn.commit()
        cursor.close()
        conn.close()
        logAction(user_id, '/verifyEditProfile', 'edit profile success', 'info')
        return redirect(link)
    except Exception as e:
        current_app.logger.info(e)
        return "Error" 


@app.route('/generateApiKey', methods=['POST'])
def generateApiKey():
    try:
        data = request.json
        dataInput = json.loads(decode(data['user']))
        user_id = dataInput['user_id']
        
        # Generate 32 char key
        import string
        import random
        alphabet = string.ascii_letters + string.digits
        new_key = ''.join(random.choices(alphabet, k=32))
        
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "UPDATE user SET apikey = %s WHERE user_id = %s"
        cursor.execute(sql, (new_key, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        # Return updated user profile
        conn = mysql.connect()
        cursor = conn.cursor()                   
        sql_getdata = "SELECT * FROM user WHERE user_id = %s"
        cursor.execute(sql_getdata, user_id)
        user_data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(user_data, columns)
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        current_app.logger.error("Error generating API key:", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})


# ============================================================
# User Registration Approval Endpoints
# ============================================================

@app.route('/getPendingUsers', methods=['POST'])
def getPendingUsers():
    """Return list of users with status_id=8 (Pending Admin Approval)."""
    try:
        dataInput = request.json
        user_data = json.loads(platform_decode(dataInput['user']))
        if not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT u.user_id, u.username, u.email, u.firstname, u.lastname,
                        u.national_id, u.national_id_book, u.usage_objective,
                        u.create_at, u.status_id
                 FROM user u
                 WHERE u.status_id = 8 AND u.status_account = 'active'
                 ORDER BY u.create_at DESC"""
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        cursor.close()
        conn.close()

        # Convert datetime objects
        for row in result:
            for k, v in row.items():
                if hasattr(v, 'isoformat'):
                    row[k] = v.isoformat()

        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        current_app.logger.error("Error in getPendingUsers:", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/approveUser', methods=['POST'])
def approveUser():
    """Approve a pending user (change status_id from 8 to 1) and send welcome email."""
    conn = None
    try:
        dataInput = request.json
        admin_data_raw = dataInput.get('user')
        if not admin_data_raw:
            return jsonify({'status': 'error', 'message': 'Admin session data is required'})
            
        admin_data = json.loads(platform_decode(admin_data_raw))
        if not checkUserIsAdmin(admin_data):
            return jsonify({"status": "error", "message": "Permission Denied: คุณไม่มีสิทธิ์อนุมัติสมาชิก"})

        target_user_id = dataInput.get('target_user_id')
        if not target_user_id:
            return jsonify({'status': 'error', 'message': 'target_user_id is required'})

        conn = mysql.connect()
        cursor = conn.cursor()

        # 1. Fetch user details first
        sql_get = "SELECT username, email, firstname, lastname FROM user WHERE user_id = %s"
        cursor.execute(sql_get, (target_user_id,))
        user_row = cursor.fetchone()
        
        if not user_row:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'ไม่พบข้อมูลผู้ใช้'})
            
        username, email, firstname, lastname = user_row

        # 2. Update status to Active (1)
        # We also force status_account = 'active' just in case it was something else
        sql_update = """
            UPDATE user 
            SET status_id = 1, status_account = 'active'
            WHERE user_id = %s AND status_id = 8
        """
        cursor.execute(sql_update, (target_user_id,))
        affected = cursor.rowcount
        
        # 3. Handle user_activity status_account to '1' (Active)
        cursor.execute("UPDATE user_activity SET status_account = '1' WHERE user_id = %s", (target_user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({'status': 'error', 'message': 'ผู้ใช้นี้ถูกอนุมัติไปแล้วหรือไม่ได้อยู่ในสถานะรออนุมัติ'})

        # 4. Log the action
        logAction(admin_data.get('user_id', 0), '/approveUser', f'Approved user {username} (ID: {target_user_id})', 'info')

        # 5. Send Welcome Email (Account Approved)
        try:
            sendMailWelcomeForRegister(target_user_id, email, firstname, lastname, '-')
            print(f"Approval email sent to {email}")
        except Exception as mail_err:
            current_app.logger.error(f"Failed to send approval email: {mail_err}")

        return jsonify({'status': 'success', 'message': f'อนุมัติผู้ใช้ {username} สำเร็จ'})

    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        current_app.logger.error(f"Error in approveUser: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/rejectUser', methods=['POST'])
def rejectUser():
    """Reject a pending user (set status_id = 7 which means deleted/rejected)."""
    try:
        dataInput = request.json
        user_data = json.loads(platform_decode(dataInput['user']))
        if not checkUserIsAdmin(user_data):
            return jsonify({"status": "Permission Denied"})

        target_user_id = dataInput.get('target_user_id')
        if not target_user_id:
            return jsonify({'status': 'error', 'message': 'target_user_id is required'})

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "UPDATE user SET status_id = 7 WHERE user_id = %s AND status_id = 8 AND status_account = 'active'"
        cursor.execute(sql, (target_user_id,))
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({'status': 'error', 'message': 'User not found or not in pending status'})

        logAction(user_data['user_id'], '/rejectUser', 'Rejected user_id: ' + str(target_user_id), 'info')
        return jsonify({'status': 'success', 'message': 'User rejected'})
    except Exception as e:
        current_app.logger.error("Error in rejectUser:", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/debug/userSchema', methods=['GET'])
def debugUserSchema():
    """Temporary debug endpoint - returns DESC user."""
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DESC user")
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result = toJson(data, columns)
        cursor.close()
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/registerSimple', methods=['POST'])
def registerSimple():
    """Simplified registration endpoint for the Intelligist DataX platform.
    Creates user with status_id=4 (Pending Email Verification) and sends verification email.
    Uses the exact same INSERT pattern as seed.py (named columns) which is proven to work.
    """
    try:
        dataInput = request.json
        username = dataInput['username']
        password = dataInput['password']
        email = dataInput['email']
        firstname = dataInput.get('firstname', '')
        lastname = dataInput.get('lastname', '')
        organization = dataInput.get('organization', '')
        link = dataInput.get('link', 'http://110.78.210.128:3001')

        # Check for duplicate username or email
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT user_id, username, email FROM user
                 WHERE (username = %s OR email = %s) AND status_id != 7 AND status_account = 'active'"""
        cursor.execute(sql, (username, email))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        existing = toJson(data, columns)
        cursor.close()
        conn.close()

        if existing:
            if existing[0]['username'] == username:
                return jsonify({'status': 'error', 'message': 'ชื่อผู้ใช้นี้ถูกใช้แล้ว'})
            if existing[0]['email'] == email:
                return jsonify({'status': 'error', 'message': 'อีเมลนี้ถูกใช้แล้ว'})

        # Generate verification token
        token = (str(uuid.uuid4()) + str(uuid.uuid1())).replace('-', '')

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "INSERT INTO token_register VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
        cursor.execute(sql, (token, username, email, 'active'))
        conn.commit()
        cursor.close()
        conn.close()

        # Get current policy
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT MAX(policy_id) as max_policy FROM codename_policy"
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        policy_result = toJson(data, columns)
        policy_id = policy_result[0]['max_policy'] if policy_result and policy_result[0]['max_policy'] else 1
        cursor.close()
        conn.close()

        # Insert user with status_id=4 (Pending Email Verification)
        # Using the EXACT same named-column pattern as seed.py which works every deployment
        conn = mysql.connect()
        cursor = conn.cursor()
        sql_user = """
            INSERT INTO user (username, password, email, firstname, lastname,
                              national_id, national_id_book, national_id_mode,
                              status_id, status_account, previlage_id, job_title,
                              policy_id, usage_objective)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_user, (
            username, password, email, firstname, lastname,
            username, '', 1,        # national_id=username, national_id_book='', mode=1
            4, 'active', 3, '',     # status=4(pending), active, privilege=3(user), job_title=''
            policy_id, organization  # policy_id, usage_objective=organization
        ))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()

        # Insert user_activity with password (same pattern as seed.py)
        conn = mysql.connect()
        cursor = conn.cursor()
        sql_activity = """
            INSERT INTO user_activity (user_id, login_status, login_respond, create_date,
                                       status_account, password, emailnews)
            VALUES (%s, %s, %s, UNIX_TIMESTAMP(), %s, %s, %s)
        """
        cursor.execute(sql_activity, (user_id, 0, 0, '0', password, '-'))
        conn.commit()
        cursor.close()
        conn.close()

        # Insert password history
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "INSERT INTO user_password_history VALUES(NULL, %s, '1', %s, UNIX_TIMESTAMP())"
        cursor.execute(sql, (user_id, password))
        conn.commit()
        cursor.close()
        conn.close()

        # Insert DataField placeholder (same pattern as seed.py)
        conn = mysql.connect()
        cursor = conn.cursor()
        sql_datafield = """
            INSERT INTO DataField (national_id, national_id_book, sublevel_id, expiration)
            VALUES (%s, %s, %s, '9999-01-01')
        """
        cursor.execute(sql_datafield, (username, '', 1.1))
        cursor.execute(sql_datafield, (username, '', 1.2))
        conn.commit()
        cursor.close()
        conn.close()

        # Insert user_agreement (optional, silently skip if consent table doesn't exist)
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            sql_max = "SELECT MAX(version) as v FROM consent_agreement WHERE status = 'active'"
            cursor.execute(sql_max)
            vdata = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            vresult = toJson(vdata, columns)
            if vresult and vresult[0]['v']:
                sql_id = "SELECT consent_agreement_id FROM consent_agreement WHERE status = 'active' AND version = %s LIMIT 1"
                cursor.execute(sql_id, (vresult[0]['v'],))
                cdata = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                cresult = toJson(cdata, columns)
                if cresult:
                    ip = request.headers.get('X-FORWARDED-FOR', '127.0.0.1')
                    sql_agree = "INSERT INTO user_agreement VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())"
                    cursor.execute(sql_agree, (ip, user_id, cresult[0]['consent_agreement_id']))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as agree_err:
            current_app.logger.warning("Could not insert user_agreement: " + str(agree_err))

        # Try to send verification email (silently fail if SMTP not available)
        try:
            # Construct the verification link
            # Use provided link or fallback to global LINK
            base_link = link if link else LINK
            sendMailConfirmRegister(user_id, token, email, base_link, firstname, lastname)
            verify_url = f"{base_link}/verify/{token}"
            print(f"DEBUG: Verification Email simulated/sent. URL: {verify_url}")
        except Exception as mail_err:
            current_app.logger.warning("Could not send verification email: " + str(mail_err))
            verify_url = f"{LINK}/verify/{token}"

        logAction(user_id, '/registerSimple', 'User registered, pending email verification', 'info')

        return jsonify({
            'status': 'success',
            'message': 'สมัครสมาชิกสำเร็จ กรุณาตรวจสอบอีเมลเพื่อยืนยันตัวตน',
            'token': token,
            'user_id': user_id,
            'verify_url': verify_url # Return URL for Simulation UI
        })
    except Exception as e:
        current_app.logger.error("Error in registerSimple:", exc_info=True)
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)})

