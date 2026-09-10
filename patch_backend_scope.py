import re

path = '/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the scope enforcement logic in /dataapi/api/v1/<dataset_id>
old_scope_logic = """        # 3. Handle Scopes (Row-Level Security)
        scope_where_clause = " 1=1 "
        scope_params = []
        if api_type == 'scope':
            cursor.execute("SELECT scope_json FROM api_scopes WHERE credential_id = %s", (credential_id,))
            scope_row = cursor.fetchone()
            if scope_row and scope_row[0]:"""

new_scope_logic = """        # 3. Handle Scopes (Row-Level Security) (DECOUPLED FROM api_type)
        scope_where_clause = " 1=1 "
        scope_params = []
        if True: # Always check for credential scopes regardless of dataset api_type
            cursor.execute("SELECT scope_json FROM api_scopes WHERE credential_id = %s", (credential_id,))
            scope_row = cursor.fetchone()
            if scope_row and scope_row[0]:"""

content = content.replace(old_scope_logic, new_scope_logic)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched successfully")
