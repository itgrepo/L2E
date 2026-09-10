import sys
sys.path.insert(0, '/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app')
from ServiceConfig.config import mysql
from flask import Flask

app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Astro@2024'
app.config['MYSQL_DATABASE_DB'] = 'intelligist_datax'
app.config['MYSQL_DATABASE_HOST'] = 'datax_db'

mysql.init_app(app)

with app.app_context():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, email, status_id FROM user WHERE username='test' OR email='jarukorn.w@gmail.com'")
    rows = cursor.fetchall()
    print(rows)
