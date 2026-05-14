import sys

file_path = "frontend/src/views/DatasetConfigView.vue"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add state variables inside script setup
target_1 = """const selectedFile = ref(null);
const uploadDatasetId = ref('');
const fileType = ref('dictionary');"""

replacement_1 = """const selectedFile = ref(null);
const uploadDatasetId = ref('');
const fileType = ref('dictionary');

const linkType = ref('api');
const linkDatasetId = ref('');
const linkUrl = ref('');

const handleLinkSubmit = async () => {
  if (!linkDatasetId.value || !linkUrl.value) {
    errorMessage.value = 'โปรดเลือกชุดข้อมูลและกรอก URL';
    return;
  }
  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    const userData = localStorage.getItem('user');
    const fd = new FormData();
    fd.append('user', btoa(userData));
    fd.append('service_id', linkDatasetId.value);
    
    // We only update the specific link field
    if (linkType.value === 'api') {
      fd.append('external_api_url', linkUrl.value);
    } else {
      fd.append('external_dashboard_url', linkUrl.value);
    }

    const response = await apiClient.put('/addService', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    if (response.data.status.includes('success')) {
      successMessage.value = 'บันทึกลิงก์สำเร็จ!';
      linkUrl.value = '';
      linkDatasetId.value = '';
    } else {
      errorMessage.value = response.data.status || 'เกิดข้อผิดพลาดในการบันทึก';
    }
  } catch (error) {
    console.error('Link update error:', error);
    errorMessage.value = 'ไม่สามารถบันทึกลิงก์ได้';
  } finally {
    isSubmitting.value = false;
  }
};"""

if target_1 in content:
    content = content.replace(target_1, replacement_1)
else:
    print("Could not find target_1 for state variables.")

# 2. Replace the HTML for the LINK TAB
target_2 = """          <!-- LINK TAB -->
          <div v-else-if="activeTab === 'link'" class="link-section">
            <h2 class="section-title">เพิ่มลิงก์ข้อมูล</h2>
            <div class="form-group" style="max-width: 600px;">
              <label>Link URL *</label>
              <input type="url" placeholder="https://example.com/api/v1/data">
            </div>
            <div class="form-actions">
              <button class="btn-save">บันทึกลิงก์</button>
            </div>
          </div>"""

replacement_2 = """          <!-- LINK TAB -->
          <div v-else-if="activeTab === 'link'" class="link-section" style="max-width: 900px; padding-top: 2rem;">
            <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

            <div class="flex items-center gap-6 mb-8 mt-2">
              <label class="flex items-center gap-2 cursor-pointer text-slate-500 font-medium">
                <div class="relative w-5 h-5 rounded-full border-2 border-slate-300 flex items-center justify-center transition-colors"
                     :class="{'border-blue-500 bg-blue-50': linkType === 'api'}">
                  <div v-if="linkType === 'api'" class="w-2.5 h-2.5 rounded-full bg-blue-500"></div>
                </div>
                <input type="radio" value="api" v-model="linkType" class="hidden">
                <span :class="linkType === 'api' ? 'text-slate-700' : ''">เพิ่มลิงก์ API</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer text-slate-500 font-medium">
                <div class="relative w-5 h-5 rounded-full border-2 border-slate-300 flex items-center justify-center transition-colors"
                     :class="{'border-blue-500 bg-blue-50': linkType === 'dashboard'}">
                  <div v-if="linkType === 'dashboard'" class="w-2.5 h-2.5 rounded-full bg-blue-500"></div>
                </div>
                <input type="radio" value="dashboard" v-model="linkType" class="hidden">
                <span :class="linkType === 'dashboard' ? 'text-slate-700' : ''">เพิ่มลิงก์ DashBoard</span>
              </label>
            </div>

            <div class="form-group mb-8">
              <label class="text-xs text-slate-500 font-bold tracking-wide uppercase">รหัสชุดข้อมูล</label>
              <select v-model="linkDatasetId" class="w-full bg-transparent border-0 border-b border-slate-400 focus:ring-0 focus:border-slate-800 text-slate-800 py-2 px-0 transition-colors" style="outline: none;">
                <option value="">รหัสชุดข้อมูล</option>
                <option v-for="ds in datasets" :key="ds.service_id" :value="ds.service_id">
                  {{ ds.dataset_id }} - {{ ds.service_name }}
                </option>
              </select>
            </div>

            <div class="form-group mb-12">
              <label class="text-xs text-slate-500 font-bold tracking-wide uppercase">{{ linkType === 'api' ? 'ลิงก์ API' : 'ลิงก์ DashBoard' }}</label>
              <input type="url" v-model="linkUrl" class="w-full bg-transparent border-0 border-b border-slate-400 focus:ring-0 focus:border-slate-800 text-slate-800 py-2 px-0 transition-colors" style="outline: none;" placeholder="https://example.com/api/v1/data">
            </div>

            <div class="flex justify-end">
              <button @click="handleLinkSubmit" class="flex items-center gap-2 px-6 py-2 rounded border border-emerald-500 text-emerald-600 bg-white hover:bg-emerald-50 font-medium transition-colors" :disabled="isSubmitting">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                </svg>
                บันทึก
              </button>
            </div>
          </div>"""

if target_2 in content:
    content = content.replace(target_2, replacement_2)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Link tab UI and Logic updated successfully.")
else:
    print("Could not find target_2 for HTML replacement.")
