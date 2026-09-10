import re

filepath = "/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix SQL
content = re.sub(
    r"WHEN s\.access_type IN \('restricted', 'pii'\) AND %s IS NOT NULL AND EXISTS \(",
    r"WHEN s.access_type IN ('internal', 'restricted', 'pii') AND %s IS NOT NULL AND EXISTS (",
    content
)

# 2. Fix UPDATE
update_search = r'cursor\.execute\("UPDATE service SET " \+ ", "\.join\(fields\) \+ " WHERE service_id = %s", values\)'
update_replace = r'''cursor.execute("UPDATE service SET " + ", ".join(fields) + " WHERE service_id = %s", values)
                    
                    if l2e_group_id is not None:
                        cursor.execute("DELETE FROM service_group_access WHERE service_id = %s", (service_id,))
                        cursor.execute("INSERT INTO service_group_access (service_id, group_id) VALUES (%s, %s)", (service_id, l2e_group_id))'''

content = re.sub(update_search, update_replace, content)

# 3. Fix INSERT
insert_search = r'cursor\.execute\(sql_insert, values\)\s+new_service_id = cursor\.lastrowid'
insert_replace = r'''cursor.execute(sql_insert, values)
                    new_service_id = cursor.lastrowid
                    
                    if l2e_group_id is not None:
                        cursor.execute("INSERT INTO service_group_access (service_id, group_id) VALUES (%s, %s)", (new_service_id, l2e_group_id))'''

content = re.sub(insert_search, insert_replace, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Regex patch applied")
