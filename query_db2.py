import sys
sys.path.insert(0, '/app')
from ServiceConfig import mysql
from flask import Flask

app = Flask(__name__)
# Try to just use the existing app's config
from app import app as main_app
with main_app.app_context():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, email, status_id FROM user WHERE username='test' OR email='jarukorn.w@gmail.com'")
    rows = cursor.fetchall()
    print(rows)
