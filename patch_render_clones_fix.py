import re

path = 'frontend/src/views/DatasetDetailView.vue'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_comp = """const combinedApis = computed(() => {
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

new_comp = """const combinedApis = computed(() => {
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
      if (clone.api_enabled === 1 || clone.api_enabled === true || clone.api_enabled === '1' || clone.api_enabled === undefined) {
        apis.push({
          api_type: clone.api_type || 'general',
          api_endpoint: clone.api_endpoint,
          service_name: clone.service_name || clone.description
        });
      }
    });
  }
  return apis;
});"""

content = content.replace(old_comp, new_comp)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
