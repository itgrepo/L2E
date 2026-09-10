filepath = "/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/Management/rolesMgmt.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """        # Check duplicate
        cursor.execute("SELECT user_id FROM user WHERE (username = %s OR email = %s) AND status_id != '7'", (username, email))
        if cursor.fetchone():
            cursor.close()
            return jsonify({"status": "error", "message": "Username or Email already exists"})"""

new_code = """        # Check duplicate
        cursor.execute("SELECT username, email FROM user WHERE (username = %s OR email = %s) AND status_id != '7'", (username, email))
        dup = cursor.fetchone()
        if dup:
            cursor.close()
            if dup[0] == username:
                return jsonify({"status": "error", "message": "Username already exists"})
            else:
                return jsonify({"status": "error", "message": "Email already exists"})"""

content = content.replace(old_code, new_code)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Backend duplicate check fixed!")
