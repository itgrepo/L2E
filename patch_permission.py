import re

filepath = "frontend/src/views/PermissionManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add translation functions
translation_funcs = """
const menuTranslations = {
  'Dashboard': { name: 'หน้าหลัก (Dashboard)', tooltip: 'ดูภาพรวมและสถิติการใช้งานของระบบ' },
  'Catalog': { name: 'บัญชีข้อมูล (Data Catalog)', tooltip: 'ค้นหาและดูรายละเอียดของชุดข้อมูลทั้งหมดในระบบ' },
  'Data Catalog': { name: 'บัญชีข้อมูล (Data Catalog)', tooltip: 'ค้นหาและดูรายละเอียดของชุดข้อมูลทั้งหมดในระบบ' },
  'API Management': { name: 'จัดการ API (API Management)', tooltip: 'สร้างและจัดการการเชื่อมต่อ API สำหรับระบบภายนอก' },
  'Dataset Approval': { name: 'อนุมัติคำขอชุดข้อมูล', tooltip: 'พิจารณาและอนุมัติคำขอเข้าถึงชุดข้อมูลที่ถูกจำกัดสิทธิ์' },
  'Permission Management': { name: 'จัดการสิทธิ์ (Permission Management)', tooltip: 'กำหนดสิทธิ์การเข้าถึงเมนูต่างๆ ของแต่ละบทบาทผู้ใช้' },
  'User Management': { name: 'จัดการผู้ใช้งาน', tooltip: 'เพิ่ม ลบ แก้ไข และกำหนดหน่วยงานของผู้ใช้งานในระบบ' },
  'Settings': { name: 'ตั้งค่าระบบ', tooltip: 'ตั้งค่าหมวดหมู่และหน่วยงานในระบบ' },
  'Group User Management': { name: 'จัดการกลุ่มผู้ใช้งาน', tooltip: 'จัดการผู้ใช้งานภายในกลุ่มของหน่วยงาน' },
  'Dataset Management': { name: 'บัญชีชุดข้อมูลหน่วยงาน', tooltip: 'จัดการ แก้ไข และเพิ่มชุดข้อมูลของหน่วยงานตนเอง' },
  'Group Dataset Management': { name: 'จัดการกลุ่มชุดข้อมูล', tooltip: 'จัดการชุดข้อมูลที่แชร์ภายในกลุ่ม' },
  'Analytics': { name: 'วิเคราะห์ข้อมูล (Analytics)', tooltip: 'ดูสรุปข้อมูลเชิงวิเคราะห์' },
  'API Monitor': { name: 'ตรวจสอบ API (API Monitor)', tooltip: 'ตรวจสอบสถานะและการทำงานของ API' }
};

const getMenuName = (name) => {
  return menuTranslations[name] ? menuTranslations[name].name : name;
};

const getMenuTooltip = (name) => {
  return menuTranslations[name] ? menuTranslations[name].tooltip : 'เปิด/ปิด สิทธิ์การใช้งานเมนูนี้';
};
"""

content = content.replace(
    'const togglePermission = async (perm) => {',
    translation_funcs + '\nconst togglePermission = async (perm) => {'
)

# Update template
content = content.replace(
    '<span class="feature-name">{{ perm.menu_name }}</span>',
    '<span class="feature-name" :title="getMenuTooltip(perm.menu_name)">{{ getMenuName(perm.menu_name) }}</span>'
)

# Also let's wrap it in an info icon? "เพิ่ม Tooltip คำอธิบายของแต่ละส่วนให้ชัด"
content = content.replace(
    '<span class="feature-name" :title="getMenuTooltip(perm.menu_name)">{{ getMenuName(perm.menu_name) }}</span>',
    '<span class="feature-name" :title="getMenuTooltip(perm.menu_name)" style="display: flex; align-items: center; gap: 6px;">{{ getMenuName(perm.menu_name) }} <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="#94a3b8"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></span>'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched PermissionManagementView")
