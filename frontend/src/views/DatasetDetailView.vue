<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient from '../utils/api';

const route = useRoute();
const activeTab = ref('overview');
const isLoading = ref(true);
const errorMessage = ref('');

const dataset = ref({
  id: route.params.id,
  title: 'Loading...',
  agency: 'Digital Experience Team',
  description: '',
  lastUpdated: 'Recently',
  accessLevel: 'Open Data',
  license: 'Creative Commons Attribution',
  image: null,
  formats: [
    { name: 'data_export.csv', size: 'Unknown', type: 'CSV' },
    { name: 'data_export.json', size: 'Unknown', type: 'JSON' }
  ]
});

const fetchDatasetDetail = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const response = await apiClient.get('/retrieveService');
    if (response.data.status === 'success') {
      const found = response.data.data.find(item => item.service_id.toString() === route.params.id.toString());
      if (found) {
        dataset.value = {
          ...dataset.value,
          id: found.service_id,
          title: found.service_name,
          description: found.service_name + ' (No detailed description available in backend)',
          image: found.service_image ? `data:image/png;base64,${found.service_image}` : null
        };
      } else {
        errorMessage.value = 'Dataset not found.';
      }
    } else {
      errorMessage.value = 'Failed to load dataset details.';
    }
  } catch (error) {
    console.error('Error fetching dataset detail:', error);
    errorMessage.value = 'An error occurred while loading the dataset.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchDatasetDetail();
});
</script>

<template>
  <div class="detail-layout">
    <AppSidebar />
    
    <main class="detail-content">
      <nav class="breadcrumb">
        <router-link to="/catalog">Catalog</router-link>
        <span class="separator">/</span>
        <span class="current">Dataset Detail</span>
      </nav>
      
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading dataset details...</p>
      </div>
      
      <div v-else-if="errorMessage" class="error-state">
        <p>{{ errorMessage }}</p>
        <button @click="fetchDatasetDetail" class="btn-outline">Retry</button>
      </div>
      
      <template v-else>
        <header class="detail-header">
        <div class="header-main">
          <div class="agency-header">
            <div class="agency-logo">กทม.</div>
            <span class="agency-name">{{ dataset.agency }}</span>
          </div>
          <h1>{{ dataset.title }}</h1>
          
          <div class="header-meta">
            <span class="meta-badge access">{{ dataset.accessLevel }}</span>
            <span class="meta-item">Updated: {{ dataset.lastUpdated }}</span>
          </div>
        </div>
        
        <div class="header-actions">
          <button class="btn-outline">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            Follow
          </button>
          <button class="btn-primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export All
          </button>
        </div>
      </header>
      
      <div class="tabs-container">
        <nav class="tabs">
          <button 
            @click="activeTab = 'overview'" 
            :class="['tab-btn', { active: activeTab === 'overview' }]"
          >Overview</button>
          <button 
            @click="activeTab = 'files'" 
            :class="['tab-btn', { active: activeTab === 'files' }]"
          >Files & Data</button>
          <button 
            @click="activeTab = 'api'" 
            :class="['tab-btn', { active: activeTab === 'api' }]"
          >API Documentation</button>
          <button 
            @click="activeTab = 'stats'" 
            :class="['tab-btn', { active: activeTab === 'stats' }]"
          >Usage Stats</button>
        </nav>
        
        <div class="tab-content">
          <div v-if="activeTab === 'overview'" class="overview-tab">
            <section class="info-section">
              <h3>Description</h3>
              <p>{{ dataset.description }}</p>
            </section>
            
            <section class="info-section grid">
              <div>
                <h4>Source</h4>
                <p>สำนักทะเบียนราษฎร์</p>
              </div>
              <div>
                <h4>License</h4>
                <p>{{ dataset.license }}</p>
              </div>
              <div>
                <h4>Maintainer</h4>
                <p>Digital Governance Team</p>
              </div>
            </section>
          </div>
          
          <div v-if="activeTab === 'files'" class="files-tab">
            <div class="file-list">
              <div v-for="file in dataset.formats" :key="file.name" class="file-item">
                <div class="file-icon">{{ file.type }}</div>
                <div class="file-info">
                  <p class="file-name">{{ file.name }}</p>
                  <p class="file-meta">{{ file.size }} • Last updated 2 days ago</p>
                </div>
                <button class="download-btn">Download</button>
              </div>
            </div>
          </div>
          
          <div v-if="activeTab === 'api'" class="api-tab">
            <div class="api-doc">
              <div class="method-badge">GET</div>
              <code class="endpoint">https://api.l2e.go.th/v1/datasets/population_2023</code>
              
              <div class="code-block">
                <pre>
curl -X GET "https://api.l2e.go.th/v1/datasets/population_2023" \
  -H "Authorization: Bearer YOUR_API_KEY"</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  items-center: center;
  justify-content: center;
  padding: 80px;
  text-align: center;
  gap: 16px;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f5f9;
  border-top-color: var(--mso-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.detail-layout {
  display: flex;
  background-color: #f8fafc;
  min-height: 100vh;
}

.detail-content {
  flex: 1;
  padding: 40px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 24px;
}

.breadcrumb a {
  color: var(--mso-accent);
  text-decoration: none;
}

.separator {
  color: #cbd5e1;
}

.current {
  color: #94a3b8;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}

.agency-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.agency-logo {
  width: 32px;
  height: 32px;
  background: #f1f5f9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
}

.agency-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
}

h1 {
  font-size: 2.25rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 16px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.meta-badge {
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 700;
}

.meta-badge.access {
  background: #fce7f3;
  color: #166534;
}

.meta-item {
  font-size: 0.875rem;
  color: #94a3b8;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: var(--mso-accent);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.btn-outline {
  background: white;
  color: #475569;
  border: 1px solid #e2e8f0;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.tabs-container {
  background: white;
  border-radius: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #f1f5f9;
  padding: 0 24px;
}

.tab-btn {
  padding: 24px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 1rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  color: var(--mso-accent);
  border-bottom-color: var(--mso-accent);
}

.tab-content {
  padding: 40px;
}

.info-section h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16px;
}

.info-section p {
  line-height: 1.6;
  color: #475569;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-top: 40px;
  padding-top: 40px;
  border-top: 1px solid #f1f5f9;
}

h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  margin-bottom: 12px;
}

.file-icon {
  width: 48px;
  height: 48px;
  background: #fdf2f8;
  color: var(--mso-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.75rem;
  border-radius: 12px;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.file-meta {
  font-size: 0.875rem;
  color: #94a3b8;
}

.download-btn {
  background: #f1f5f9;
  color: #475569;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.api-doc {
  background: #0f172a;
  padding: 24px;
  border-radius: 16px;
  color: white;
}

.method-badge {
  display: inline-block;
  background: var(--mso-accent);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  margin-bottom: 12px;
}

.endpoint {
  display: block;
  font-family: monospace;
  color: #94a3b8;
  margin-bottom: 24px;
}

.code-block {
  background: #1e293b;
  padding: 16px;
  border-radius: 8px;
  font-family: monospace;
}

pre {
  margin: 0;
  color: #e2e8f0;
}
</style>
