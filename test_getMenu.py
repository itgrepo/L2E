import sys
sys.path.insert(0, '/app')
import pymysql

conn = pymysql.connect(host='datax_db', user='astro', password='password123', database='datax_db', port=3306)
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = """SELECT menu_name.menu_name 
            FROM `menu_permission` 
        LEFT JOIN menu_name 
            ON menu_permission.menu_name_id = menu_name.menu_name_id 
        WHERE menu_permission.previlage_id = 1
            AND menu_permission.value = 'Yes' AND menu_name IS NOT NULL"""
cursor.execute(sql)
print("Result for previlage 1:", cursor.fetchall())
