import re

def replace_in_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

replace_in_file('frontend/src/components/AppFooter.vue', [
    ('support@datax.go.th', 'support@dataportal.go.th')
])

replace_in_file('frontend/src/views/RegisterView.vue', [
    ('somchai_datax', 'somchai_dataportal')
])

