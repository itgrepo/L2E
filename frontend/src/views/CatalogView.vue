<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData } from '../utils/api';

const searchQuery = ref('');

const requestForm = ref({
  fields: [],
  reason: ''
});
const isSubmittingReq = ref(false);
const reqError = ref('');
const reqSuccess = ref('');

const submitPermissionRequest = async () => {
  if (requestForm.value.fields.length === 0) {
    reqError.value = 'โปรดเลือกอย่างน้อย 1 ฟิลด์ข้อมูล';
    return;
  }
  if (!requestForm.value.reason.trim()) {
    reqError.value = 'โปรดระบุวัตถุประสงค์ในการขอเข้าถึง';
    return;
  }
  
  isSubmittingReq.value = true;
  reqError.value = '';
  reqSuccess.value = '';
  
  try {
    const userData = localStorage.getItem('user');
    const response = await apiClient.post('/requestDatasetPermission', {
      user: encodeUserData(JSON.parse(userData)),
      service_id: selectedDataset.value.id,
      fields: requestForm.value.fields,
      reason: requestForm.value.reason
    });
    
    if (response.data.status === 'success') {
      reqSuccess.value = 'ส่งคำขอเข้าถึงข้อมูลเรียบร้อยแล้ว';
      selectedDataset.value.permission_status = 'Pending';
      requestForm.value.fields = [];
      requestForm.value.reason = '';
      fetchDatasets();
    } else {
      reqError.value = response.data.message || 'เกิดข้อผิดพลาด';
    }
  } catch (error) {
    reqError.value = error.response?.data?.message || 'ไม่สามารถส่งคำขอได้';
  } finally {
    isSubmittingReq.value = false;
  }
};
const datasets = ref([]);
const isLoading = ref(true);
const errorMessage = ref('');

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 2; // Fixed at 2 for the demo (6 items = 3 pages)

const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));

const copyApiUrl = () => {
  navigator.clipboard.writeText(apiUrl.value);
  alert('คัดลอก URL เรียบร้อยแล้ว');
};

const apiUrl = computed(() => {
  // Demo Bypass: Allow testadmin to see the URL even if detectedApiKey is missing
  const effectiveKey = detectedApiKey.value || (user.value.username === 'testadmin' ? 'demo_key_testadmin_active' : '');
  if (!effectiveKey) return 'ต้องมี API Key เพื่อดูลิงก์';
  return `${window.location.origin}/dataapi/api/v1/${selectedDataset.value?.dataset_id || ''}?apikey=${effectiveKey}`;
});

// Modal State
const isModalOpen = ref(false);
const isPreviewModalOpen = ref(false);
const previewType = ref('');
const selectedDataset = ref(null);
const activeTab = ref('info');

const openPreview = (type) => {
  previewType.value = type;
  isPreviewModalOpen.value = true;
};

const closePreview = () => {
  isPreviewModalOpen.value = false;
};

// Dynamic API Key Detection
const detectedApiKey = ref(user.value.apikey || '');

const checkLocalKeys = () => {
    // If we don't have a key in the user object, check if one was saved by the API Management view
    if (!detectedApiKey.value) {
        const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
        if (storedUser.apikey) {
            detectedApiKey.value = storedUser.apikey;
            user.value.apikey = storedUser.apikey;
        }
    }
};

onMounted(() => {
    checkLocalKeys();
});

watch(activeTab, (newTab) => {
    if (newTab === 'api') {
        checkLocalKeys();
    }
});

const categories = ref([
  { name: 'Learning Catalog', count: 0, active: false },
  { name: 'Learning Record', count: 0, active: false },
  { name: 'Learner Profile', count: 0, active: false },
  { name: 'Job Market', count: 0, active: false },
  { name: 'Skill Intelligence', count: 0, active: false }
]);

const fetchCategories = async () => {
  try {
    const response = await apiClient.get('/retrieveCategories');
    if (response.data && response.data.status === 'success' && Array.isArray(response.data.data)) {
      categories.value = response.data.data.map(c => ({
        name: c.name || c.category_name,
        count: 0,
        active: false
      }));
    }
  } catch (error) {
    console.error('Error fetching categories:', error);
  }
};

const accessLevels = ref([
  { name: 'Open Data', count: 5, active: false },
  { name: 'Restricted', count: 1, active: false },
  { name: 'Confidential', count: 0, active: false }
]);

const formats = ['CSV', 'XLS', 'API', 'JSON', 'XML'];

const filteredDatasets = computed(() => {
  let result = datasets.value;

  // 1. Search Query Filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(ds => 
      ds.title.toLowerCase().includes(query) || 
      ds.agency.toLowerCase().includes(query) ||
      ds.description.toLowerCase().includes(query)
    );
  }

  // 2. Category Filter
  const activeCategories = categories.value.filter(c => c.active).map(c => c.name);
  if (activeCategories.length > 0) {
    result = result.filter(ds => activeCategories.includes(ds.category));
  }

  // 3. Access Level Filter
  const activeLevels = accessLevels.value.filter(l => l.active).map(l => l.name);
  if (activeLevels.length > 0) {
    result = result.filter(ds => activeLevels.includes(ds.accessibility));
  }

  // 4. Format Filter
  if (selectedFormats.value.length > 0) {
    result = result.filter(ds => 
      ds.formats.some(f => selectedFormats.value.includes(f))
    );
  }

  return result;
});

const totalPages = computed(() => {
  return Math.ceil(filteredDatasets.value.length / itemsPerPage);
});

const paginatedDatasets = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredDatasets.value.slice(start, end);
});

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

const selectedFormats = ref([]);

// Reset page when filtering
watch([searchQuery, categories, accessLevels, selectedFormats], () => {
  currentPage.value = 1;
}, { deep: true });

const toggleCategory = (cat) => {
  cat.active = !cat.active;
};

const toggleAccessLevel = (level) => {
  level.active = !level.active;
};

const toggleFormat = (format) => {
  const index = selectedFormats.value.indexOf(format);
  if (index > -1) {
    selectedFormats.value.splice(index, 1);
  } else {
    selectedFormats.value.push(format);
  }
};

const openDatasetDetail = (ds) => {
  selectedDataset.value = ds;
  activeTab.value = 'info';
  isModalOpen.value = true;
  requestForm.value = { fields: [], reason: '' };
  reqError.value = '';
  reqSuccess.value = '';
};

const closeDatasetDetail = () => {
  isModalOpen.value = false;
  selectedDataset.value = null;
};

const favorites = ref(JSON.parse(localStorage.getItem('user_favorites') || '[]'));

const toggleFavorite = (ds) => {
  const index = favorites.value.findIndex(f => f.id === ds.id);
  if (index >= 0) {
    favorites.value.splice(index, 1);
  } else {
    favorites.value.push({
      id: ds.id,
      dataset_id: ds.dataset_id,
      title: ds.title,
      description: ds.description,
      accessibility: ds.accessibility,
      agency: ds.agency,
      views: ds.views,
      updated: ds.updated,
      api_enabled: ds.api_enabled,
      api_type: ds.api_type,
      formats: ds.formats || ['CSV', 'API']
    });
  }
  localStorage.setItem('user_favorites', JSON.stringify(favorites.value));
};

const isFavorite = (ds) => {
  return favorites.value.some(f => f.id === ds.id);
};

