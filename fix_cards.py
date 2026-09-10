with open('frontend/src/views/DatasetDetailView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# Add v-if to Card 1
content = content.replace(
    '<!-- Card 1: File for API -->\n                <div class="api-doc"',
    '<!-- Card 1: File for API -->\n                <div v-if="selectedDataset.file_path" class="api-doc"'
)

# Add v-if to Card 2
content = content.replace(
    '<!-- Card 2: Public API -->\n                <div class="api-doc"',
    '<!-- Card 2: Public API -->\n                <div v-if="!selectedDataset.api_type || selectedDataset.api_type === \'general\'" class="api-doc"'
)

# Add v-if to Card 3
content = content.replace(
    '<!-- Card 3: Scope API -->\n                <div class="api-doc"',
    '<!-- Card 3: Scope API -->\n                <div v-if="selectedDataset.api_type === \'scope\'" class="api-doc"'
)

with open('frontend/src/views/DatasetDetailView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

