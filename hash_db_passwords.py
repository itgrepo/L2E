import hmac
import hashlib
import mysql.connector

def hash_password(password):
    if not password:
        return password
    password = str(password)
    if len(password) == 64 and all(c in "0123456789abcdefABCDEF" for c in password):
        return password
    if password.startswith("$2b$"):
        return password
    key = b"e9NHdT3GU6wBdWlw3RTqvrShGzyerRl4BaMhFeUI3v4j6U0opW5a19HQHDAHHCrhYXq8oG6D"
    msg = password.encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3307,
        user="astro",
        password="password123",
        database="datax_db_3003"
    )
    cursor = conn.cursor(dictionary=True)
    
    # 1. Update user
    cursor.execute("SELECT user_id, password FROM user")
    users = cursor.fetchall()
    for u in users:
        new_pass = hash_password(u['password'])
        if new_pass != u['password']:
            cursor.execute("UPDATE user SET password = %s WHERE user_id = %s", (new_pass, u['user_id']))
    
    # 2. Update user_activity
    cursor.execute("SELECT user_id, password FROM user_activity")
    activities = cursor.fetchall()
    for a in activities:
        new_pass = hash_password(a['password'])
        if new_pass != a['password']:
            cursor.execute("UPDATE user_activity SET password = %s WHERE user_id = %s", (new_pass, a['user_id']))
            
    # 3. Update user_password_history
    cursor.execute("SELECT id, password FROM user_password_history")
    history = cursor.fetchall()
    for h in history:
        new_pass = hash_password(h['password'])
        if new_pass != h['password']:
            cursor.execute("UPDATE user_password_history SET password = %s WHERE id = %s", (new_pass, h['id']))
            
    conn.commit()
    cursor.close()
    conn.close()
    print("Database passwords hashed successfully.")
except Exception as e:
    print(f"Error: {e}")
