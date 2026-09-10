import re

file_path = '/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/login.py'
with open(file_path, 'r') as f:
    content = f.read()

target = """                if count_login >= 5:
                    return jsonify({"status": 'Your account is locked'})"""

replacement = """                if count_login >= 5:
                    try:
                        if email and check_email_format(email):
                            import uuid
                            token = (str(uuid.uuid4()) + str(uuid.uuid1())).replace('-', '')
                            conn2 = mysql.connect()
                            cursor2 = conn2.cursor()
                            cursor2.execute("INSERT INTO token_unlock_account VALUES (NULL, %s, %s, %s, %s, CURRENT_TIMESTAMP)", (token, username, email, 'active'))
                            conn2.commit()
                            cursor2.close()
                            conn2.close()
                            sendMailUnlockAccount(token, email, link, username, result_username[0]['user_id'])
                    except Exception as e:
                        print("Error sending unlock email:", e)
                    return jsonify({"status": 'Your account is locked'})"""

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w') as f:
        f.write(content)
    print("Patched login.py successfully.")
else:
    print("Target not found in login.py")
