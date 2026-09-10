import sys
sys.path.insert(0, '/app')
from ServiceConfig import mysql
from app import app as main_app
with main_app.app_context():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE '%org%'")
    rows = cursor.fetchall()
    print([r[0] for r in rows])
