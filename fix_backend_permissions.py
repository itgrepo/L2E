import re
import sys

filepath = "/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the SQL in retrieveService for internal group access
old_sql_1 = "WHEN s.access_type IN ('restricted', 'pii') AND %s IS NOT NULL AND EXISTS (SELECT 1 FROM service_group_access sga JOIN group_user_detail gud ON sga.group_id = gud.group_id WHERE sga.service_id = s.service_id AND gud.user_id = %s) THEN 1"
new_sql_1 = "WHEN s.access_type IN ('internal', 'restricted', 'pii') AND %s IS NOT NULL AND EXISTS (SELECT 1 FROM service_group_access sga JOIN group_user_detail gud ON sga.group_id = gud.group_id WHERE sga.service_id = s.service_id AND gud.user_id = %s) THEN 1"

if old_sql_1 in content:
    content = content.replace(old_sql_1, new_sql_1)
    print("Patched retrieveService SQL successfully.")
else:
    print("Could not find retrieveService SQL to patch.")

# 2. Fix addService to sync service_group_access
# We need to find where dataset is inserted or updated.
# In `addService`, we have an INSERT block and an UPDATE block.
# Let's use a regex to find the end of the INSERT execution and UPDATE execution.
# Or better, let's just find the exact lines to inject the sync logic.

update_sync_block = """                    cursor.execute("UPDATE service SET " + ", ".join(fields) + " WHERE service_id = %s", values)
                    
                    # SYNC GROUP ACCESS
                    if l2e_group_id is not None:
                        cursor.execute("DELETE FROM service_group_access WHERE service_id = %s", (service_id,))
                        cursor.execute("INSERT INTO service_group_access (service_id, group_id) VALUES (%s, %s)", (service_id, l2e_group_id))
"""
if 'cursor.execute("UPDATE service SET " + ", ".join(fields) + " WHERE service_id = %s", values)' in content:
    content = content.replace(
        'cursor.execute("UPDATE service SET " + ", ".join(fields) + " WHERE service_id = %s", values)', 
        update_sync_block
    )
    print("Patched addService (UPDATE) successfully.")

insert_sync_block = """                    cursor.execute(sql_insert, values)
                    new_service_id = cursor.lastrowid
                    
                    # SYNC GROUP ACCESS
                    if l2e_group_id is not None:
                        cursor.execute("INSERT INTO service_group_access (service_id, group_id) VALUES (%s, %s)", (new_service_id, l2e_group_id))
"""
if 'cursor.execute(sql_insert, values)\n                    new_service_id = cursor.lastrowid' in content:
    content = content.replace(
        'cursor.execute(sql_insert, values)\n                    new_service_id = cursor.lastrowid',
        insert_sync_block
    )
    print("Patched addService (INSERT) successfully.")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
