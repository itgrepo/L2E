import sys

file_path = "frontend/src/views/ProfileView.vue"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add script setup logic
target_1 = """const isLoading = ref(false);
const message = ref({ text: '', type: '' });"""

replacement_1 = """const isLoading = ref(false);
const isGeneratingKey = ref(false);
const message = ref({ text: '', type: '' });

const copyApiKey = () => {
  if (user.value.apikey) {
    navigator.clipboard.writeText('?apikey=' + user.value.apikey);
    message.value = { text: 'คัดลอก API Key ลงคลิปบอร์ดสำเร็จ!', type: 'success' };
    setTimeout(() => { 
      if(message.value.text.includes('คลิปบอร์ด')) message.value = { text: '', type: '' }; 
    }, 3000);
  }
};

const generateApiKey = async () => {
  if (user.value.apikey && !confirm('การสร้าง Key ใหม่จะทำให้ Key เดิมหลุดการเชื่อมต่อ และใช้งานไม่ได้อีก คุณแน่ใจหรือไม่?')) {
    return;
  }
  
  isGeneratingKey.value = true;
  message.value = { text: '', type: '' };
  
  try {
    const payload = {
      user: { user_id: user.value.user_id }
    };
    
    // Use the postWithUser helper that encodes the payload
    const response = await postWithUser('/generateApiKey', payload.user);
    if (response.data.status === 'success') {
      message.value = { text: 'API Key ใหม่ถูกสร้างและบันทึกเรียบร้อย!', type: 'success' };
      const updatedUser = { ...user.value, ...response.data.data[0] };
      user.value = updatedUser;
      localStorage.setItem('user', JSON.stringify(updatedUser)); // Persist key locally
    } else {
      message.value = { text: response.data.message || 'ไม่สามารถสร้าง API Key ได้', type: 'error' };
    }
  } catch (error) {
    console.error('Error Generating Key:', error);
    message.value = { text: 'เกิดข้อผิดพลาดในการสร้างคีย์', type: 'error' };
  } finally {
    isGeneratingKey.value = false;
  }
};"""

# Add user.apikey initialization
target_1_b = """  usage_objective: '',
  other_object: '',
  role: 'User'
});"""

replacement_1_b = """  usage_objective: '',
  other_object: '',
  apikey: '',
  role: 'User'
});"""


# Add HTML structure
target_2 = """            <div class="form-group full">
              <label>Other Details</label>
              <input type="text" v-model="user.other_object">
            </div>
            
            <div class="form-actions">"""

replacement_2 = """            <div class="form-group full">
              <label>Other Details</label>
              <input type="text" v-model="user.other_object">
            </div>
            
            <div class="form-group full" style="margin-top: 24px; padding-top: 24px; border-top: 1px solid #e2e8f0;">
              <label class="flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-600" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 8a6 6 0 01-7.743 5.743L10 14l-1 1-1 1H6v2H2v-4l4.257-4.257A6 6 0 1118 8zm-6-4a1 1 0 100 2 2 2 0 012 2 1 1 0 102 0 4 4 0 00-4-4z" clip-rule="evenodd" />
                </svg>
                API Key (สำหรับเชื่อมต่อข้อมูล)
              </label>
              <div style="display: flex; align-items: center; gap: 12px; margin-top: 8px;">
                <input 
                  type="text" 
                  :value="user.apikey ? '?apikey=' + user.apikey : 'ระบบต้องการ API Key สำหรับเชื่อมต่อ'" 
                  disabled 
                  style="flex: 1; font-family: monospace; background-color: #f1f5f9; color: #334155;"
                >
                <button v-if="user.apikey" type="button" @click="copyApiKey" class="btn-outline flex items-center gap-2" style="white-space: nowrap; height: 100%;">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  คัดลอก
                </button>
                <button type="button" @click="generateApiKey" class="btn-primary" :disabled="isGeneratingKey" style="white-space: nowrap; height: 100%;">
                  {{ user.apikey ? 'สร้าง Key ใหม่ (Refresh)' : 'สร้าง API Key' }}
                </button>
              </div>
              <p style="font-size: 0.8rem; color: #64748b; margin-top: 10px;">
                * API Key ใช้เป็น Parameter ยืนยันตัวตนเวลาเรียก Endpoint (เช่น <code>?apikey=...</code>) โปรดเก็บรักษาให้ปลอดภัย
              </p>
            </div>
            
            <div class="form-actions">"""

if target_1 in content and target_2 in content:
    content = content.replace(target_1, replacement_1)
    content = content.replace(target_1_b, replacement_1_b)
    content = content.replace(target_2, replacement_2)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("ProfileView updated successfully.")
else:
    print("Warning: Target strings not found.")