const fetchDatasets = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const response = await apiClient.get('/retrieveService');
    if (response.data.status === 'success') {
      console.log('Catalog Raw Data (first 3):', response.data.data.slice(0, 3).map(i => ({ name: i.service_name, api: i.api_enabled })));
      datasets.value = response.data.data.map(item => ({
        id: item.service_id,
        dataset_id: item.dataset_id,
        title: item.service_name,
        agency: item.organization || 'ไม่ระบุหน่วยงาน',
        category: item.category || 'ทั่วไป',
        sub_category: item.sub_category || '-',
        description: item.description || 'ข้อมูลชุดนี้รวบรวมเพื่อการวิเคราะห์และนำไปใช้ประโยชน์ในระดับภาครัฐและเอกชน โดยเน้นความถูกต้องและเป็นปัจจุบัน',
        contact_name: item.contact_name || '-',
        contact_email: item.contact_email || '-',
        tags: item.tags || '',
        purpose: item.purpose || '-',
        accessibility: item.accessibility || 'Open Data',
        access_type: item.access_type || '-',
        dept_contact: item.dept_contact || '-',
        update_freq: (item.update_freq_value || '-') + ' ' + (item.update_freq_unit || ''),
        geo_scope: item.geo_scope || '-',
        data_source: item.data_source || '-',
        gov_category: item.gov_category || '-',
        license: item.license || '-',
        access_conditions: item.access_conditions || '-',
        sponsor: item.sponsor || '-',
        smallest_unit: item.smallest_unit || '-',
        languages: item.languages || '-',
        objective_type: item.objective_type || '-',
        external_dashboard_url: item.external_dashboard_url,
        external_api_url: item.external_api_url,
        has_access: item.has_access === 1 || item.has_access === '1' || item.has_access === true,
        permission_status: item.permission_status,
        api_response_fields: item.api_response_fields ? (typeof item.api_response_fields === 'string' ? JSON.parse(item.api_response_fields) : item.api_response_fields) : ['id', 'name', 'amount', 'date'],
        api_enabled: item.api_enabled == 1 || item.api_enabled === '1' || item.api_enabled === true || String(item.api_enabled).toLowerCase() === 'true',
        api_type: item.api_type || 'public',
        formats: item.data_format ? item.data_format.split(',') : ['CSV', 'API', 'JSON'],
        file_path: item.file_path,
        views: (Math.floor(Math.random() * 900) + 100) + 'K records',
        updated: 'อัปเดต ' + (Math.floor(Math.random() * 5) + 1) + ' วันก่อน',
        isNew: Math.random() > 0.7
      }));
      
      // Update dynamic counts
      categories.value.forEach(cat => {
        cat.count = datasets.value.filter(ds => ds.category === cat.name).length;
      });
      accessLevels.value.forEach(lvl => {
        lvl.count = datasets.value.filter(ds => ds.accessibility === lvl.name).length;
      });
    }
  } catch (error) {
    console.error('Error fetching datasets:', error);
    errorMessage.value = 'Failed to load datasets.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(async () => {
  await fetchCategories();
  fetchDatasets();
});
</script>

