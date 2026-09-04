with open('frontend/src/views/DatasetConfigView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

import re

computed_code = """
const showGovConflict = computed(() => {
  if (datasetConfig.value.service_type === 'private' && datasetConfig.value.category === 'ข้อมูลสาธารณะ') {
    return true;
  }
  return false;
});
"""

# Wait, what are the exact field names?
