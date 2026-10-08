from flask import request, jsonify
from ServiceConfig import *
from .validators import validate_dataset_masters
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
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx', 'xls', 'zip', 'xml', 'json'}

def safe_unicode_filename(filename):
    if not filename:
        return 'unnamed_file'
    fname = os.path.basename(filename).strip()
    fname = re.sub(r'[/\\:\*\?"<>\|\x00]', '_', fname)
    return fname or 'unnamed_file'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_remove_uploaded_file(fname):
    if fname:
        target = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.exists(target) and os.path.isfile(target):
            try:
                os.remove(target)
            except OSError:
                pass


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
    except Exception as e:
        current_app.logger.error(f"Audit Log Error: {e}")

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
                
                # Wave 2 Masters
                l2e_group_id_raw = request.form.get('l2e_group_id', '')
                l2e_group_id = int(l2e_group_id_raw) if l2e_group_id_raw else None
                source_system_id_raw = request.form.get('source_system_id', '')
                source_system_id = int(source_system_id_raw) if source_system_id_raw else None
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
                if date_start == '': date_start = None
                if date_updated == '': date_updated = None
                if geo_published_date == '': geo_published_date = None
                if geo_reference_time == '': geo_reference_time = None


                conn = mysql.connect()
                cursor = conn.cursor()
                
                is_valid, err_msg = validate_dataset_masters(cursor, category, organization, access_type, l2e_group_id, source_system_id, dataset_id)
                if not is_valid:
                    cursor.close()
                    conn.close()
                    return jsonify({"status": err_msg}), 400

                # Check organization binding for Role 3
                user_data = getattr(request, 'current_user', {})
                previlage_id = str(user_data.get('previlage_id', ''))
                org_id = user_data.get('org_id')
                if previlage_id == '3' and org_id:
                    cursor.execute("SELECT org_name FROM organization WHERE org_id = %s", (org_id,))
                    org_row = cursor.fetchone()
                    user_org_name = org_row[0] if org_row else ''
                    if user_org_name != organization:
                        cursor.close()
                        conn.close()
                        return jsonify({"status": "คุณมีสิทธิ์จัดการชุดข้อมูลเฉพาะของหน่วยงานที่คุณสังกัดเท่านั้น"}), 403

                if not dataset_id:
                    cursor.close()
                    conn.close()
                    return jsonify({"status": "Dataset ID is required for new datasets"}), 400

                if not source_system_id:
                    cursor.close()
                    conn.close()
                    return jsonify({"status": "Source System is required for new datasets"}), 400
                    
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
                        filename = f"ds_{dataset_id}_{safe_unicode_filename(data_file.filename)}"
                        data_file.save(os.path.join(UPLOAD_FOLDER, filename))
                        file_path = filename

                    dict_file = request.files.get('dictionary_file')
                    dict_path = None
                    if dict_file and allowed_file(dict_file.filename):
                        filename = f"dict_{dataset_id}_{safe_unicode_filename(dict_file.filename)}"
                        dict_file.save(os.path.join(UPLOAD_FOLDER, filename))
                        dict_path = filename

                    samp_file = request.files.get('sampling_file')
                    samp_path = None
                    if samp_file and allowed_file(samp_file.filename):
                        filename = f"samp_{dataset_id}_{safe_unicode_filename(samp_file.filename)}"
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
                        geo_reference_time, geo_published_date,
                        l2e_group_id, source_system_id
                    ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    
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
                        geo_reference_time, geo_published_date,
                        l2e_group_id, source_system_id
                    ))
                    conn.commit()
                    
                    # Notify All Users about the new dataset
                    try:
                        from .email_service import notify_dataset_created
                        cursor.execute("SELECT email FROM user WHERE status_account = 'active' AND email IS NOT NULL")
                        all_emails = [row[0] for row in cursor.fetchall() if row[0]]
                        if all_emails:
                            notify_dataset_created(service_name, description, all_emails)
                    except Exception as e:
                        current_app.logger.error(f"Error sending dataset creation email: {e}")
                        
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'insert new service success'})
                else:
                    cursor.close()
                    conn.close()
                    return jsonify({"status":"Error: Dataset Name หรือ Dataset ID ซ้ำ"})
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
                
                # Wave 2 Masters
                l2e_group_id_raw = request.form.get('l2e_group_id')
                l2e_group_id = int(l2e_group_id_raw) if l2e_group_id_raw else None
                source_system_id_raw = request.form.get('source_system_id')
                source_system_id = int(source_system_id_raw) if source_system_id_raw else None
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
                if date_start == '': date_start = None
                if date_updated == '': date_updated = None
                if geo_published_date == '': geo_published_date = None
                if geo_reference_time == '': geo_reference_time = None


                conn = mysql.connect()
                cursor = conn.cursor()
                
                is_valid, err_msg = validate_dataset_masters(cursor, category, organization, access_type, l2e_group_id, source_system_id, dataset_id)
                if not is_valid:
                    cursor.close()
                    conn.close()
                    return jsonify({"status": err_msg}), 400
                    
                sql = "SELECT service_id, dataset_id, service_url, file_path, excel_file_path, data_dictionary_path, data_sampling_path, api_response_fields, api_enabled FROM service WHERE service_id = %s"
                cursor.execute(sql, (service_id,))
                service_result = cursor.fetchall()
                
                if len(service_result) != 0:
                    svc_row_info = service_result[0]
                    existing_dataset_id = svc_row_info[1]
                    existing_service_url = svc_row_info[2]
                    old_file_path = svc_row_info[3]
                    old_excel_path = svc_row_info[4]
                    old_dict_path = svc_row_info[5]
                    old_samp_path = svc_row_info[6]
                    old_api_res_fields = svc_row_info[7] if len(svc_row_info) > 7 else None
                    has_existing_api_fields = bool(old_api_res_fields and str(old_api_res_fields).strip() not in ['', '[]', 'null', 'None'])

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
                    if request.form.get('l2e_group_id') is not None: fields.append("l2e_group_id = %s"); values.append(l2e_group_id)
                    if request.form.get('source_system_id') is not None: fields.append("source_system_id = %s"); values.append(source_system_id)
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
                    file_type = request.form.get('file_type')
                    if data_file:
                        ext = data_file.filename.rsplit('.', 1)[-1].lower() if '.' in data_file.filename else ''
                        if file_type == 'dictionary' and ext not in ['csv', 'xls', 'xlsx']:
                            cursor.close()
                            conn.close()
                            return jsonify({"status": "รูปแบบไฟล์ Data Dictionary ไม่ถูกต้อง (รองรับเฉพาะ CSV, Excel)"}), 400
                        elif file_type == 'zip' and ext != 'zip':
                            cursor.close()
                            conn.close()
                            return jsonify({"status": "รูปแบบไฟล์ Sampling ไม่ถูกต้อง (รองรับเฉพาะ ZIP)"}), 400
                        elif file_type == 'main' and ext not in ['csv', 'xls', 'xlsx', 'xml', 'json']:
                            cursor.close()
                            conn.close()
                            return jsonify({"status": "รูปแบบไฟล์ Data File For API ไม่ถูกต้อง (รองรับเฉพาะ CSV, Excel, XML, JSON)"}), 400
                        elif file_type == 'excel' and ext not in ['xls', 'xlsx']:
                            cursor.close()
                            conn.close()
                            return jsonify({"status": "รูปแบบไฟล์ Dataset (Excel) ไม่ถูกต้อง (รองรับเฉพาะ Excel)"}), 400
                        elif not allowed_file(data_file.filename):
                            cursor.close()
                            conn.close()
                            return jsonify({"status": "นามสกุลไฟล์ไม่ได้รับอนุญาต"}), 400
                            
                        clean_fname = safe_unicode_filename(data_file.filename)
                        filename = f"ds_{service_id}_{clean_fname}"
                        save_path = os.path.join(UPLOAD_FOLDER, filename)
                        data_file.save(save_path)

                        if file_type == 'dictionary':
                            try:
                                import pandas as pd
                                if ext == 'csv':
                                    try:
                                        df = pd.read_csv(save_path, nrows=5, encoding='utf-8-sig')
                                    except UnicodeDecodeError:
                                        df = pd.read_csv(save_path, nrows=5, encoding='cp874')
                                else:
                                    df = pd.read_excel(save_path, nrows=5)
                                columns = [str(c).strip() for c in df.columns if str(c).strip() and not str(c).startswith('Unnamed:')]
                                if not columns:
                                    raise ValueError('ไม่พบคอลัมน์ในไฟล์ Data Dictionary')
                            except Exception as ve:
                                try:
                                    os.remove(save_path)
                                except OSError:
                                    pass
                                cursor.close()
                                conn.close()
                                return jsonify({"status": f"ไฟล์ Data Dictionary ไม่ผ่านการตรวจสอบ: {str(ve)[:150]}"}), 400

                            fields.append("data_dictionary_path = %s")
                            values.append(filename)
                            if not has_existing_api_fields:
                                fields.append("api_response_fields = %s")
                                values.append(json.dumps(columns))

                            if not old_file_path and ext in ['csv', 'xls', 'xlsx']:
                                fields.append("file_path = %s")
                                values.append(filename)
                                if ext in ['xls', 'xlsx'] and not old_excel_path:
                                    fields.append("excel_file_path = %s")
                                    values.append(filename)

                            if old_dict_path and old_dict_path != filename and old_dict_path != old_file_path:
                                safe_remove_uploaded_file(old_dict_path)

                        elif file_type == 'main':
                            try:
                                columns = []
                                if ext == 'csv':
                                    import pandas as pd
                                    try:
                                        df = pd.read_csv(save_path, nrows=5, encoding='utf-8-sig')
                                    except UnicodeDecodeError:
                                        df = pd.read_csv(save_path, nrows=5, encoding='cp874')
                                    columns = [str(c).strip() for c in df.columns if str(c).strip() and not str(c).startswith('Unnamed:')]
                                elif ext in ['xls', 'xlsx']:
                                    import pandas as pd
                                    df = pd.read_excel(save_path, nrows=5)
                                    columns = [str(c).strip() for c in df.columns if str(c).strip() and not str(c).startswith('Unnamed:')]
                                elif ext == 'json':
                                    with open(save_path, 'r', encoding='utf-8') as jf:
                                        jdata = json.load(jf)
                                    if isinstance(jdata, list) and len(jdata) > 0 and isinstance(jdata[0], dict):
                                        columns = list(jdata[0].keys())
                                    elif isinstance(jdata, dict):
                                        if 'data' in jdata and isinstance(jdata['data'], list) and len(jdata['data']) > 0 and isinstance(jdata['data'][0], dict):
                                            columns = list(jdata['data'][0].keys())
                                        elif 'rows' in jdata and isinstance(jdata['rows'], list) and len(jdata['rows']) > 0 and isinstance(jdata['rows'][0], dict):
                                            columns = list(jdata['rows'][0].keys())
                                        elif 'items' in jdata and isinstance(jdata['items'], list) and len(jdata['items']) > 0 and isinstance(jdata['items'][0], dict):
                                            columns = list(jdata['items'][0].keys())
                                        else:
                                            columns = list(jdata.keys())
                                    columns = [str(c).strip() for c in columns if str(c).strip()]
                                elif ext == 'xml':
                                    import xml.etree.ElementTree as ET
                                    tree = ET.parse(save_path)
                                    root = tree.getroot()
                                    found_cols = []
                                    for child in root:
                                        for sub in child:
                                            tag = sub.tag.split('}')[-1] if '}' in sub.tag else sub.tag
                                            if tag not in found_cols:
                                                found_cols.append(tag)
                                        if not found_cols and child.attrib:
                                            for k in child.attrib.keys():
                                                if k not in found_cols:
                                                    found_cols.append(k)
                                    if not found_cols:
                                        for child in root:
                                            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                                            if tag not in found_cols:
                                                found_cols.append(tag)
                                    columns = [str(c).strip() for c in found_cols if str(c).strip()]

                                if not columns:
                                    raise ValueError('ไม่สามารถอ่าน Header หรือฟิลด์ข้อมูลจากไฟล์ได้')
                            except Exception as ve:
                                try:
                                    os.remove(save_path)
                                except OSError:
                                    pass
                                cursor.close()
                                conn.close()
                                return jsonify({"status": f"ไฟล์ Data File For API ไม่ผ่านการตรวจสอบ: {str(ve)[:150]}"}), 400

                            if ext in ['xls', 'xlsx']:
                                fields.append("excel_file_path = %s")
                                values.append(filename)
                                fields.append("file_path = %s")
                                values.append(filename)
                                if old_excel_path and old_excel_path != filename:
                                    safe_remove_uploaded_file(old_excel_path)
                                if old_file_path and old_file_path != filename and old_file_path != old_excel_path:
                                    safe_remove_uploaded_file(old_file_path)
                            else:
                                fields.append("file_path = %s")
                                values.append(filename)
                                if old_file_path and old_file_path != filename:
                                    safe_remove_uploaded_file(old_file_path)

                            if not old_dict_path and ext in ['csv', 'xls', 'xlsx']:
                                fields.append("data_dictionary_path = %s")
                                values.append(filename)

                            # Save parsed response fields ONLY if no API fields exist yet (Public API always prioritized)
                            if not has_existing_api_fields:
                                fields.append("api_response_fields = %s")
                                values.append(json.dumps(columns))

                            # Enable API automatically
                            fields.append("api_enabled = %s")
                            values.append(1)

                            target_ds = existing_dataset_id or dataset_id or str(service_id)
                            fields.append("api_endpoint = COALESCE(NULLIF(api_endpoint, ''), %s)")
                            values.append(target_ds)

                            fields.append("api_type = COALESCE(NULLIF(api_type, ''), 'general')")

                            # Auto endpoint setting
                            if not existing_service_url or existing_service_url in ('#', '', '/api/data/#') or not service_url:
                                auto_endpoint = f"/api/data/{target_ds}"
                                fields.append("service_url = %s")
                                values.append(auto_endpoint)

                        elif file_type == 'zip':
                            fields.append("data_sampling_path = %s")
                            values.append(filename)
                            if old_samp_path and old_samp_path != filename:
                                safe_remove_uploaded_file(old_samp_path)

                        elif file_type == 'excel':
                            fields.append("excel_file_path = %s")
                            values.append(filename)
                            if not old_file_path:
                                fields.append("file_path = %s")
                                values.append(filename)
                            if old_excel_path and old_excel_path != filename:
                                safe_remove_uploaded_file(old_excel_path)

                        else:
                            fields.append("file_path = %s")
                            values.append(filename)
                            if not old_dict_path and ext in ['csv', 'xls', 'xlsx']:
                                fields.append("data_dictionary_path = %s")
                                values.append(filename)
                            if old_file_path and old_file_path != filename:
                                safe_remove_uploaded_file(old_file_path)

                    if not fields:
                        return jsonify({"status":"No fields to update"})

                    sql_update = f"UPDATE service SET {', '.join(fields)} WHERE service_id = %s"
                    values.append(service_id)
                    
                    cursor.execute(sql_update, tuple(values))
                    conn.commit()
                    
                    # Notify Admin and Current User about the dataset update
                    try:
                        from .email_service import notify_dataset_updated
                        
                        # Fetch admins
                        cursor.execute("SELECT email FROM user WHERE previlage_id = 1 AND status_account = 'active' AND email IS NOT NULL")
                        admin_emails = [row[0] for row in cursor.fetchall() if row[0]]
                        
                        # Fetch current user email
                        current_user_email = user_data.get('email')
                        
                        notify_emails = set(admin_emails)
                        if current_user_email:
                            notify_emails.add(current_user_email)
                            
                        if notify_emails:
                            notify_dataset_updated(service_name or str(service_id), list(notify_emails))
                    except Exception as e:
                        current_app.logger.error(f"Error sending dataset update email: {e}")
                        
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


