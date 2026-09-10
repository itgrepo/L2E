import re

file_path = '/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/Management/groupMgmt.py'
with open(file_path, 'r') as f:
    content = f.read()

# Replace SELECT * FROM menu_name with deduplicated query
old_sql = "sql = \"SELECT * FROM `menu_name` WHERE menu_name NOT IN ('User Management','Permission Management','Service Configuration')\""
new_sql = "sql = \"SELECT MIN(menu_name_id) as menu_name_id, menu_name FROM `menu_name` WHERE menu_name NOT IN ('User Management','Permission Management','Service Configuration') GROUP BY menu_name\""
content = content.replace(old_sql, new_sql)

with open(file_path, 'w') as f:
    f.write(content)