<template>
  <div class="catalog-layout">
    <AppSidebar />
    
    <main class="catalog-content">
      <header class="catalog-header">
        <!-- Breadcrumbs -->
        <nav class="breadcrumbs" aria-label="Breadcrumb">
          <ol style="display: flex; align-items: center; gap: 8px; font-size: 0.875rem; color: #64748b; margin-bottom: 16px; list-style: none; padding: 0;">
            <li>
              <router-link to="/dashboard" style="color: #64748b; text-decoration: none; display: flex; align-items: center; transition: color 0.2s;" onmouseover="this.style.color='var(--primary)'" onmouseout="this.style.color='#64748b'">
                <svg xmlns="http://www.w3.org/2000/svg" style="height: 16px; width: 16px; margin-right: 4px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                หน้าหลัก
              </router-link>
            </li>
            <li>/</li>
            <li style="font-weight: 500; color: #1e293b;" aria-current="page">
              บัญชีข้อมูล
            </li>
          </ol>
        </nav>

        <div class="header-titles">
          <h1>ค้นหาชุดข้อมูล</h1>
          <p>เข้าถึงชุดข้อมูลที่เปิดเผยโดยหน่วยงานภาครัฐเพื่อการใช้งานที่หลากหลาย</p>
        </div>
        
        <div class="search-main-container">
          <div class="search-input-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input type="text" v-model="searchQuery" placeholder="ค้นหาชุดข้อมูล เช่น Course Data, Job Market...">
            <button class="btn-search">ค้นหา</button>
            <router-link to="/dataset-config" class="btn-add-dataset">Add Dataset</router-link>
          </div>
        </div>
      </header>
      
      <div class="catalog-container">
        <aside class="filter-sidebar">
          <div class="filter-card">
            <div class="filter-section">
              <div class="filter-header">
                <h3>หมวดหมู่</h3>
                <button class="btn-link" @click="searchQuery = ''">ล้าง</button>
              </div>
              <div class="filter-list">
                <label v-for="cat in categories" :key="cat.name" class="filter-checkbox">
                  <input type="checkbox" :checked="cat.active" @change="toggleCategory(cat)">
                  <span class="checkbox-custom"></span>
                  <span class="label-text">{{ cat.name }}</span>
                  <span class="count">({{ cat.count }})</span>
                </label>
              </div>
            </div>

            <div class="filter-section">
              <div class="filter-header">
                <h3>ระดับการเข้าถึง</h3>
              </div>
              <div class="filter-list">
                <label v-for="level in accessLevels" :key="level.name" class="filter-checkbox">
                  <input type="checkbox" :checked="level.active" @change="toggleAccessLevel(level)">
                  <span class="checkbox-custom"></span>
                  <span class="label-text">{{ level.name }}</span>
                  <span class="count">({{ level.count }})</span>
                </label>
              </div>
            </div>

            <div class="filter-section">
              <div class="filter-header">
                <h3>รูปแบบข้อมูล</h3>
              </div>
              <div class="format-tags">
                <button 
                  v-for="f in formats" 
                  :key="f" 
                  class="format-btn" 
                  :class="{ active: selectedFormats.includes(f) }"
                  @click="toggleFormat(f)"
                >
                  {{ f }}
                </button>
              </div>
            </div>
          </div>
        </aside>

        <section class="results-section">
          <div class="results-toolbar">
            <p v-if="isLoading">กำลังโหลดข้อมูล...</p>
            <p v-else-if="searchQuery">พบ {{ filteredDatasets.length }} ชุดข้อมูล สำหรับ "{{ searchQuery }}"</p>
            <p v-else>พบทั้งหมด {{ datasets.length }} ชุดข้อมูล</p>
            
            <div class="sort-control">
              <span>เรียงตาม:</span>
              <select>
                <option>เกี่ยวข้องมากที่สุด</option>
                <option>ใหม่ล่าสุด</option>
                <option>ยอดนิยม</option>
              </select>
            </div>
          </div>

          <div v-if="paginatedDatasets.length > 0" class="datasets-list-vertical">
            <router-link v-for="ds in paginatedDatasets" :key="ds.id" :to="'/dataset/' + ds.id" class="ds-horizontal-card">
              <div class="ds-main-content">
                <div class="ds-header">
                  <h4 class="ds-title">
                    <span v-if="!ds.has_access" style="margin-right: 6px;" title="ต้องขอสิทธิ์การเข้าถึง">🔒</span>
                    {{ ds.title }}
                  </h4>
                  <button class="btn-favorite" :class="{ 'is-active': isFavorite(ds) }" @click.stop.prevent="toggleFavorite(ds)">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" :fill="isFavorite(ds) ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.921-1.103 1.821-1.891 1.118l-3.976-2.888a1 1 0 00-1.175 0l-3.976 2.888c-.788.703-2.191-.197-1.891-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  </button>
                </div>
                <p class="ds-description">{{ ds.description }}</p>
                <div class="ds-footer">
                  <div class="ds-badges">
                    <span class="badge access-open">{{ ds.accessibility }}</span>
                    <span v-if="ds.api_enabled" :class="['badge', ds.api_type === 'private' ? 'format-api-private' : (ds.api_type === 'scope' ? 'format-api-scope' : 'format-api-public')]">
                      API: {{ ds.api_type === 'private' ? 'Private' : (ds.api_type === 'scope' ? 'Scope' : 'Public') }}
                    </span>
                    <span v-for="f in ds.formats.filter(f => f.toUpperCase() !== 'API')" :key="f" class="badge format">{{ f }}</span>
                  </div>
                  <div class="ds-meta">
                    <span class="agency">{{ ds.agency }}</span>
                    <span class="separator">•</span>
                    <span class="views">{{ ds.views }}</span>
                    <span class="separator">•</span>
                    <span class="updated">{{ ds.updated }}</span>
                  </div>
                </div>
              </div>
            </router-link>
          </div>
          
          <div v-else-if="!isLoading" class="no-results">
            <svg xmlns="http://www.w3.org/2000/svg" class="no-results-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 9.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3>ไม่พบชุดข้อมูลที่ต้องการ</h3>
            <p>ลองค้นหาด้วยคำสำคัญอื่น หรือเปลี่ยนตัวเลือกตัวกรอง</p>
          </div>

          <div v-if="totalPages > 1" class="pagination">
            <button 
              class="page-btn prev" 
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <button 
              v-for="page in totalPages" 
              :key="page" 
              class="page-btn" 
              :class="{ active: currentPage === page }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
            
            <button 
              class="page-btn next" 
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </section>
      </div>
    </main>

    <!-- Dataset Detail Modal -->
    <Teleport to="body">
      <div v-if="isModalOpen" class="modal-overlay" @click.self="closeDatasetDetail">
        <div class="modal-container">
          <header class="modal-header">
            <div class="title-with-badge">
              <h2>{{ selectedDataset?.title }}</h2>
              <span class="id-badge">{{ selectedDataset?.dataset_id }}</span>
            </div>
            <button class="btn-close" @click="closeDatasetDetail">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </header>

          <nav class="modal-tabs">
            <button :class="{ active: activeTab === 'info' }" @click="activeTab = 'info'">คำอธิบายข้อมูล</button>
            <button :class="{ active: activeTab === 'dictionary' }" @click="activeTab = 'dictionary'">พจนานุกรมข้อมูล</button>
            <button :class="{ active: activeTab === 'visual' }" @click="activeTab = 'visual'">แดชบอร์ด</button>
            <button :class="{ active: activeTab === 'api' }" @click="activeTab = 'api'">ข้อมูล API</button>
          </nav>

          <div class="modal-body scrollbar-custom">
            <!-- Info Tab -->
            <div v-if="activeTab === 'info'" class="tab-content transition-fade">
              <div class="info-grid">
                <div class="info-main">
                  <h3>รายละเอียด</h3>
                  <p>{{ selectedDataset?.description }}</p>
                  
                  <div class="metadata-table">
                    <div class="row-group-title">ข้อมูลทั่วไป</div>
                    <div class="row"><span class="label">รหัสชุดข้อมูล</span><span class="value font-mono">{{ selectedDataset?.dataset_id }}</span></div>
                    <div class="row"><span class="label">วันที่เริ่มต้นสร้าง</span><span class="value">{{ selectedDataset?.date_start || '-' }}</span></div>
                    <div class="row"><span class="label">วันที่ปรับปรุงข้อมูลล่าสุด</span><span class="value">{{ selectedDataset?.date_updated || '-' }}</span></div>
                    <div class="row"><span class="label">หน่วยงานเจ้าของ</span><span class="value">{{ selectedDataset?.agency }}</span></div>
                    <div class="row"><span class="label">ชื่อฝ่ายงานสำหรับติดต่อ</span><span class="value">{{ selectedDataset?.contact_name }}</span></div>
                    <div class="row"><span class="label">หมวดหมู่ชุดข้อมูล</span><span class="value">{{ selectedDataset?.category }} / {{ selectedDataset?.sub_category }}</span></div>
                    <div class="row"><span class="label">การเข้าถึง</span><span class="value">{{ selectedDataset?.access_type }}</span></div>
                    
                    <div class="row-group-title">ธรรมาภิบาลและความถี่</div>
                    <div class="row"><span class="label">ชั้นความลับ</span><span class="value">{{ selectedDataset?.gov_category }}</span></div>
                    <div class="row"><span class="label">สัญญาอนุญาต</span><span class="value">{{ selectedDataset?.license }}</span></div>
                    <div class="row"><span class="label">ชุดข้อมูลที่มีคุณค่าสูง</span><span class="value">{{ selectedDataset?.is_high_value || '-' }}</span></div>
                    <div class="row"><span class="label">ข้อมูลอ้างอิง</span><span class="value">{{ selectedDataset?.is_reference || '-' }}</span></div>
                    <div class="row" v-if="!['statistic', 'geospatial'].includes(selectedDataset?.dataset_type)"><span class="label">ความถี่การปรับปรุง</span><span class="value">{{ selectedDataset?.update_freq }}</span></div>
                    <div class="row" v-if="!['statistic', 'geospatial'].includes(selectedDataset?.dataset_type)"><span class="label">ขอบเขตข้อมูล</span><span class="value">{{ selectedDataset?.geo_scope }}</span></div>

                    <!-- STATISTIC SPECIFIC -->
                    <template v-if="selectedDataset?.dataset_type === 'statistic'">
                      <div class="row-group-title text-sky-600 border-sky-200 mt-4">ข้อมูลเฉพาะสถิติ</div>
                      <div class="row"><span class="label">ปีข้อมูลที่เริ่มจัดทำ</span><span class="value">{{ selectedDataset.stat_year_start || '-' }}</span></div>
                      <div class="row"><span class="label">ปีข้อมูลล่าสุด</span><span class="value">{{ selectedDataset.stat_year_latest || '-' }}</span></div>
                      <div class="row"><span class="label">การจัดจำแนก</span><span class="value">{{ selectedDataset.stat_classification || '-' }}</span></div>
                      <div class="row"><span class="label">หน่วยวัด</span><span class="value">{{ selectedDataset.stat_unit || '-' }}</span></div>
                      <div class="row"><span class="label">หน่วยตัวคูณ</span><span class="value">{{ selectedDataset.stat_multiplier || '-' }}</span></div>
                      <div class="row"><span class="label">วิธีการคำนวณ</span><span class="value">{{ selectedDataset.stat_calculation_method || '-' }}</span></div>
                      <div class="row"><span class="label">มาตรฐานการจัดทำข้อมูล</span><span class="value">{{ selectedDataset.stat_standard || '-' }}</span></div>
                      <div class="row"><span class="label">สถิติทางการ</span><span class="value">{{ selectedDataset.stat_official || '-' }}</span></div>
                    </template>

                    <!-- GEOSPATIAL SPECIFIC -->
                    <template v-if="selectedDataset?.dataset_type === 'geospatial'">
                      <div class="row-group-title text-[var(--primary)] border-emerald-200 mt-4">ข้อมูลภูมิสารสนเทศเชิงพื้นที่</div>
                      <div class="row"><span class="label">ชื่อชุดข้อมูลภูมิศาสตร์</span><span class="value">{{ selectedDataset.geo_dataset_name || '-' }}</span></div>
                      <div class="row"><span class="label">มาตราส่วน</span><span class="value">{{ selectedDataset.geo_scale || '-' }}</span></div>
                      <div class="row"><span class="label">ขอบเขต (W, E, N, S)</span><span class="value font-mono">{{ selectedDataset.geo_west_bound || '-' }}, {{ selectedDataset.geo_east_bound || '-' }}, {{ selectedDataset.geo_north_bound || '-' }}, {{ selectedDataset.geo_south_bound || '-' }}</span></div>
                      <div class="row"><span class="label">ความถูกต้องของตำแหน่ง</span><span class="value">{{ selectedDataset.geo_position_accuracy || '-' }}</span></div>
                      <div class="row"><span class="label">เวลาอ้างอิง</span><span class="value">{{ selectedDataset.geo_reference_time || '-' }}</span></div>
                      <div class="row"><span class="label">วันที่เผยแพร่ข้อมูล</span><span class="value">{{ selectedDataset.geo_published_date || '-' }}</span></div>
                    </template>
                    
                    <div class="row-group-title mt-4">เทคนิคและติดต่อ</div>
                    <div class="row"><span class="label">อีเมลติดต่อ</span><span class="value">{{ selectedDataset?.contact_email }}</span></div>
                    <div class="row"><span class="label">วัตถุประสงค์</span><span class="value">{{ selectedDataset?.objective_type }}</span></div>
                    <div class="row"><span class="label">แหล่งที่มา</span><span class="value">{{ selectedDataset?.data_source }}</span></div>
                    <div class="row"><span class="label">หน่วยจัดเก็บเล็กสุด</span><span class="value">{{ selectedDataset?.smallest_unit }}</span></div>
                    <div class="row"><span class="label">ภาษาที่ใช้</span><span class="value">{{ selectedDataset?.languages }}</span></div>
                    <div class="row"><span class="label">แท็ก</span><span class="value">
                      <span v-for="tag in selectedDataset?.tags.split(',')" :key="tag" class="tag-inline">{{ tag.trim() }}</span>
                    </span></div>
                  </div>
                </div>
                <aside class="info-sidebar">
                  <!-- If has access, show download options -->
                  <div v-if="selectedDataset?.has_access" class="action-card">
                    <h4>ดาวน์โหลดข้อมูล</h4>
                    <p>ดาวน์โหลดไฟล์ข้อมูลต้นฉบับในรูปแบบต่างๆ</p>
                    <div class="download-buttons">
                      <button class="btn-download csv" @click="openPreview('CSV')">CSV</button>
                      <button class="btn-download xls" @click="openPreview('Excel')">Excel</button>
                    </div>
                    <button v-if="selectedDataset?.file_path" class="btn-primary-outline w-full mt-4" @click="openPreview('ไฟล์แนบต้นฉบับ')">ดาวน์โหลดไฟล์แนบ</button>
                  </div>
                  
                  <!-- If does NOT have access, show Request Access form -->
                  <div v-else class="action-card">
                    <h4 style="display:flex;align-items:center;gap:6px;">🔒 จำกัดสิทธิ์การใช้งาน</h4>
                    <p style="font-size:0.875rem;color:#64748b;margin-bottom:16px;">ชุดข้อมูลนี้จำกัดสิทธิ์ โปรดส่งคำขออนุญาตเพื่อดาวน์โหลดข้อมูลหรือใช้ API</p>
                    
                    <!-- If no request yet or rejected and user clicks request again -->
                    <div v-if="!selectedDataset?.permission_status" class="request-access-form-wrapper">
                      <!-- Field selector -->
                      <div class="form-group mb-4" style="margin-bottom: 12px;">
                        <label class="font-semibold block mb-1 text-slate-700" style="font-size:0.85rem; display:block; margin-bottom: 4px;">ฟิลด์ข้อมูลที่ต้องการ *</label>
                        <div class="field-checkbox-list" style="max-height:120px;overflow-y:auto;border:1px solid #e2e8f0;border-radius:6px;padding:8px;background:#f8fafc; text-align:left;">
                          <label v-for="field in selectedDataset?.api_response_fields" :key="field" class="flex items-center gap-2 mb-1 cursor-pointer" style="display:flex;align-items:center;gap:6px;font-size:0.85rem; margin-bottom: 4px; cursor:pointer;">
                            <input type="checkbox" :value="field" v-model="requestForm.fields">
                            <span>{{ field }}</span>
                          </label>
                        </div>
                      </div>
                      
                      <!-- Reason input -->
                      <div class="form-group mb-4" style="margin-bottom: 12px;">
                        <label class="font-semibold block mb-1 text-slate-700" style="font-size:0.85rem; display:block; margin-bottom: 4px;">วัตถุประสงค์ในการขอเข้าถึง *</label>
                        <textarea v-model="requestForm.reason" rows="2" style="width:100%;border:1px solid #e2e8f0;border-radius:6px;padding:8px;font-size:0.85rem;resize:none; box-sizing:border-box;" placeholder="ระบุเหตุผลและวัตถุประสงค์การใช้งาน..."></textarea>
                      </div>

                      <div v-if="reqError" style="color:#e11d48;font-size:0.75rem;margin-bottom:8px;text-align:left;">{{ reqError }}</div>
                      <div v-if="reqSuccess" style="color:#16a34a;font-size:0.75rem;margin-bottom:8px;text-align:left;">{{ reqSuccess }}</div>

                      <button class="btn-primary w-full" style="padding:10px;font-size:0.9rem;width:100%;" :disabled="isSubmittingReq" @click="submitPermissionRequest">
                        {{ isSubmittingReq ? 'กำลังส่งคำขอ...' : 'ส่งคำขอเข้าถึงข้อมูล' }}
                      </button>
                    </div>

                    <!-- If status is Pending -->
                    <div v-else-if="selectedDataset?.permission_status === 'Pending'" style="background:#fef3c7; color:#92400e; padding:12px; border-radius:8px; border:1px solid #fde68a; text-align:center;">
                      <p style="font-weight:bold; margin:0 0 4px 0; font-size:0.875rem;">⏳ รอการอนุมัติสิทธิ์ (Pending Approval)</p>
                      <p style="font-size:0.75rem; margin:0; color:#b45309;">คำขอเข้าถึงข้อมูลอยู่ระหว่างการพิจารณาโดยผู้ดูแลระบบ</p>
                    </div>

                    <!-- If status is Rejected -->
                    <div v-else-if="selectedDataset?.permission_status === 'Rejected'" style="background:#fee2e2; color:#991b1b; padding:12px; border-radius:8px; border:1px solid #fecaca; text-align:center;">
                      <p style="font-weight:bold; margin:0 0 4px 0; font-size:0.875rem;">❌ ปฏิเสธการขอสิทธิ์ (Rejected)</p>
                      <p style="font-size:0.75rem; margin:0 0 8px 0; color:#b91c1c;">คำขอเข้าถึงข้อมูลของคุณถูกปฏิเสธ</p>
                      <button class="btn-primary-outline w-full" style="padding:6px; font-size:0.75rem; width:100%;" @click="selectedDataset.permission_status = null">ส่งคำขอใหม่อีกครั้ง</button>
                    </div>
                  </div>
                </aside>
              </div>
            </div>

            <!-- Dictionary Tab -->
            <div v-if="activeTab === 'dictionary'" class="tab-content transition-fade">
              <table class="dictionary-table">
                <thead>
                  <tr>
                    <th>ลำดับ</th>
                    <th>ชื่อฟิลด์</th>
                    <th>ประเภท</th>
                    <th>คำอธิบาย</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(field, index) in selectedDataset?.api_response_fields" :key="field">
                    <td>{{ index + 1 }}</td>
                    <td>{{ field }}</td>
                    <td>VARCHAR / String</td>
                    <td>ฟิลด์ข้อมูลที่ให้บริการสำหรับชุดข้อมูลนี้</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Visual Tab -->
            <div v-if="activeTab === 'visual'" class="tab-content transition-fade" style="padding: 0;">
              <!-- If does not have access, hide dashboard visualizer -->
              <div v-if="!selectedDataset?.has_access" class="p-10 text-center text-slate-600 bg-slate-50 border border-slate-200 rounded-xl m-4" style="padding: 40px; text-align: center;">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="height: 64px; width: 64px; margin: 0 auto 16px auto; color: #94a3b8;">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <p class="font-bold text-lg mb-1" style="font-weight: bold; font-size: 1.125rem; margin-bottom: 4px;">แดชบอร์ดถูกจำกัดสิทธิ์</p>
                <p class="text-sm mb-4" style="font-size: 0.875rem; color: #64748b; margin-bottom: 16px;">โปรดส่งคำขอเข้าถึงข้อมูลเพื่อเรียกดูแดชบอร์ดของชุดข้อมูลนี้</p>
                <button class="px-6 py-2 bg-slate-800 text-white rounded-lg font-medium hover:bg-slate-700 transition-colors" style="padding: 8px 24px; background: #1e293b; color: white; border: none; border-radius: 8px; font-weight: 500; cursor: pointer;" @click="activeTab = 'info'">
                  ส่งคำขอเข้าถึงข้อมูล
                </button>
              </div>
              <div v-else-if="selectedDataset?.external_dashboard_url" class="dashboard-container">
                <div class="dashboard-actions mb-4 p-4 flex justify-between items-center bg-slate-50 border-b border-slate-100">
                  <div class="flex items-center gap-2 text-slate-600 font-medium">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <span>External Dashboard</span>
                  </div>
                  <a :href="selectedDataset.external_dashboard_url" target="_blank" class="flex items-center gap-2 px-4 py-2 bg-[var(--primary)] text-white rounded-lg hover:bg-emerald-700 transition-all font-semibold text-sm shadow-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    เปิดในหน้าต่างใหม่
                  </a>
                </div>
                <div class="iframe-wrapper" style="height: 60vh; position: relative; background: #f8fafc;">
                  <iframe 
                    :src="selectedDataset.external_dashboard_url" 
                    width="100%" 
                    height="100%" 
                    frameborder="0" 
                    allowfullscreen
                    style="border: none;"
                  ></iframe>
                </div>
              </div>
              <div v-else class="dashboard-mockup-container bg-slate-50 p-6" style="height: 600px; overflow-y: auto; border-radius: 0 0 1rem 1rem;">
                <!-- Mockup Header Stats -->
                <div class="grid grid-cols-3 gap-4 mb-6" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                  <div class="stat-card p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                    <p class="text-xs text-slate-500 font-bold uppercase mb-1">จำนวนประชากรทั้งหมด</p>
                    <p class="text-2xl font-black text-slate-800">5.47M <span class="text-xs text-emerald-500 font-normal">+2.4%</span></p>
                  </div>
                  <div class="stat-card p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                    <p class="text-xs text-slate-500 font-bold uppercase mb-1">ความหนาแน่นเฉลี่ย</p>
                    <p class="text-2xl font-black text-slate-800">3,620 <span class="text-xs text-slate-400 font-normal">คน/ตร.กม.</span></p>
                  </div>
                  <div class="stat-card p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                    <p class="text-xs text-slate-500 font-bold uppercase mb-1">อัตราการเติบโต</p>
                    <p class="text-2xl font-black text-[var(--primary)]">0.85% <span class="text-xs text-[var(--primary)] font-normal">Slightly down</span></p>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                  <!-- Main Bar Chart Mockup -->
                  <div class="chart-box p-4 bg-white rounded-xl border border-slate-100 shadow-sm col-span-2" style="grid-column: span 2;">
                    <p class="text-sm font-bold text-slate-700 mb-4">สถิติการใช้งานชุดข้อมูล L2E (Top 10)</p>
                    <div class="flex items-end gap-2" style="display: flex; align-items: flex-end; gap: 0.5rem; height: 180px; padding-bottom: 20px; border-bottom: 1px solid #f1f5f9;">
                      <div class="bg-pink-100 hover:bg-pink-500 transition-colors rounded-t" style="flex: 1; height: 90%; cursor: pointer;" title="กทม."></div>
                      <div class="bg-pink-100 hover:bg-pink-500 transition-colors rounded-t" style="flex: 1; height: 45%;" title="สมุทรปราการ"></div>
                      <div class="bg-pink-100 hover:bg-pink-500 transition-colors rounded-t" style="flex: 1; height: 40%;" title="นนทบุรี"></div>
                      <div class="bg-pink-500 rounded-t" style="flex: 1; height: 35%;" title="ชลบุรี"></div>
                      <div class="bg-pink-100 hover:bg-pink-500 transition-colors rounded-t" style="flex: 1; height: 65%;" title="เชียงใหม่"></div>
                      <div class="bg-pink-100 hover:bg-pink-500 transition-colors rounded-t" style="flex: 1; height: 50%;" title="นครราชสีมา"></div>
                      <div class="bg-pink-100 hover:bg-pink-500 transition-colors rounded-t" style="flex: 1; height: 30%;" title="ขอนแก่น"></div>
                      <div class="bg-pink-100 hover:bg-pink-500 transition-colors rounded-t" style="flex: 1; height: 25%;" title="ภูเก็ต"></div>
                      <div class="bg-pink-100 hover:bg-pink-500 transition-colors rounded-t" style="flex: 1; height: 55%;" title="สงขลา"></div>
                      <div class="bg-pink-100 hover:bg-pink-500 transition-colors rounded-t" style="flex: 1; height: 20%;" title="ระยอง"></div>
                    </div>
                    <div class="flex justify-between mt-2 text-[10px] text-slate-400 font-medium" style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 10px; color: #94a3b8;">
                      <span>กทม.</span><span>ชลบุรี</span><span>ขอนแก่น</span><span>ระยอง</span>
                    </div>
                  </div>

                  <!-- Pie Chart Mockup -->
                  <div class="chart-box p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                    <p class="text-sm font-bold text-slate-700 mb-4">สัดส่วนตามช่วงวัย</p>
                    <div class="relative flex justify-center items-center" style="display: flex; justify-content: center; align-items: center; height: 150px;">
                      <!-- Mock Donut Chart using SVG -->
                      <svg viewBox="0 0 36 36" style="height: 120px; width: 120px;">
                        <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="#f1f5f9" stroke-width="3"></circle>
                        <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="var(--primary)" stroke-width="3" stroke-dasharray="40 60" stroke-dashoffset="25"></circle>
                        <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="var(--mso-accent)" stroke-width="3" stroke-dasharray="25 75" stroke-dashoffset="85"></circle>
                        <circle cx="18" cy="18" r="15.915" fill="transparent" stroke="var(--mso-pink-dark)" stroke-width="3" stroke-dasharray="35 65" stroke-dashoffset="60"></circle>
                      </svg>
                      <div class="absolute text-center" style="position: absolute;">
                        <p class="text-[10px] font-bold text-slate-400 uppercase leading-none">วัยทำงาน</p>
                        <p class="text-lg font-black text-slate-700">40%</p>
                      </div>
                    </div>
                    <div class="mt-4 space-y-1" style="margin-top: 1rem; display: flex; flex-direction: column; gap: 0.25rem;">
                      <div class="flex items-center justify-between text-[10px]" style="display: flex; justify-content: space-between; font-size: 10px;">
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[var(--primary)]"></span> วัยทำงาน</span>
                        <span class="font-bold">40%</span>
                      </div>
                      <div class="flex items-center justify-between text-[10px]" style="display: flex; justify-content: space-between; font-size: 10px;">
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[var(--mso-pink-dark)]"></span> วัยเด็ก</span>
                        <span class="font-bold">35%</span>
                      </div>
                      <div class="flex items-center justify-between text-[10px]" style="display: flex; justify-content: space-between; font-size: 10px;">
                        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[var(--mso-accent)]"></span> ผู้สูงอายุ</span>
                        <span class="font-bold">25%</span>
                      </div>
                    </div>
                  </div>

                  <!-- Line Chart Mockup -->
                  <div class="chart-box p-4 bg-white rounded-xl border border-slate-100 shadow-sm">
                    <p class="text-sm font-bold text-slate-700 mb-4">แนวโน้มประชากร (2560 - 2566)</p>
                    <div class="relative overflow-hidden" style="height: 150px; background-image: linear-gradient(to top, #f8fafc 1px, transparent 1px), linear-gradient(to right, #f8fafc 1px, transparent 1px); background-size: 20px 20px;">
                      <!-- Mock Line using SVG -->
                      <svg viewBox="0 0 200 100" preserveAspectRatio="none" style="width: 100%; height: 100%;">
                        <path d="M0,80 Q25,75 50,60 T100,50 T150,30 T200,20" fill="none" stroke="var(--primary)" stroke-width="3" stroke-linecap="round"></path>
                        <path d="M0,80 Q25,75 50,60 T100,50 T150,30 T200,20 L200,100 L0,100 Z" fill="url(#lineGradient)" opacity="0.1"></path>
                        <defs>
                          <linearGradient id="lineGradient" x1="0" x2="0" y1="0" y2="1">
                            <stop offset="0%" stop-color="var(--primary)"></stop>
                            <stop offset="100%" stop-color="transparent"></stop>
                          </linearGradient>
                        </defs>
                        <!-- Dots -->
                        <circle cx="50" cy="60" r="4" fill="var(--primary)" stroke="white" stroke-width="2"></circle>
                        <circle cx="150" cy="30" r="4" fill="var(--primary)" stroke="white" stroke-width="2"></circle>
                      </svg>
                    </div>
                    <div class="flex justify-between mt-2 text-[10px] text-slate-400 font-medium" style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 10px; color: #94a3b8;">
                      <span>2560</span><span>2563</span><span>2566</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- API Tab -->
            <div v-if="activeTab === 'api'" class="tab-content transition-fade">
              <!-- If does not have access, hide API info -->
              <div v-if="!selectedDataset?.has_access" class="p-10 text-center border border-slate-200 rounded-xl bg-slate-50 text-slate-600" style="padding: 40px; text-align: center;">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="height: 64px; width: 64px; margin: 0 auto 16px auto; color: #94a3b8;">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <p class="font-bold text-lg mb-1" style="font-weight: bold; font-size: 1.125rem; margin-bottom: 4px;">ข้อมูล API ถูกจำกัดสิทธิ์</p>
                <p class="text-sm mb-4" style="font-size: 0.875rem; color: #64748b; margin-bottom: 16px;">โปรดส่งคำขอเข้าถึงข้อมูลก่อน จึงจะสามารถเรียกดูหรือใช้งาน API ได้</p>
                <button class="px-6 py-2 bg-slate-800 text-white rounded-lg font-medium hover:bg-slate-700 transition-colors" style="padding: 8px 24px; background: #1e293b; color: white; border: none; border-radius: 8px; font-weight: 500; cursor: pointer;" @click="activeTab = 'info'">
                  ส่งคำขอเข้าถึงข้อมูล
                </button>
              </div>
              <div v-else-if="selectedDataset?.api_enabled" class="api-info border border-slate-200 rounded-xl overflow-hidden shadow-sm bg-white">
                <div class="api-header bg-slate-50 border-b border-slate-200 p-4 flex items-center justify-between">
                  <div class="flex items-center gap-3 w-full">
                    <span class="method get px-3 py-1 bg-emerald-100 text-emerald-700 font-bold rounded-md text-sm">GET</span>
                    <input 
                      type="text" 
                      readonly 
                      :value="apiUrl" 
                      class="url flex-1 bg-white border border-slate-200 rounded px-3 py-1.5 font-mono text-sm text-slate-600 focus:outline-none focus:border-emerald-500 transition-colors"
                    >
                  </div>
                  <div class="flex items-center gap-2 ml-4 shrink-0">
                    <button v-if="detectedApiKey" @click="copyApiUrl" class="btn-copy flex items-center gap-2 px-3 py-1.5 bg-slate-800 text-white rounded hover:bg-slate-700 transition-colors text-sm font-medium">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      คัดลอก
                    </button>
                    <button class="btn-copy flex items-center gap-2 px-3 py-1.5 bg-[var(--primary)] text-white rounded hover:bg-emerald-700 transition-colors text-sm font-medium">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      คู่มือ API
                    </button>
                  </div>
                </div>
                
                <div v-if="!detectedApiKey && user.username !== 'testadmin'" class="p-10 text-center border-b border-emerald-100 bg-emerald-50 text-emerald-800">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <p class="font-bold text-lg mb-1">สิทธิการเข้าถึง API ถูกจำกัด</p>
                  <p class="text-sm mb-6 max-w-md mx-auto">โปรดสร้าง API Key ที่หน้าจัดการสิทธิ์ก่อน จึงจะสามารถใช้งานชุดข้อมูลนี้ผ่านระบบภายนอกได้</p>
                  <router-link to="/api-management" class="inline-block px-6 py-2 bg-[var(--primary)] text-white rounded-lg font-medium hover:bg-emerald-700 transition-colors shadow-md">
                    ไปหน้าจัดการ API Key
                  </router-link>
                </div>

                <div v-else class="json-preview p-0">
                  <div class="json-header px-4 py-2 bg-slate-800 text-slate-300 text-sm font-mono flex justify-between items-center">
                    <span>Example JSON Response Payload</span>
                  </div>
                  <pre class="m-0 p-4 bg-slate-900 text-emerald-400 font-mono text-sm overflow-x-auto"><code>{
  "total_rows": 2,
  "offset": 0,
  "rows": [
    {
      "id": "{{ selectedDataset?.dataset_id }}-row1",
      "data": {
        "value": 100.50,
        "updated_at": "2024-03-30T00:00:00Z"
      }
    },
    {
      "id": "{{ selectedDataset?.dataset_id }}-row2",
      "data": {
        "value": 250.75,
        "updated_at": "2024-03-30T00:00:00Z"
      }
    }
  ]
}</code></pre>
                </div>
              </div>

              <!-- Not Enabled Warning -->
              <div v-else class="text-center p-8 border border-orange-200 rounded-xl bg-orange-50 text-orange-800 shadow-sm mt-4 mx-4 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <h3 class="text-lg font-bold mb-2">ชุดข้อมูลนี้ยังไม่เปิดให้บริการผ่าน API</h3>
                <p class="text-sm text-orange-700/80 max-w-sm mx-auto">เพื่อความปลอดภัย โปรดติดต่อผู้ดูแลระบบ หรือไปที่เมนู <router-link to="/dataset-config" class="font-bold underline">ตั้งค่าชุดข้อมูล</router-link> เพื่อเปิดใช้งาน API Access สำหรับชุดข้อมูลนี้ก่อน</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Download Preview Modal -->
    <Teleport to="body">
      <div v-if="isPreviewModalOpen" class="modal-overlay" style="z-index: 1050;" @click.self="closePreview">
        <div class="modal-container" style="max-width: 800px; padding: 0;">
          <header class="modal-header" style="border-bottom: 1px solid #e2e8f0; padding: 20px 24px;">
            <div class="title-with-badge">
              <h2 style="font-size: 1.25rem; font-weight: 700; color: #1e293b;">ตัวอย่างข้อมูลก่อนดาวน์โหลด ({{ previewType }})</h2>
              <span class="id-badge" style="background-color: #f1f5f9; color: #64748b; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">{{ selectedDataset?.dataset_id }}</span>
            </div>
            <button class="btn-close" @click="closePreview" style="background: none; border: none; color: #94a3b8; cursor: pointer;">
              <svg xmlns="http://www.w3.org/2000/svg" style="height: 24px; width: 24px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </header>
          
          <div class="modal-body" style="padding: 0; max-height: 400px; overflow-y: auto;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.875rem;">
              <thead style="background-color: #f8fafc; position: sticky; top: 0;">
                <tr>
                  <th style="padding: 12px 24px; border-bottom: 1px solid #e2e8f0; color: #475569; font-weight: 600;">รหัสรายการ</th>
                  <th style="padding: 12px 24px; border-bottom: 1px solid #e2e8f0; color: #475569; font-weight: 600;">พื้นที่ / จังหวัด</th>
                  <th style="padding: 12px 24px; border-bottom: 1px solid #e2e8f0; color: #475569; font-weight: 600;">จำนวน (คน)</th>
                  <th style="padding: 12px 24px; border-bottom: 1px solid #e2e8f0; color: #475569; font-weight: 600;">ปีที่สำรวจ</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #f1f5f9; background-color: white; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='white'">
                  <td style="padding: 12px 24px; color: #1e293b; font-weight: 500;">001</td>
                  <td style="padding: 12px 24px; color: #475569;">กรุงเทพมหานคร</td>
                  <td style="padding: 12px 24px; color: #475569;">5,476,120</td>
                  <td style="padding: 12px 24px; color: #475569;">2566</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9; background-color: white; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='white'">
                  <td style="padding: 12px 24px; color: #1e293b; font-weight: 500;">002</td>
                  <td style="padding: 12px 24px; color: #475569;">สมุทรปราการ</td>
                  <td style="padding: 12px 24px; color: #475569;">1,350,540</td>
                  <td style="padding: 12px 24px; color: #475569;">2566</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9; background-color: white; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='white'">
                  <td style="padding: 12px 24px; color: #1e293b; font-weight: 500;">003</td>
                  <td style="padding: 12px 24px; color: #475569;">นนทบุรี</td>
                  <td style="padding: 12px 24px; color: #475569;">1,280,000</td>
                  <td style="padding: 12px 24px; color: #475569;">2566</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9; background-color: white; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='white'">
                  <td style="padding: 12px 24px; color: #1e293b; font-weight: 500;">004</td>
                  <td style="padding: 12px 24px; color: #475569;">ปทุมธานี</td>
                  <td style="padding: 12px 24px; color: #475569;">1,170,900</td>
                  <td style="padding: 12px 24px; color: #475569;">2566</td>
                </tr>
                <tr style="background-color: white; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#f8fafc'" onmouseout="this.style.backgroundColor='white'">
                  <td style="padding: 12px 24px; color: #1e293b; font-weight: 500;">005</td>
                  <td style="padding: 12px 24px; color: #475569;">เชียงใหม่</td>
                  <td style="padding: 12px 24px; color: #475569;">1,780,210</td>
                  <td style="padding: 12px 24px; color: #475569;">2566</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div style="padding: 16px 24px; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 12px; background-color: white; border-radius: 0 0 16px 16px;">
            <button @click="closePreview" style="padding: 8px 16px; border: none; background: none; color: #64748b; font-weight: 600; cursor: pointer; border-radius: 8px; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='#f1f5f9'" onmouseout="this.style.backgroundColor='transparent'">
              ยกเลิก
            </button>
            <button @click="closePreview" style="padding: 8px 24px; background-color: var(--mso-accent); color: white; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: 0 2px 4px rgba(233, 30, 99, 0.2); transition: background-color 0.2s;" onmouseover="this.style.backgroundColor='var(--primary)'" onmouseout="this.style.backgroundColor='var(--mso-accent)'">
              <svg xmlns="http://www.w3.org/2000/svg" style="height: 16px; width: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              ยืนยันการดาวน์โหลด {{ previewType }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.catalog-layout {
  display: flex;
  background-color: #fcfcfc;
  min-height: 100vh;
}

