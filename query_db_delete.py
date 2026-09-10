import sys
sys.path.insert(0, '/app')
from ServiceConfig import mysql
from app import app as main_app
with main_app.app_context():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user WHERE username = 'ForT005' OR email = 'Jarukorn83@gmail.com'")
    conn.commit()
    print("Deleted ForT005")
