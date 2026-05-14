import pymysql
import json

def check_schema():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='ieat_pass',
            db='psu_backend',
            port=3307  # Port on UAT server
        )
        cursor = conn.cursor()
        cursor.execute("DESC user")
        columns = cursor.fetchall()
        print(json.dumps(columns, indent=2))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
