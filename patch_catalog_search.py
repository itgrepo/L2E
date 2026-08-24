import re

filepath = "frontend/src/views/CatalogView.vue"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

script_patch = """
const showSuggestions = ref(false);

const searchSuggestions = computed(() => {
  if (!searchQuery.value.trim()) return [];
  const query = searchQuery.value.toLowerCase().trim();
  const suggestions = [];
  const maxSuggestions = 8;
  
  datasets.value.forEach(ds => {
    if (ds.title.toLowerCase().includes(query) && !suggestions.find(s => s.text === ds.title)) {
      suggestions.push({ text: ds.title, type: 'ชุดข้อมูล' });
    }
  });
  
  datasets.value.forEach(ds => {
    if (ds.tags) {
      const tagsList = ds.tags.split(',');
      tagsList.forEach(t => {
        const tag = t.trim();
        if (tag.toLowerCase().includes(query) && !suggestions.find(s => s.text === tag)) {
          suggestions.push({ text: tag, type: 'แท็ก' });
        }
      });
    }
  });
  
  return suggestions.slice(0, maxSuggestions);
});

const selectSuggestion = (text) => {
  searchQuery.value = text;
  showSuggestions.value = false;
};

const hideSuggestions = () => {
  setTimeout(() => {
    showSuggestions.value = false;
  }, 200);
};

const highlight = (text, query) => {
  if (!query) return text;
  const escapedQuery = query.replace(/[.*+?^${}()|[\]\\\\]/g, '\\\\$&');
  const regex = new RegExp(`(${escapedQuery})`, 'gi');
  return text.replace(regex, '<strong style="color: var(--primary);">$1</strong>');
};

const requestForm = ref({"""

content = content.replace("const requestForm = ref({", script_patch)

template_find = """<input type="text" v-model="searchQuery" placeholder="ค้นหาชุดข้อมูล เช่น Course Data, Job Market...">"""
template_replace = """<input type="text" v-model="searchQuery" @focus="showSuggestions = true" @blur="hideSuggestions" placeholder="ค้นหาชุดข้อมูล เช่น Course Data, Job Market...">
            
            <ul v-if="showSuggestions && searchSuggestions.length > 0" class="auto-suggestions-dropdown">
              <li v-for="(sug, index) in searchSuggestions" :key="index" @mousedown.prevent="selectSuggestion(sug.text)">
                <div class="sug-content">
                  <svg v-if="sug.type === 'ชุดข้อมูล'" xmlns="http://www.w3.org/2000/svg" class="sug-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="sug-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <span v-html="highlight(sug.text, searchQuery)"></span>
                </div>
                <span class="sug-type">{{ sug.type }}</span>
              </li>
            </ul>"""

content = content.replace(template_find, template_replace)

css_patch = """
</style>
<style scoped>
.search-input-wrapper {
  position: relative;
}

.auto-suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  list-style: none;
  padding: 8px 0;
  z-index: 50;
  max-height: 300px;
  overflow-y: auto;
}

.auto-suggestions-dropdown li {
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #f8fafc;
}

.auto-suggestions-dropdown li:last-child {
  border-bottom: none;
}

.auto-suggestions-dropdown li:hover {
  background-color: #f1f5f9;
}

.sug-content {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: #334155;
}

.sug-icon {
  width: 16px;
  height: 16px;
  color: #94a3b8;
}

.sug-type {
  font-size: 0.7rem;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 12px;
  color: #64748b;
  font-weight: 600;
}
</style>
"""

content = content.replace("</style>", css_patch)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("CatalogView.vue patched.")
