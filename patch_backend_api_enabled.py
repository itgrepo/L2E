path = '/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py'
import os
os.system(f"ssh -i key/ssh-key-2026-08-24.key -o StrictHostKeyChecking=no l2e-prd-dataexchange@134.185.175.106 'cat {path}' > temp_backend.py")

with open('temp_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_sql = '''sql = "SELECT service_name, api_endpoint, description, api_type, status FROM service WHERE dataset_id LIKE %s AND status = 'Active'"'''
new_sql = '''sql = "SELECT service_name, api_endpoint, description, api_type, status, api_enabled FROM service WHERE dataset_id LIKE %s AND status = 'Active'"'''
content = content.replace(old_sql, new_sql)

with open('temp_backend.py', 'w', encoding='utf-8') as f:
    f.write(content)

os.system(f"scp -i key/ssh-key-2026-08-24.key -o StrictHostKeyChecking=no temp_backend.py l2e-prd-dataexchange@134.185.175.106:{path}")
os.system("ssh -i key/ssh-key-2026-08-24.key -o StrictHostKeyChecking=no l2e-prd-dataexchange@134.185.175.106 'docker restart datax_backend'")