@app.route('/getApiServices', methods=['GET', 'POST'])
@require_admin
def getApiServices():
    try:
        user_data = getattr(request, 'current_user', {})
        org_id = user_data.get('org_id')
        previlage_id = str(user_data.get('previlage_id', ''))
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        if previlage_id == '3' and org_id:
            cursor.execute("SELECT org_name FROM organization WHERE org_id = %s", (org_id,))
            org_row = cursor.fetchone()
            org_name = org_row[0] if org_row else ''
            
            sql = "SELECT * FROM service WHERE organization = %s ORDER BY service_id DESC"
            cursor.execute(sql, (org_name,))
        else:
            # Fetch all clones regardless of status
            sql = "SELECT * FROM service ORDER BY service_id DESC"
            cursor.execute(sql)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        service_result = toJson(data, columns)
        conn.close()
        
        for i in range(len(service_result)):
            if service_result[i].get('service_image'):
                service_result[i]['service_image'] = base64.b64encode(service_result[i]['service_image']).decode('utf-8')
                
        return jsonify({"status": "success", "data": service_result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


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
            sql = "SELECT * FROM service WHERE (dataset_id IS NULL OR dataset_id NOT LIKE 'API\_CLONE\_%%')"
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


@app.route('/toggleServiceStatus', methods=['POST'])
@require_admin
def toggleServiceStatus():
    try:
        dataInput = request.json
        service_id = dataInput.get('service_id')
        new_status = dataInput.get('status')
        
        if not service_id or not new_status:
            return jsonify({'status': 'error', 'message': 'Missing service_id or status'}), 400
            
        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "UPDATE service SET status = %s WHERE service_id = %s"
        cursor.execute(sql, (new_status, service_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error in toggleServiceStatus: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/getDatasetApiEndpoints', methods=['POST'])
def getDatasetApiEndpoints():
    try:
        dataInput = request.json or {}
        dataset_id = dataInput.get('dataset_id')
        if not dataset_id:
            return jsonify({'status': 'error', 'message': 'Missing dataset_id'})
            
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Match API_CLONE_[dataset_id]_[api_endpoint]
        pattern = f"API\_CLONE\_{dataset_id}\_%"
        sql = "SELECT service_name, api_endpoint, description, api_type, status FROM service WHERE dataset_id LIKE %s AND status = 'Active'"
        cursor.execute(sql, (pattern,))
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in data]
        
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/retrieveService', methods=['GET'])
@app.route('/retrieveService', methods=['GET', 'POST'])
def retrieveService():
    try:
        user_id = None
        user_data = {}
        # Try to get user info if provided
        dataInput = request.json if request.is_json else request.form
        user_str = dataInput.get('user')
        if user_str:
            decoded_user = platform_decode(user_str)
            user_data = safe_json_loads(decoded_user)
            user_id = user_data.get('user_id')
            # Only R4 (System Admin) is full ADMIN
            if user_data.get('previlage_id') and str(user_data.get('previlage_id')) == '4':
                user_id = 'ADMIN' 

        conn = mysql.connect()
        cursor = conn.cursor()
        
        if user_id == 'ADMIN':
            sql = "SELECT *, 1 AS has_access, 1 AS has_dashboard_access, 1 AS has_api_access, NULL AS permission_status, NULL AS dashboard_permission_status, NULL AS api_permission_status FROM service WHERE status = 'Active' AND (dataset_id IS NULL OR dataset_id NOT LIKE 'API\_CLONE\_%%')"
            cursor.execute(sql)
        else:
            org_id = user_data.get('org_id')
            user_org_name = ''
            if org_id:
                cursor.execute("SELECT org_name FROM organization WHERE org_id = %s", (org_id,))
                org_row = cursor.fetchone()
                if org_row:
                    user_org_name = org_row[0]

            sql = """
                SELECT s.*,
                       (CASE 
                           WHEN s.access_type = 'public' THEN 1
                           WHEN s.access_type = 'internal' AND %s IN ('1', '3', '4', '5') THEN 1
                           WHEN %s = '3' AND s.organization = %s THEN 1
                           WHEN s.access_type IN ('internal', 'restricted', 'pii') AND %s IS NOT NULL AND EXISTS (
                               SELECT 1 FROM service_user_access sua WHERE sua.service_id = s.service_id AND sua.user_id = %s AND (sua.allow_dashboard = 1 OR sua.allow_dashboard IS NULL)
                           ) THEN 1
                           WHEN s.access_type IN ('restricted', 'pii') AND %s IS NOT NULL AND EXISTS (
                               SELECT 1 FROM service_group_access sga
                               JOIN group_user_detail gud ON sga.group_id = gud.group_id
                               WHERE sga.service_id = s.service_id AND gud.user_id = %s
                           ) THEN 1
                           ELSE 0
                       END) AS has_dashboard_access,
                       (CASE 
                           WHEN s.access_type = 'public' THEN 1
                           WHEN s.access_type = 'internal' AND %s IN ('1', '3', '4', '5') THEN 1
                           WHEN %s = '3' AND s.organization = %s THEN 1
                           WHEN s.access_type IN ('internal', 'restricted', 'pii') AND %s IS NOT NULL AND EXISTS (
                               SELECT 1 FROM service_user_access sua WHERE sua.service_id = s.service_id AND sua.user_id = %s AND (sua.allow_api = 1 OR sua.allow_api IS NULL)
                           ) THEN 1
                           WHEN s.access_type IN ('restricted', 'pii') AND %s IS NOT NULL AND EXISTS (
                               SELECT 1 FROM service_group_access sga
                               JOIN group_user_detail gud ON sga.group_id = gud.group_id
                               WHERE sga.service_id = s.service_id AND gud.user_id = %s
                           ) THEN 1
                           ELSE 0
                       END) AS has_api_access,
                       (SELECT status FROM dataset_permission_requests r 
                        WHERE r.service_id = s.service_id AND r.user_id = %s 
                          AND (r.request_type = 'dashboard' OR r.request_type = 'all' OR r.request_type IS NULL)
                        ORDER BY r.created_at DESC LIMIT 1) AS dashboard_permission_status,
                       (SELECT status FROM dataset_permission_requests r 
                        WHERE r.service_id = s.service_id AND r.user_id = %s 
                          AND (r.request_type = 'api' OR r.request_type = 'all' OR r.request_type IS NULL)
                        ORDER BY r.created_at DESC LIMIT 1) AS api_permission_status,
                       (CASE 
                           WHEN s.access_type = 'public' THEN 1
                           WHEN s.access_type = 'internal' AND %s IN ('1', '3', '4', '5') THEN 1
                           WHEN %s = '3' AND s.organization = %s THEN 1
                           WHEN s.access_type IN ('internal', 'restricted', 'pii') AND %s IS NOT NULL AND EXISTS (
                               SELECT 1 FROM service_user_access sua WHERE sua.service_id = s.service_id AND sua.user_id = %s
                           ) THEN 1
                           WHEN s.access_type IN ('restricted', 'pii') AND %s IS NOT NULL AND EXISTS (
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
                WHERE s.status = 'Active' AND (s.dataset_id IS NULL OR s.dataset_id NOT LIKE 'API\_CLONE\_%%')
            """
            previlage_id = str(user_data.get('previlage_id', '2'))
            cursor.execute(sql, (
                previlage_id, previlage_id, user_org_name, user_id, user_id, user_id, user_id, # has_dashboard_access (7)
                previlage_id, previlage_id, user_org_name, user_id, user_id, user_id, user_id, # has_api_access (7)
                user_id, # dashboard_permission_status (1)
                user_id, # api_permission_status (1)
                previlage_id, previlage_id, user_org_name, user_id, user_id, user_id, user_id, # has_access (7)
                user_id # permission_status (1)
            ))
            
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

import pandas as pd
from flask import Response
import io


@app.route('/dataapi/api/v1/<dataset_id>/file', methods=['GET'])
def get_dataset_file_api(dataset_id):
    import os
    import pandas as pd
    import hashlib
    import uuid
    import json
    
    request_id = str(uuid.uuid4())
    
    try:
        apikey_header = request.headers.get('x-api-key')
        apikey_query = request.args.get('apikey')
        apikey = apikey_header if apikey_header else apikey_query
        
        conn = mysql.connect()
        cursor = conn.cursor()

        sql_check_service = """
            SELECT service_id, api_enabled, api_type, COALESCE(NULLIF(file_path, ''), excel_file_path) AS file_path, service_name, access_type
            FROM service 
            WHERE (dataset_id = %s OR api_endpoint = %s OR service_id = %s) AND status = 'Active' LIMIT 1
        """
        cursor.execute(sql_check_service, (dataset_id, dataset_id, dataset_id))
        svc_row = cursor.fetchone()
        
        if not svc_row:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Service not found or inactive', 'request_id': request_id}), 404

        real_service_id, api_enabled, api_type, file_path, service_name, access_type = svc_row

        user_id = 0
        user_role = '2'
        # Enforce API Key
        if api_type != 'public' or access_type in ['internal', 'restricted', 'pii']:
            if not apikey:
                cursor.close()
                conn.close()
                return jsonify({'status': 'error', 'message': 'Missing apikey parameter', 'request_id': request_id}), 401
                
            if "." in apikey:
                public_key_id = apikey.split('.')[0]
                secret_hash = hashlib.sha256(apikey.encode('utf-8')).hexdigest()

                sql_cred = "SELECT c.status, c.expires_at FROM api_credentials c WHERE c.public_key_id = %s AND c.secret_hash = %s AND c.service_id = %s"
                cursor.execute(sql_cred, (public_key_id, secret_hash, real_service_id))
                cred_row = cursor.fetchone()

                if not cred_row:
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'error', 'message': 'Invalid API key for this dataset', 'request_id': request_id}), 403
                    
                if cred_row[0] != 'active':
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'error', 'message': 'API Key is inactive', 'request_id': request_id}), 403
            else:
                sql_user = "SELECT user_id, previlage_id FROM user WHERE apikey = %s "
                cursor.execute(sql_user, (apikey,))
                user_row = cursor.fetchone()
                if not user_row:
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'error', 'message': 'Invalid Global API Key', 'request_id': request_id}), 401
                user_id, user_role = user_row
        if not file_path:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'No file attached to this dataset', 'request_id': request_id}), 404
            
        cursor.close()
        conn.close()

        # Read the file
        upload_folder = os.path.join(os.getcwd(), 'uploads')
        full_path = os.path.join(upload_folder, file_path)
        
        if not os.path.exists(full_path):
            return jsonify({'status': 'error', 'message': 'File missing on server', 'request_id': request_id}), 404
            
        ext = file_path.split('.')[-1].lower()
        if ext in ['csv']:
            try:
                df = pd.read_csv(full_path, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(full_path, encoding='cp874')
            df = df.fillna("")
            json_data = df.to_dict(orient='records')
        elif ext in ['xls', 'xlsx']:
            df = pd.read_excel(full_path)
            df = df.fillna("")
            json_data = df.to_dict(orient='records')
        elif ext == 'json':
            with open(full_path, 'r', encoding='utf-8') as f:
                raw_json = json.load(f)
            if isinstance(raw_json, list):
                json_data = raw_json
            elif isinstance(raw_json, dict):
                if 'data' in raw_json and isinstance(raw_json['data'], list):
                    json_data = raw_json['data']
                elif 'rows' in raw_json and isinstance(raw_json['rows'], list):
                    json_data = raw_json['rows']
                elif 'items' in raw_json and isinstance(raw_json['items'], list):
                    json_data = raw_json['items']
                else:
                    json_data = [raw_json]
            else:
                json_data = []
        elif ext == 'xml':
            import xml.etree.ElementTree as ET
            tree = ET.parse(full_path)
            root = tree.getroot()
            json_data = []
            for child in root:
                row = {}
                for sub in child:
                    tag = sub.tag.split('}')[-1] if '}' in sub.tag else sub.tag
                    row[tag] = (sub.text or '').strip()
                if not row and child.attrib:
                    row = dict(child.attrib)
                if row:
                    json_data.append(row)
            if not json_data:
                row = {}
                for child in root:
                    tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                    row[tag] = (child.text or '').strip()
                if row:
                    json_data.append(row)
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported file format', 'request_id': request_id}), 400
        
        return jsonify({
            'status': 'success',
            'dataset_id': dataset_id,
            'dataset_name': service_name,
            'total_rows': len(json_data),
            'rows': json_data
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "request_id": request_id}), 500



@app.route('/exportData/<dataset_id>', methods=['GET'])
def exportData(dataset_id):
    try:
        format_type = request.args.get('format', 'csv').lower()
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "SELECT dataset_id, api_db_name, api_endpoint FROM service WHERE dataset_id = %s OR api_endpoint = %s LIMIT 1"
        cursor.execute(sql, (dataset_id, dataset_id))
        service_data = cursor.fetchone()
        
        if not service_data:
            cursor.execute("SELECT dataset_id, api_db_name, api_endpoint FROM service WHERE service_id = %s LIMIT 1", (dataset_id,))
            service_data = cursor.fetchone()
            
        if not service_data:
            return jsonify({"status": "error", "message": "Dataset not found"}), 404
            
        columns = [column[0] for column in cursor.description]
        service = dict(zip(columns, service_data))
        
        db_name = service.get('api_db_name')
        source_name = service.get('api_endpoint')
        
        if not db_name or not source_name or db_name not in ALLOWED_DATABASES:
            return jsonify({"status": "error", "message": "This dataset does not have database records attached"}), 400
            
        oracle_conn = get_oracle_connection(db_name)
        oracle_cursor = oracle_conn.cursor()
        
        final_sql = f'SELECT * FROM "{db_name}"."{source_name}" FETCH FIRST 5000 ROWS ONLY'
        oracle_cursor.execute(final_sql)
        rows_data = oracle_cursor.fetchall()
        
        ora_columns = [col[0] for col in oracle_cursor.description]
        oracle_cursor.close()
        oracle_conn.close()
        
        df = pd.DataFrame(rows_data, columns=ora_columns)
        
        if format_type == 'excel' or format_type == 'xls':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            output.seek(0)
            return Response(
                output.read(),
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-disposition": f"attachment; filename={dataset_id}.xlsx"}
            )
        else: # Default CSV
            csv_data = df.to_csv(index=False)
            return Response(
                csv_data,
                mimetype="text/csv",
                headers={"Content-disposition": f"attachment; filename={dataset_id}.csv"}
            )
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/dataapi/api/v1/<dataset_id>', methods=['GET'])
def get_dataset_api(dataset_id):
    import json
    from flask import Response
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
                
                # Format as requested for PII/Restricted Audit Log
                import json
                try:
                    sensitivity_val = access_type if 'access_type' in locals() else 'unknown'
                except:
                    sensitivity_val = 'unknown'
                    
                audit_info = {
                    "actor_user_id": user_id_val or 0,
                    "dataset_id": dataset_id,
                    "sensitivity": sensitivity_val,
                    "result": "Denied" if status_code >= 400 else "Allowed",
                    "action": "data_access",
                    "request_id": request_id,
                    "message": msg
                }
                detail = json.dumps(audit_info)
                
                cursor.execute(log_sql, (user_id_val or 0, detail, path, ip_addr))
                conn.commit()
            except Exception as e:
                current_app.logger.error(f"Failed to log API usage: {e}")

        # First, fetch service configuration by dataset_id
        sql_svc_config = """SELECT service_id, api_enabled, api_type, api_db_name, api_source_name, api_source_type, 
                                   api_request_fields, api_response_fields, service_name, access_type,
                                   COALESCE(NULLIF(file_path, ''), excel_file_path) AS file_path
                            FROM service WHERE (dataset_id = %s OR api_endpoint = %s OR service_id = %s) AND status = 'Active' LIMIT 1"""
        cursor.execute(sql_svc_config, (dataset_id, dataset_id, dataset_id))
        svc_row = cursor.fetchone()
        
        if not svc_row:
            log_api_usage(0, 'Service not found or inactive', 404)
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Service not found or inactive', 'request_id': request_id}), 404

        real_service_id, api_enabled, api_type, db_name, source_name, source_type, req_fields_raw, res_fields_raw, service_name, access_type, file_path = svc_row

        if not api_enabled:
            log_api_usage(0, 'API access is disabled for this dataset', 403)
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'API access is disabled for this dataset', 'request_id': request_id}), 403

        # Enforce key check if NOT public or if access_type requires authentication
        user_id = 0
        credential_id = None
        user_role = '2'
        expires_at = None
        
        if api_type != 'public' or access_type in ['internal', 'restricted', 'pii']:
            if not apikey:
                log_api_usage(0, 'Missing apikey parameter for private/restricted API', 401)
                cursor.close()
                conn.close()
                return jsonify({'status': 'error', 'message': 'Missing apikey parameter', 'request_id': request_id}), 401

            if "." in apikey:
                public_key_id = apikey.split('.')[0]
                secret_hash = hashlib.sha256(apikey.encode('utf-8')).hexdigest()

                sql_cred = "SELECT c.credential_id, c.user_id, c.status, c.expires_at, u.previlage_id FROM api_credentials c JOIN user u ON c.user_id = u.user_id WHERE c.public_key_id = %s AND c.secret_hash = %s AND c.service_id = %s"
                cursor.execute(sql_cred, (public_key_id, secret_hash, real_service_id))
                cred_row = cursor.fetchone()

                if not cred_row:
                    log_api_usage(0, 'Invalid API key for this dataset', 403)
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'error', 'message': 'Invalid or inactive API key', 'request_id': request_id}), 403

                credential_id, user_id, cred_status, expires_at, user_role = cred_row
                
                if cred_status != 'active':
                    log_api_usage(user_id, 'API Key is inactive', 403)
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'error', 'message': 'API Key is inactive', 'request_id': request_id}), 403

                if expires_at and expires_at < datetime.now():
                    log_api_usage(user_id, 'API Key expired', 403)
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'error', 'message': 'API Key has expired', 'request_id': request_id}), 403
            else:
                sql_user = "SELECT user_id, previlage_id FROM user WHERE apikey = %s "
                cursor.execute(sql_user, (apikey,))
                user_row = cursor.fetchone()
                if not user_row:
                    log_api_usage(0, 'Invalid Global API Key', 403)
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'error', 'message': 'Invalid Global API Key', 'request_id': request_id}), 403
                user_id, user_role = user_row
        else:
            if apikey:
                if "." in apikey:
                    public_key_id = apikey.split('.')[0]
                    secret_hash = hashlib.sha256(apikey.encode('utf-8')).hexdigest()
                    sql_user = "SELECT c.credential_id, c.user_id, u.previlage_id FROM api_credentials c JOIN user u ON c.user_id = u.user_id WHERE c.public_key_id = %s AND c.secret_hash = %s LIMIT 1"
                    cursor.execute(sql_user, (public_key_id, secret_hash))
                    user_row = cursor.fetchone()
                    if user_row:
                        credential_id, user_id, user_role = user_row
                else:
                    sql_user = "SELECT user_id, previlage_id FROM user WHERE apikey = %s "
                    cursor.execute(sql_user, (apikey,))
                    user_row = cursor.fetchone()
                    if user_row:
                        user_id, user_role = user_row

        if not db_name or not source_name:
            if file_path:
                upload_folder = os.path.join(os.getcwd(), 'uploads')
                full_path = os.path.join(upload_folder, file_path)
                if not os.path.exists(full_path):
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'error', 'message': 'File missing on server', 'request_id': request_id}), 404

                ext = file_path.split('.')[-1].lower()
                import pandas as pd
                try:
                    if ext == 'csv':
                        try:
                            df = pd.read_csv(full_path, encoding='utf-8-sig')
                        except UnicodeDecodeError:
                            df = pd.read_csv(full_path, encoding='cp874')
                    elif ext in ['xls', 'xlsx']:
                        df = pd.read_excel(full_path)
                    elif ext == 'json':
                        with open(full_path, 'r', encoding='utf-8') as f:
                            raw_json = json.load(f)
                        if isinstance(raw_json, list):
                            df = pd.DataFrame(raw_json)
                        elif isinstance(raw_json, dict):
                            if 'data' in raw_json and isinstance(raw_json['data'], list):
                                df = pd.DataFrame(raw_json['data'])
                            elif 'rows' in raw_json and isinstance(raw_json['rows'], list):
                                df = pd.DataFrame(raw_json['rows'])
                            else:
                                df = pd.DataFrame([raw_json])
                        else:
                            df = pd.DataFrame()
                    else:
                        df = pd.DataFrame()
                except Exception as fe:
                    cursor.close()
                    conn.close()
                    return jsonify({'status': 'error', 'message': f'Error reading data file: {str(fe)}', 'request_id': request_id}), 500

                # Scope conditions & field filters for file data
                user_req_fields = []
                user_res_fields = []
                user_conditions = []
                if credential_id:
                    cursor.execute("SELECT scope_json FROM api_scopes WHERE credential_id = %s", (credential_id,))
                    scope_row = cursor.fetchone()
                    if scope_row and scope_row[0]:
                        try:
                            scope_obj = json.loads(scope_row[0]) if isinstance(scope_row[0], str) else scope_row[0]
                            if isinstance(scope_obj, dict) and ('request_fields' in scope_obj or 'response_fields' in scope_obj or 'conditions' in scope_obj):
                                user_req_fields = scope_obj.get('request_fields', []) or []
                                user_res_fields = scope_obj.get('response_fields', []) or []
                                user_conditions = scope_obj.get('conditions', []) or []
                            elif isinstance(scope_obj, list):
                                user_conditions = scope_obj
                            elif isinstance(scope_obj, dict):
                                user_conditions = scope_obj
                        except Exception as se:
                            current_app.logger.error(f"File scope filter error: {se}")

                    # 1. Apply user row conditions (Row-Level Security)
                    if isinstance(user_conditions, list):
                        for cond in user_conditions:
                            s_field = cond.get('field')
                            s_op = str(cond.get('operator', '=')).upper()
                            s_val = cond.get('value')
                            if s_field and s_field in df.columns:
                                if s_op == '=':
                                    df = df[df[s_field].astype(str) == str(s_val)]
                                elif s_op == '!=':
                                    df = df[df[s_field].astype(str) != str(s_val)]
                                elif s_op == '>':
                                    try: df = df[pd.to_numeric(df[s_field]) > float(s_val)]
                                    except: df = df[df[s_field].astype(str) > str(s_val)]
                                elif s_op == '<':
                                    try: df = df[pd.to_numeric(df[s_field]) < float(s_val)]
                                    except: df = df[df[s_field].astype(str) < str(s_val)]
                                elif s_op == '>=':
                                    try: df = df[pd.to_numeric(df[s_field]) >= float(s_val)]
                                    except: df = df[df[s_field].astype(str) >= str(s_val)]
                                elif s_op == '<=':
                                    try: df = df[pd.to_numeric(df[s_field]) <= float(s_val)]
                                    except: df = df[df[s_field].astype(str) <= str(s_val)]
                                elif s_op == 'LIKE':
                                    df = df[df[s_field].astype(str).str.contains(str(s_val), case=False, na=False)]
                                elif s_op == 'IN' and isinstance(s_val, list):
                                    df = df[df[s_field].isin(s_val)]
                    elif isinstance(user_conditions, dict):
                        for s_field, s_vals in user_conditions.items():
                            if s_field in df.columns and isinstance(s_vals, list):
                                df = df[df[s_field].isin(s_vals)]

                # 2. Determine allowed Request Fields (Field Request)
                allowed_req_fields = user_req_fields if user_req_fields else []
                if not allowed_req_fields and req_fields_raw:
                    try: allowed_req_fields = json.loads(req_fields_raw) or []
                    except: allowed_req_fields = []

                for arg in request.args:
                    if arg not in ['apikey', 'key'] and allowed_req_fields:
                        if arg not in allowed_req_fields:
                            cursor.close()
                            conn.close()
                            return jsonify({'status': 'error', 'message': f'Disallowed request field: {arg}', 'request_id': request_id}), 400

                # Apply query filter parameters
                for arg in request.args:
                    if arg not in ['apikey', 'key'] and arg in df.columns:
                        if not allowed_req_fields or arg in allowed_req_fields:
                            val = request.args.get(arg)
                            if val is not None and val != '':
                                df = df[df[arg].astype(str) == str(val)]

                # 3. Response fields filtering (Field Response per user vs global)
                allowed_res_fields = user_res_fields if user_res_fields else []
                if not allowed_res_fields and res_fields_raw:
                    try: allowed_res_fields = json.loads(res_fields_raw) or []
                    except: allowed_res_fields = []

                if allowed_res_fields:
                    avail_cols = [c for c in allowed_res_fields if c in df.columns]
                    if avail_cols:
                        df = df[avail_cols]

                df = df.fillna("")
                records = df.to_dict(orient='records')

                cursor.close()
                conn.close()
                return jsonify({
                    'status': 'success',
                    'count': len(records),
                    'data': records,
                    'request_id': request_id
                })
            else:
                cursor.close()
                conn.close()
                return jsonify({'status': 'error', 'message': 'Service source not configured', 'request_id': request_id}), 500

        # Parse JSON fields
        try:
            req_fields_list = json.loads(req_fields_raw) if req_fields_raw else []
            res_fields_list = json.loads(res_fields_raw) if res_fields_raw else []
        except Exception as e:
            current_app.logger.error(f"JSON Parse Error: {e} -> RAW: {req_fields_raw}")
            req_fields_list = []
            res_fields_list = []
            
        current_app.logger.info(f"REQ LIST VALID: {req_fields_list}")
            
        # Validate dynamic SQL identifiers
        if not re.match(r'^[a-zA-Z0-9_]+$', source_name):
            return jsonify({'status': 'error', 'message': 'Invalid source name', 'request_id': request_id}), 400
            
        # 3. Handle Scopes (Row-Level Security & Per-User Fields)
        scope_where_clause = " 1=1 "
        scope_params = []
        user_req_fields = []
        user_res_fields = []
        user_conditions = []

        if credential_id:
            cursor.execute("SELECT scope_json FROM api_scopes WHERE credential_id = %s", (credential_id,))
            scope_row = cursor.fetchone()
            if scope_row and scope_row[0]:
                try:
                    scope_obj = json.loads(scope_row[0]) if isinstance(scope_row[0], str) else scope_row[0]
                    if isinstance(scope_obj, dict) and ('request_fields' in scope_obj or 'response_fields' in scope_obj or 'conditions' in scope_obj):
                        user_req_fields = scope_obj.get('request_fields', []) or []
                        user_res_fields = scope_obj.get('response_fields', []) or []
                        user_conditions = scope_obj.get('conditions', []) or []
                    elif isinstance(scope_obj, list):
                        user_conditions = scope_obj
                    elif isinstance(scope_obj, dict):
                        user_conditions = scope_obj

                    allowed_ops = ['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN']
                    if isinstance(user_conditions, list):
                        for idx, cond in enumerate(user_conditions):
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
                    elif isinstance(user_conditions, dict):
                        for field, values in user_conditions.items():
                            if values and isinstance(values, list):
                                if not re.match(r'^[a-zA-Z0-9_]+$', field): continue
                                placeholders = ', '.join(['%s'] * len(values))
                                scope_where_clause += f" AND `{field}` IN ({placeholders})"
                                scope_params.extend(values)
                except Exception as e:
                    current_app.logger.error(f"[{request_id}] Scope parsing error: {e}")

        # 4. Handle User Filters (Request Fields - Per User Scope or Global)
        effective_req_fields = user_req_fields if user_req_fields else req_fields_list
        effective_req_fields_valid = [f for f in effective_req_fields if re.match(r'^[a-zA-Z0-9_]+$', f)]

        effective_res_fields = user_res_fields if user_res_fields else res_fields_list
        effective_res_fields_valid = [f for f in effective_res_fields if re.match(r'^[a-zA-Z0-9_]+$', f)]

        filter_where_clause = ""
        filter_params = []
        
        # Deny unallowed request fields
        for arg in request.args:
            if arg not in ['apikey', 'key']:
                if effective_req_fields_valid and arg not in effective_req_fields_valid:
                    return jsonify({'status': 'error', 'message': f'Disallowed request field: {arg}'}), 400
                
        for field in effective_req_fields_valid:
            val = request.args.get(field)
            if val:
                filter_where_clause += f" AND `{field}` = %s"
                filter_params.append(val)

        # 5. Build Dynamic SQL safely
        # Limit response fields to what was configured
        select_clause = "*"
        if effective_res_fields_valid:
            select_clause = ", ".join([f"`{f}`" for f in effective_res_fields_valid])

        # Whitelist databases check again (backend layer)
        if db_name not in ALLOWED_DATABASES:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Database not in whitelist', 'request_id': request_id}), 403

        # Construct final SQL
        all_params = scope_params + filter_params
        
        if db_name in ['STG_DATAEXCHAGE', 'DWH_DATAEXCHAGE']:
            import re
            bind_counter = 0
            def replace_bind(match):
                nonlocal bind_counter
                bind_counter += 1
                return f":{bind_counter}"

            scope_where_clause_ora = re.sub(r'%s', replace_bind, scope_where_clause)
            filter_where_clause_ora = re.sub(r'%s', replace_bind, filter_where_clause)
            
            # Oracle identifiers might be uppercase. Safest is double quotes if it was unquoted, or just uppercase.
            select_clause_ora = "*"
            if effective_res_fields_valid:
                select_clause_ora = ", ".join([f'"{f}"' for f in effective_res_fields_valid])
            
            # Replace backticks in where clauses
            scope_where_clause_ora = scope_where_clause_ora.replace('`', '"')
            filter_where_clause_ora = filter_where_clause_ora.replace('`', '"')

            final_sql = f'SELECT {select_clause_ora} FROM "{db_name}"."{source_name}" WHERE {scope_where_clause_ora} {filter_where_clause_ora} FETCH FIRST 1000 ROWS ONLY'
            
            # Oracle connection
            oracle_conn = get_oracle_connection(db_name)
            oracle_cursor = oracle_conn.cursor()
            oracle_cursor.execute(final_sql, all_params)
            rows_data = oracle_cursor.fetchall()
            columns = [col[0] for col in oracle_cursor.description]
            
            results = [dict(zip(columns, row)) for row in rows_data]
            
            # Must read LOBs before closing oracle connection
            for row in results:
                for k, v in row.items():
                    if hasattr(v, 'read'):
                        try:
                            row[k] = str(v.read())
                        except:
                            row[k] = str(v)
                            
            oracle_cursor.close()
            oracle_conn.close()
            
        else:
            final_sql = f"SELECT {select_clause} FROM `{db_name}`.`{source_name}` WHERE {scope_where_clause} {filter_where_clause} LIMIT 1000"
            
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
                elif hasattr(v, 'read'): # Handle LOB objects (Oracle CLOB/BLOB)
                    try:
                        row[k] = str(v.read())
                    except:
                        row[k] = str(v)

        log_api_usage(user_id, 'API Invoked Successfully', 200)

        cursor.close()
        conn.close()

        json_str = json.dumps({
            'status': 'success',
            'dataset_id': dataset_id,
            'dataset_name': service_name,
            'total_rows': len(results),
            'rows': results
        }, ensure_ascii=False)
        
        response = Response(json_str, content_type='application/json; charset=utf-8')
        
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
# Oracle ADW Connection Helper
# ============================================================
def get_oracle_connection(schema):
    import oracledb
    password = 'GoU8iFg24y90r243whrefWLq!'
    config_dir = '/app/Wallet_L2EPRDDWH'
    dsn = 'l2eprddwh_high'
    return oracledb.connect(user=schema, password=password, config_dir=config_dir, wallet_location=config_dir, wallet_password=password, dsn=dsn)

