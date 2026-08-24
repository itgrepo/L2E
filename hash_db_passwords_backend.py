import sys
sys.path.append("/home/ubuntu/Intelligist_DataX_Deploy_3003/backendold/Astro_backend/app")
from ServiceConfig import mysql, app
from ServiceConfig.__init__ import hash_password

with app.app_context():
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # Update user
    cursor.execute("SELECT user_id, password FROM user")
    users = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    users_dict = [dict(zip(columns, row)) for row in users]
    for u in users_dict:
        new_pass = hash_password(u['password'])
        if new_pass != u['password']:
            cursor.execute("UPDATE user SET password = %s WHERE user_id = %s", (new_pass, u['user_id']))
    
    # Update user_activity
    cursor.execute("SELECT user_id, password FROM user_activity")
    activities = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    activities_dict = [dict(zip(columns, row)) for row in activities]
    for a in activities_dict:
        new_pass = hash_password(a['password'])
        if new_pass != a['password']:
            cursor.execute("UPDATE user_activity SET password = %s WHERE user_id = %s", (new_pass, a['user_id']))
            
    # Update user_password_history
    cursor.execute("SELECT id, password FROM user_password_history")
    history = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    history_dict = [dict(zip(columns, row)) for row in history]
    for h in history_dict:
        new_pass = hash_password(h['password'])
        if new_pass != h['password']:
            cursor.execute("UPDATE user_password_history SET password = %s WHERE id = %s", (new_pass, h['id']))
            
    conn.commit()
    cursor.close()
    conn.close()
    print("Database passwords hashed successfully.")
