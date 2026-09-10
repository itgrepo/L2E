import re

path = 'frontend/src/views/DatasetDetailView.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add computed property for combined APIs
comp_code = """const showMouModal = ref(false);
const activeTab = ref('description');
const apiClones = ref([]);"""

new_comp_code = """const showMouModal = ref(false);
const activeTab = ref('description');
const apiClones = ref([]);

const combinedApis = computed(() => {
  let apis = [];
  if (selectedDataset.value && selectedDataset.value.api_enabled) {
    apis.push({
      api_type: selectedDataset.value.api_type || 'general',
      api_endpoint: selectedDataset.value.api_endpoint || selectedDataset.value.dataset_id,
      service_name: selectedDataset.value.title
    });
  }
  if (apiClones.value && apiClones.value.length > 0) {
    apiClones.value.forEach(clone => {
      apis.push({
        api_type: clone.api_type || 'general',
        api_endpoint: clone.api_endpoint,
        service_name: clone.service_name || clone.description
      });
    });
  }
  return apis;
});"""
content = content.replace(comp_code, new_comp_code)

# Replace the HTML for API tab
html_to_replace = """            <!-- API Tab -->
            <div v-if="activeTab === 'api'" class="api-tab transition-fade">
              <!-- If does not have API enabled -->
              <div v-if="!selectedDataset.api_enabled" style="padding:40px; text-align:center; background:#f8fafc; border:1px solid #e2e8f0; border-radius:16px;">
                <p style="font-weight:bold; font-size:1.1rem; color:#475569; margin:0 0 8px 0;">🔒 ข้อมูล API เฉพาะ Private API</p>
                <p style="font-size:0.875rem; color:#64748b; margin:0;">ชุดข้อมูลนี้ยังไม่เปิดบริการเรียกใช้ผ่านช่องทาง API สำหรับระดับสิทธิ์ของคุณ</p>
              </div>
              
              <!-- If has API, show details -->
              <div v-else class="api-cards" style="display: flex; flex-direction: column; gap: 1rem;">
                
                <!-- Card 1: File for API -->
                <div v-if="selectedDataset.file_path" class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white;">
                  <h3 style="margin: 0 0 16px 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                    File for API
                  </h3>
                  <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' + userApiKey)">คัดลอกเพื่อใช้งาน API</div>
                  <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem;">
                    {{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>
                  </code>
                  <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                    <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>"</pre>
                  </div>
                </div>

                <!-- Card 2: Public API -->
                <div v-if="!selectedDataset.api_type || selectedDataset.api_type === 'general'" class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white;">
                  <h3 style="margin: 0 0 16px 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>
                    Public API (General)
                  </h3>
                  <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '?apikey=' + userApiKey)">คัดลอกเพื่อใช้งาน API</div>
                  <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem;">
                    {{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>
                  </code>
                  <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                    <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>"</pre>
                  </div>
                </div>

                
                
<!-- Card 3: Scope API -->
                <div v-if="selectedDataset.api_type === 'scope'" class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white;">
                  <h3 style="margin: 0 0 16px 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                    Scope API (Granular Access)
                  </h3>
                  <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '?apikey=' + userApiKey + '&[column_name]=[value]')">คัดลอกเพื่อใช้งาน API</div>
                  <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem;">
                    {{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>&[column_name]=[value]
                  </code>
                  <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                    <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>&[column_name]=[value]"</pre>
                  </div>
                </div>
              </div>
            </div>"""

new_html = """            <!-- API Tab -->
            <div v-if="activeTab === 'api'" class="api-tab transition-fade">
              <!-- If does not have API enabled and no clones -->
              <div v-if="combinedApis.length === 0" style="padding:40px; text-align:center; background:#f8fafc; border:1px solid #e2e8f0; border-radius:16px;">
                <p style="font-weight:bold; font-size:1.1rem; color:#475569; margin:0 0 8px 0;">🔒 ข้อมูล API เฉพาะ Private API</p>
                <p style="font-size:0.875rem; color:#64748b; margin:0;">ชุดข้อมูลนี้ยังไม่เปิดบริการเรียกใช้ผ่านช่องทาง API สำหรับระดับสิทธิ์ของคุณ</p>
              </div>
              
              <!-- If has API, show details -->
              <div v-else class="api-cards" style="display: flex; flex-direction: column; gap: 1rem;">
                
                <!-- Card 1: File for API (Only show once if original dataset has file_path) -->
                <div v-if="selectedDataset.file_path" class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white;">
                  <h3 style="margin: 0 0 16px 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                    File for API
                  </h3>
                  <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' + userApiKey)">คัดลอกเพื่อใช้งาน API</div>
                  <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem;">
                    {{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>
                  </code>
                  <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                    <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>"</pre>
                  </div>
                </div>

                <!-- Loop through all configured APIs (Original + Clones) -->
                <div v-for="(api, index) in combinedApis" :key="index">
                  <!-- General API -->
                  <div v-if="api.api_type === 'general' || api.api_type === 'public' || api.api_type === 'private'" class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white;">
                    <h3 style="margin: 0 0 16px 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>
                      Public API (General) - {{ api.api_endpoint }}
                    </h3>
                    <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + api.api_endpoint + '?apikey=' + userApiKey)">คัดลอกเพื่อใช้งาน API</div>
                    <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem;">
                      {{ selectedDataset.external_api_url || apiBaseUrl + api.api_endpoint + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>
                    </code>
                    <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                      <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || apiBaseUrl + api.api_endpoint + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>"</pre>
                    </div>
                  </div>

                  <!-- Scope API -->
                  <div v-if="api.api_type === 'scope'" class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white;">
                    <h3 style="margin: 0 0 16px 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                      Scope API (Granular Access) - {{ api.api_endpoint }}
                    </h3>
                    <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + api.api_endpoint + '?apikey=' + userApiKey + '&[column_name]=[value]')">คัดลอกเพื่อใช้งาน API</div>
                    <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem;">
                      {{ selectedDataset.external_api_url || apiBaseUrl + api.api_endpoint + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>&[column_name]=[value]
                    </code>
                    <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                      <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || apiBaseUrl + api.api_endpoint + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>&[column_name]=[value]"</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>"""

content = content.replace(html_to_replace, new_html)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
