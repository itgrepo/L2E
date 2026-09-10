import re

with open('frontend/src/views/DatasetDetailView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add api_endpoint
content = content.replace(
    "external_api_url: found.external_api_url,",
    "external_api_url: found.external_api_url,\n          api_endpoint: found.api_endpoint,"
)

# 2. Update Card 1, Card 2, Card 3 endpoints
content = content.replace(
    "apiBaseUrl + selectedDataset.dataset_id + '/file?apikey='",
    "apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey='"
)
content = content.replace(
    "apiBaseUrl + selectedDataset.dataset_id + '?apikey='",
    "apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '?apikey='"
)

# 3. Remove Custom Endpoints List HTML block
start_marker = "<!-- Custom Endpoints List -->"
end_marker = "<!-- Card 3: Scope API -->"
start_idx = content.find(start_marker)
end_idx = content.find(end_marker)
if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + "\n" + content[end_idx:]

with open('frontend/src/views/DatasetDetailView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

