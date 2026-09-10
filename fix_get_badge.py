import re

with open('frontend/src/views/DatasetDetailView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Add copyToClipboard function
script_setup_idx = content.find('const toggleFavorite =')
if script_setup_idx != -1:
    copy_func = """
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    alert('คัดลอกสำเร็จ');
  } catch (err) {
    console.error('Failed to copy', err);
  }
};

"""
    content = content[:script_setup_idx] + copy_func + content[script_setup_idx:]


# Replace the 3 GET badges
# Card 1
content = content.replace(
    '<div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px;">GET</div>',
    """<div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' + userApiKey)">คัดลอกเพื่อใช้งาน API</div>""",
    1
)

# Card 2
content = content.replace(
    '<div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px;">GET</div>',
    """<div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '?apikey=' + userApiKey)">คัดลอกเพื่อใช้งาน API</div>""",
    1
)

# Card 3
content = content.replace(
    '<div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px;">GET</div>',
    """<div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '?apikey=' + userApiKey + '&[column_name]=[value]')">คัดลอกเพื่อใช้งาน API</div>""",
    1
)

with open('frontend/src/views/DatasetDetailView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