# ============================================================
# ============================================================
# API Configuration & Management Endpoints
@app.route('/cloneServiceForApi', methods=['POST'])
@require_admin
def cloneServiceForApi():
    try:
        dataInput = request.json
        original_service_id = dataInput.get('original_service_id')
        api_endpoint = dataInput.get('api_endpoint')
        new_service_id = f"{original_service_id}_{api_endpoint}"
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check if original exists
        cursor.execute("SELECT * FROM service WHERE service_id = %s", (original_service_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'status': 'error', 'message': 'Original service not found'})
            
        columns = [col[0] for col in cursor.description]
        orig_data = dict(zip(columns, row))
        
        # Prepare cloned data
        orig_data.pop('service_id', None)  # Let it auto-increment
        orig_data['dataset_id'] = f"API_CLONE_{orig_data.get('dataset_id', original_service_id)}_{api_endpoint}" 
        orig_data['service_name'] = dataInput.get('api_name', orig_data['service_name'])
        orig_data['description'] = dataInput.get('api_description', orig_data['description'])
        orig_data['api_enabled'] = 1 if dataInput.get('api_enabled') in ['true', '1', True, 'Active = Enable'] else 0
        orig_data['api_type'] = dataInput.get('api_type', 'general')
        orig_data['api_endpoint'] = api_endpoint
        orig_data['api_db_name'] = dataInput.get('api_db_name')
        orig_data['api_source_name'] = dataInput.get('api_source_name')
        
        import json
        req_fields = dataInput.get('api_request_fields', [])
        res_fields = dataInput.get('api_response_fields', [])
        orig_data['api_request_fields'] = json.dumps(req_fields) if isinstance(req_fields, list) else req_fields
        orig_data['api_response_fields'] = json.dumps(res_fields) if isinstance(res_fields, list) else res_fields
        
        # Build INSERT
        cols = []
        vals = []
        placeholders = []
        for k, v in orig_data.items():
            if k == 'service_image': continue # Skip image to avoid large blob duplication issues or handle properly
            cols.append(f"`{k}`")
            vals.append(v)
            placeholders.append("%s")
            
        insert_sql = f"INSERT INTO service ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        
        try:
            cursor.execute(insert_sql, tuple(vals))
            conn.commit()
        except Exception as e:
            if 'Duplicate entry' in str(e):
                # If updating existing clone
                update_cols = []
                update_vals = []
                for k, v in orig_data.items():
                    if k in ['service_id', 'dataset_id', 'service_image']: continue
                    update_cols.append(f"`{k}` = %s")
                    update_vals.append(v)
                update_vals.append(orig_data['dataset_id'])
                update_sql = f"UPDATE service SET {', '.join(update_cols)} WHERE dataset_id = %s"
                cursor.execute(update_sql, tuple(update_vals))
                conn.commit()
            else:
                raise e
                
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'dataset_id': orig_data['dataset_id']})
    except Exception as e:
        import traceback
        current_app.logger.error(f"Clone API Error: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================

# Hardcoded whitelist of databases the admin is allowed to expose via API
ALLOWED_DATABASES = ['DWH_DATAEXCHAGE', 'STG_DATAEXCHAGE']

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

        if db_name in ['STG_DATAEXCHAGE', 'DWH_DATAEXCHAGE']:
            conn = get_oracle_connection(db_name)
            cursor = conn.cursor()
            # In Oracle ADW, we check user_tables and user_views for the logged-in schema
            sql = """SELECT table_name, 'table' as table_type FROM user_tables 
                     UNION 
                     SELECT view_name, 'view' as table_type FROM user_views 
                     ORDER BY table_name"""
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            result = []
            for row in data:
                result.append({'name': row[0], 'type': row[1].lower()})
        else:
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


@app.route('/previewTableData', methods=['POST'])
@require_admin
def previewTableData():
    try:
        dataInput = request.json
        db_name = dataInput.get('db_name', '')
        table_name = dataInput.get('table_name', '')
        
        if not db_name or not table_name:
            return jsonify({"status": "error", "message": "Missing db or table name"})
            
        def clean_row(row):
            clean = []
            for item in row:
                if hasattr(item, 'read'):
                    try:
                        clean.append(str(item.read()))
                    except:
                        clean.append(str(item))
                elif hasattr(item, 'isoformat'):
                    clean.append(item.isoformat())
                else:
                    clean.append(item)
            return clean

        if db_name == 'datax_db_3003':
            conn = mysql.connect()
            cursor = conn.cursor()
            sql = f"SELECT * FROM {table_name} LIMIT 5"
            cursor.execute(sql)
            data = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, clean_row(row))) for row in data]
            cursor.close()
            conn.close()
            return jsonify({"status": "success", "data": result})
        elif db_name in ALLOWED_DATABASES:
            conn = get_oracle_connection(db_name)
            cursor = conn.cursor()
            sql = f'SELECT * FROM "{db_name}"."{table_name}" FETCH FIRST 5 ROWS ONLY'
            cursor.execute(sql)
            data = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, clean_row(row))) for row in data]
            cursor.close()
            conn.close()
            return jsonify({"status": "success", "data": result})
        else:
            return jsonify({"status": "error", "message": "Unsupported database"})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


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

        if db_name in ['STG_DATAEXCHAGE', 'DWH_DATAEXCHAGE']:
            conn = get_oracle_connection(db_name)
            cursor = conn.cursor()
            sql = """SELECT column_name, data_type, nullable
                     FROM user_tab_columns
                     WHERE table_name = :1
                     ORDER BY column_id"""
            cursor.execute(sql, [table_name])
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            result = [{'name': row[0], 'type': row[1], 'nullable': 'YES' if row[2] == 'Y' else 'NO'} for row in data]
        else:
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
                 WHERE c.service_id = %s AND s.scope_id IS NULL
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
            import dateutil.parser
            try:
                expires_at = dateutil.parser.parse(expires_at).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
            sql_insert = "INSERT INTO api_credentials (service_id, user_id, public_key_id, secret_hash, key_last_four, status, expires_at) VALUES (%s, %s, %s, %s, %s, 'active', %s)"
            cursor.execute(sql_insert, (service_id, target_user_id, public_key_id, secret_hash, key_last_four, expires_at))
        else:
            sql_insert = "INSERT INTO api_credentials (service_id, user_id, public_key_id, secret_hash, key_last_four, status) VALUES (%s, %s, %s, %s, %s, 'active')"
            cursor.execute(sql_insert, (service_id, target_user_id, public_key_id, secret_hash, key_last_four))
        credential_id = cursor.lastrowid

        # Insert scope if provided
        request_fields = dataInput.get('request_fields', [])
        response_fields = dataInput.get('response_fields', [])
        if scope_json or request_fields or response_fields:
            if isinstance(scope_json, dict) and ('request_fields' in scope_json or 'response_fields' in scope_json or 'conditions' in scope_json):
                standard_scope_obj = {
                    'request_fields': scope_json.get('request_fields', request_fields or []),
                    'response_fields': scope_json.get('response_fields', response_fields or []),
                    'conditions': scope_json.get('conditions', [])
                }
            else:
                standard_scope_obj = {
                    'request_fields': request_fields or [],
                    'response_fields': response_fields or [],
                    'conditions': scope_json if isinstance(scope_json, (list, dict)) else []
                }
            scope_str = json.dumps(standard_scope_obj)
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
            import dateutil.parser
            try:
                expires_at = dateutil.parser.parse(expires_at).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
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
        scope_json = dataInput.get('scope_json')
        request_fields = dataInput.get('request_fields', [])
        response_fields = dataInput.get('response_fields', [])

        if isinstance(scope_json, dict) and ('request_fields' in scope_json or 'response_fields' in scope_json or 'conditions' in scope_json):
            standard_scope_obj = {
                'request_fields': scope_json.get('request_fields', request_fields or []),
                'response_fields': scope_json.get('response_fields', response_fields or []),
                'conditions': scope_json.get('conditions', [])
            }
        else:
            standard_scope_obj = {
                'request_fields': request_fields or [],
                'response_fields': response_fields or [],
                'conditions': scope_json if isinstance(scope_json, (list, dict)) else []
            }
        scope_str = json.dumps(standard_scope_obj)

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
        success_where = where_clause + " AND log_detail LIKE '[200]%%'"
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
@app.route('/getSystemActivityLogs', methods=['POST'])
@require_admin
def getSystemActivityLogs():
    """Detailed list of System Activity logs (excluding API hits) with user info."""
    try:
        dataInput = request.json
        
        limit = dataInput.get('limit', 50)
        offset = dataInput.get('offset', 0)
        start_date = dataInput.get('start_date')
        end_date = dataInput.get('end_date')
        
        where_clause = "WHERE l.type != 'API'"
        params = []
        if start_date:
            where_clause += " AND l.create_at >= %s"
            params.append(start_date)
        if end_date:
            if len(end_date) == 10: end_date += " 23:59:59"
            where_clause += " AND l.create_at <= %s"
            params.append(end_date)
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = f"""
            SELECT l.log_id, l.user_id, u.username, u.email, l.log_detail, l.path, l.type, l.ip, l.device, l.create_at 
            FROM log l
            LEFT JOIN user u ON l.user_id = u.user_id
            {where_clause} 
            ORDER BY l.create_at DESC 
            LIMIT %s OFFSET %s
        """
        
        full_params = tuple(params) + (limit, offset)
        cursor.execute(sql, full_params)
        
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
        for row in result:
            if row.get('create_at'):
                row['create_at'] = str(row['create_at'])
            if not row.get('username'):
                row['username'] = row.get('email') or f"Unknown User (ID: {row.get('user_id')})"

        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result, 'limit': limit, 'offset': offset})
    except Exception as e:
        import traceback
        current_app.logger.error(f"System Activity Logs Error: {traceback.format_exc()}")
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
        
        # 4.5. Organizations Count
        cursor.execute("SELECT COUNT(*) as count FROM organization")
        organizations_count = cursor.fetchone()[0]
        
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
            'hero_stats': {
                'datasets_count': datasets_count,
                'organizations_count': organizations_count,
                'api_calls_count': api_calls_count
            },
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
        
        user_str = dataInput.get('user')
        if user_str and not user_id:
            decoded_user = platform_decode(user_str)
            parsed_user = safe_json_loads(decoded_user)
            user_id = parsed_user.get('user_id')
            
        service_id = dataInput.get('service_id')
        request_type = dataInput.get('request_type', 'all')
        fields = dataInput.get('fields', [])
        reason = dataInput.get('reason', '')
        mou_file_base64 = dataInput.get('mou_file')
        mou_filename = dataInput.get('mou_filename', '')
        
        if not user_id or not service_id:
            return jsonify({'status': 'error', 'message': 'Missing user or service ID'}), 400
            
        if not reason or not reason.strip():
            return jsonify({'status': 'error', 'message': 'โปรดระบุวัตถุประสงค์ในการขอเข้าถึง'}), 400

        if request_type == 'api' and (not fields or len(fields) == 0):
            return jsonify({'status': 'error', 'message': 'โปรดเลือกอย่างน้อย 1 ฟิลด์ข้อมูลที่ต้องการใช้งาน'}), 400
            
        fields_json = json.dumps(fields) if fields else '[]'
        
        mou_file_path = None
        if mou_file_base64 and mou_filename:
            try:
                import time
                if ',' in mou_file_base64:
                    header, base64_data = mou_file_base64.split(',', 1)
                else:
                    base64_data = mou_file_base64
                file_bytes = base64.b64decode(base64_data)
                
                clean_name = safe_unicode_filename(mou_filename) or 'mou_document.pdf'
                saved_filename = f"mou_req_{user_id}_{service_id}_{int(time.time())}_{clean_name}"
                saved_filepath = os.path.join(UPLOAD_FOLDER, saved_filename)
                with open(saved_filepath, 'wb') as f:
                    f.write(file_bytes)
                mou_file_path = saved_filename
            except Exception as fe:
                current_app.logger.warning(f"Error saving MOU file: {fe}")
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check if there is already a Pending request for this type or 'all'
        sql_check = "SELECT request_id FROM dataset_permission_requests WHERE user_id = %s AND service_id = %s AND (request_type = %s OR request_type = 'all' OR %s = 'all') AND status = 'Pending'"
        cursor.execute(sql_check, (user_id, service_id, request_type, request_type))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            type_label = 'แดชบอร์ด' if request_type == 'dashboard' else ('API' if request_type == 'api' else 'ชุดข้อมูลนี้')
            return jsonify({'status': 'error', 'message': f'คุณได้ส่งคำขอเข้าถึง{type_label}ที่อยู่ระหว่างรอดำเนินการแล้ว'}), 400
            
        # Insert request
        sql_insert = """INSERT INTO dataset_permission_requests (user_id, service_id, fields_json, reason, status, mou_file_path, mou_filename, request_type) 
                        VALUES (%s, %s, %s, %s, 'Pending', %s, %s, %s)"""
        cursor.execute(sql_insert, (user_id, service_id, fields_json, reason, mou_file_path, mou_filename, request_type))
        conn.commit()
        
        # Log the action
        logAction(user_id, '/requestDatasetPermission', f'Request dataset permission ({request_type}) for service_id {service_id}', 'info')
        
        # Notify Admins
        try:
            from .email_service import notify_access_request
            cursor.execute("SELECT email FROM user WHERE previlage_id = 1 AND status_account = 'active' AND email IS NOT NULL")
            admin_emails = [row[0] for row in cursor.fetchall() if row[0]]
            
            if admin_emails:
                cursor.execute("SELECT service_name FROM service WHERE service_id = %s", (service_id,))
                svc = cursor.fetchone()
                svc_name = svc[0] if svc else str(service_id)
                
                cursor.execute("SELECT username FROM user WHERE user_id = %s", (user_id,))
                usr = cursor.fetchone()
                usr_name = usr[0] if usr else str(user_id)
                
                notify_access_request(svc_name, usr_name, admin_emails)
        except Exception as e:
            current_app.logger.error(f"Error sending access request email: {e}")
            
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
        
        user_str = dataInput.get('user')
        if user_str and not user_data.get('user_id'):
            decoded_user = platform_decode(user_str)
            user_data = safe_json_loads(decoded_user)
            
        # Verify admin status
        if not checkUserIsAdmin(user_data) and str(user_data.get('previlage_id')) not in ['1', '3', '4', '5']:
            return jsonify({'status': 'error', 'message': 'Permission Denied'}), 403
            
        filter_status = dataInput.get('status', 'Pending')
        
        conn = mysql.connect()
        cursor = conn.cursor()
        if filter_status == 'All':
            sql = """SELECT r.request_id, r.user_id, r.service_id, r.fields_json, r.reason, r.status, r.created_at,
                            r.mou_file_path, r.mou_filename, r.request_type,
                            u.username, u.firstname, u.lastname, u.email, COALESCE(org.org_name, '') AS organization,
                            s.service_name, s.dataset_id, s.organization as dataset_org
                     FROM dataset_permission_requests r
                     JOIN user u ON r.user_id = u.user_id
                     LEFT JOIN organization org ON u.org_id = org.org_id
                     JOIN service s ON r.service_id = s.service_id
                     ORDER BY r.created_at DESC"""
            cursor.execute(sql)
        else:
            sql = """SELECT r.request_id, r.user_id, r.service_id, r.fields_json, r.reason, r.status, r.created_at,
                            r.mou_file_path, r.mou_filename, r.request_type,
                            u.username, u.firstname, u.lastname, u.email, COALESCE(org.org_name, '') AS organization,
                            s.service_name, s.dataset_id, s.organization as dataset_org
                     FROM dataset_permission_requests r
                     JOIN user u ON r.user_id = u.user_id
                     LEFT JOIN organization org ON u.org_id = org.org_id
                     JOIN service s ON r.service_id = s.service_id
                     WHERE r.status = %s
                     ORDER BY r.created_at DESC"""
            cursor.execute(sql, (filter_status,))
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
        
        user_str = dataInput.get('user')
        if user_str and not user_data.get('user_id'):
            decoded_user = platform_decode(user_str)
            user_data = safe_json_loads(decoded_user)
            
        request_id = dataInput.get('request_id')
        
        if not checkUserIsAdmin(user_data) and str(user_data.get('previlage_id')) not in ['1', '3', '4', '5']:
            return jsonify({'status': 'error', 'message': 'Permission Denied'}), 403
            
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Get request info
        sql_req = "SELECT user_id, service_id, request_type FROM dataset_permission_requests WHERE request_id = %s"
        cursor.execute(sql_req, (request_id,))
        req_row = cursor.fetchone()
        
        if not req_row:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Request not found'}), 404
            
        target_user_id, service_id, req_type = req_row
        
        # Get granular permissions from request or defaults
        allow_dictionary = 1
        allow_dashboard = 1 if dataInput.get('allow_dashboard', (req_type in ('dashboard', 'all', None))) else 0
        allow_api = 1 if dataInput.get('allow_api', (req_type in ('api', 'all', None))) else 0

        # Update request status
        sql_update = """
            UPDATE dataset_permission_requests 
            SET status = 'Approved',
                approved_dictionary = %s,
                approved_dashboard = %s,
                approved_api = %s
            WHERE request_id = %s
        """
        cursor.execute(sql_update, (allow_dictionary, allow_dashboard, allow_api, request_id))
        
        # Grant access in service_user_access (preserving previous grants with GREATEST)
        sql_grant = """
            INSERT INTO service_user_access (service_id, user_id, allow_dictionary, allow_dashboard, allow_api) 
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            allow_dictionary = 1,
            allow_dashboard = GREATEST(COALESCE(allow_dashboard, 0), VALUES(allow_dashboard)),
            allow_api = GREATEST(COALESCE(allow_api, 0), VALUES(allow_api))
        """
        cursor.execute(sql_grant, (service_id, target_user_id, allow_dictionary, allow_dashboard, allow_api))
        
        conn.commit()
        
        # Log action
        logAction(user_data.get('user_id'), '/approveDatasetRequest', f'Approved request {request_id} ({req_type}) for user_id {target_user_id} on service_id {service_id}', 'info')
        
        # Notify User
        try:
            from .email_service import notify_access_approved
            cursor.execute("SELECT email FROM user WHERE user_id = %s", (target_user_id,))
            target_user_email = cursor.fetchone()
            
            if target_user_email and target_user_email[0]:
                cursor.execute("SELECT service_name FROM service WHERE service_id = %s", (service_id,))
                svc = cursor.fetchone()
                svc_name = svc[0] if svc else str(service_id)
                notify_access_approved(svc_name, [target_user_email[0]])
        except Exception as e:
            current_app.logger.error(f"Error sending access approved email: {e}")
            
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
        
        user_str = dataInput.get('user')
        if user_str and not user_data.get('user_id'):
            decoded_user = platform_decode(user_str)
            user_data = safe_json_loads(decoded_user)
            
        request_id = dataInput.get('request_id')
        
        if not checkUserIsAdmin(user_data) and str(user_data.get('previlage_id')) not in ['1', '3', '4', '5']:
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
    """Get all scopes across all services with parsed request_fields, response_fields, and conditions."""
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
                        srv.service_name, srv.dataset_id, srv.api_db_name, srv.api_source_name,
                        srv.api_request_fields AS global_request_fields,
                        srv.api_response_fields AS global_response_fields
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
            raw_scope = row.get('scope_json')
            req_f = []
            res_f = []
            conds = []
            if raw_scope:
                try:
                    scope_obj = json.loads(raw_scope) if isinstance(raw_scope, str) else raw_scope
                    if isinstance(scope_obj, dict) and ('request_fields' in scope_obj or 'response_fields' in scope_obj or 'conditions' in scope_obj):
                        req_f = scope_obj.get('request_fields', []) or []
                        res_f = scope_obj.get('response_fields', []) or []
                        conds = scope_obj.get('conditions', []) or []
                    elif isinstance(scope_obj, list):
                        conds = scope_obj
                    elif isinstance(scope_obj, dict):
                        conds = scope_obj
                    row['scope_json'] = scope_obj
                except:
                    pass
            row['request_fields'] = req_f
            row['response_fields'] = res_f
            row['conditions'] = conds

        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/saveApiScopeForUser', methods=['POST'])
