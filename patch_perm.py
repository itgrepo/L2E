import re
filepath = "frontend/src/views/PermissionManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the <h4> tag to show translated name and tooltip
old_h4 = "<h4>{{ perm.menu_name }}</h4>"
new_h4 = """<h4 :title="getMenuTooltip(perm.menu_name)" style="display: flex; align-items: center; gap: 6px; cursor: help;">
                    {{ getMenuName(perm.menu_name) }} 
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#94a3b8">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </h4>"""
content = content.replace(old_h4, new_h4)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
