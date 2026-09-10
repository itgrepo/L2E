filepath = '/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

import re
old_code = r"""            # If user is admin \(previlage_id != 3\), show all active services
            if user_data.get\('previlage_id'\) and str\(user_data.get\('previlage_id'\)\) in \['3', '4'\]:
                user_id = 'ADMIN' 

        conn = mysql.connect\(\)
        cursor = conn.cursor\(\)
        
        current_app.logger.info\(f"DEBUG retrieveService: user_data=\{user_data\}, user_id=\{user_id\}"\)
        
        if user_id == 'ADMIN':"""

new_code = """            # If user is admin, show all active services
            if user_id and not user_data.get('previlage_id'):
                try:
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.execute("SELECT previlage_id FROM user WHERE user_id=%s", (user_id,))
                    row = cursor.fetchone()
                    if row:
                        user_data['previlage_id'] = row[0]
                    cursor.close()
                    conn.close()
                except Exception as e:
                    pass
                    
            if user_data.get('previlage_id') and str(user_data.get('previlage_id')) in ['3', '4']:
                user_id = 'ADMIN' 

        conn = mysql.connect()
        cursor = conn.cursor()
        
        if user_id == 'ADMIN':"""

content = re.sub(old_code, new_code, content)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("retrieveService admin check patched!")