@require_admin
def saveApiScopeForUser():
    """Upsert a credential and save its scope (request_fields, response_fields, conditions)."""
    try:
        dataInput = request.json
        user_data = getattr(request, 'current_user', {})
        if not user_data.get("user_id") and not checkUserIsAdmin(user_data):
            return jsonify({"status": "error", "message": "Unauthorized"}), 401

        service_id = dataInput['service_id']
        target_user_id = dataInput['target_user_id']
        scope_json = dataInput.get('scope_json')
        request_fields = dataInput.get('request_fields', [])
        response_fields = dataInput.get('response_fields', [])
        expires_at = dataInput.get('expires_at')

        # Structure standardized scope object (1 User : 1 API)
        if isinstance(scope_json, dict) and ('request_fields' in scope_json or 'response_fields' in scope_json or 'conditions' in scope_json):
            standard_scope_obj = {
                'request_fields': scope_json.get('request_fields', request_fields or []),
                'response_fields': scope_json.get('response_fields', response_fields or []),
                'conditions': scope_json.get('conditions', [])
            }
        else:
            standard_scope_obj = {
                'request_fields': request_fields or [],
                'response_fields': response_fields or [],
                'conditions': scope_json if isinstance(scope_json, (list, dict)) else []
            }
        scope_str = json.dumps(standard_scope_obj)

        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT credential_id FROM api_credentials WHERE service_id=%s AND user_id=%s", (service_id, target_user_id))
        cred = cursor.fetchone()
        
        full_secret_key = None
        if cred:
            credential_id = cred[0]
            if expires_at:
                try:
                    import dateutil.parser
                    exp_dt = dateutil.parser.parse(expires_at).strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("UPDATE api_credentials SET expires_at=%s WHERE credential_id=%s", (exp_dt, credential_id))
                except Exception:
                    pass
        else:
            import secrets
            import string
            import hashlib
            alphabet = string.ascii_letters + string.digits
            public_key_id = 'datax_' + ''.join(secrets.choice(alphabet) for i in range(12))
            secret_part = secrets.token_hex(16)
            full_secret_key = f"{public_key_id}.{secret_part}"
            
            secret_hash = hashlib.sha256(full_secret_key.encode('utf-8')).hexdigest()
            key_last_four = full_secret_key[-4:]
            
            if expires_at:
                try:
                    import dateutil.parser
                    exp_dt = dateutil.parser.parse(expires_at).strftime("%Y-%m-%d %H:%M:%S")
                    sql_insert = "INSERT INTO api_credentials (service_id, user_id, public_key_id, secret_hash, key_last_four, status, expires_at) VALUES (%s, %s, %s, %s, %s, 'active', %s)"
                    cursor.execute(sql_insert, (service_id, target_user_id, public_key_id, secret_hash, key_last_four, exp_dt))
                except Exception:
                    sql_insert = "INSERT INTO api_credentials (service_id, user_id, public_key_id, secret_hash, key_last_four, status) VALUES (%s, %s, %s, %s, %s, 'active')"
                    cursor.execute(sql_insert, (service_id, target_user_id, public_key_id, secret_hash, key_last_four))
            else:
                sql_insert = "INSERT INTO api_credentials (service_id, user_id, public_key_id, secret_hash, key_last_four, status) VALUES (%s, %s, %s, %s, %s, 'active')"
                cursor.execute(sql_insert, (service_id, target_user_id, public_key_id, secret_hash, key_last_four))
            credential_id = cursor.lastrowid
            
        cursor.execute("SELECT scope_id FROM api_scopes WHERE credential_id=%s", (credential_id,))
        if cursor.fetchone():
            cursor.execute("UPDATE api_scopes SET scope_json=%s WHERE credential_id=%s", (scope_str, credential_id))
        else:
            cursor.execute("INSERT INTO api_scopes (credential_id, scope_json) VALUES (%s, %s)", (credential_id, scope_str))
            
        conn.commit()
        cursor.close()
        conn.close()
        
        resp = {'status': 'success'}
        if full_secret_key:
            resp['secret_key'] = full_secret_key
        return jsonify(resp)
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



