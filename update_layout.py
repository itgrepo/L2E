import json

file_path = '/app/uploads/page_layout.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for section in data:
    if section.get('type') == 'StatsBanner':
        section['visible'] = False

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
