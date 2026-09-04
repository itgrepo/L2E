import re

def replace_in_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

# AboutView.vue
replace_in_file('frontend/src/views/AboutView.vue', [
    ('เกี่ยวกับ DataX Portal', 'เกี่ยวกับ Data Portal'),
    ('DataX Portal (แพลตฟอร์ม', 'Data Portal (แพลตฟอร์ม'),
    ('<div class="logo-placeholder">DataX</div>', '<div class="logo-placeholder">Data Portal</div>')
])

# DatasetConfigView.vue
replace_in_file('frontend/src/views/DatasetConfigView.vue', [
    ('จัดการและตั้งค่าชุดข้อมูลในระบบ DataX Portal', 'จัดการและตั้งค่าชุดข้อมูลในระบบ Data Portal')
])

# MonitorView.vue
replace_in_file('frontend/src/views/MonitorView.vue', [
    ('ตรวจสอบสถานะการทำงานและ Log ของระบบ DataX', 'ตรวจสอบสถานะการทำงานและ Log ของระบบ Data Portal'),
    ('DataX Quick Action', 'Data Portal Quick Action'),
    ('DataX API Service', 'Data Portal API Service'),
    ('DataX Portal Web', 'Data Portal Web')
])

# RegisterView.vue
replace_in_file('frontend/src/views/RegisterView.vue', [
    ('<h1>DataX Portal</h1>', '<h1>Data Portal</h1>'),
    ('กรอกข้อมูลเพื่อเริ่มต้นใช้งาน DataX Portal', 'กรอกข้อมูลเพื่อเริ่มต้นใช้งาน Data Portal')
])

