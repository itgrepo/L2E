filepath = "/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's ensure editService syncs group access too!
old_code = """                    sql_update = f"UPDATE service SET {', '.join(fields)} WHERE service_id = %s"
                    values.append(service_id)
                    
                    cursor.execute(sql_update, tuple(values))
                    conn.commit()"""

new_code = """                    sql_update = f"UPDATE service SET {', '.join(fields)} WHERE service_id = %s"
                    values.append(service_id)
                    
                    cursor.execute(sql_update, tuple(values))
                    
                    if l2e_group_id_raw: # if group was updated
                        if l2e_group_id:
                            cursor.execute("INSERT INTO service_group_access (service_id, group_id, allow_dictionary, allow_dashboard, allow_api) VALUES (%s, %s, 1, 1, 1) ON DUPLICATE KEY UPDATE allow_dictionary=1, allow_dashboard=1, allow_api=1", (service_id, l2e_group_id))
                        else:
                            cursor.execute("DELETE FROM service_group_access WHERE service_id = %s", (service_id,))
                            
                    conn.commit()"""

if "if l2e_group_id_raw:" not in content:
    content = content.replace(old_code, new_code)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Group sync in PUT added.")
