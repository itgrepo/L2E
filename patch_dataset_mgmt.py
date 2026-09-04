import re

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace status badge with a toggle switch
    status_td = """                <td>
                  <label class="switch">
                    <input type="checkbox" :checked="d.status === 'Active'" @change="handleToggleStatus(d)">
                    <span class="slider round"></span>
                  </label>
                  <span style="font-size: 0.75rem; margin-left: 8px; font-weight: 600;" :style="{ color: d.status === 'Active' ? '#10b981' : '#94a3b8' }">
                    {{ d.status === 'Active' ? 'Active' : 'Inactive' }}
                  </span>
                </td>"""
    
    # We need to find the status column block
    content = re.sub(
        r'<td>\s*<span class="status-badge"[^>]*>\s*\{\{\s*d\.status\s*\}\}\s*</span>\s*</td>',
        status_td,
        content
    )

    # 2. Remove the toggle button from actions
    content = re.sub(
        r'<button class="action-btn toggle" @click="handleToggleStatus\(d\)"[^>]*>\s*<svg.*?</svg>\s*</button>',
        '',
        content,
        flags=re.DOTALL
    )

    # 3. Add switch CSS if it doesn't exist
    if '.switch {' not in content:
        switch_css = """
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  vertical-align: middle;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  transition: .4s;
}
.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}
input:checked + .slider {
  background-color: #10b981;
}
input:checked + .slider:before {
  transform: translateX(20px);
}
.slider.round {
  border-radius: 24px;
}
.slider.round:before {
  border-radius: 50%;
}
"""
        content = content.replace('</style>', switch_css + '</style>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

patch_file('frontend/src/views/DatasetManagementView.vue')
patch_file('frontend/src/views/GroupDatasetManagementView.vue')
