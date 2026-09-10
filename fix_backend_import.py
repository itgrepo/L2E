import re

filepath = "/home/l2e-prd-dataexchange/L2E/backendold/Astro_backend/app/ServiceConfig/bigdataservice.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken indentation
content = content.replace("    import json\nimport threading", "    import json")
content = content.replace("import json\nimport threading", "import json")

# Add import threading safely at the top
if "import threading" not in content:
    content = "import threading\n" + content

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
