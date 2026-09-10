filepath = '/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/login.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Replace first occurrence
old_code_1 = r"if int\(result2\[0\]\['login_respond'\]\) - int\(result2\[0\]\['create_date'\]\) >= result_time_activity\[0\]\['duration'\]:  # 7776000"
new_code_1 = r"if int(result2[0]['login_respond']) - int(result2[0]['create_date']) >= result_time_activity[0]['duration'] * 86400:  # 7776000 (90 days)"
content = re.sub(old_code_1, new_code_1, content)

# Replace second occurrence
old_code_2 = r"if int\(result2\[0\]\['login_respond'\]\) - int\(result2\[0\]\['create_date'\]\) >= result_time_activity\[0\]\['duration'\]:"
new_code_2 = r"if int(result2[0]['login_respond']) - int(result2[0]['create_date']) >= result_time_activity[0]['duration'] * 86400:"
content = re.sub(old_code_2, new_code_2, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("login duration patched!")
