filepath = "/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """                    ))
                    conn.commit()
                    
                    # Notify All Users about the new dataset"""

new_code = """                    ))
                    service_id = cursor.lastrowid
                    user_id = getattr(request, 'current_user', {}).get('user_id')
                    
                    # 1. Grant access to creator
                    if user_id and service_id:
                        cursor.execute("INSERT INTO service_user_access (service_id, user_id, allow_dictionary, allow_dashboard, allow_api) VALUES (%s, %s, 1, 1, 1)", (service_id, user_id))
                    
                    # 2. Grant access to group if l2e_group_id provided
                    if l2e_group_id and service_id:
                        cursor.execute("INSERT INTO service_group_access (service_id, group_id, allow_dictionary, allow_dashboard, allow_api) VALUES (%s, %s, 1, 1, 1)", (service_id, l2e_group_id))
                        
                    conn.commit()
                    
                    # Notify All Users about the new dataset"""

content = content.replace(old_code, new_code)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("addService permissions patched!")
