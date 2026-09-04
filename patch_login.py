import re

filepath = "frontend/src/views/LoginView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace locked-alert content
locked_alert_html = """<div v-if="errorMessage && errorMessage.includes('ถูกระงับการใช้งานชั่วคราว')" class="locked-alert" style="background-color: #fef2f2; color: #991b1b; border: 2px solid #f87171; padding: 16px; border-radius: 8px; margin-bottom: 24px; font-weight: 600; text-align: center; box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.1);">
          {{ errorMessage }}
          <div style="margin-top: 12px;">
            <router-link to="/contact" style="display: inline-block; padding: 8px 16px; background-color: #ef4444; color: white; border-radius: 6px; text-decoration: none; font-size: 0.9rem;">
              ติดต่อผู้ดูแลระบบ (Contact Admin)
            </router-link>
          </div>
        </div>"""

content = re.sub(
    r'<div v-if="errorMessage && errorMessage.includes\(\'ถูกระงับการใช้งานชั่วคราว\'\)" class="locked-alert"[^>]*>\s*\{\{\s*errorMessage\s*\}\}\s*</div>',
    locked_alert_html,
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched LoginView")
