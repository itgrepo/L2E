import sys

file_path = "frontend/src/views/CatalogView.vue"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target_script = """const errorMessage = ref('');

// Modal State"""
replacement_script = """const errorMessage = ref('');

const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));

const copyApiUrl = () => {
  const url = `${window.location.origin}/dataapi/api/v1/${selectedDataset.value?.dataset_id}?apikey=${user.value.apikey}`;
  navigator.clipboard.writeText(url);
  alert('คัดลอก URL เรียบร้อยแล้ว');
};

// Modal State"""

target_html = """            <!-- API Tab -->
            <div v-if="activeTab === 'api'" class="tab-content transition-fade">
              <div class="api-info">
                <div class="api-header">
                  <span class="method get">GET</span>
                  <code class="url">http://localhost:8000/api/v1/dataset/{{ selectedDataset?.dataset_id }}</code>
                </div>
                <div class="json-preview">
                  <div class="json-header">
                    <span>Example JSON Response</span>
                    <button class="btn-copy">คัดลอก</button>
                  </div>
                  <pre><code>{
  "status": "success",
  "data": {
    "dataset_id": "{{ selectedDataset?.dataset_id }}",
    "items": [
      {
        "id": 1,
        "name": "Item Name 1",
        "value": 100.50,
        "updated_at": "2024-03-30T00:00:00Z"
      },
      {
        "id": 2,
        "name": "Item Name 2",
        "value": 250.75,
        "updated_at": "2024-03-30T00:00:00Z"
      }
    ]
  }
}</code></pre>
                </div>
              </div>
            </div>"""

replacement_html = """            <!-- API Tab -->
            <div v-if="activeTab === 'api'" class="tab-content transition-fade">
              <div class="api-info border border-slate-200 rounded-xl overflow-hidden shadow-sm bg-white">
                <div class="api-header bg-slate-50 border-b border-slate-200 p-4 flex items-center justify-between">
                  <div class="flex items-center gap-3 w-full">
                    <span class="method get px-3 py-1 bg-emerald-100 text-emerald-700 font-bold rounded-md text-sm">GET</span>
                    <input 
                      type="text" 
                      readonly 
                      :value="user.apikey ? `${window.location.origin}/dataapi/api/v1/${selectedDataset?.dataset_id}?apikey=${user.apikey}` : 'ต้องมี API Key เพื่อดูลิงก์'" 
                      class="url flex-1 bg-white border border-slate-200 rounded px-3 py-1.5 font-mono text-sm text-slate-600 focus:outline-none focus:border-emerald-500 transition-colors"
                    >
                  </div>
                  <div class="flex items-center gap-2 ml-4 shrink-0">
                    <button v-if="user.apikey" @click="copyApiUrl" class="btn-copy flex items-center gap-2 px-3 py-1.5 bg-slate-800 text-white rounded hover:bg-slate-700 transition-colors text-sm font-medium">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      คัดลอก
                    </button>
                    <button class="btn-copy flex items-center gap-2 px-3 py-1.5 bg-emerald-600 text-white rounded hover:bg-emerald-700 transition-colors text-sm font-medium">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      คู่มือ API
                    </button>
                  </div>
                </div>
                
                <div v-if="!user.apikey" class="p-6 text-center border-b border-emerald-100 bg-emerald-50 text-emerald-800">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 mx-auto mb-2 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <p class="font-bold mb-1">คุณยังไม่มี API Key สำหรับการเข้าถึงแบบ Programmatic</p>
                  <p class="text-sm mb-4">ระบบต้องการเปิดใช้งานและสร้าง API Key ก่อน จึงจะสามารถคัดลอกลิงก์การเข้าถึงแบบปลอดภัยได้</p>
                  <router-link to="/profile" class="inline-block px-5 py-2.5 bg-emerald-600 text-white rounded-md font-medium hover:bg-emerald-700 transition-colors shadow-sm">
                    ไปที่การตั้งค่า Profile
                  </router-link>
                </div>

                <div class="json-preview p-0">
                  <div class="json-header px-4 py-2 bg-slate-800 text-slate-300 text-sm font-mono flex justify-between items-center">
                    <span>Example JSON Response Payload</span>
                  </div>
                  <pre class="m-0 p-4 bg-slate-900 text-emerald-400 font-mono text-sm overflow-x-auto"><code>{
  "total_rows": 2,
  "offset": 0,
  "rows": [
    {
      "id": "{{ selectedDataset?.dataset_id }}-row1",
      "data": {
        "value": 100.50,
        "updated_at": "2024-03-30T00:00:00Z"
      }
    },
    {
      "id": "{{ selectedDataset?.dataset_id }}-row2",
      "data": {
        "value": 250.75,
        "updated_at": "2024-03-30T00:00:00Z"
      }
    }
  ]
}</code></pre>
                </div>
              </div>
            </div>"""

if target_script in content and target_html in content:
    content = content.replace(target_script, replacement_script)
    content = content.replace(target_html, replacement_html)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("CatalogView API tab refactored.")
else:
    print("Missing strings!")
