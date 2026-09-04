# coding=utf-8
import codecs

with codecs.open('/tmp/bigdataservice.py', 'r', 'utf-8') as f:
    content = f.read()

fix_func = """def fix_chinese_to_thai(text):
    if not isinstance(text, str): return text
    try:
        # Check if contains Chinese characters commonly resulting from GBK misinterpretation of TIS-620
        # Instead of checking, we can just try, but it might fail on real Chinese.
        # However, for Thai MOOC data, we expect Thai.
        return text.encode('gbk').decode('tis-620')
    except:
        pass
    
    try:
        return text.encode('latin1').decode('tis-620')
    except:
        return text

def recursively_fix_thai(data):
    if isinstance(data, list):
        return [recursively_fix_thai(item) for item in data]
    elif isinstance(data, dict):
        return {k: recursively_fix_thai(v) for k, v in data.items()}
    elif isinstance(data, str):
        return fix_chinese_to_thai(data)
    return data
"""

if 'def recursively_fix_thai' not in content:
    content = content.replace("import oracledb\n", "import oracledb\n\n" + fix_func)

# Apply in exportData
old_export = "results = [dict(zip(columns, row)) for row in rows_data]"
new_export = "results = [dict(zip(columns, row)) for row in rows_data]\n            results = recursively_fix_thai(results)"
content = content.replace(old_export, new_export)

# Apply in get_dataset_file_api
old_api = "response_data = [dict(zip(columns, row)) for row in rows_data]"
new_api = "response_data = [dict(zip(columns, row)) for row in rows_data]\n            response_data = recursively_fix_thai(response_data)"
content = content.replace(old_api, new_api)

with codecs.open('/tmp/bigdataservice.py', 'w', 'utf-8') as f:
    f.write(content)
