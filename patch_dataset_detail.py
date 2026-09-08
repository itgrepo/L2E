import re

path = 'frontend/src/views/DatasetDetailView.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add apiClones to state
content = re.sub(
    r"(const showMouModal = ref\(false\);)",
    r"\1\nconst apiClones = ref([]);\n",
    content
)

# 2. Add combinedApis computed property
comp_str = """
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
content = re.sub(
    r"(const apiClones = ref\(\[\]\);\n)",
    r"\1" + comp_str,
    content
)

# 3. Add fetch clones to fetchDatasetDetail
fetch_end_str = "dictionary: found.dictionary || [],"
fetch_insert = """
        // Fetch clones for API tab
        try {
          const cloneRes = await apiClient.post('/getDatasetApiEndpoints', { dataset_id: found.dataset_id || found.service_id });
          if (cloneRes.data && cloneRes.data.data) {
             apiClones.value = cloneRes.data.data;
          }
        } catch (e) {
          console.error('Failed to fetch clones', e);
        }
"""
content = content.replace(fetch_end_str, fetch_end_str + fetch_insert)


with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
