# coding=utf-8
import codecs

with codecs.open('/Users/natthawutjantakul/intelligist_dataX/bigdataservice_broken.py', 'r', 'utf-8') as f:
    content = f.read()

bad_block = """def fix_chinese_to_thai(text):
    if not isinstance(text, str): return text
    try:
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
    return data"""

# Clean up all occurrences of bad_block
content = content.replace(bad_block, "")

# Ensure we don't have stray empty lines from the replacement
# Now insert it EXACTLY ONCE at the top-level import json
content = content.replace("import json", "import json\n\n" + bad_block, 1)

with codecs.open('/Users/natthawutjantakul/intelligist_dataX/bigdataservice_fixed.py', 'w', 'utf-8') as f:
    f.write(content)

print("Fix applied successfully!")
