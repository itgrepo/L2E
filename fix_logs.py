import os

register_path = "/home/ubuntu/Intelligist_DataX_Deploy_3003/backendold/Astro_backend/app/ServiceConfig/register.py"
roles_path = "/home/ubuntu/Intelligist_DataX_Deploy_3003/backendold/Astro_backend/app/Management/rolesMgmt.py"

with open(register_path, "r") as f:
    content = f.read()

old_reg_log = "logAction(user_id, '/registerSimple', 'User registered, pending email verification', 'info')"
new_reg_log = """import datetime
        now_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        log_msg = f'User registered | วันลงทะเบียน: {now_str} | วันอนุมัติ: - | ประเภท: ผู้ใช้งานทั่วไป (General User)'
        logAction(user_id, '/registerSimple', log_msg, 'info')"""
content = content.replace(old_reg_log, new_reg_log)

old_app_log = "logAction(admin_data.get('user_id', 0), '/approveUser', f'Approved user {username} (ID: {target_user_id})', 'info')"
new_app_log = """import datetime
        cursor.execute("SELECT create_at FROM user WHERE user_id = %s", (target_user_id,))
        reg_row = cursor.fetchone()
        reg_str = '-'
        if reg_row and reg_row[0]:
            try:
                reg_str = reg_row[0].strftime('%d/%m/%Y %H:%M:%S')
            except:
                reg_str = str(reg_row[0])
        now_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        log_msg = f'Approved user {username} (ID: {target_user_id}) | วันลงทะเบียน: {reg_str} | วันอนุมัติ: {now_str} | ประเภท: ผู้ใช้งานทั่วไป (General User)'
        logAction(admin_data.get('user_id', 0), '/approveUser', log_msg, 'info')"""
content = content.replace(old_app_log, new_app_log)

with open(register_path, "w") as f:
    f.write(content)

with open(roles_path, "r") as f:
    rcontent = f.read()

old_cre_log = 'logAction(user_id=user_data.get(\'user_id\'), path="/mgmt/createUser", log=f"Admin created user: {username}", type="info")'
new_cre_log = """import datetime
        now_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        log_msg = f'Admin created user: {username} | วันลงทะเบียน: {now_str} | วันอนุมัติ: {now_str} | ประเภท: สร้างโดยแอดมิน (Admin)'
        logAction(user_id=user_data.get('user_id'), path="/mgmt/createUser", log=log_msg, type="info")"""
rcontent = rcontent.replace(old_cre_log, new_cre_log)

with open(roles_path, "w") as f:
    f.write(rcontent)

print("Logs updated successfully.")
