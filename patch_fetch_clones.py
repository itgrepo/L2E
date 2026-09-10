import re

path = 'frontend/src/views/DatasetDetailView.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add apiClones to state
state_code = """const showMouModal = ref(false);
const activeTab = ref('description');"""
new_state_code = """const showMouModal = ref(false);
const activeTab = ref('description');
const apiClones = ref([]);"""
content = content.replace(state_code, new_state_code)

# Add fetch clones to fetchDatasetDetail
fetch_code = """      if (found) {
        selectedDataset.value = {
          id: found.service_id,
          title: found.service_name,
          category: found.category_name,
          records: found.record_count || '0',
          agency: found.owner_name || 'N/A',
          contact: found.owner_name || 'N/A',
          description: found.description || 'ไม่มีคำอธิบายสำหรับชุดข้อมูลนี้',
          dictionary: found.dictionary || [],
          formats: ['API'],
          isFavorite: favorites.value.some(fav => fav.id === found.service_id),
          dataset_id: found.dataset_id || found.service_id,
          api_enabled: found.api_enabled,
          api_type: found.api_type,
          api_endpoint: found.api_endpoint,
          file_path: found.file_path,
          permission_status: found.permission_status,
          has_access: found.has_access
        };
      }"""

new_fetch_code = """      if (found) {
        selectedDataset.value = {
          id: found.service_id,
          title: found.service_name,
          category: found.category_name,
          records: found.record_count || '0',
          agency: found.owner_name || 'N/A',
          contact: found.owner_name || 'N/A',
          description: found.description || 'ไม่มีคำอธิบายสำหรับชุดข้อมูลนี้',
          dictionary: found.dictionary || [],
          formats: ['API'],
          isFavorite: favorites.value.some(fav => fav.id === found.service_id),
          dataset_id: found.dataset_id || found.service_id,
          api_enabled: found.api_enabled,
          api_type: found.api_type,
          api_endpoint: found.api_endpoint,
          file_path: found.file_path,
          permission_status: found.permission_status,
          has_access: found.has_access
        };
        
        // Fetch clones for API tab
        try {
          const cloneRes = await apiClient.post('/getDatasetApiEndpoints', { dataset_id: selectedDataset.value.dataset_id });
          if (cloneRes.data && cloneRes.data.data) {
             apiClones.value = cloneRes.data.data;
          }
        } catch (e) {
          console.error('Failed to fetch clones', e);
        }
      }"""

content = content.replace(fetch_code, new_fetch_code)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

