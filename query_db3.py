import sys
sys.path.insert(0, '/app')
from ServiceConfig import mysql
from app import app as main_app
with main_app.app_context():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user.user_id, user.username, user.email, user.status_id 
        FROM `user`
        LEFT JOIN codename_previlage as cp ON cp.previlage_id = user.previlage_id
        LEFT JOIN organization org ON user.org_id = org.org_id
        WHERE user.status_id != '7' AND user.email = 'jarukorn.w@gmail.com'
    """)
    rows = cursor.fetchall()
    print(rows)
