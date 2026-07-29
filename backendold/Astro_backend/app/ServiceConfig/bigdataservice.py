from flask import request, jsonify
from ServiceConfig import *
from ServiceConfig.register import *
from ServiceConfig.notification_util import notify_user, notify_all_users
import base64
import io 
import json
import os
import sys
from datetime import datetime
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx', 'xls', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def log_api_audit(action, target_user_id=None, service_id=None, credential_id=None, result='success'):
    try:
        user_data = getattr(request, 'current_user', {})
        actor_user_id = user_data.get('user_id', 0)
        ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')[:500]
        
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """INSERT INTO api_audit_log (actor_user_id, target_user_id, service_id, credential_id, action, result, ip_address, user_agent) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (actor_user_id, target_user_id, service_id, credential_id, action, result, ip_addr, user_agent))
        conn.commit()
        cursor.close()
        conn.close()
        log_api_audit('update_api_config', service_id=service_id)
    except Exception as e:
        current_app.logger.error(f"Audit Log Error: {e}")

def platform_decode(data):
    if not data:
        return data
    
    # 1. If it looks like JSON already, return it
    if isinstance(data, str) and data.strip().startswith('{'):
        return data

    try:
        # 2. Try standard Base64 first
        # Add padding if missing
        padded_data = data
        missing_padding = len(padded_data) % 4
        if missing_padding:
            padded_data += '=' * (4 - missing_padding)
        return base64.b64decode(padded_data).decode('utf-8')
    except:
        try:
            # 3. Fallback to legacy obfuscated format
            return decode(data).decode('utf-8')
        except:
            # 4. Return as is
            return data

@app.route('/addService', methods=['POST','PUT'])
@require_admin
def addService():
    try:
        if request.method == 'POST':
            user_data = json.loads(platform_decode(request.form['user']))
            # Loosen check for presentation
            if True: # Admin check handled by decorator
                service_name = request.form['service_name']
                service_url = request.form.get('service_url', '#')
                service_image = request.files.get('file')
                service_status = request.form.get('service_status', 'Active')
                
                # Metadata Fields
                dataset_id = request.form.get('dataset_id', '')
                category = request.form.get('category', '')
                sub_category = request.form.get('sub_category', '')
                organization = request.form.get('organization', '')
                accessibility = request.form.get('accessibility', 'Public')
                access_type = request.form.get('access_type', 'เลือกการเข้าถึง')
                contact_name = request.form.get('contact_name', '')
                contact_email = request.form.get('contact_email', '')
                tags = request.form.get('tags', '')
                description = request.form.get('description', '')
                purpose = request.form.get('purpose', '')
                
                # New M-Society Fields
                dept_contact = request.form.get('dept_contact', '')
                update_freq_unit = request.form.get('update_freq_unit', '')
                update_freq_value = request.form.get('update_freq_value')
                geo_scope = request.form.get('geo_scope', '')
                data_source = request.form.get('data_source', '')
                data_format = request.form.get('data_format', '')
                gov_category = request.form.get('gov_category', '')
                license = request.form.get('license', '')
                access_conditions = request.form.get('access_conditions', '')
                sponsor = request.form.get('sponsor', '')
                smallest_unit = request.form.get('smallest_unit', '')
                url_ext = request.form.get('url', '')
                languages = request.form.get('languages', '')
                objective_type = request.form.get('objective_type', '')
                external_dashboard_url = request.form.get('external_dashboard_url', '')
                external_api_url = request.form.get('external_api_url', '')
                date_start = request.form.get('date_start')
                date_updated = request.form.get('date_updated')
                is_high_value = request.form.get('is_high_value', 'ไม่ใช่')
                is_reference = request.form.get('is_reference', 'ไม่ใช่')
                dataset_type = request.form.get('dataset_type', 'record')
                stat_year_start = request.form.get('stat_year_start')
                stat_year_latest = request.form.get('stat_year_latest')
                stat_classification = request.form.get('stat_classification')
                stat_unit = request.form.get('stat_unit')
                stat_multiplier = request.form.get('stat_multiplier')
                stat_calculation_method = request.form.get('stat_calculation_method')
                stat_standard = request.form.get('stat_standard')
                stat_official = request.form.get('stat_official', 'ไม่ใช่')
                geo_dataset_name = request.form.get('geo_dataset_name')
                geo_scale = request.form.get('geo_scale')
                geo_west_bound = request.form.get('geo_west_bound')
                geo_east_bound = request.form.get('geo_east_bound')
                geo_north_bound = request.form.get('geo_north_bound')
                geo_south_bound = request.form.get('geo_south_bound')
                geo_position_accuracy = request.form.get('geo_position_accuracy')
                geo_reference_time = request.form.get('geo_reference_time')
                geo_published_date = request.form.get('geo_published_date')
                api_enabled_raw = request.form.get('api_enabled')
                api_enabled = 1 if api_enabled_raw in ['true', '1', True] else (0 if api_enabled_raw in ['false', '0', False] else None)

                conn = mysql.connect()
                cursor = conn.cursor()
                
                # Check for duplicate Dataset ID or Name
                sql = "SELECT service_id FROM service WHERE service_name = %s OR (dataset_id = %s AND dataset_id != '')"
                cursor.execute(sql, (service_name, dataset_id))
                result_data = cursor.fetchall()
                
                if(len(result_data) == 0):
                    image_blob = None
                    if service_image:
                        image_blob = service_image.read()
                        
                    # Handle specialized file uploads
                    data_file = request.files.get('data_file')
                    file_path = None
                    if data_file and allowed_file(data_file.filename):
                        filename = secure_filename(f"ds_{dataset_id}_{data_file.filename}")
                        data_file.save(os.path.join(UPLOAD_FOLDER, filename))
                        file_path = filename

                    dict_file = request.files.get('dictionary_file')
                    dict_path = None
                    if dict_file and allowed_file(dict_file.filename):
                        filename = secure_filename(f"dict_{dataset_id}_{dict_file.filename}")
                        dict_file.save(os.path.join(UPLOAD_FOLDER, filename))
                        dict_path = filename

                    samp_file = request.files.get('sampling_file')
                    samp_path = None
                    if samp_file and allowed_file(samp_file.filename):
                        filename = secure_filename(f"samp_{dataset_id}_{samp_file.filename}")
                        samp_file.save(os.path.join(UPLOAD_FOLDER, filename))
                        samp_path = filename

                    sql_insert = """INSERT INTO service(
                        service_name, service_url, service_image, status,
                        dataset_id, category, sub_category, organization,
                        accessibility, contact_name, contact_email, tags,
                        description, purpose, file_path, dept_contact,
                        update_freq_unit, update_freq_value, geo_scope,
                        data_source, data_format, gov_category, license,
                        access_conditions, sponsor, smallest_unit, url,
                        languages, objective_type, data_dictionary_path,
                        data_sampling_path, external_dashboard_url, external_api_url,
                        access_type, date_start, date_updated, is_high_value, is_reference,
                        dataset_type, stat_year_start, stat_year_latest, stat_classification,
                        stat_unit, stat_multiplier, stat_calculation_method, stat_standard,
                        stat_official, geo_dataset_name, geo_scale, geo_west_bound,
                        geo_east_bound, geo_north_bound, geo_south_bound, geo_position_accuracy,
                        geo_reference_time, geo_published_date
                    ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    
                    cursor.execute(sql_insert, (
                        service_name, service_url, image_blob, service_status,
                        dataset_id, category, sub_category, organization,
                        accessibility, contact_name, contact_email, tags,
                        description, purpose, file_path, dept_contact,
                        update_freq_unit, update_freq_value, geo_scope,
                        data_source, data_format, gov_category, license,
                        access_conditions, sponsor, smallest_unit, url_ext,
                        languages, objective_type, dict_path,
                        samp_path, external_dashboard_url, external_api_url,
                        access_type, date_start, date_updated, is_high_value, is_reference,
                        dataset_type, stat_year_start, stat_year_latest, stat_classification,
                        stat_unit, stat_multiplier, stat_calculation_method, stat_standard,
                        stat_official, geo_dataset_name, geo_scale, geo_west_bound,
                        geo_east_bound, geo_north_bound, geo_south_bound, geo_position_accuracy,
                        geo_reference_time, geo_published_date
                    ))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'insert new service success'})
                else:
                    cursor.close()
                    conn.close()
                    return jsonify({"status":"Error: Service name or Dataset ID duplicate"})
            else:
                return jsonify({"status":"Permission Denied"})
        elif request.method == 'PUT':
            user_data = json.loads(platform_decode(request.form['user']))
            # Loosen check for presentation
            if True: # Admin check handled by decorator
                service_id = request.form['service_id']
                service_image = request.files.get('file')
                service_name = request.form.get('service_name')
                service_url = request.form.get('service_url')
                service_status = request.form.get('service_status')
                
                # New fields
                dataset_id = request.form.get('dataset_id')
                category = request.form.get('category')
                sub_category = request.form.get('sub_category')
                organization = request.form.get('organization')
                accessibility = request.form.get('accessibility')
                access_type = request.form.get('access_type')
                contact_name = request.form.get('contact_name')
                contact_email = request.form.get('contact_email')
                tags = request.form.get('tags')
                description = request.form.get('description')
                purpose = request.form.get('purpose')
                
                # New fields
                dept_contact = request.form.get('dept_contact')
                update_freq_unit = request.form.get('update_freq_unit')
                update_freq_value = request.form.get('update_freq_value')
                geo_scope = request.form.get('geo_scope')
                data_source = request.form.get('data_source')
                data_format = request.form.get('data_format')
                gov_category = request.form.get('gov_category')
                license = request.form.get('license')
                access_conditions = request.form.get('access_conditions')
                sponsor = request.form.get('sponsor')
                smallest_unit = request.form.get('smallest_unit')
                url_ext = request.form.get('url')
                languages = request.form.get('languages')
                objective_type = request.form.get('objective_type')
                external_dashboard_url = request.form.get('external_dashboard_url')
                external_api_url = request.form.get('external_api_url')
                date_start = request.form.get('date_start')
                date_updated = request.form.get('date_updated')
                is_high_value = request.form.get('is_high_value')
                is_reference = request.form.get('is_reference')
                dataset_type = request.form.get('dataset_type')
                stat_year_start = request.form.get('stat_year_start')
                stat_year_latest = request.form.get('stat_year_latest')
                stat_classification = request.form.get('stat_classification')
                stat_unit = request.form.get('stat_unit')
                stat_multiplier = request.form.get('stat_multiplier')
                stat_calculation_method = request.form.get('stat_calculation_method')
                stat_standard = request.form.get('stat_standard')
                stat_official = request.form.get('stat_official')
                geo_dataset_name = request.form.get('geo_dataset_name')
                geo_scale = request.form.get('geo_scale')
                geo_west_bound = request.form.get('geo_west_bound')
                geo_east_bound = request.form.get('geo_east_bound')
                geo_north_bound = request.form.get('geo_north_bound')
                geo_south_bound = request.form.get('geo_south_bound')
                geo_position_accuracy = request.form.get('geo_position_accuracy')
                geo_reference_time = request.form.get('geo_reference_time')
                geo_published_date = request.form.get('geo_published_date')
                api_enabled_raw = request.form.get('api_enabled')
                api_enabled = 1 if api_enabled_raw in ['true', '1', True] else (0 if api_enabled_raw in ['false', '0', False] else None)

                conn = mysql.connect()
                cursor = conn.cursor()
                sql = "SELECT service_id FROM service WHERE service_id = %s"
                cursor.execute(sql, (service_id))
                service_result = cursor.fetchall()
                
                if len(service_result) != 0:
                    # Construct update query dynamically for provided fields
                    fields = []
                    values = []
                    
                    if service_name is not None: fields.append("service_name = %s"); values.append(service_name)
                    if service_url is not None: fields.append("service_url = %s"); values.append(service_url)
                    if service_status is not None: fields.append("status = %s"); values.append(service_status)
                    if dataset_id is not None: fields.append("dataset_id = %s"); values.append(dataset_id)
                    if category is not None: fields.append("category = %s"); values.append(category)
                    if sub_category is not None: fields.append("sub_category = %s"); values.append(sub_category)
                    if organization is not None: fields.append("organization = %s"); values.append(organization)
                    if accessibility is not None: fields.append("accessibility = %s"); values.append(accessibility)
                    if access_type is not None: fields.append("access_type = %s"); values.append(access_type)
                    if contact_name is not None: fields.append("contact_name = %s"); values.append(contact_name)
                    if contact_email is not None: fields.append("contact_email = %s"); values.append(contact_email)
                    if tags is not None: fields.append("tags = %s"); values.append(tags)
                    if description is not None: fields.append("description = %s"); values.append(description)
                    if purpose is not None: fields.append("purpose = %s"); values.append(purpose)
                    
                    # New M-Society fields update logic
                    if dept_contact is not None: fields.append("dept_contact = %s"); values.append(dept_contact)
                    if update_freq_unit is not None: fields.append("update_freq_unit = %s"); values.append(update_freq_unit)
                    if update_freq_value is not None: fields.append("update_freq_value = %s"); values.append(update_freq_value)
                    if geo_scope is not None: fields.append("geo_scope = %s"); values.append(geo_scope)
                    if data_source is not None: fields.append("data_source = %s"); values.append(data_source)
                    if data_format is not None: fields.append("data_format = %s"); values.append(data_format)
                    if gov_category is not None: fields.append("gov_category = %s"); values.append(gov_category)
                    if license is not None: fields.append("license = %s"); values.append(license)
                    if access_conditions is not None: fields.append("access_conditions = %s"); values.append(access_conditions)
                    if sponsor is not None: fields.append("sponsor = %s"); values.append(sponsor)
                    if smallest_unit is not None: fields.append("smallest_unit = %s"); values.append(smallest_unit)
                    if url_ext is not None: fields.append("url = %s"); values.append(url_ext)
                    if languages is not None: fields.append("languages = %s"); values.append(languages)
                    if objective_type is not None: fields.append("objective_type = %s"); values.append(objective_type)
                    if external_dashboard_url is not None: fields.append("external_dashboard_url = %s"); values.append(external_dashboard_url)
                    if external_api_url is not None: fields.append("external_api_url = %s"); values.append(external_api_url)
                    if date_start is not None: fields.append("date_start = %s"); values.append(date_start)
                    if date_updated is not None: fields.append("date_updated = %s"); values.append(date_updated)
                    if is_high_value is not None: fields.append("is_high_value = %s"); values.append(is_high_value)
                    if is_reference is not None: fields.append("is_reference = %s"); values.append(is_reference)
                    if dataset_type is not None: fields.append("dataset_type = %s"); values.append(dataset_type)
                    if stat_year_start is not None: fields.append("stat_year_start = %s"); values.append(stat_year_start)
                    if stat_year_latest is not None: fields.append("stat_year_latest = %s"); values.append(stat_year_latest)
                    if stat_classification is not None: fields.append("stat_classification = %s"); values.append(stat_classification)
                    if stat_unit is not None: fields.append("stat_unit = %s"); values.append(stat_unit)
                    if stat_multiplier is not None: fields.append("stat_multiplier = %s"); values.append(stat_multiplier)
                    if stat_calculation_method is not None: fields.append("stat_calculation_method = %s"); values.append(stat_calculation_method)
                    if stat_standard is not None: fields.append("stat_standard = %s"); values.append(stat_standard)
                    if stat_official is not None: fields.append("stat_official = %s"); values.append(stat_official)
                    if geo_dataset_name is not None: fields.append("geo_dataset_name = %s"); values.append(geo_dataset_name)
                    if geo_scale is not None: fields.append("geo_scale = %s"); values.append(geo_scale)
                    if geo_west_bound is not None: fields.append("geo_west_bound = %s"); values.append(geo_west_bound)
                    if geo_east_bound is not None: fields.append("geo_east_bound = %s"); values.append(geo_east_bound)
                    if geo_north_bound is not None: fields.append("geo_north_bound = %s"); values.append(geo_north_bound)
                    if geo_south_bound is not None: fields.append("geo_south_bound = %s"); values.append(geo_south_bound)
                    if geo_position_accuracy is not None: fields.append("geo_position_accuracy = %s"); values.append(geo_position_accuracy)
                    if geo_reference_time is not None: fields.append("geo_reference_time = %s"); values.append(geo_reference_time)
                    if geo_published_date is not None: fields.append("geo_published_date = %s"); values.append(geo_published_date)
                    if api_enabled is not None: fields.append("api_enabled = %s"); values.append(api_enabled)
                    
                    # Handle separate file upload if present
                    data_file = request.files.get('data_file')
                    if data_file and allowed_file(data_file.filename):
                        filename = secure_filename(f"ds_{service_id}_{data_file.filename}")
                        save_path = os.path.join(UPLOAD_FOLDER, filename)
                        data_file.save(save_path)
                        fields.append("file_path = %s")
                        values.append(filename)

                    if not fields:
                        return jsonify({"status":"No fields to update"})

                    sql_update = f"UPDATE service SET {', '.join(fields)} WHERE service_id = %s"
                    values.append(service_id)
                    
                    cursor.execute(sql_update, tuple(values))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return jsonify({'status':'update service success'})
                else:
                    cursor.close()
                    conn.close()
                    return jsonify({"status":"Error service not found"})
            else:
                return jsonify({"status":"Permission Denied"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error"})

@app.route('/getService', methods=['POST'])
@require_admin
def getService():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Loosen check for presentation: any valid user payload passes
        if True: # Admin check handled by decorator
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = "SELECT * FROM service"
            cursor.execute(sql)
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            service_result = toJson(data, columns)
            conn.commit()
            cursor.close()
            conn.close()
            result = []
            for i in range(len(service_result)):
                if service_result[i]['service_image'] not in [None,""]:
                    service_result[i]['service_image'] = base64.b64encode(service_result[i]['service_image'])
                    service_result[i]['service_image'] = service_result[i]['service_image'].decode('utf-8')
                    result.append(service_result[i])
                else:
                    result.append(service_result[i])
            return jsonify({'data':result,'status': 'success'})
        else:
            return jsonify({"status":"Permission Denied"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error"})


@app.route('/getServiceCredential', methods=['POST'])
@require_admin
def getServiceCredential():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        service_id = dataInput['service_id']
        # a = 0
        # if a==0 :
        # Loosen check for presentation
        if True: # Admin check handled by decorator
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = """SELECT username,PASSWORD
                    FROM service_credential
                LEFT JOIN service_credential_transaction
                    ON service_credential_transaction.credential_id = service_credential.credential_id
                LEFT JOIN service
                    ON service_credential_transaction.service_id = service.service_id
                WHERE service.service_id = %s """
            cursor.execute(sql,(service_id))
            data = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            service_result = toJson(data, columns)
            conn.commit()
            return jsonify({'data':service_result,'status': 'success'})
        else:
            return jsonify({"status":"Permission Denied"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error"})

@app.route('/addServiceCredential', methods=['POST','PUT'])
@require_admin
def addServiceCredential():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # a = 0
        # if a==0 :
        # Loosen check for presentation
        if True: # Admin check handled by decorator
            if request.method == 'POST':
                service_id = dataInput['service_id']
                service_username = dataInput['service_username']
                service_password = dataInput['service_password']
                conn = mysql.connect()
                cursor = conn.cursor()
                sql = "SELECT service_id FROM service WHERE service_id = %s"
                cursor.execute(sql,(service_id))
                data = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                service_id = toJson(data, columns)
                # print(service_id)
                conn.commit()
                if len(service_id) != 0 :
                    sql = """SELECT service_credential.username 
                                FROM service_credential
                            LEFT JOIN service_credential_transaction
                                ON service_credential_transaction.credential_id = service_credential.credential_id
                            WHERE service_credential_transaction.service_id = %s AND service_credential.username = %s"""
                    cursor.execute(sql,(service_username))
                    data = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    service_username = toJson(data, columns)
                    if len(service_username) == 0 :
                        sql_insertCredential = "INSERT INTO service_credential VALUES (NULL,%s,%s,NULL)"
                        cursor.execute(sql_insertCredential,(service_username,service_password))
                        conn.commit()
                        sql_credID = """SELECT service_credential.credential_id,MAX(credential_timestamp)
                                            FROM service_credential
                                        LEFT JOIN service_credential_transaction
                                            ON service_credential.credential_id = service_credential_transaction.credential_id
                                        LEFT JOIN service
                                            ON service.service_id = service_credential_transaction.service_id
                                        WHERE service.service_id = %s"""
                        cursor.execute(sql_credID,(service_id))
                        data = cursor.fetchall()
                        columns = [column[0] for column in cursor.description]
                        credential_id = toJson(data, columns)
                        conn.commit()
                        service_id = int(service_id[0]['service_id'])
                        credential_id = int(credential_id[0]['credential_id'])
                        sql_insertTransac = "INSERT INTO service_credential_transaction VALUES (NULL,%s,%s,NULL)"
                        cursor.execute(sql_insertTransac,(service_id,credential_id))
                        conn.commit()
                        return jsonify({'status': 'success'})
                    else:
                        return jsonify({'status': 'Error This username of service is already exist'})   
                else:
                    return jsonify({'status': 'Service not found'})
            else:
                pass
        else:
            return jsonify({"status":"Permission Denied"})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Line number: ", line_number)
        print("Error: " + str(e))
        return jsonify({"status": "Error: " + str(e),"Line number": line_number})
        # return jsonify({"status": "Error"})

@app.route('/retrieveService', methods=['GET'])
@app.route('/retrieveService', methods=['GET', 'POST'])
def retrieveService():
    try:
        user_id = None
        # Try to get user info if provided
        dataInput = request.json if request.is_json else request.form
        user_str = dataInput.get('user')
        if user_str:
            decoded_user = platform_decode(user_str)
            user_data = safe_json_loads(decoded_user)
            user_id = user_data.get('user_id')
            # If user is admin (previlage_id != 3), show all active services
            if user_data.get('previlage_id') and str(user_data.get('previlage_id')) != '3':
                user_id = 'ADMIN' 

        conn = mysql.connect()
        cursor = conn.cursor()
        
        if user_id == 'ADMIN':
            sql = "SELECT *, 1 AS has_access, NULL AS permission_status FROM service WHERE status = 'Active'"
            cursor.execute(sql)
        else:
            sql = """
                SELECT s.*,
                       (CASE 
                           WHEN NOT EXISTS (SELECT 1 FROM service_group_access sga WHERE sga.service_id = s.service_id)
                                AND NOT EXISTS (SELECT 1 FROM service_user_access sua WHERE sua.service_id = s.service_id) THEN 1
                           WHEN %s IS NOT NULL AND EXISTS (SELECT 1 FROM service_user_access sua WHERE sua.service_id = s.service_id AND sua.user_id = %s) THEN 1
                           WHEN %s IS NOT NULL AND EXISTS (
                               SELECT 1 FROM service_group_access sga
                               JOIN group_user_detail gud ON sga.group_id = gud.group_id
                               WHERE sga.service_id = s.service_id AND gud.user_id = %s
                           ) THEN 1
                           ELSE 0
                       END) AS has_access,
                       (SELECT status FROM dataset_permission_requests r 
                        WHERE r.service_id = s.service_id AND r.user_id = %s 
                        ORDER BY r.created_at DESC LIMIT 1) AS permission_status
                FROM service s
                WHERE s.status = 'Active'
            """
            cursor.execute(sql, (user_id, user_id, user_id, user_id, user_id))
            
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        service_result = toJson(data, columns)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'data': service_result, 'status': 'success'})
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("Error in retrieveService: ", str(e), " at line ", line_number)
        return jsonify({"status": "Error: " + str(e), "Line number": line_number})
@app.route('/dataapi/api/v1/<dataset_id>', methods=['GET'])
def get_dataset_api(dataset_id):
    """
    Main Data API endpoint.
    Retrieves real rows based on service configuration and user credentials.
    """
    conn = None
    cursor = None
    import re
    import hashlib
    import uuid
    request_id = str(uuid.uuid4())
    deprecated_transport = False
    
    try:
        apikey_header = request.headers.get('x-api-key')
        apikey_query = request.args.get('apikey')
        
        if apikey_header:
            apikey = apikey_header
        elif apikey_query:
            apikey = apikey_query
            deprecated_transport = True
        else:
            apikey = None
            
        ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        conn = mysql.connect()
        cursor = conn.cursor()

        # Helper function to log API usage easily
        def log_api_usage(user_id_val, msg, status_code):
            try:
                log_sql = """INSERT INTO log (user_id, log_detail, type, path, ip, country) 
                             VALUES (%s, %s, 'API', %s, %s, 'None')"""
                path = f"/dataapi/api/v1/{dataset_id}"
                detail = f"[{status_code}] {msg}"
                cursor.execute(log_sql, (user_id_val or 0, detail, path, ip_addr))
                conn.commit()
            except Exception as e:
                current_app.logger.error(f"Failed to log API usage: {e}")

        # First, fetch service configuration by dataset_id
        sql_svc_config = """SELECT service_id, api_enabled, api_type, api_db_name, api_source_name, api_source_type, 
                                   api_request_fields, api_response_fields, service_name
                            FROM service WHERE dataset_id = %s AND status = 'Active'"""
        cursor.execute(sql_svc_config, (dataset_id,))
        svc_row = cursor.fetchone()
        
        if not svc_row:
            log_api_usage(0, 'Service not found or inactive', 404)
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Service not found or inactive', 'request_id': request_id}), 404

        real_service_id, api_enabled, api_type, db_name, source_name, source_type, req_fields_raw, res_fields_raw, service_name = svc_row

        if not api_enabled:
            log_api_usage(0, 'API access is disabled for this dataset', 403)
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'API access is disabled for this dataset', 'request_id': request_id}), 403

        # Enforce key check if NOT public
        user_id = 0
        credential_id = None
        user_role = '3'
        expires_at = None
        
        if api_type != 'public':
            # Check if apikey is provided
            if not apikey:
                log_api_usage(0, 'Missing apikey parameter for private/restricted API', 401)
                cursor.close()
                conn.close()
                return jsonify({'status': 'error', 'message': 'Missing apikey parameter', 'request_id': request_id}), 401

            # Hash check
            if "." not in apikey:
                log_api_usage(0, 'Invalid API key format', 403)
                cursor.close()
                conn.close()
                return jsonify({'status': 'error', 'message': 'Invalid or inactive API key', 'request_id': request_id}), 403
                
            public_key_id = apikey.split('.')[0]
            secret_hash = hashlib.sha256(apikey.encode('utf-8')).hexdigest()

            # Validate API Credential
            sql_cred = """SELECT c.credential_id, c.user_id, c.status, c.expires_at, u.previlage_id
                            FROM api_credentials c
                            JOIN user u ON c.user_id = u.user_id
                            WHERE c.public_key_id = %s AND c.secret_hash = %s AND c.service_id = %s"""
            cursor.execute(sql_cred, (public_key_id, secret_hash, real_service_id))
            cred_row = cursor.fetchone()

            if not cred_row:
                log_api_usage(0, 'Invalid API key for this dataset', 403)
                cursor.close()
                conn.close()
                return jsonify({'status': 'error', 'message': 'Invalid or inactive API key', 'request_id': request_id}), 403

            credential_id, user_id, cred_status, expires_at, user_role = cred_row
            
            # Check Credential Status
            if cred_status != 'active':
                log_api_usage(user_id, 'API Key is inactive', 403)
                cursor.close()
                conn.close()
                return jsonify({'status': 'error', 'message': 'API Key is inactive', 'request_id': request_id}), 403

            # Check expiration
            if expires_at and expires_at < datetime.now():
                log_api_usage(user_id, 'API Key has expired', 403)
                cursor.close()
                conn.close()
                return jsonify({'status': 'error', 'message': 'API Key has expired', 'request_id': request_id}), 403

            # Check Dataset Access Permissions (Group / User restrictions)
            if str(user_role) == '3': # Regular user
                sql_check_restrict = """
                    SELECT 
                        (SELECT COUNT(*) FROM service_group_access WHERE service_id = %s) as group_count,
                        (SELECT COUNT(*) FROM service_user_access WHERE service_id = %s) as user_count
                """
                cursor.execute(sql_check_restrict, (real_service_id, real_service_id))
                r_count = cursor.fetchone()
                
                if r_count[0] > 0 or r_count[1] > 0:
                    sql_verify = """
                        SELECT 1 FROM service_user_access WHERE service_id = %s AND user_id = %s
                        UNION
                        SELECT 1 FROM service_group_access sga
                        JOIN group_user_detail gud ON sga.group_id = gud.group_id
                        WHERE sga.service_id = %s AND gud.user_id = %s
                    """
                    cursor.execute(sql_verify, (real_service_id, user_id, real_service_id, user_id))
                    if not cursor.fetchone():
                        log_api_usage(user_id, 'Access Denied (Permission Restriction)', 403)
                        cursor.close()
                        conn.close()
                        return jsonify({'status': 'error', 'message': 'Access Denied: You do not have permission to access this dataset', 'request_id': request_id}), 403
        else:
            # If public and apikey is provided, try to find who invoked it (optional logging)
            if apikey and "." in apikey:
                public_key_id = apikey.split('.')[0]
                secret_hash = hashlib.sha256(apikey.encode('utf-8')).hexdigest()
                sql_user = """SELECT api_credentials.user_id, user.previlage_id 
                             FROM api_credentials 
                             JOIN user ON api_credentials.user_id = user.user_id 
                             WHERE public_key_id = %s AND secret_hash = %s LIMIT 1"""
                cursor.execute(sql_user, (public_key_id, secret_hash))
                user_row = cursor.fetchone()
                if user_row:
                    user_id, user_role = user_row

        if not db_name or not source_name:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Service source not configured', 'request_id': request_id}), 500

        # Parse JSON fields
        try:
            req_fields_list = json.loads(req_fields_raw) if req_fields_raw else []
            res_fields_list = json.loads(res_fields_raw) if res_fields_raw else []
        except:
            req_fields_list = []
            res_fields_list = []
            
        # Validate dynamic SQL identifiers
        if not re.match(r'^[a-zA-Z0-9_]+$', source_name):
            return jsonify({'status': 'error', 'message': 'Invalid source name', 'request_id': request_id}), 400
            
        req_fields_list_valid = []
        for f in req_fields_list:
            if re.match(r'^[a-zA-Z0-9_]+$', f):
                req_fields_list_valid.append(f)
                
        res_fields_list_valid = []
        for f in res_fields_list:
            if re.match(r'^[a-zA-Z0-9_]+$', f):
                res_fields_list_valid.append(f)

        # 3. Handle Scopes (Row-Level Security)
        scope_where_clause = " 1=1 "
        scope_params = []
        if api_type == 'scope':
            cursor.execute("SELECT scope_json FROM api_scopes WHERE credential_id = %s", (credential_id,))
            scope_row = cursor.fetchone()
            if scope_row and scope_row[0]:
                try:
                    scope_obj = json.loads(scope_row[0]) if isinstance(scope_row[0], str) else scope_row[0]
                    allowed_ops = ['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN']
                    if isinstance(scope_obj, list):
                        for idx, cond in enumerate(scope_obj):
                            field = cond.get('field')
                            op = str(cond.get('operator', '=')).upper()
                            val = cond.get('value')
                            logic = str(cond.get('logic', 'AND')).upper()
                            if logic not in ['AND', 'OR']: logic = 'AND'
                            if field and op in allowed_ops:
                                if not re.match(r'^[a-zA-Z0-9_]+$', field): continue
                                prefix = f" {logic} " if idx > 0 else " AND "
                                if op == 'IN' and isinstance(val, list):
                                    if val:
                                        placeholders = ', '.join(['%s'] * len(val))
                                        scope_where_clause += f"{prefix}`{field}` IN ({placeholders})"
                                        scope_params.extend(val)
                                else:
                                    scope_where_clause += f"{prefix}`{field}` {op} %s"
                                    scope_params.append(val)
                            else:
                                if field:
                                    return jsonify({'status': 'error', 'message': f'Invalid scope operator: {op}'}), 400
                    elif isinstance(scope_obj, dict):
                        for field, values in scope_obj.items():
                            if values and isinstance(values, list):
                                if not re.match(r'^[a-zA-Z0-9_]+$', field): continue
                                placeholders = ', '.join(['%s'] * len(values))
                                scope_where_clause += f" AND `{field}` IN ({placeholders})"
                                scope_params.extend(values)
                except Exception as e:
                    current_app.logger.error(f"[{request_id}] Scope parsing error: {e}")

        # 4. Handle User Filters (Request Fields)
        filter_where_clause = ""
        filter_params = []
        
        # Deny unallowed request fields
        for arg in request.args:
            if arg != 'apikey' and arg not in req_fields_list_valid:
                return jsonify({'status': 'error', 'message': f'Disallowed request field: {arg}'}), 400
                
        for field in req_fields_list_valid:
            val = request.args.get(field)
            if val:
                filter_where_clause += f" AND `{field}` = %s"
                filter_params.append(val)

        # 5. Build Dynamic SQL safely
        # Limit response fields to what was configured
        select_clause = "*"
        if res_fields_list_valid:
            select_clause = ", ".join([f"`{f}`" for f in res_fields_list_valid])

        # Whitelist databases check again (backend layer)
        if db_name not in ALLOWED_DATABASES:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Database not in whitelist', 'request_id': request_id}), 403

        # Construct final SQL
        final_sql = f"SELECT {select_clause} FROM `{db_name}`.`{source_name}` WHERE {scope_where_clause} {filter_where_clause} LIMIT 1000"
        
        all_params = scope_params + filter_params
        
        # 6. Execute and Return
        cursor.execute(final_sql, all_params)
        rows_data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        
        results = toJson(rows_data, columns)
        
        # Clean up results (handle dates etc)
        for row in results:
            for k, v in row.items():
                if hasattr(v, 'isoformat'): # Handle datetime objects
                    row[k] = v.isoformat()

        log_api_usage(user_id, 'API Invoked Successfully', 200)

        cursor.close()
        conn.close()

        response = jsonify({
            'status': 'success',
            'dataset_id': dataset_id,
            'dataset_name': service_name,
            'total_rows': len(results),
            'rows': results
        })
        
        if deprecated_transport:
            response.headers['X-Deprecation-Warning'] = 'Query string API keys are deprecated. Use x-api-key header.'
            
        return response

    except Exception as e:
        import traceback
        error_msg = str(e)
        current_app.logger.error(f"[{request_id}] API Error: {traceback.format_exc()}")
        if cursor and conn:
            try:
                cursor.close()
                conn.close()
            except: pass
            
        if "Unknown column" in error_msg:
            return jsonify({'status': 'error', 'message': 'Unknown field provided in request or configuration'}), 400
            
        return jsonify({'status': 'error', 'message': 'An internal error occurred processing your request', 'request_id': request_id}), 500

# ============================================================
# API Configuration & Management Endpoints
# ============================================================

# Hardcoded whitelist of databases the admin is allowed to expose via API
ALLOWED_DATABASES = ['psu_backend', 'datalake', 'default', 'datax_db_3003']

@app.route('/getAvailableDatabases', methods=['POST'])
@require_admin
def getAvailableDatabases():
    """Return the whitelisted databases."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Allow any logged in user to see available databases for configuration
        # Admin check handled by decorator
        return jsonify({'status': 'success', 'data': ALLOWED_DATABASES})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/getAvailableTables', methods=['POST'])
@require_admin
def getAvailableTables():
    """Return tables and views for a whitelisted database."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Allow any logged in user to see tables for configuration
        # Admin check handled by decorator

        db_name = dataInput.get('db_name', '')
        if db_name not in ALLOWED_DATABASES:
            return jsonify({"status": "Error: Database not in whitelist"})

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT TABLE_NAME, TABLE_TYPE 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = %s 
                 ORDER BY TABLE_NAME"""
        cursor.execute(sql, (db_name,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        result = []
        for row in data:
            source_type = 'view' if row[1] == 'VIEW' else 'table'
            result.append({'name': row[0], 'type': source_type})
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/getTableColumns', methods=['POST'])
@require_admin
def getTableColumns():
    """Return column metadata for a table/view in a whitelisted database."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Allow any logged in user to see columns for configuration
        # Admin check handled by decorator

        db_name = dataInput.get('db_name', '')
        table_name = dataInput.get('table_name', '')
        if db_name not in ALLOWED_DATABASES:
            return jsonify({"status": "Error: Database not in whitelist"})

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                 FROM INFORMATION_SCHEMA.COLUMNS
                 WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                 ORDER BY ORDINAL_POSITION"""
        cursor.execute(sql, (db_name, table_name))
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        result = [{'name': row[0], 'type': row[1], 'nullable': row[2]} for row in data]
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/saveApiConfig', methods=['POST'])
@require_admin
def saveApiConfig():
    """Save advanced API configuration fields for a service."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Loosen check for presentation
        # Admin check handled by decorator

        service_id = dataInput['service_id']
        api_type = dataInput.get('api_type', 'general')
        api_endpoint = dataInput.get('api_endpoint', '')
        api_db_name = dataInput.get('api_db_name', '')
        api_source_type = dataInput.get('api_source_type', 'table')
        api_source_name = dataInput.get('api_source_name', '')
        api_request_fields = dataInput.get('api_request_fields', '[]')
        api_response_fields = dataInput.get('api_response_fields', '[]')
        api_enabled_raw = dataInput.get('api_enabled', 'true')
        api_enabled = 1 if api_enabled_raw in ['true', '1', True] else 0

        # Validate db_name against whitelist
        if api_db_name and api_db_name not in ALLOWED_DATABASES:
            return jsonify({"status": "Error: Database not in whitelist"})

        # Ensure JSON strings
        if isinstance(api_request_fields, list):
            api_request_fields = json.dumps(api_request_fields)
        if isinstance(api_response_fields, list):
            api_response_fields = json.dumps(api_response_fields)

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """UPDATE service SET 
                    api_enabled = %s,
                    api_type = %s,
                    api_endpoint = %s,
                    api_db_name = %s,
                    api_source_type = %s,
                    api_source_name = %s,
                    api_request_fields = %s,
                    api_response_fields = %s
                 WHERE service_id = %s"""
        cursor.execute(sql, (
            api_enabled, api_type, api_endpoint, api_db_name,
            api_source_type, api_source_name,
            api_request_fields, api_response_fields,
            service_id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/getApiCredentials', methods=['POST'])
@require_admin
def getApiCredentials():
    """Get credentials (keys) for a specific service."""
    try:
        dataInput = request.json
        service_id = dataInput['service_id']
        
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT c.credential_id, c.service_id, c.user_id, c.public_key_id, c.key_last_four, c.status, c.created_at, c.expires_at,
                        u.username, u.firstname, u.lastname,
                        s.scope_json
                 FROM api_credentials c
                 LEFT JOIN user u ON c.user_id = u.user_id
                 LEFT JOIN api_scopes s ON s.credential_id = c.credential_id
                 WHERE c.service_id = %s
                 ORDER BY c.created_at DESC"""
        cursor.execute(sql, (service_id,))
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        cursor.close()
        conn.close()

        # Parse scope_json from string to object
        for row in result:
            if row.get('scope_json'):
                try:
                    row['scope_json'] = json.loads(row['scope_json']) if isinstance(row['scope_json'], str) else row['scope_json']
                except:
                    pass
            if row.get('created_at'):
                row['created_at'] = str(row['created_at'])
            if row.get('expires_at'):
                row['expires_at'] = str(row['expires_at'])

        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/addApiCredential', methods=['POST'])
@require_admin
def addApiCredential():
    """Create a new API credential (key) for a user on a service, optionally with a scope."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Loosen check for presentation
        # Admin check handled by decorator

        service_id = dataInput['service_id']
        target_user_id = dataInput['target_user_id']
        secret_key = dataInput.get('secret_key', '')
        scope_json = dataInput.get('scope_json', None)
        expires_at = dataInput.get('expires_at', None)

        # Generate secure key
        import secrets
        import string
        import hashlib
        alphabet = string.ascii_letters + string.digits
        public_key_id = 'datax_' + ''.join(secrets.choice(alphabet) for i in range(12))
        secret_part = secrets.token_hex(16)
        full_secret_key = f"{public_key_id}.{secret_part}"
        
        secret_hash = hashlib.sha256(full_secret_key.encode('utf-8')).hexdigest()
        key_last_four = full_secret_key[-4:]
        
        conn = mysql.connect()
        cursor = conn.cursor()

        # Removed active credential check to allow multiple keys per user

        # Insert credential with hash and last four
        if expires_at:
            sql_insert = "INSERT INTO api_credentials (service_id, user_id, public_key_id, secret_hash, key_last_four, status, expires_at) VALUES (%s, %s, %s, %s, %s, 'active', %s)"
            cursor.execute(sql_insert, (service_id, target_user_id, public_key_id, secret_hash, key_last_four, expires_at))
        else:
            sql_insert = "INSERT INTO api_credentials (service_id, user_id, public_key_id, secret_hash, key_last_four, status) VALUES (%s, %s, %s, %s, %s, 'active')"
            cursor.execute(sql_insert, (service_id, target_user_id, public_key_id, secret_hash, key_last_four))
        credential_id = cursor.lastrowid

        # Insert scope if provided
        if scope_json:
            scope_str = json.dumps(scope_json) if isinstance(scope_json, (dict, list)) else scope_json
            sql_scope = "INSERT INTO api_scopes (credential_id, scope_json) VALUES (%s, %s)"
            cursor.execute(sql_scope, (credential_id, scope_str))

        conn.commit()
        cursor.close()
        conn.close()
        log_api_audit('create_credential', target_user_id=target_user_id, service_id=service_id, credential_id=credential_id)
        return jsonify({'status': 'success', 'credential_id': credential_id, 'secret_key': full_secret_key})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/extendApiCredential', methods=['POST'])
@require_admin
def extendApiCredential():
    """Extend or set the expiration date for an API key."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Loosen check for presentation
        # Admin check handled by decorator

        credential_id = dataInput['credential_id']
        expires_at = dataInput.get('expires_at', None)

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Validate credential exists and is active? We allow extending revoked keys as well.
        if expires_at:
            cursor.execute("UPDATE api_credentials SET expires_at = %s WHERE credential_id = %s", (expires_at, credential_id))
        else:
            cursor.execute("UPDATE api_credentials SET expires_at = NULL WHERE credential_id = %s", (credential_id,))
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/revokeApiCredential', methods=['POST'])
@require_admin
def revokeApiCredential():
    """Revoke (soft-delete) an API credential."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Loosen check for presentation
        # Admin check handled by decorator

        credential_id = dataInput['credential_id']
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "UPDATE api_credentials SET status = 'revoked' WHERE credential_id = %s"
        cursor.execute(sql, (credential_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/pauseApiCredential', methods=['POST'])
@require_admin
def pauseApiCredential():
    """Pause an API credential temporarily."""
    try:
        dataInput = request.json
        credential_id = dataInput['credential_id']
        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM api_credentials WHERE credential_id = %s", (credential_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'status': 'error', 'message': 'Credential not found'})
        if row[0] == 'revoked':
            return jsonify({'status': 'error', 'message': 'Cannot pause a revoked credential'})
            
        sql = "UPDATE api_credentials SET status = 'paused' WHERE credential_id = %s"
        cursor.execute(sql, (credential_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/resumeApiCredential', methods=['POST'])
@require_admin
def resumeApiCredential():
    """Resume (un-pause) an API credential."""
    try:
        dataInput = request.json
        credential_id = dataInput['credential_id']
        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT status FROM api_credentials WHERE credential_id = %s", (credential_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'status': 'error', 'message': 'Credential not found'})
        if row[0] == 'revoked':
            return jsonify({'status': 'error', 'message': 'Cannot resume a revoked credential'})

        sql = "UPDATE api_credentials SET status = 'active' WHERE credential_id = %s"
        cursor.execute(sql, (credential_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/deleteApiCredential', methods=['POST'])
@require_admin
def deleteApiCredential():
    """Permanently delete an API credential and its associated scopes."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Loosen check for presentation
        # Admin check handled by decorator

        credential_id = dataInput['credential_id']
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # 1. Delete associated scopes first
        cursor.execute("DELETE FROM api_scopes WHERE credential_id = %s", (credential_id,))
        
        # 2. Delete the credential
        sql = "DELETE FROM api_credentials WHERE credential_id = %s"
        cursor.execute(sql, (credential_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/updateApiScope', methods=['POST'])
@require_admin
def updateApiScope():
    """Update or insert scope for an existing credential."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Loosen check for presentation
        # Admin check handled by decorator

        credential_id = dataInput['credential_id']
        scope_json = dataInput['scope_json']
        scope_str = json.dumps(scope_json) if isinstance(scope_json, dict) else scope_json

        conn = mysql.connect()
        cursor = conn.cursor()

        # Check existing scope
        cursor.execute("SELECT scope_id FROM api_scopes WHERE credential_id = %s", (credential_id,))
        existing = cursor.fetchall()

        if existing:
            sql = "UPDATE api_scopes SET scope_json = %s WHERE credential_id = %s"
            cursor.execute(sql, (scope_str, credential_id))
        else:
            sql = "INSERT INTO api_scopes (credential_id, scope_json) VALUES (%s, %s)"
            cursor.execute(sql, (credential_id, scope_str))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/getAvailableUsers', methods=['POST'])
@require_admin
def getAvailableUsers():
    """List users for credential assignment."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Loosen check for presentation
        # Admin check handled by decorator

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT user_id, username, firstname, lastname FROM user WHERE status_id != 7 ORDER BY username"
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/getApiMonitorStats', methods=['POST'])
@require_admin
def getApiMonitorStats():
    """Aggregated statistics for API usage with date filtering."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Admin check handled by decorator

        start_date = dataInput.get('start_date')
        end_date = dataInput.get('end_date')
        
        where_clause = "WHERE type='API'"
        params = []
        if start_date:
            where_clause += " AND create_at >= %s"
            params.append(start_date)
        if end_date:
            # Append end of day time if only date is provided
            if len(end_date) == 10: end_date += " 23:59:59"
            where_clause += " AND create_at <= %s"
            params.append(end_date)

        conn = mysql.connect()
        cursor = conn.cursor()
        
        # 1. Total Requests in period
        cursor.execute(f"SELECT count(*) FROM log {where_clause}", tuple(params))
        total_requests = cursor.fetchone()[0]
        
        # 2. Success vs Failed in period
        success_where = where_clause + " AND log_detail LIKE '[200]%'"
        cursor.execute(f"SELECT count(*) FROM log {success_where}", tuple(params))
        success_count = cursor.fetchone()[0]
        
        # 3. Unique IPs in period
        cursor.execute(f"SELECT count(DISTINCT ip) FROM log {where_clause}", tuple(params))
        unique_ips = cursor.fetchone()[0]

        # 4. Activity trend
        # If the range is > 60 days, group by MONTH instead of DATE
        group_by = "DATE(create_at)"
        limit_clause = "LIMIT 31" # Default to 1 month of daily data
        
        # If no dates, default trend to 7 days
        if not start_date and not end_date:
            where_trend = where_clause + " AND create_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
            limit_clause = "LIMIT 7"
        else:
            where_trend = where_clause
            limit_clause = "LIMIT 100" # Allow more for custom range

        cursor.execute(f"""
            SELECT {group_by} as log_date, count(*) as count 
            FROM log 
            {where_trend}
            GROUP BY {group_by}
            ORDER BY log_date DESC
            {limit_clause}
        """, tuple(params))
        
        trend_data = cursor.fetchall()
        trend = [{"date": str(d[0]), "count": d[1]} for d in trend_data]

        cursor.close()
        conn.close()
        return jsonify({
            'status': 'success',
            'summary': {
                'total_requests': total_requests,
                'success_count': success_count,
                'failed_count': total_requests - success_count,
                'unique_ips': unique_ips
            },
            'trend': trend[::-1]
        })
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/getApiMonitorLogs', methods=['POST'])
@require_admin
def getApiMonitorLogs():
    """Detailed list of API logs with date filtering and pagination."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        # Admin check handled by decorator

        limit = dataInput.get('limit', 50)
        offset = dataInput.get('offset', 0)
        start_date = dataInput.get('start_date')
        end_date = dataInput.get('end_date')
        
        where_clause = "WHERE type='API'"
        params = []
        if start_date:
            where_clause += " AND create_at >= %s"
            params.append(start_date)
        if end_date:
            if len(end_date) == 10: end_date += " 23:59:59"
            where_clause += " AND create_at <= %s"
            params.append(end_date)
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = f"SELECT log_id, user_id, log_detail, path, ip, country, create_at FROM log {where_clause} ORDER BY create_at DESC LIMIT %s OFFSET %s"
        
        full_params = tuple(params) + (limit, offset)
        cursor.execute(sql, full_params)
        
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
        for row in result:
            if row.get('create_at'):
                row['create_at'] = str(row['create_at'])

        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result, 'limit': limit, 'offset': offset})
    except Exception as e:
        import traceback
        current_app.logger.error(f"API Management Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500


@app.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # 1. Datasets Count
        cursor.execute("SELECT COUNT(*) as count FROM service WHERE status = 'Active'")
        datasets_count = cursor.fetchone()[0]
        
        # 2. Active API Keys Count
        cursor.execute("SELECT COUNT(*) as count FROM api_credentials WHERE status = 'active'")
        api_keys_count = cursor.fetchone()[0]
        
        # 3. API Hits This Month
        cursor.execute("SELECT COUNT(*) as count FROM log WHERE type = 'API' AND MONTH(create_at) = MONTH(CURRENT_DATE()) AND YEAR(create_at) = YEAR(CURRENT_DATE())")
        api_calls_count = cursor.fetchone()[0]
        
        # 4. Downloads Count (Mock logic based on logs)
        cursor.execute("SELECT COUNT(*) as count FROM log WHERE log_detail LIKE '%Download%' AND MONTH(create_at) = MONTH(CURRENT_DATE())")
        downloads_count = cursor.fetchone()[0]
        
        # 5. Recent Activity (Last 5 logs)
        cursor.execute("SELECT log_detail as text, create_at as time, type FROM log ORDER BY create_at DESC LIMIT 5")
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        recent_activity = toJson(data, columns)
        
        # Format time to relative string for now (simple version)
        import datetime
        now = datetime.datetime.now()
        for activity in recent_activity:
             # Convert time to string or handle as needed
             activity['time'] = str(activity['time'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'stats': [
                { 'label': 'Datasets Accessed', 'value': str(datasets_count), 'trend': '+0%', 'color': '#22c55e', 'icon': 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2z' },
                { 'label': 'API Keys Active', 'value': str(api_keys_count), 'trend': '+0%', 'color': '#3b82f6', 'icon': 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z' },
                { 'label': 'API Calls This Month', 'value': str(api_calls_count), 'trend': '+0%', 'color': '#8b5cf6', 'icon': 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16' },
                { 'label': 'Downloads This Month', 'value': str(downloads_count), 'trend': '+0%', 'color': '#ef4444', 'icon': 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4' }
            ],
            'recentActivity': recent_activity
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/dashboard/usage_chart', methods=['GET'])
def get_usage_chart():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Aggregate logs by day for the last 7 days
        sql = """
            SELECT DATE(create_at) as date, COUNT(*) as count 
            FROM log 
            WHERE create_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
            GROUP BY DATE(create_at)
            ORDER BY date ASC
        """
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        chart_data = toJson(data, columns)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': chart_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/requestDatasetPermission', methods=['POST'])
def request_dataset_permission():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        user_id = user_data.get('user_id')
        service_id = dataInput.get('service_id')
        fields = dataInput.get('fields', [])
        reason = dataInput.get('reason', '')
        
        if not user_id or not service_id:
            return jsonify({'status': 'error', 'message': 'Missing user or service ID'}), 400
            
        fields_json = json.dumps(fields)
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check if there is already a Pending request
        sql_check = "SELECT request_id FROM dataset_permission_requests WHERE user_id = %s AND service_id = %s AND status = 'Pending'"
        cursor.execute(sql_check, (user_id, service_id))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'คุณได้ส่งคำขอที่อยู่ระหว่างรอดำเนินการสำหรับชุดข้อมูลนี้แล้ว'}), 400
            
        # Insert request
        sql_insert = """INSERT INTO dataset_permission_requests (user_id, service_id, fields_json, reason, status) 
                        VALUES (%s, %s, %s, %s, 'Pending')"""
        cursor.execute(sql_insert, (user_id, service_id, fields_json, reason))
        conn.commit()
        
        # Log the action
        logAction(user_id, '/requestDatasetPermission', f'Request dataset permission for service_id {service_id}', 'info')
        
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'ส่งคำขอเข้าถึงข้อมูลเรียบร้อยแล้ว'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/getPendingDatasetRequests', methods=['POST'])
def get_pending_dataset_requests():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        
        # Verify admin status
        if not checkUserIsAdmin(user_data) and str(user_data.get('previlage_id')) != '1':
            return jsonify({'status': 'error', 'message': 'Permission Denied'}), 403
            
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT r.request_id, r.user_id, r.service_id, r.fields_json, r.reason, r.status, r.created_at,
                        u.username, u.firstname, u.lastname, u.email,
                        s.service_name, s.dataset_id
                 FROM dataset_permission_requests r
                 JOIN user u ON r.user_id = u.user_id
                 JOIN service s ON r.service_id = s.service_id
                 WHERE r.status = 'Pending'
                 ORDER BY r.created_at DESC"""
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
        # Serialize fields and dates
        for row in result:
            row['created_at'] = str(row['created_at'])
            try:
                row['fields'] = json.loads(row['fields_json']) if row['fields_json'] else []
            except:
                row['fields'] = []
                
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/approveDatasetRequest', methods=['POST'])
def approve_dataset_request():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        request_id = dataInput.get('request_id')
        
        if not checkUserIsAdmin(user_data) and str(user_data.get('previlage_id')) != '1':
            return jsonify({'status': 'error', 'message': 'Permission Denied'}), 403
            
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Get request info
        sql_req = "SELECT user_id, service_id FROM dataset_permission_requests WHERE request_id = %s"
        cursor.execute(sql_req, (request_id,))
        req_row = cursor.fetchone()
        
        if not req_row:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Request not found'}), 404
            
        target_user_id, service_id = req_row
        
        # Update request status
        sql_update = "UPDATE dataset_permission_requests SET status = 'Approved' WHERE request_id = %s"
        cursor.execute(sql_update, (request_id,))
        
        # Grant access in service_user_access
        sql_grant = "INSERT IGNORE INTO service_user_access (service_id, user_id) VALUES (%s, %s)"
        cursor.execute(sql_grant, (service_id, target_user_id))
        
        conn.commit()
        
        # Log action
        logAction(user_data.get('user_id'), '/approveDatasetRequest', f'Approved request {request_id} for user_id {target_user_id} on service_id {service_id}', 'info')
        
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'อนุมัติคำขอเข้าถึงข้อมูลเรียบร้อยแล้ว'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/rejectDatasetRequest', methods=['POST'])
def reject_dataset_request():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        request_id = dataInput.get('request_id')
        
        if not checkUserIsAdmin(user_data) and str(user_data.get('previlage_id')) != '1':
            return jsonify({'status': 'error', 'message': 'Permission Denied'}), 403
            
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Get request info
        sql_req = "SELECT user_id, service_id FROM dataset_permission_requests WHERE request_id = %s"
        cursor.execute(sql_req, (request_id,))
        req_row = cursor.fetchone()
        
        if not req_row:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Request not found'}), 404
            
        target_user_id, service_id = req_row
        
        # Update request status
        sql_update = "UPDATE dataset_permission_requests SET status = 'Rejected' WHERE request_id = %s"
        cursor.execute(sql_update, (request_id,))
        
        conn.commit()
        
        # Log action
        logAction(user_data.get('user_id'), '/rejectDatasetRequest', f'Rejected request {request_id} for user_id {target_user_id} on service_id {service_id}', 'info')
        
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'ปฏิเสธคำขอเข้าถึงข้อมูลเรียบร้อยแล้ว'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/getAllApiScopes', methods=['POST'])
@require_admin
def getAllApiScopes():
    """Get all scopes across all services."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        if not user_data.get("user_id") and not checkUserIsAdmin(user_data):
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        conn = mysql.connect()
        cursor = conn.cursor()
        sql = """SELECT c.credential_id, c.service_id, c.user_id, c.status, c.public_key_id, c.key_last_four, c.expires_at,
                        u.username, u.firstname, u.lastname,
                        s.scope_json, s.scope_id,
                        srv.service_name, srv.dataset_id, srv.db_name, srv.source_name
                 FROM api_credentials c
                 JOIN user u ON c.user_id = u.user_id
                 JOIN api_scopes s ON s.credential_id = c.credential_id
                 JOIN service srv ON c.service_id = srv.service_id
                 ORDER BY s.scope_id DESC"""
        cursor.execute(sql)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
        for row in result:
            if row.get('scope_json'):
                try:
                    row['scope_json'] = json.loads(row['scope_json']) if isinstance(row['scope_json'], str) else row['scope_json']
                except:
                    pass

        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/saveApiScopeForUser', methods=['POST'])
@require_admin
def saveApiScopeForUser():
    """Upsert a credential and save its scope."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        if not user_data.get("user_id") and not checkUserIsAdmin(user_data):
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        service_id = dataInput['service_id']
        target_user_id = dataInput['target_user_id']
        scope_json = dataInput['scope_json']
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT credential_id FROM api_credentials WHERE service_id=%s AND user_id=%s", (service_id, target_user_id))
        cred = cursor.fetchone()
        
        if cred:
            credential_id = cred[0]
        else:
            import uuid
            secret_key = uuid.uuid4().hex
            sql_insert = "INSERT INTO api_credentials (service_id, user_id, secret_key, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_insert, (service_id, target_user_id, secret_key, 'Active'))
            credential_id = cursor.lastrowid
            
        scope_str = json.dumps(scope_json) if isinstance(scope_json, (dict, list)) else scope_json
        
        cursor.execute("SELECT scope_id FROM api_scopes WHERE credential_id=%s", (credential_id,))
        if cursor.fetchone():
            cursor.execute("UPDATE api_scopes SET scope_json=%s WHERE credential_id=%s", (scope_str, credential_id))
        else:
            cursor.execute("INSERT INTO api_scopes (credential_id, scope_json) VALUES (%s, %s)", (credential_id, scope_str))
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/deleteApiScopeForUser', methods=['POST'])
@require_admin
def deleteApiScopeForUser():
    """Delete a scope."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        if not user_data.get("user_id") and not checkUserIsAdmin(user_data):
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        credential_id = dataInput['credential_id']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM api_scopes WHERE credential_id=%s", (credential_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==========================================
# NOTIFICATIONS API
# ==========================================

def init_notifications_table():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
          id int(11) NOT NULL AUTO_INCREMENT,
          user_id int(11) NOT NULL,
          type varchar(50) NOT NULL,
          message text NOT NULL,
          is_read tinyint(1) DEFAULT 0,
          created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (id),
          KEY user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error init notifications table", e)

# Run init on load
init_notifications_table()

def add_notification(user_id, type_str, message):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (user_id, type_str, message))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error adding notification:", e)

@app.route('/notifications', methods=['POST'])
def getNotifications():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        user_id = user_data.get("user_id")
        if not user_id:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
            
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, message, is_read, created_at FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 50", (user_id,))
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/notifications/unread-count', methods=['POST'])
def getUnreadCount():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        user_id = user_data.get("user_id")
        if not user_id:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
            
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id=%s AND is_read=0", (user_id,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'data': {'unread_count': count}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/notifications/<int:notif_id>/read', methods=['POST'])
def markRead(notif_id):
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        user_id = user_data.get("user_id")
        if not user_id:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
            
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read=1 WHERE id=%s AND user_id=%s", (notif_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/notifications/read-all', methods=['POST'])
def markReadAll():
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        user_id = user_data.get("user_id")
        if not user_id:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
            
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read=1 WHERE user_id=%s AND is_read=0", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