@app.route('/toggleApiEnabled', methods=['POST'])
@require_admin
def toggleApiEnabled():
    try:
        dataInput = request.json
        service_id = dataInput.get('service_id')
        api_enabled = dataInput.get('api_enabled')
        
        if not service_id or api_enabled is None:
            return jsonify({'status': 'error', 'message': 'Missing service_id or api_enabled'}), 400
            
        conn = mysql.connect()
        cursor = conn.cursor()
        
        sql = "UPDATE service SET api_enabled = %s WHERE service_id = %s"
        cursor.execute(sql, (api_enabled, service_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error in toggleApiEnabled: " + str(e))
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/deleteApiService', methods=['POST'])
@require_admin
def deleteApiService():
    try:
        dataInput = request.json
        service_id = dataInput.get('service_id')
        
        if not service_id:
            return jsonify({'status': 'error', 'message': 'Missing service_id'})
            
        conn = mysql.connect()
        cursor = conn.cursor()
        
        # Check if service is an API (has api_type)
        cursor.execute("SELECT api_type FROM service WHERE service_id = %s", (service_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            cursor.close()
            conn.close()
            return jsonify({'status': 'error', 'message': 'Cannot delete original dataset or service not found'})
            
        # Delete related metadata_permission (it uses metadata_id)
        cursor.execute("DELETE FROM metadata_permission WHERE metadata_id = %s", (service_id,))
        
        # Delete related api_scopes and credentials
        cursor.execute("DELETE FROM api_scopes WHERE credential_id IN (SELECT credential_id FROM api_credentials WHERE service_id = %s)", (service_id,))
        cursor.execute("DELETE FROM api_credentials WHERE service_id = %s", (service_id,))
        
        # Finally delete service
        cursor.execute("DELETE FROM service WHERE service_id = %s", (service_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'API deleted successfully'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"Delete API Error: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/updateApiService', methods=['POST'])
@require_admin
def updateApiService():
    try:
        dataInput = request.json
        service_id = dataInput.get('service_id')
        
        if not service_id:
            return jsonify({'status': 'error', 'message': 'Missing service_id'})
            
        api_name = dataInput.get('api_name')
        api_endpoint = dataInput.get('api_endpoint')
        api_description = dataInput.get('api_description')
        api_enabled = 1 if dataInput.get('api_enabled') in ['true', '1', True, 'Active = Enable'] else 0
        api_type = dataInput.get('api_type')
        api_db_name = dataInput.get('api_db_name')
        api_source_name = dataInput.get('api_source_name')
        
        import json
        req_fields = dataInput.get('api_request_fields', [])
        res_fields = dataInput.get('api_response_fields', [])
        req_str = json.dumps(req_fields) if isinstance(req_fields, list) else req_fields
        res_str = json.dumps(res_fields) if isinstance(res_fields, list) else res_fields
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        update_sql = """
            UPDATE service 
            SET service_name = %s, api_endpoint = %s, description = %s, api_enabled = %s, 
                api_type = %s, api_db_name = %s, api_source_name = %s, 
                api_request_fields = %s, api_response_fields = %s
            WHERE service_id = %s
        """
        cursor.execute(update_sql, (
            api_name, api_endpoint, api_description, api_enabled, 
            api_type, api_db_name, api_source_name, 
            req_str, res_str, service_id
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'API updated successfully'})
    except Exception as e:
        import traceback
        current_app.logger.error(f"Update API Error: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)})