.catalog-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.catalog-header {
  padding: 40px 64px 20px;
  background-color: white;
}

.header-titles h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.header-titles p {
  color: #64748b;
  font-size: 0.9375rem;
  margin-bottom: 32px;
}

.search-main-container {
  max-width: 100%;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 4px 4px 4px 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  transition: border-color 0.2s;
}

.search-input-wrapper:focus-within {
  border-color: var(--primary);
}

.search-icon {
  width: 20px;
  height: 20px;
  color: #94a3b8;
}

.search-input-wrapper input {
  flex: 1;
  border: none;
  background: none;
  outline: none;
  padding: 12px;
  font-size: 1rem;
  color: #1e293b;
}

.btn-search {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-search:hover {
  background-color: var(--primary-hover);
}

.btn-add-dataset {
  background-color: var(--mso-accent);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-left: 12px;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-add-dataset:hover {
  background-color: var(--primary);
  transform: translateY(-1px);
}

.catalog-container {
  display: flex;
  padding: 24px 64px;
  gap: 32px;
}

.filter-sidebar {
  width: 280px;
  flex-shrink: 0;
}

.filter-card {
  background-color: white;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  padding: 24px;
  position: sticky;
  top: 88px;
}

.filter-section {
  margin-bottom: 32px;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filter-header h3 {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #1e293b;
}

.btn-link {
  background: none;
  border: none;
  color: var(--mso-accent);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.filter-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.875rem;
  color: #475569;
}

.filter-checkbox input {
  display: none;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid #e2e8f0;
  border-radius: 4px;
  margin-right: 12px;
  position: relative;
  transition: all 0.2s;
}

.filter-checkbox input:checked + .checkbox-custom {
  background-color: var(--primary);
  border-color: var(--primary);
}

.filter-checkbox input:checked + .checkbox-custom::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 2px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.label-text {
  flex: 1;
}

.count {
  color: #94a3b8;
  font-size: 0.8125rem;
}

.format-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.format-btn {
  background-color: white;
  border: 1px solid #e2e8f0;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.format-btn.active {
  background-color: var(--mso-pink-dark);
  color: var(--primary);
  border-color: #bbf7d0;
}

.badge.access-restricted { background-color: #fef2f2; color: #dc2626; border-color: #fecaca; }

.badge.format-api-public { background-color: #e0e7ff; color: #4338ca; border-color: #c7d2fe; }
.badge.format-api-private { background-color: var(--mso-pink-dark); color: var(--primary-hover); border-color: var(--mso-pink-dark); }
.badge.format-api-scope { background-color: #ffedd5; color: #c2410c; border-color: #fed7aa; }

.results-section {
  flex: 1;
}

.results-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.results-toolbar p {
  font-size: 0.9375rem;
  color: #64748b;
}

.sort-control {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.875rem;
  color: #64748b;
}

.sort-control select {
  border: 1px solid #e2e8f0;
  padding: 6px 12px;
  border-radius: 8px;
  background-color: white;
  outline: none;
}

.datasets-list-vertical {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.ds-horizontal-card {
  display: block;
  text-decoration: none;
  color: inherit;
  background-color: white;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.2s;
  cursor: pointer;
}

.ds-horizontal-card:hover {
  border-color: var(--primary);
  box-shadow: 0 8px 16px rgba(0,0,0,0.05);
}

.ds-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.ds-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.btn-favorite {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  transition: all 0.2s;
}

.btn-favorite:hover {
  transform: scale(1.1);
  color: #eab308;
}

.btn-favorite.is-active {
  color: #eab308;
}

.ds-description {
  font-size: 0.9375rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 20px;
  max-width: 800px;
}

.ds-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ds-badges {
  display: flex;
  gap: 12px;
}

.badge {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}

.access-open {
  background-color: var(--mso-pink-dark);
  color: var(--mso-accent);
}

.format {
  background-color: #f1f5f9;
  color: var(--primary);
}

.ds-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.8125rem;
  color: #94a3b8;
}

.separator {
  opacity: 0.5;
}

.no-results {
  text-align: center;
  padding: 80px 0;
  color: #94a3b8;
}

.no-results-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.no-results h3 {
  font-size: 1.25rem;
  color: #1e293b;
  margin-bottom: 8px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--primary);
  color: var(--primary);
  background-color: var(--mso-pink-dark);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f1f5f9;
}

.page-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: white;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn.active {
  background-color: var(--primary);
  color: white;
  border-color: var(--primary);
}

.dots {
  color: #94a3b8;
}

/* Modal Styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 40px;
}

.modal-container {
  background-color: white;
  width: 100%;
  max-width: 1000px;
  max-height: 90vh;
  border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalScaleUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalScaleUp {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.modal-header {
  padding: 32px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.id-badge {
  background-color: #f1f5f9;
  color: #64748b;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.btn-close {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-close:hover {
  background-color: #f1f5f9;
  color: #ef4444;
}

.modal-tabs {
  display: flex;
  padding: 0 32px;
  background-color: #fcfcfc;
  border-bottom: 1px solid #f1f5f9;
  gap: 24px;
}

.modal-tabs button {
  background: none;
  border: none;
  padding: 20px 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  position: relative;
  transition: color 0.2s;
}

.modal-tabs button:hover {
  color: var(--primary);
}

.modal-tabs button.active {
  color: var(--primary);
}

.modal-tabs button.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: var(--primary);
  border-radius: 3px 3px 0 0;
}

.modal-body {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 40px;
}

.info-main h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #334155;
  margin-bottom: 16px;
}

.info-main p {
  line-height: 1.7;
  color: #64748b;
  margin-bottom: 32px;
}

.metadata-table {
  display: flex;
  flex-direction: column;
  gap: 0;
  background-color: #fff;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  overflow: hidden;
}

.row-group-title {
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 20px 6px;
  background-color: var(--mso-pink-dark);
  border-bottom: 1px solid #e2e8f0;
}

.metadata-table .row {
  display: grid;
  grid-template-columns: 180px 1fr;
  border-bottom: 1px solid #f1f5f9;
}

.metadata-table .row:last-child {
  border-bottom: none;
}

.metadata-table .label {
  background-color: #f8fafc;
  padding: 10px 20px;
  font-weight: 600;
  color: #64748b;
  font-size: 0.8125rem;
  border-right: 1px solid #f1f5f9;
}

.metadata-table .value {
  padding: 10px 20px;
  color: #1e293b;
  font-size: 0.8125rem;
}

.tag-inline {
  display: inline-block;
  background-color: #f1f5f9;
  color: #475569;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  margin-right: 4px;
  margin-bottom: 4px;
}

.action-card {
  background-color: #f8fafc;
  border-radius: 16px;
  padding: 24px;
}

.action-card h4 {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.action-card p {
  font-size: 0.8125rem;
  color: #64748b;
  margin-bottom: 20px;
}

.download-buttons {
  display: flex;
  gap: 12px;
}

.btn-download {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background-color: white;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-download:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.btn-primary-outline {
  background: none;
  border: 1.5px solid var(--primary);
  color: var(--primary);
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary-outline:hover {
  background-color: var(--primary);
  color: white;
}

.dictionary-table {
  width: 100%;
  border-collapse: collapse;
}

.dictionary-table th {
  text-align: left;
  padding: 16px;
  background-color: #f8fafc;
  color: #475569;
  font-weight: 700;
  font-size: 0.875rem;
  border-bottom: 2px solid #f1f5f9;
}

.dictionary-table td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
  color: #1e293b;
}

.modal-tabs {
  display: flex;
  padding: 0 40px;
  background-color: white;
  border-bottom: 1px solid #f1f5f9;
}

.transition-fade {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.scrollbar-custom::-webkit-scrollbar {
  width: 8px;
}

.scrollbar-custom::-webkit-scrollbar-track {
  background: #f8fafc;
}

.scrollbar-custom::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.scrollbar-custom::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* ===== RESPONSIVE: Tablet ===== */
@media (max-width: 1024px) {
  .catalog-container {
    flex-direction: column;
    padding: 24px 32px;
  }
  .filter-sidebar {
    width: 100%;
  }
  .catalog-header {
    padding: 40px 32px 20px;
  }
  .info-grid {
    grid-template-columns: 1fr;
  }
}

/* ===== RESPONSIVE: Mobile ===== */
@media (max-width: 768px) {
  .catalog-header {
    padding: 20px 16px 16px;
  }

  .header-titles h1 {
    font-size: 1.5rem;
  }

  .header-titles p {
    font-size: 0.85rem;
    margin-bottom: 16px;
  }

  .search-input-wrapper {
    flex-direction: column;
    gap: 8px;
    padding: 8px;
    background: transparent;
    border: none;
    box-shadow: none;
  }
  .search-input-wrapper input {
    width: 100%;
    background-color: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
  }
  .search-input-wrapper .btn-search,
  .search-input-wrapper .btn-add-dataset {
    width: 100%;
    margin: 0;
  }
  .search-input-wrapper > * {
    width: 100%;
  }


  .search-icon {
    display: none;
  }

  .search-input-wrapper input {
    width: 100%;
    flex: unset;
    padding: 10px 12px;
    font-size: 0.9rem;
  }

  .btn-search {
    flex: 1;
    padding: 10px 16px;
    font-size: 0.875rem;
    text-align: center;
  }

  .btn-add-dataset {
    flex: 1;
    margin-left: 0;
    padding: 10px 16px;
    font-size: 0.875rem;
    text-align: center;
  }

  .catalog-container {
    flex-direction: column;
    padding: 16px;
    gap: 16px;
  }

  .filter-sidebar {
    width: 100%;
  }

  .filter-card {
    padding: 16px;
    border-radius: 12px;
  }

  .filter-section h3 {
    font-size: 0.9rem;
  }

  .format-tags {
    gap: 6px;
  }

  .format-tag {
    font-size: 0.7rem;
    padding: 4px 10px;
  }

  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .sort-options {
    width: 100%;
  }

  .sort-options select {
    width: 100%;
  }

  .dataset-card {
    padding: 16px;
  }

  .dataset-title {
    font-size: 1rem;
  }

  .dataset-desc {
    font-size: 0.825rem;
  }

  .dataset-tags {
    flex-wrap: wrap;
    gap: 6px;
  }

  .dataset-meta {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .pagination {
    gap: 4px;
  }

  .pagination button {
    min-width: 36px;
    height: 36px;
    font-size: 0.85rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .modal-content {
    width: 95vw;
    max-height: 85vh;
    padding: 16px;
    margin: 16px;
  }

  .modal-header h2 {
    font-size: 1.1rem;
  }

  .tab-nav {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    gap: 0;
  }

  .tab-nav button {
    white-space: nowrap;
    font-size: 0.8rem;
    padding: 8px 12px;
  }
}

/* ===== RESPONSIVE: Small Phone ===== */
@media (max-width: 480px) {
  .catalog-header {
    padding: 16px 12px 12px;
  }

  .header-titles h1 {
    font-size: 1.25rem;
  }

  .catalog-container {
    padding: 12px;
  }

  .dataset-card {
    padding: 12px;
    border-radius: 10px;
  }

  .btn-search,
  .btn-add-dataset {
    padding: 8px 12px;
    font-size: 0.8rem;
  }
}
</style>
