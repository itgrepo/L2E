import re

with open('frontend/src/views/DatasetDetailView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add file state to requestForm
content = re.sub(
    r'const requestForm = ref\(\{\n\s*fields: \[\],\n\s*reason: \'\'\n\s*\}\);',
    r"const requestForm = ref({\n  fields: [],\n  reason: '',\n  mouFile: null,\n  mouFileName: ''\n});",
    content
)

# 2. Add handle file change function
handle_file_fn = """
const handleMouFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    requestForm.value.mouFileName = file.name;
    const reader = new FileReader();
    reader.onload = (e) => {
      requestForm.value.mouFile = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    requestForm.value.mouFile = null;
    requestForm.value.mouFileName = '';
  }
};
"""

content = content.replace("const submitPermissionRequest = async () => {", handle_file_fn + "\nconst submitPermissionRequest = async () => {")

# 3. Add to API call payload
content = re.sub(
    r'reason: requestForm\.value\.reason',
    r'reason: requestForm.value.reason,\n      mou_file: requestForm.value.mouFile,\n      mou_filename: requestForm.value.mouFileName',
    content
)

# 4. Clear fields on success
content = re.sub(
    r'requestForm\.value\.reason = \'\';',
    r"requestForm.value.reason = '';\n      requestForm.value.mouFile = null;\n      requestForm.value.mouFileName = '';",
    content
)

# 5. Add UI file input
file_ui = """                      <!-- MOU File Upload -->
                      <div class="form-group mb-4" style="margin-bottom: 12px;">
                        <label class="font-semibold block mb-1 text-slate-700" style="font-size:0.85rem; display:block; margin-bottom: 4px; font-weight:600;">เอกสารประกอบคำขอ (MOU / Request Letter)</label>
                        <p style="font-size:0.75rem; color:#64748b; margin-bottom:4px;">กรุณาอัปโหลดบันทึกข้อความนำส่ง, หนังสือข้อตกลง MOU หรือเอกสารสิทธิ์การใช้ข้อมูล (PDF, JPG, PNG)</p>
                        <input type="file" @change="handleMouFileChange" accept=".pdf,image/*" style="width:100%;border:1px solid #e2e8f0;border-radius:6px;padding:6px;font-size:0.8rem;background:#f8fafc;cursor:pointer;">
                      </div>
"""

content = content.replace(
    """<div v-if="reqError" style="color:#e11d48;font-size:0.75rem;margin-bottom:8px;text-align:left;">{{ reqError }}</div>""",
    file_ui + """\n                      <div v-if="reqError" style="color:#e11d48;font-size:0.75rem;margin-bottom:8px;text-align:left;">{{ reqError }}</div>"""
)

with open('frontend/src/views/DatasetDetailView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched DatasetDetailView.vue")
