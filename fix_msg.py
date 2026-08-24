filepath = "backendold/Astro_backend/app/ServiceConfig/category_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

import re
# Replace problematic json response string
content = re.sub(r'return jsonify\(\{"status": "Invalid characters.*?"\}\)', 'return jsonify({"status": "Invalid characters in name. Special symbols are not allowed."})', content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
