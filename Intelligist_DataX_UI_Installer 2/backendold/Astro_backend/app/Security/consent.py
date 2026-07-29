from ServiceConfig import *
import base64

@app.route('/acceptNewConsent', methods=['POST'])
def acceptNewConsent():
    try:
        ip = request.headers.get('X-FORWARDED-FOR',None)
        dataInput = request.json
        user_id = decode(dataInput['user_id'])
        conn = mysql.connect()
        cursor = conn.cursor()
        sql_max = "SELECT version FROM consent_agreement WHERE status = 'active'"
        # sql_max = "SELECT MAX(version) FROM consent_agreement WHERE status = 'active'"
        cursor.execute(sql_max)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_max = toJson(data, columns)
        sql_id = "SELECT consent_agreement_id FROM consent_agreement WHERE status = 'active' AND version = %s"
        cursor.execute(sql_id, (result_max[0]['version']))
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        result_id = toJson(data, columns)
        # sql = "UPDATE user_agreement SET ip = %s , consent_agreement_id = %s , date_time = UNIX_TIMESTAMP() WHERE user_id = %s "
        # cursor.execute(sql, (ip ,result_id[0]['consent_agreement_id'], user_id))
        ### เปลี่ยนจาก Update row ให้เป็น insert เพื่อ เก็บ Log ทุกครั้งที่กด Consent ###
        sql = "INSERT INTO user_agreement VALUES (NULL, %s, %s, %s, UNIX_TIMESTAMP())"
        cursor.execute(sql, (ip, user_id, result_id[0]['consent_agreement_id']))
        ############################################################################# 
        sql = "UPDATE user_activity SET status_account = '1' WHERE user_id = %s "
        cursor.execute(sql, user_id)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "Accept Success"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error acceptNewConsent"+str(e)})

@app.route('/Consent', methods=['POST','PUT'])
def Consent():
    try:
        if request.method == 'POST':
            dataInput = request.json
            file_name = request.form['file_name']
            status = request.form['status']
            # version = request.form['version']
            consent_text = request.form['consent_text']
            # consent_file = request.files['file']
            # start_date = request.form['start_date']
            # end_date = request.form['end_date']
            # consent_file = consent_file.read()
            user_data = json.loads(decode(request.form['user']))
            # user_data = json.loads(decode(dataInput['user']))
            # a = 0
            # if a==0 :
            if checkUserIsAdmin(user_data) :
                conn = mysql.connect()
                cursor = conn.cursor()
                if(status == "active"):
                    sql_update_data = '''UPDATE consent_agreement as consent1 
                                            SET consent1.status="inactive" 
                                        WHERE consent1.consent_agreement_id IN
                                            (SELECT consent_agreement_id FROM 
                                                (SELECT consent_agreement_id FROM consent_agreement) as consent2 
                                                WHERE status = "active")'''
                    cursor.execute(sql_update_data)
                    conn.commit()
                sql_insert_data = "INSERT INTO consent_agreement VALUES(NULL,%s,(SELECT MAX(b.version+1) FROM consent_agreement as b),%s,NULL,%s,CURRENT_TIMESTAMP)"
                cursor.execute(sql_insert_data, (file_name,status,consent_text))
                conn.commit()
                cursor.close()
                conn.close()
                logAction(user_data['user_id'], '/Consent', 'Add consent'+file_name+'success', 'info')
                return jsonify({'status': 'Add new consent success'})
            else:
                logAction(user_data['user_id'], '/Consent', 'Permission Denied', 'warning')
                return jsonify({"status":"Permission Denied"})
        if request.method == 'PUT':
            # user_data = json.loads(decode(dataInput['user']))
            user_data = json.loads(decode(request.form['user']))
            consent_agreement_id = request.form['consent_agreement_id']
            file_name = request.form['file_name']
            # version = request.form['version']
            status = request.form['status']
            consent_text = request.form['consent_text']
            # consent_file = request.files['file']
            # start_date = request.form['start_date']
            # end_date = request.form['end_date']
            # consent_file = consent_file.read()
            conn = mysql.connect()
            cursor = conn.cursor()
            if checkUserIsAdmin(user_data) :
                if(status == "active"):
                    sql_update_data1 = '''UPDATE consent_agreement as consent1 
                                            SET consent1.status="inactive" 
                                        WHERE consent1.consent_agreement_id IN
                                            (SELECT consent_agreement_id FROM 
                                                (SELECT consent_agreement_id FROM consent_agreement) as consent2 
                                                WHERE status = "active")'''
                    cursor.execute(sql_update_data1)
                    conn.commit()
                    sql_update = "UPDATE consent_agreement SET file_name = %s , status = %s ,consent_text = %s WHERE consent_agreement_id = %s"
                    cursor.execute(sql_update, (file_name,status,consent_text,consent_agreement_id))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    logAction(user_data['user_id'], '/Consent', 'Edit consent '+str(consent_agreement_id)+' success', 'info')
                    return jsonify({'status': 'update '+file_name+' success'})
                else:
                    sql_check_consent = '''SELECT status FROM consent_agreement WHERE consent_agreement_id = %s'''
                    cursor.execute(sql_check_consent,(consent_agreement_id))
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    result = toJson(data, columns)
                    status_check = 0
                    if(result[0]['status'] == "active"):
                        logAction(user_data['user_id'], '/Consent', 'cannot change all consent to inactive', 'warning')
                        return jsonify({'status':'Error cannot change all consent to inactive'})
                    elif(status == "inactive"):
                        sql_update = "UPDATE consent_agreement SET file_name = %s , status = %s ,consent_text = %s WHERE consent_agreement_id = %s"
                        cursor.execute(sql_update, (file_name,status,consent_text,consent_agreement_id))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        logAction(user_data['user_id'], '/Consent', 'Edit consent '+str(consent_agreement_id)+' success', 'info')
                        return jsonify({'status': 'update '+file_name+' success'})
            else:
                return jsonify({"status":"Permission Denied"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})

