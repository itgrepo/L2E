import sys, pymysql
sys.path.insert(0, '/app')
conn = pymysql.connect(host='datax_db', user='astro', password='password123', database='datax_db', port=3306)
cursor = conn.cursor(pymysql.cursors.DictCursor)
cursor.execute("SELECT username, email FROM user WHERE username='testxxx0001'")
print(cursor.fetchall())
