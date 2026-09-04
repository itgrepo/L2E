# coding=utf-8
import codecs

with codecs.open('src/views/RegisterView.vue', 'r', 'utf-8') as f:
    content = f.read()

# Add required to input
old_input = '<input id="reg-org" v-model="organization" type="text" placeholder="ชื่อหน่วยงาน (ไม่บังคับ)" :disabled="isLoading">'
new_input = '<input id="reg-org" v-model="organization" type="text" placeholder="ชื่อหน่วยงาน / สังกัด *" required :disabled="isLoading">'
content = content.replace(old_input, new_input)

# Add label
old_label = '<label for="reg-org">หน่วยงาน/สังกัด</label>'
new_label = '<label for="reg-org">หน่วยงาน/สังกัด *</label>'
content = content.replace(old_label, new_label)

# Add validation in JS
old_val = "if (!agreeTerms.value) {"
new_val = """if (!organization.value.trim()) {
      errorMessage.value = 'กรุณาระบุหน่วยงานหรือสังกัด';
      return;
    }
    if (!agreeTerms.value) {"""
content = content.replace(old_val, new_val)

# Add password complexity validation
# Item 6: Password requirements
old_pw_val = """if (password.value !== confirmPassword.value) {
      errorMessage.value = 'รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน';
      return;
    }"""
new_pw_val = """if (password.value !== confirmPassword.value) {
      errorMessage.value = 'รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน';
      return;
    }
    const pwRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$/;
    if (!pwRegex.test(password.value)) {
      errorMessage.value = 'รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร, ประกอบด้วยตัวพิมพ์ใหญ่, ตัวพิมพ์เล็ก, ตัวเลข และอักขระพิเศษ (@$!%*?&)';
      return;
    }"""
content = content.replace(old_pw_val, new_pw_val)

with codecs.open('src/views/RegisterView.vue', 'w', 'utf-8') as f:
    f.write(content)
