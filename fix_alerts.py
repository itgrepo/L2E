import re

with open('frontend/src/views/DatasetConfigView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove inline alerts
content = re.sub(r'<div v-if="successMessage" class="alert alert-success">\{\{\s*successMessage\s*\}\}</div>\n*', '', content)
content = re.sub(r'<div v-if="errorMessage" class="alert alert-danger">\{\{\s*errorMessage\s*\}\}</div>\n*', '', content)

# Add modal before </main>
modal_html = """
      <!-- Notification Modal -->
      <div v-if="successMessage || errorMessage" class="modal-overlay" style="z-index: 10000; display: flex; align-items: center; justify-content: center; background-color: rgba(0,0,0,0.5);">
        <div class="modal" style="max-width: 400px; text-align: center; border-radius: 12px; overflow: hidden; background: white; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
          <div style="padding: 32px 24px;">
            <!-- Success Icon -->
            <div v-if="successMessage" style="width: 64px; height: 64px; border-radius: 50%; background: #d4edda; color: #28a745; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 16px;">&#10003;</div>
            <!-- Error Icon -->
            <div v-if="errorMessage" style="width: 64px; height: 64px; border-radius: 50%; background: #f8d7da; color: #dc3545; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 16px;">&#10005;</div>
            
            <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 8px; color: #333;">
              {{ successMessage ? 'สำเร็จ' : 'ข้อผิดพลาด' }}
            </h3>
            <p style="color: #666; margin-bottom: 24px; font-size: 16px; line-height: 1.5;">
              {{ successMessage || errorMessage }}
            </p>
            <button type="button" @click="successMessage = ''; errorMessage = ''" style="background-color: var(--primary); color: white; border: none; border-radius: 8px; padding: 10px 32px; font-size: 16px; font-weight: 500; cursor: pointer; transition: background 0.2s;">
              ตกลง
            </button>
          </div>
        </div>
      </div>
"""

content = content.replace("    </main>", modal_html + "    </main>")

with open('frontend/src/views/DatasetConfigView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

