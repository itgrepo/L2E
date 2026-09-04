# coding=utf-8
import codecs

with codecs.open('src/views/LoginView.vue', 'r', 'utf-8') as f:
    content = f.read()

# Update validation
old_val = """    if (result.status === 'locked' || (result.message && result.message.includes('ถูกระงับ'))) {
      errorMessage.value = 'บัญชีของคุณถูกระงับการใช้งานชั่วคราว กรุณาติดต่อผู้ดูแลระบบ';
    } else {"""
new_val = """    if (result.status === 'locked' || result.status === 'Your account is locked' || (result.status && result.status.includes('Your account is locked')) || (result.message && result.message.includes('ถูกระงับ'))) {
      errorMessage.value = '🚨 บัญชีของคุณถูกระงับการใช้งานชั่วคราวเนื่องจากกรอกรหัสผ่านผิดเกินจำนวนครั้งที่กำหนด กรุณาติดต่อผู้ดูแลระบบหรือทำการปลดล็อคผ่านอีเมล';
    } else {"""
content = content.replace(old_val, new_val)

# Update template for banner
old_html = """        <div v-if="errorMessage" class="error-alert">
          {{ errorMessage }}
        </div>"""
new_html = """        <div v-if="errorMessage && errorMessage.includes('ถูกระงับการใช้งานชั่วคราว')" class="locked-alert" style="background-color: #fef2f2; color: #991b1b; border: 2px solid #f87171; padding: 16px; border-radius: 8px; margin-bottom: 24px; font-weight: 600; text-align: center; box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.1);">
          {{ errorMessage }}
        </div>
        <div v-else-if="errorMessage" class="error-alert">
          {{ errorMessage }}
        </div>"""
content = content.replace(old_html, new_html)

with codecs.open('src/views/LoginView.vue', 'w', 'utf-8') as f:
    f.write(content)
