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
        cursor.execute("SELECT user_id FROM user WHERE status_account = 'active'")
        users = cursor.fetchall()
        for u in users:
            cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (u[0], notif_type, message))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to notify all users:", e)

def notify_dataset_interest(service_id, notif_type, message):
    """Notify users who have accessed or requested this dataset, or all active users if general."""
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        # Find users who have access or pending requests for this service
        cursor.execute("""
            SELECT DISTINCT user_id FROM (
                SELECT user_id FROM service_user_access WHERE service_id = %s
                UNION
                SELECT user_id FROM dataset_permission_requests WHERE service_id = %s
            ) AS interested_users
        """, (service_id, service_id))
        users = cursor.fetchall()
        
        # If specific interested users exist, notify them; otherwise notify all active users
        user_ids = [u[0] for u in users if u[0]]
        if not user_ids:
            cursor.execute("SELECT user_id FROM user WHERE status_account = 'active'")
            user_ids = [u[0] for u in cursor.fetchall() if u[0]]
            
        for uid in set(user_ids):
            cursor.execute("INSERT INTO notifications (user_id, type, message) VALUES (%s, %s, %s)", (uid, notif_type, message))
            
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to notify dataset interest:", e)
