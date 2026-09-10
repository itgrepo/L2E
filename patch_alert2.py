filepath = "frontend/src/views/DatasetManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_html = """      <!-- Alert Banner -->
      <transition name="fade">
        <div v-if="alertMessage.text" :class="['alert-banner', alertMessage.type]">
          {{ alertMessage.text }}
        </div>
      </transition>"""

new_html = """      <!-- Alert Banner -->
      <transition name="fade">
        <div v-if="alertMessage.text" :class="['alert-banner', alertMessage.type]">
          <div style="flex: 1;">{{ alertMessage.text }}</div>
          <button @click="alertMessage.text = ''" class="alert-close-btn" aria-label="Close alert">&times;</button>
        </div>
      </transition>"""

if old_html in content:
    content = content.replace(old_html, new_html)

old_css = """.alert-banner {
    padding: 14px 24px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.95rem;
    position: fixed;
    top: 30px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    min-width: 300px;
    text-align: center;
}"""

new_css = """.alert-banner {
    padding: 14px 24px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.95rem;
    position: fixed;
    top: 30px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999 !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    min-width: 300px;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}
.alert-close-btn {
    background: transparent;
    border: none;
    color: inherit;
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
    opacity: 0.6;
    padding: 0;
    margin: -4px -8px -4px 0;
    transition: opacity 0.2s;
}
.alert-close-btn:hover {
    opacity: 1;
}"""

if old_css in content:
    content = content.replace(old_css, new_css)
elif ".alert-banner {" in content:
    print("Warning: CSS might be different in DatasetManagementView")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Alert patched in DatasetManagementView")