@app.route('/fetch_Consent', methods=['POST'])
def fetch_Consent():
    try:
        dataInput = request.json
        user_data = json.loads(decode(dataInput['user']))
        if checkUserIsAdmin(user_data) :
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "SELECT * FROM consent_agreement"
            cursor.execute(sql)
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result_data = toJson(data, columns)
            # print(result_data)
            if len(result_data) != 0:
                for i in range(len(result_data)):
                    if result_data[i]['consent_file'] not in (None,""):
                        result_data[i]['consent_file'] = base64.b64encode(result_data[i]['consent_file'])
                        result_data[i]['consent_file'] = result_data[i]['consent_file'].decode('utf-8')
            return jsonify({'data':result_data,'status': 'success'})
        else:
            return jsonify({"status":"Permission Denied"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})


@app.route('/Lastest_Consent', methods=['GET'])
def Lastest_Consent():
    try:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "SELECT consent_text FROM consent_agreement WHERE status = 'active'"
            cursor.execute(sql)
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result_data = toJson(data, columns)
            #print(result_data)
            # service_image = service_image.read()
            # if len(result_data) != 0:
            #     for i in range(len(result_data)):
            #         if result_data[i]['consent_file'] not in (None,""):
            #             result_data[i]['consent_file'] = base64.b64encode(result_data[i]['consent_file'])
            #             result_data[i]['consent_file'] = result_data[i]['consent_file'].decode('utf-8')
            return jsonify({'data':result_data,'status': 'success'})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})

@app.route('/AcceptCookie', methods=['POST'])
def AcceptCookie():
    try:
        dataInput = request.json
        browsers_name = dataInput['browsers_Name']
        browsers_version = dataInput['browsers_version']
        #---#
        ip = request.headers.get('X-FORWARDED-FOR',None)
        # ip = "192.168.2.36,70.41.3.18,150.172.238.178"
        ip_address = ip.split(',')
        ip_check = ip_address[0].split('.')
        conn = mysql.connect()
        cursor = conn.cursor()
        #--------------------------------------------------#
        sql = "INSERT INTO AcceptCookie VALUES (NULL, CURRENT_TIMESTAMP, %s, %s, %s, %s )"
        cursor.execute(sql, (browsers_name, browsers_version, ip_address[0], 'None'))
        conn.commit()
        cursor.close()
        return jsonify({"status": "AcceptCookie Success"})
    except Exception as e:
        print("Error: " + str(e))
        return jsonify({"status": "Error"})        
        # return jsonify({"status": "Error :"+str(e)})
#################################################################################