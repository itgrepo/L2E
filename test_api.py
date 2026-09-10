import sys, pymysql
sys.path.insert(0, '/app')
conn = pymysql.connect(host='datax_db', user='astro', password='password123', database='datax_db', port=3306)
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "SELECT MIN(menu_name_id) as menu_name_id, menu_name FROM `menu_name` WHERE menu_name NOT IN ('User Management','Permission Management','Service Configuration') GROUP BY menu_name"
cursor.execute(sql)
print(cursor.fetchall())
