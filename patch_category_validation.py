import re

filepath = "backendold/Astro_backend/app/ServiceConfig/category_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

validation_function = """import json
import re

def is_valid_category_name(name):
    if not name or len(str(name)) > 255:
        return False
    # Deny characters commonly used in injection attacks (XSS, SQLi, SSTI)
    forbidden_chars = r"['\"<>{};=*%\\]"
    if re.search(forbidden_chars, str(name)):
        return False
    return True
"""

content = content.replace("import json\n", validation_function)

# Patch addCategory
target_add = """        name = dataInput.get('name')
        if not name:
            return jsonify({"status": "Category name is required"})"""
replace_add = """        name = dataInput.get('name')
        if not name:
            return jsonify({"status": "Category name is required"})
        
        if not is_valid_category_name(name):
            return jsonify({"status": "Invalid characters in category name. Symbols like ', \", <, >, {, } are not allowed."})"""
content = content.replace(target_add, replace_add)

# Patch updateCategory
target_update = """        cat_id = dataInput.get('id')
        name = dataInput.get('name')

        if not cat_id or not name:
            return jsonify({"status": "Category ID and name are required"})"""
replace_update = """        cat_id = dataInput.get('id')
        name = dataInput.get('name')

        if not cat_id or not name:
            return jsonify({"status": "Category ID and name are required"})
            
        if not is_valid_category_name(name):
            return jsonify({"status": "Invalid characters in category name. Symbols like ', \", <, >, {, } are not allowed."})"""
content = content.replace(target_update, replace_update)

# Patch addSubCategory
target_addsub = """        category_name = dataInput.get('category_name')
        sub_category_name = dataInput.get('sub_category_name')

        if not category_name or not sub_category_name:
            return jsonify({"status": "Category and Sub-Category names are required"})"""
replace_addsub = """        category_name = dataInput.get('category_name')
        sub_category_name = dataInput.get('sub_category_name')

        if not category_name or not sub_category_name:
            return jsonify({"status": "Category and Sub-Category names are required"})
            
        if not is_valid_category_name(sub_category_name):
            return jsonify({"status": "Invalid characters in sub-category name. Symbols like ', \", <, >, {, } are not allowed."})"""
content = content.replace(target_addsub, replace_addsub)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("category_service.py patched with input validation.")
