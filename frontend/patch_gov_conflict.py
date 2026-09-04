# coding=utf-8
import codecs
import re

with codecs.open('src/views/DatasetConfigView.vue', 'r', 'utf-8') as f:
    content = f.read()

computed_code = """
const showGovConflict = computed(() => {
  if (!formData.value.access_type || !formData.value.gov_category) return false;
  const access = formData.value.access_type.toLowerCase();
  const gov = formData.value.gov_category;
  return (access === 'restricted' || access === 'internal' || access === 'pii') && (gov.includes('สาธารณะ') || gov.includes('Public'));
});
"""

if 'showGovConflict' not in content:
    content = content.replace("const submitForm = async () => {", computed_code + "\nconst submitForm = async () => {")

alert_html = """
                <div v-if="showGovConflict" style="margin-bottom: 20px; padding: 12px 16px; background: #fff3cd; border-left: 4px solid #ffc107; color: #856404; border-radius: 4px; font-size: 0.9rem;">
                  <strong>ข้อควรระวัง (Data Governance Conflict):</strong> การตั้งค่าสิทธิ์เข้าถึงเป็นข้อมูลปิด (Private/Restricted) ขัดแย้งกับการระบุธรรมาภิบาลข้อมูลให้เป็น "ข้อมูลสาธารณะ" โปรดตรวจสอบให้แน่ใจก่อนทำการบันทึก
                </div>
                <div class="form-actions">
"""

content = content.replace('<div class="form-actions">', alert_html, 1)

with codecs.open('src/views/DatasetConfigView.vue', 'w', 'utf-8') as f:
    f.write(content)
