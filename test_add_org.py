import sys
import os
import pymysql

conn = pymysql.connect(
    host='110.78.210.129',
    user='astro',
    password='password123',
    database='datax_db_3003',
    port=3306,
    cursorclass=pymysql.cursors.DictCursor
)

try:
    cursor = conn.cursor()
    org_name = 'Test Script Org'
    org_description = 'desc'
    contact_name = 'c'
    contact_email = 'e@e.com'
    contact_phone = '123'
    is_active = 1
    role_ids = [1, 2]

    unique_roles = list(set(role_ids))
    if unique_roles:
        format_strings = ','.join(['%s'] * len(unique_roles))
        cursor.execute(f"SELECT id FROM organization_role_master WHERE id IN ({format_strings})", tuple(unique_roles))
        valid_roles = [row['id'] for row in cursor.fetchall()]
        print(f"valid_roles: {valid_roles}")
        if len(valid_roles) != len(unique_roles):
            raise ValueError("One or more role_ids are invalid")

    sql = "INSERT INTO organization (org_name, org_description, contact_name, contact_email, contact_phone, is_active) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (org_name, org_description, contact_name, contact_email, contact_phone, is_active))
    org_id = cursor.lastrowid
    print(f"org_id: {org_id}")

    for role_id in unique_roles:
        cursor.execute("INSERT INTO organization_role_mapping (organization_id, role_id) VALUES (%s, %s)", (org_id, role_id))
        
    conn.commit()
    print("Success")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
