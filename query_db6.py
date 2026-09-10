import sys
sys.path.insert(0, '/app')
from ServiceConfig import mysql
from app import app as main_app
with main_app.app_context():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN org_id INT NULL;")
        conn.commit()
        print("Column org_id added successfully")
    except Exception as e:
        print(f"Error: {e}")
