import os
import re

def replace_in_file(filepath, old_str, new_str):
    with open(filepath, 'r') as f:
        content = f.read()
    if old_str in content:
        content = content.replace(old_str, new_str)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")

def replace_regex_in_file(filepath, pattern, replacement):
    with open(filepath, 'r') as f:
        content = f.read()
    new_content, count = re.subn(pattern, replacement, content)
    if count > 0:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated {filepath} (regex)")

base_dir = "backendold/Astro_backend/app"

# groupMgmt.py
replace_in_file(f"{base_dir}/Management/groupMgmt.py", "previlage_id == 1", "previlage_id == 4")
replace_in_file(f"{base_dir}/Management/groupMgmt.py", "previlage_id != 1", "previlage_id != 4")

# rolesMgmt.py
replace_in_file(f"{base_dir}/Management/rolesMgmt.py", "previlage_id = 3", "previlage_id = 2")

# bigdataservice.py
replace_in_file(f"{base_dir}/ServiceConfig/bigdataservice.py", "user_role = '3'", "user_role = '2'")
replace_in_file(f"{base_dir}/ServiceConfig/bigdataservice.py", "str(user_role) == '3'", "str(user_role) not in ['3', '4']") # Since 3, 4 are admins

# __init__.py
replace_regex_in_file(f"{base_dir}/ServiceConfig/__init__.py", r"str\(result_check_Permission\[0\]\['previlage_id'\]\) not in \['3'\]", r"str(result_check_Permission[0]['previlage_id']) in ['3', '4']")
replace_in_file(f"{base_dir}/ServiceConfig/__init__.py", "previlage_id = 1 is Admin", "previlage_id = 4 is Admin")

print("Done updates")
