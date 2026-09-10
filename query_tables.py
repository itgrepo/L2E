import pymysql
conn = pymysql.connect(host='datax_db', user='astro', password='password123', database='datax_db', port=3306)
cursor = conn.cursor(pymysql.cursors.DictCursor)
cursor.execute("SELECT mp.menu_name_id, mp.value, mn.menu_name FROM menu_permission mp JOIN menu_name mn ON mp.menu_name_id = mn.menu_name_id WHERE mp.previlage_id=1")
for row in cursor.fetchall():
    print(f"ID {row['menu_name_id']}: {row['menu_name']} = {row['value']}")
