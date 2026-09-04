# coding=utf-8
import codecs

with codecs.open('src/views/DatasetConfigView.vue', 'r', 'utf-8') as f:
    content = f.read()

old_select = """<select v-model="formData.status" class="form-select-custom" required>
                      <option value="Inactive">เลือกสถานะการใช้งาน(Inactive = ไม่แสดงผล / Active = แสดงผล )</option>
                      <option value="Active">Active</option>
                      <option value="Inactive">Inactive</option>
                    </select>"""

new_toggle = """<div class="toggle-status-wrapper" style="display: flex; align-items: center; height: 42px;">
                      <label class="switch">
                        <input type="checkbox" :checked="formData.status === 'Active'" @change="formData.status = $event.target.checked ? 'Active' : 'Inactive'">
                        <span class="slider round"></span>
                      </label>
                      <span style="margin-left:12px; font-weight:600;" :style="{ color: formData.status === 'Active' ? '#10b981' : '#64748b' }">
                        {{ formData.status === 'Active' ? 'เปิดใช้งาน (Active)' : 'ปิดใช้งาน (Inactive)' }}
                      </span>
                    </div>"""

content = content.replace(old_select, new_toggle)

css_to_add = """
/* Toggle Switch */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 28px;
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
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}
input:checked + .slider {
  background-color: #10b981;
}
input:checked + .slider:before {
  transform: translateX(22px);
}
.slider.round {
  border-radius: 34px;
}
.slider.round:before {
  border-radius: 50%;
}
"""

if '.switch {' not in content:
    content = content.replace('</style>', css_to_add + '\n</style>')

with codecs.open('src/views/DatasetConfigView.vue', 'w', 'utf-8') as f:
    f.write(content)
