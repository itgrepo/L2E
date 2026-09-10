import re

path = 'frontend/src/views/DatasetDetailView.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add apiClones and combinedApis to script setup
script_marker = "const customApiEndpoints = ref([]);"
insertion = """
const customApiEndpoints = ref([]);
const apiClones = ref([]);

const combinedApis = computed(() => {
  let apis = [];
  if (selectedDataset.value && (selectedDataset.value.api_enabled === 1 || selectedDataset.value.api_enabled === true || selectedDataset.value.api_enabled === '1')) {
    apis.push({
      api_type: selectedDataset.value.api_type || 'general',
      api_endpoint: selectedDataset.value.api_endpoint || selectedDataset.value.dataset_id,
      service_name: selectedDataset.value.title
    });
  }
  if (apiClones.value && apiClones.value.length > 0) {
    apiClones.value.forEach(clone => {
      if (clone.api_enabled === 1 || clone.api_enabled === true || clone.api_enabled === '1' || clone.api_enabled === undefined || clone.status === 'Active') {
        apis.push({
          api_type: clone.api_type || 'general',
          api_endpoint: clone.api_endpoint,
          service_name: clone.service_name || clone.description
        });
      }
    });
  }
  return apis;
});
"""
content = content.replace(script_marker, insertion)

# 2. Add API fetch
fetch_marker = "api_enabled: found.api_enabled == 1 || found.api_enabled === '1' || found.api_enabled === true,"
fetch_insertion = """
          api_enabled: found.api_enabled == 1 || found.api_enabled === '1' || found.api_enabled === true,
        };

        // Fetch clones for API tab
        try {
          const cloneRes = await apiClient.post('/getDatasetApiEndpoints', { dataset_id: found.dataset_id || found.service_id });
          if (cloneRes.data && cloneRes.data.data) {
             apiClones.value = cloneRes.data.data;
          }
        } catch (e) {
          console.error('Failed to fetch clones', e);
        }
        
        // Merge the rest just to satisfy old code
        selectedDataset.value = {
          ...selectedDataset.value,
"""
content = content.replace(fetch_marker, fetch_insertion)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
