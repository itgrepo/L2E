# -*- coding: utf-8 -*-
from ServiceConfig import (
    app, mysql, jsonify, request, toJson, logAction, decode,
    safe_json_loads, platform_decode, auth_serializer, require_admin
)
import pyotp
import json
import sys
import time
from flask import current_app


def complete_user_login(user_row, activity_row, result_time_activity, username, user_id):
    """Finalizes a successful login session, generating tokens, updating statuses, and logging."""
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # 1. Generate auth token
    token_payload = {
        "user_id": user_row["user_id"],
        "username": user_row["username"],
        "email": user_row.get("email", ""),
        "previlage_id": user_row.get("previlage_id"),
        "org_id": user_row.get("org_id")
    }
    user_row['token'] = auth_serializer.dumps(token_payload)
    
    # 2. Check consent agreement policy
    sql_consent = """SELECT consent_agreement.version
                     FROM consent_agreement 
                     LEFT JOIN user_agreement 
                         ON user_agreement.consent_agreement_id = consent_agreement.consent_agreement_id 
                     WHERE user_agreement.user_id = %s AND 
                     user_agreement.date_time = (SELECT MAX(date_time) FROM user_agreement WHERE user_id = %s)"""
    cursor.execute(sql_consent, (user_id, user_id))
    data_consent = cursor.fetchall()
    columns_consent = [col[0] for col in cursor.description]
    result_version = toJson(data_consent, columns_consent)
    
    check_version = result_version[0]['version'] if len(result_version) > 0 else 1
    
    from ServiceConfig.login import checkPolicy
    check_policy = checkPolicy(check_version)
    
    login_status_val = str(activity_row.get('login_status', '0'))
    
    if login_status_val != '2':
        if str(user_row.get('previlage_id')) not in ['3', '4']:  # Normal Users
            user_row['isAdmin'] = 'false'
            is_approved = False if str(user_row.get('status_id')) == '8' or str(user_row.get('previlage_id')) == '1' else True
            user_row['is_approved'] = is_approved
            user_row['requires_onboarding'] = not is_approved
            
            sql_up_user = """UPDATE user SET status_id = CASE WHEN status_id = 8 THEN 8 ELSE 2 END, count_login = 0, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status_id != '7' AND status_account='active'"""
            cursor.execute(sql_up_user, (username,))
            conn.commit()
            logAction(user_row['user_id'], '/login', 'login success (2FA verified)', 'info')
            
            sql_up_act = """UPDATE user_activity SET login_respond = UNIX_TIMESTAMP(), login_status = 1 WHERE user_id = %s"""
            cursor.execute(sql_up_act, (user_id,))
            conn.commit()
            
            sql_act_check = """SELECT login_respond, create_date, status_account FROM user_activity WHERE user_id = %s"""
            cursor.execute(sql_act_check, (user_id,))
            data_act2 = cursor.fetchall()
            columns_act2 = [col[0] for col in cursor.description]
            result2 = toJson(data_act2, columns_act2)
            cursor.close()
            conn.close()
            
            if len(result2) > 0 and len(result_time_activity) > 0:
                if int(result2[0].get('login_respond', 0)) - int(result2[0].get('create_date', 0)) >= result_time_activity[0].get('duration', 7776000):
                    return jsonify({"status": "change password", "data": user_row})
                else:
                    if check_policy == "success":
                        return jsonify({"status": "success", "data": user_row})
                    else:
                        logAction(user_row['user_id'], '/login', 'policy is update', 'info')
                        return jsonify({"status": "policy is update", "data": user_row})
            else:
                return jsonify({"status": "success", "data": user_row})
        else:  # Admin or Root
            user_row['isAdmin'] = 'true'
            user_row['is_approved'] = True
            user_row['requires_onboarding'] = False
            
            sql_up_admin = """UPDATE user SET status_id = 2, count_login = 0, create_at = CURRENT_TIMESTAMP WHERE username = %s AND status_id != '7' AND status_account='active'"""
            cursor.execute(sql_up_admin, (username,))
            conn.commit()
            
            sql_up_admin_act = """UPDATE user_activity SET status_account = '1', login_respond = UNIX_TIMESTAMP(), login_status = 1 WHERE user_id = %s"""
            cursor.execute(sql_up_admin_act, (user_id,))
            conn.commit()
            
            sql_admin_act_check = """SELECT login_respond, create_date, status_account FROM user_activity WHERE user_id = %s"""
            cursor.execute(sql_admin_act_check, (user_id,))
            data_act2 = cursor.fetchall()
            columns_act2 = [col[0] for col in cursor.description]
            result2 = toJson(data_act2, columns_act2)
            cursor.close()
            conn.close()
            
            if len(result2) > 0 and len(result_time_activity) > 0:
                if int(result2[0].get('login_respond', 0)) - int(result2[0].get('create_date', 0)) >= result_time_activity[0].get('duration', 7776000):
                    logAction(user_row['user_id'], '/login', 'change password admin', 'info')
                    return jsonify({"status": "change password admin", "data": user_row})
                else:
                    logAction(user_row['user_id'], '/login', 'user is admin (2FA verified)', 'info')
                    return jsonify({"status": "user is admin", "data": user_row, "status2": check_policy})
            else:
                return jsonify({"status": "user is admin", "data": user_row, "status2": check_policy})
    else:  # login_status == '2'
        sql_st2 = "UPDATE user_activity SET login_status = '1' WHERE user_id = %s"
        cursor.execute(sql_st2, (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        if str(user_row.get('previlage_id')) in ['3', '4']:
            user_row['isAdmin'] = 'true'
            return jsonify({"status": "user is admin", "data": user_row})
        else:
            user_row['isAdmin'] = 'false'
            return jsonify({"status": "success", "data": user_row, "status2": check_policy})


def complete_user_login_from_id(user_id):
    """Helper to fetch user data and execute final login session completion."""
    conn = mysql.connect()
    cursor = conn.cursor()
    
    sql_user = """SELECT user.*, DataField.sublevel_id, sublevel_master.Level_Master_id FROM user
    JOIN user_activity ON user.user_id = user_activity.user_id
    LEFT JOIN DataField ON user.national_id_book = DataField.national_id_book and user.national_id = DataField.national_id
    LEFT JOIN sublevel_master ON DataField.sublevel_id = sublevel_master.sublevel_id
    WHERE user.user_id = %s
    and DataField.sublevel_id = (select max(aa.sublevel_id) from DataField aa where user.national_id_book = aa.national_id_book and user.national_id = aa.national_id and aa.expiration >= CURRENT_DATE)
    and expiration >= CURRENT_DATE"""
    cursor.execute(sql_user, (user_id,))
    data = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    result = toJson(data, columns)
    
    if len(result) == 0:
        cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = toJson(data, columns)
        
    if len(result) > 0 and "password" in result[0]:
        del result[0]["password"]
        
    cursor.execute("SELECT * FROM user_activity WHERE user_id = %s", (user_id,))
    data_act = cursor.fetchall()
    columns_act = [col[0] for col in cursor.description]
    result1 = toJson(data_act, columns_act)
    
    cursor.execute("SELECT duration FROM timetable_activity WHERE activity_desc = 'ForceChangePassword'")
    data_tt = cursor.fetchall()
    columns_tt = [col[0] for col in cursor.description]
    result_time_activity = toJson(data_tt, columns_tt)
    cursor.close()
    conn.close()
    
    if len(result) == 0 or len(result1) == 0:
        return jsonify({"status": "error", "message": "User not found"}), 404
        
    username = result[0]['username']
    return complete_user_login(result[0], result1[0], result_time_activity, username, user_id)


# ==============================================================================
# 2FA API Routes
# ==============================================================================

@app.route('/2fa/login-verify', methods=['POST'])
@app.route('/api/2fa/login-verify', methods=['POST'])
def two_factor_login_verify():
    """Verifies the 6-digit TOTP code during 2-Step Login for users with 2FA already enabled."""
    try:
        data = request.json or {}
        temp_token = data.get('temp_token')
        otp = str(data.get('otp', '')).strip().replace(' ', '')
        
        if not temp_token or not otp:
            return jsonify({"status": "error", "message": "กรุณาระบุรหัส OTP 6 หลัก"}), 400
            
        try:
            payload = auth_serializer.loads(temp_token, max_age=600)
        except Exception as e:
            return jsonify({"status": "error", "message": "เซสชันการเข้าสู่ระบบหมดอายุแล้ว กรุณาล็อกอินใหม่อีกครั้ง"}), 401
            
        if payload.get('action') != 'login_2fa' or not payload.get('user_id'):
            return jsonify({"status": "error", "message": "โทเค็นการยืนยันตัวตนไม่ถูกต้อง"}), 401
            
        user_id = payload['user_id']
        
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT secret_key, is_enabled FROM user_two_factor WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row or not row[0] or row[1] != 1:
            return jsonify({"status": "error", "message": "บัญชีนี้ยังไม่ได้เปิดใช้งาน 2FA"}), 400
            
        secret_key = row[0]
        totp = pyotp.TOTP(secret_key)
        
        # valid_window=1 allows 1 window before and 1 after (handles +/- 30s clock drift)
        if not totp.verify(otp, valid_window=1):
            logAction(user_id, '/api/2fa/login-verify', '2FA OTP verification failed: incorrect or expired code', 'warning')
            return jsonify({"status": "error", "message": "รหัส OTP 6 หลักไม่ถูกต้องหรือหมดอายุแล้ว กรุณาลองใหม่อีกครั้ง"}), 400
            
        # OTP is correct -> complete the login
        return complete_user_login_from_id(user_id)
        
    except Exception as e:
        current_app.logger.error(f"2FA Login Verify Error: {e}")
        return jsonify({"status": "error", "message": "เกิดข้อผิดพลาดในการตรวจสอบ 2FA"}), 500


@app.route('/2fa/setup-and-login-verify', methods=['POST'])
@app.route('/api/2fa/setup-and-login-verify', methods=['POST'])
def two_factor_setup_and_login_verify():
    """Verifies the 6-digit TOTP code and activates 2FA on first login, then logs the user in."""
    try:
        data = request.json or {}
        temp_token = data.get('temp_token')
        otp = str(data.get('otp', '')).strip().replace(' ', '')
        
        if not temp_token or not otp:
            return jsonify({"status": "error", "message": "กรุณาระบุรหัส OTP 6 หลัก"}), 400
            
        try:
            payload = auth_serializer.loads(temp_token, max_age=900)
        except Exception:
            return jsonify({"status": "error", "message": "เซสชันการตั้งค่า 2FA หมดอายุแล้ว กรุณาล็อกอินเพื่อลองใหม่อีกครั้ง"}), 401
            
        if payload.get('action') != 'setup_2fa' or not payload.get('user_id') or not payload.get('secret_key'):
            return jsonify({"status": "error", "message": "ข้อมูลการตั้งค่าไม่ถูกต้อง"}), 401
            
        user_id = payload['user_id']
        secret_key = payload['secret_key']
        
        totp = pyotp.TOTP(secret_key)
        if not totp.verify(otp, valid_window=1):
            return jsonify({"status": "error", "message": "รหัส OTP 6 หลักไม่ถูกต้อง กรุณาตรวจสอบรหัสในแอป Google Authenticator อีกครั้ง"}), 400
            
        # Activate 2FA in database
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_two_factor (user_id, secret_key, is_enabled)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE secret_key = %s, is_enabled = 1, updated_at = CURRENT_TIMESTAMP
        """, (user_id, secret_key, secret_key))
        cursor.execute("UPDATE user SET 2fa_status = 'on' WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        logAction(user_id, '/api/2fa/setup-and-login-verify', '2FA enabled successfully on first login', 'info')
        
        # Complete login
        return complete_user_login_from_id(user_id)
        
    except Exception as e:
        current_app.logger.error(f"2FA Setup and Login Error: {e}")
        return jsonify({"status": "error", "message": "เกิดข้อผิดพลาดในการตั้งค่า 2FA"}), 500


def _extract_user(data):
    if not isinstance(data, dict):
        return {}
    user_val = data.get('user')
    if isinstance(user_val, dict):
        return user_val
    elif isinstance(user_val, str) and user_val:
        try:
            parsed = safe_json_loads(platform_decode(user_val))
            if isinstance(parsed, dict) and parsed:
                return parsed
        except Exception:
            pass
        try:
            parsed = auth_serializer.loads(user_val, max_age=86400 * 30)
            if isinstance(parsed, dict) and parsed:
                return parsed
        except Exception:
            pass
    if data.get('user_id'):
        return {'user_id': data.get('user_id'), 'username': data.get('username')}
    return getattr(request, 'current_user', {}) or {}


@app.route('/2fa/status', methods=['POST'])
@app.route('/api/2fa/status', methods=['POST'])
def two_factor_status():
    """Checks the 2FA status for the authenticated user."""
    try:
        data = request.json or {}
        user_data = _extract_user(data)
        user_id = user_data.get('user_id')
        
        if not user_id:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
            
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 2fa_status FROM user WHERE user_id = %s", (user_id,))
        user_row = cursor.fetchone()
        cursor.execute("SELECT is_enabled, secret_key FROM user_two_factor WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        user_2fa = str(user_row[0]).lower() if user_row and user_row[0] else 'off'
        is_enabled = bool(row and row[0] == 1 and user_2fa == 'on')
        return jsonify({
            "status": "success",
            "is_enabled": is_enabled,
            "two_factor_status": "on" if is_enabled else "off"
        })
    except Exception as e:
        current_app.logger.error(f"2FA Status Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/2fa/setup', methods=['POST'])
@app.route('/api/2fa/setup', methods=['POST'])
def two_factor_setup_for_profile():
    """Generates a secret key and otpauth URL for a user setting up 2FA from their profile."""
    try:
        data = request.json or {}
        user_data = _extract_user(data)
        user_id = user_data.get('user_id')
        username = user_data.get('username', 'user')
        
        if not user_id:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
            
        secret_key = pyotp.random_base32()
        otpauth_url = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=username,
            issuer_name="Learn2Earn DataX"
        )
        
        # Save inactive secret key temporarily
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_two_factor (user_id, secret_key, is_enabled)
            VALUES (%s, %s, 0)
            ON DUPLICATE KEY UPDATE secret_key = %s, is_enabled = 0
        """, (user_id, secret_key, secret_key))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "secret_key": secret_key,
            "otpauth_url": otpauth_url
        })
    except Exception as e:
        current_app.logger.error(f"2FA Profile Setup Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/2fa/verify-and-enable', methods=['POST'])
@app.route('/api/2fa/verify-and-enable', methods=['POST'])
def two_factor_verify_and_enable():
    """Verifies OTP and permanently enables 2FA from Profile view."""
    try:
        data = request.json or {}
        user_data = _extract_user(data)
        user_id = user_data.get('user_id')
        otp = str(data.get('otp', '')).strip().replace(' ', '')
        
        if not user_id or not otp:
            return jsonify({"status": "error", "message": "กรุณาระบุรหัส OTP 6 หลัก"}), 400
            
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT secret_key FROM user_two_factor WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        
        if not row or not row[0]:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "ไม่พบข้อมูล Secret Key กรุณากดเริ่มต้นใหม่อีกครั้ง"}), 400
            
        secret_key = row[0]
        totp = pyotp.TOTP(secret_key)
        if not totp.verify(otp, valid_window=1):
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "รหัส OTP 6 หลักไม่ถูกต้องหรือหมดอายุแล้ว"}), 400
            
        cursor.execute("UPDATE user_two_factor SET is_enabled = 1, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s", (user_id,))
        cursor.execute("UPDATE user SET 2fa_status = 'on' WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        logAction(user_id, '/api/2fa/verify-and-enable', '2FA enabled from profile', 'info')
        return jsonify({"status": "success", "message": "เปิดใช้งาน Google Authenticator เรียบร้อยแล้ว"})
        
    except Exception as e:
        current_app.logger.error(f"2FA Verify Enable Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/2fa/disable', methods=['POST'])
@app.route('/api/2fa/disable', methods=['POST'])
def two_factor_disable():
    """Disables 2FA after password confirmation."""
    try:
        data = request.json or {}
        user_data = _extract_user(data)
        user_id = user_data.get('user_id')
        password = data.get('password')
        
        if not user_id or not password:
            return jsonify({"status": "error", "message": "กรุณากรอกรหัสผ่านเพื่อยืนยันการปิดใช้งาน"}), 400
            
        # Verify password
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user.user_id, user_activity.password FROM user 
            JOIN user_activity ON user.user_id = user_activity.user_id 
            WHERE user.user_id = %s AND user.status_id != '7'
        """, (user_id,))
        matched = cursor.fetchone()
        
        if not matched:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "ไม่พบผู้ใช้งาน"}), 404
            
        db_pwd = matched[1]
        from ServiceConfig.login import decode_raw_password
        raw_input = decode_raw_password(password)
        raw_db = decode_raw_password(db_pwd)
        
        if password != db_pwd and raw_input != raw_db and raw_input != db_pwd:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "รหัสผ่านไม่ถูกต้อง"}), 400
            
        cursor.execute("UPDATE user_two_factor SET is_enabled = 0, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s", (user_id,))
        cursor.execute("UPDATE user SET 2fa_status = 'off' WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        logAction(user_id, '/api/2fa/disable', '2FA disabled by user', 'info')
        return jsonify({"status": "success", "message": "ปิดการใช้งาน Google Authenticator เรียบร้อยแล้ว"})
        
    except Exception as e:
        current_app.logger.error(f"2FA Disable Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/2fa/admin-reset', methods=['POST'])
@app.route('/api/2fa/admin-reset', methods=['POST'])
@require_admin
def two_factor_admin_reset():
    """Admin function to reset 2FA for a user who lost their device."""
    try:
        data = request.json or {}
        caller_data = getattr(request, 'current_user', {})
        target_user_id = data.get('target_user_id')
        
        if not target_user_id:
            return jsonify({"status": "error", "message": "กรุณาระบุ target_user_id"}), 400
            
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM user WHERE user_id = %s", (target_user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "ไม่พบผู้ใช้งานนี้ในระบบ"}), 404
            
        cursor.execute("UPDATE user_two_factor SET is_enabled = 0, secret_key = '', updated_at = CURRENT_TIMESTAMP WHERE user_id = %s", (target_user_id,))
        cursor.execute("UPDATE user SET 2fa_status = 'on' WHERE user_id = %s", (target_user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        logAction(
            caller_data.get('user_id', 0),
            '/api/2fa/admin-reset',
            f"Reset 2FA for user {target_user[0]} (ID: {target_user_id})",
            'warning'
        )
        return jsonify({"status": "success", "message": f"รีเซ็ต 2FA สำหรับผู้ใช้ {target_user[0]} เรียบร้อยแล้ว"})
        
    except Exception as e:
        current_app.logger.error(f"Admin 2FA Reset Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
