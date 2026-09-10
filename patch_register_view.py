filepath = "frontend/src/views/RegisterView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_html = """          <div class="success-steps">
            <div class="flow-step">
              <div class="flow-number done">✓</div>
              <span>สมัครสมาชิก</span>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step current">
              <div class="flow-number">2</div>
              <span>ยืนยันอีเมล</span>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">
              <div class="flow-number">3</div>
              <span>ใช้งานได้</span>
            </div>
          </div>

          <router-link to="/login" class="back-to-login">← กลับไปหน้าเข้าสู่ระบบ</router-link>
        </div>"""

new_html = """          <div class="success-steps">
            <div class="flow-step">
              <div class="flow-number done">✓</div>
              <span>สมัครสมาชิก</span>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step current">
              <div class="flow-number">2</div>
              <span>ยืนยันอีเมล</span>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">
              <div class="flow-number">3</div>
              <span>ใช้งานได้</span>
            </div>
          </div>
          
          <div v-if="successData && successData.email_sent === false" style="margin: 20px 0; padding: 16px; background: #fff3cd; border-radius: 8px; border: 1px solid #ffeeba;">
            <p style="color: #856404; font-size: 0.9rem; margin-bottom: 12px; font-weight: bold;">
              ⚠️ ระบบไม่สามารถส่งอีเมลยืนยันได้ (เซิร์ฟเวอร์อีเมลไม่ตอบสนอง)
            </p>
            <p style="color: #856404; font-size: 0.85rem; margin-bottom: 16px;">
              คุณสามารถกดปุ่มด้านล่างเพื่อทำการยืนยันอีเมลด้วยตนเอง (Bypass) สำหรับการทดสอบระบบ:
            </p>
            <router-link :to="`/verify/${successData.token}`" style="display: inline-block; padding: 8px 16px; background: #28a745; color: white; border-radius: 4px; text-decoration: none; font-weight: bold;">
              👉 คลิกเพื่อยืนยันอีเมล (จำลอง)
            </router-link>
          </div>

          <router-link to="/login" class="back-to-login">← กลับไปหน้าเข้าสู่ระบบ</router-link>
        </div>"""

content = content.replace(old_html, new_html)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("RegisterView.vue patched!")
