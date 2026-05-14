import pymysql
import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '110.78.210.128'), # UAT DB
    'user': os.environ.get('DB_USER', 'astro'),
    'password': os.environ.get('DB_PASS', 'zjkoC]6p'),
    'db': os.environ.get('DB_NAME', 'psu_backend'),
    'port': int(os.environ.get('DB_PORT', 3307)),
    'charset': 'utf8mb4'
}

def check_user(username):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            print(f"--- Checking users with username: {username} ---")
            cursor.execute("SELECT user_id, username, status_id, status_account, email FROM user WHERE username = %s ORDER BY user_id DESC", (username,))
            users = cursor.fetchall()
            for u in users:
                print(f"User ID: {u['user_id']}, Status: {u['status_id']}, Account: {u['status_account']}, Email: {u['email']}")
                
            print(f"\n--- Checking user_activity for these IDs ---")
            if users:
                ids = [str(u['user_id']) for u in users]
                cursor.execute(f"SELECT user_id, status_account, create_date FROM user_activity WHERE user_id IN ({','.join(ids)})")
                activities = cursor.fetchall()
                for a in activities:
                    print(f"User ID: {a['user_id']}, Activity Status: {a['status_account']}, Create Date: {a['create_date']}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_user('approve_test_user')
