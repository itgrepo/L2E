from ServiceConfig import mysql

def notify_user(user_id, notif_type, message):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (user_id, notif_type, message))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to send notification:", e)

def notify_all_users(notif_type, message):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user WHERE status = 'Active'")
        users = cursor.fetchall()
        for u in users:
            cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (u[0], notif_type, message))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to notify all users:", e)
