<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData } from '../utils/api';

const route = useRoute();
const router = useRouter();

const activeTab = ref('info');
const isLoading = ref(true);
const errorMessage = ref('');

const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));
const selectedDataset = ref(null);
const apiBaseUrl = computed(() => `${window.location.origin}/dataapi/api/v1/`);
const userApiKey = computed(() => user.value.apikey || '[YOUR_API_KEY]');
const dashboardRequestForm = ref({
  reason: '',
  mouFile: null,
  mouFileName: '',
  isSubmitting: false,
  error: '',
  success: ''
});

const apiRequestForm = ref({
  fields: [],
  reason: '',
  mouFile: null,
  mouFileName: '',
  isSubmitting: false,
  error: '',
  success: ''
});

const customApiEndpoints = ref([]);
const apiClones = ref([]);

const combinedApis = computed(() => {
  let apis = [];
  if (selectedDataset.value && (selectedDataset.value.api_enabled === 1 || selectedDataset.value.api_enabled === true || selectedDataset.value.api_enabled === '1')) {
    apis.push({
      api_type: selectedDataset.value.api_type || 'general',
      api_endpoint: selectedDataset.value.api_endpoint || selectedDataset.value.dataset_id,
      service_name: selectedDataset.value.title,
      api_response_fields: selectedDataset.value.api_response_fields || []
    });
  }
  if (apiClones.value && apiClones.value.length > 0) {
    apiClones.value.forEach(clone => {
      if (clone.api_enabled === 1 || clone.api_enabled === true || clone.api_enabled === '1' || clone.api_enabled === undefined || clone.status === 'Active') {
        let respFields = [];
        if (clone.api_response_fields) {
          try {
            respFields = typeof clone.api_response_fields === 'string' ? JSON.parse(clone.api_response_fields) : clone.api_response_fields;
          } catch(e) { respFields = []; }
        }
        apis.push({
          api_type: clone.api_type || 'general',
          api_endpoint: clone.api_endpoint || (selectedDataset.value ? (selectedDataset.value.api_endpoint || selectedDataset.value.dataset_id) : ''),
          service_name: clone.service_name || clone.description,
          api_response_fields: respFields
        });
      }
    });
  }
  return apis;
});


const favorites = ref(JSON.parse(localStorage.getItem('user_favorites') || '[]'));

const isFavorite = (ds) => {
  return favorites.value.some(fav => fav.id === ds.id);
};


const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    alert('คัดลอกสำเร็จ');
  } catch (err) {
    console.error('Failed to copy', err);
  }
};

const toggleFavorite = (ds) => {
  const index = favorites.value.findIndex(fav => fav.id === ds.id);
  if (index >= 0) {
    favorites.value.splice(index, 1);
  } else {
    favorites.value.push({
      id: ds.id,
      name: ds.title,
      agency: ds.agency,
      formats: ds.formats
    });
  }
  localStorage.setItem('user_favorites', JSON.stringify(favorites.value));
};

const getAccessInfo = (item) => {
  const raw = String((item && (item.access_type || item.accessibility)) || 'public').trim().toLowerCase();
  if (raw === 'internal' || raw === 'ภายในหน่วยงาน') {
    return {
      key: 'internal',
      label: 'ภายในหน่วยงาน (Internal)',
      shortLabel: 'Internal',
      cssClass: 'access-internal'
    };
  }
  if (raw === 'restricted' || raw === 'จำกัดสิทธิ์' || raw === 'private' || raw === 'confidential') {
    return {
      key: 'restricted',
      label: 'จำกัดสิทธิ์ (Restricted)',
      shortLabel: 'Restricted',
      cssClass: 'access-restricted'
    };
  }
  if (raw === 'pii' || raw === 'ข้อมูลส่วนบุคคล') {
    return {
      key: 'pii',
      label: 'ข้อมูลส่วนบุคคล (PII)',
      shortLabel: 'PII',
      cssClass: 'access-pii'
    };
  }
  return {
    key: 'public',
    label: 'สาธารณะ (Public)',
    shortLabel: 'Public',
    cssClass: 'access-public'
  };
};

const fetchDatasetDetail = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const userStr = localStorage.getItem('user');
    let payload = {};
    if (userStr) {
      payload.user = encodeUserData(JSON.parse(userStr));
    }
    const response = await apiClient.post('/retrieveService', payload);
    if (response.data.status === 'success') {
      const found = response.data.data.find(item => item.service_id.toString() === route.params.id.toString());
      if (found) {
        const accessInfo = getAccessInfo(found);
        selectedDataset.value = {
          id: found.service_id,
          dataset_id: found.dataset_id,
          title: found.service_name,
          agency: found.organization || 'ไม่ระบุหน่วยงาน',
          category: found.category || 'ทั่วไป',
          sub_category: found.sub_category || '-',
          description: found.description || 'ข้อมูลชุดนี้รวบรวมเพื่อการวิเคราะห์และนำไปใช้ประโยชน์ในระดับภาครัฐและเอกชน',
          contact_name: found.contact_name || '-',
          contact_email: found.contact_email || '-',
          tags: found.tags || '',
          purpose: found.purpose || '-',
          accessibility: accessInfo.shortLabel,
          access_type_raw: accessInfo.key,
          access_type_label: accessInfo.label,
          accessClass: accessInfo.cssClass,
          access_type: accessInfo.label,
          dept_contact: found.dept_contact || '-',
          update_freq: (found.update_freq_value || '-') + ' ' + (found.update_freq_unit || ''),
          geo_scope: found.geo_scope || '-',
          data_source: found.data_source || '-',
          gov_category: found.gov_category || '-',
          license: found.license || '-',
          access_conditions: found.access_conditions || '-',
          sponsor: found.sponsor || '-',
          smallest_unit: found.smallest_unit || '-',
          languages: found.languages || '-',
          objective_type: found.objective_type || '-',
          external_dashboard_url: found.external_dashboard_url,
          external_api_url: found.external_api_url,
          api_endpoint: found.api_endpoint,
          api_type: found.api_type,
          has_access: found.has_access === 1 || found.has_access === '1' || found.has_access === true,
          has_dashboard_access: found.has_dashboard_access === 1 || found.has_dashboard_access === '1' || found.has_dashboard_access === true,
          has_api_access: found.has_api_access === 1 || found.has_api_access === '1' || found.has_api_access === true,
          permission_status: found.permission_status,
          dashboard_permission_status: found.dashboard_permission_status,
          api_permission_status: found.api_permission_status,
          api_response_fields: found.api_response_fields ? (typeof found.api_response_fields === 'string' ? JSON.parse(found.api_response_fields) : found.api_response_fields) : [],
          
          api_enabled: found.api_enabled == 1 || found.api_enabled === '1' || found.api_enabled === true,
        };

        // Fetch clones for API tab
        try {
          const cloneRes = await apiClient.post('/getDatasetApiEndpoints', { 
            dataset_id: found.dataset_id || found.service_id,
            user: localStorage.getItem('user')
          });
          if (cloneRes.data && cloneRes.data.data) {
             apiClones.value = cloneRes.data.data.map(clone => {
               let respFields = clone.api_response_fields;
               if (typeof respFields === 'string') {
                 try { respFields = JSON.parse(respFields); } catch(e) { respFields = []; }
               }
               return {
                 ...clone,
                 api_response_fields: Array.isArray(respFields) ? respFields : []
               };
             });
          }
        } catch (e) {
          console.error('Failed to fetch clones', e);
        }
        
        // Merge the rest just to satisfy old code
        selectedDataset.value = {
          ...selectedDataset.value,

          formats: found.data_format ? found.data_format.split(',') : ['CSV', 'API', 'JSON'],
          file_path: found.file_path,
          excel_file_path: found.excel_file_path,
          data_dictionary_path: found.data_dictionary_path,
          data_sampling_path: found.data_sampling_path,
          updated: 'ปรับปรุงเมื่อ 2 วันที่แล้ว',
          dataset_type: found.dataset_type || 'general',
          stat_year_start: found.stat_year_start,
          stat_year_latest: found.stat_year_latest,
          stat_classification: found.stat_classification,
          stat_unit: found.stat_unit,
          stat_multiplier: found.stat_multiplier,
          stat_calculation_method: found.stat_calculation_method,
          stat_standard: found.stat_standard,
          stat_official: found.stat_official,
          geo_dataset_name: found.geo_dataset_name,
          geo_scale: found.geo_scale,
          geo_west_bound: found.geo_west_bound,
          geo_east_bound: found.geo_east_bound,
          geo_north_bound: found.geo_north_bound,
          geo_south_bound: found.geo_south_bound,
          geo_position_accuracy: found.geo_position_accuracy,
          geo_reference_time: found.geo_reference_time,
          geo_published_date: found.geo_published_date
        };
      } else {
        errorMessage.value = 'ไม่พบชุดข้อมูลดังกล่าวในระบบ';
      }
    } else {
      errorMessage.value = 'ดึงข้อมูลชุดข้อมูลไม่สำเร็จ';
    }
  } catch (error) {
    console.error('Error fetching dataset detail:', error);
    errorMessage.value = 'เกิดข้อผิดพลาดในการโหลดรายละเอียดชุดข้อมูล';
  } finally {
    isLoading.value = false;
  }
};

const isValidMouFile = (file) => {
  if (!file) return { valid: false, error: 'กรุณาเลือกไฟล์เอกสารแนบ' };
  
  const fileName = file.name.toLowerCase();
  const fileType = (file.type || '').toLowerCase();
  
  // Explicitly block SVG
  if (fileName.endsWith('.svg') || fileType.includes('svg')) {
    return { valid: false, error: 'ไม่อนุญาตให้อัปโหลดไฟล์ SVG รองรับเฉพาะ PDF หรือรูปภาพ (PNG, JPG, JPEG) เท่านั้น' };
  }
  
  const allowedExtensions = ['.pdf', '.jpg', '.jpeg', '.png'];
  const allowedMimeTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/pjpeg'];
  
  const hasValidExt = allowedExtensions.some(ext => fileName.endsWith(ext));
  const hasValidMime = allowedMimeTypes.includes(fileType) || (!fileType && hasValidExt);
  
  if (!hasValidExt || !hasValidMime) {
    return { valid: false, error: 'รองรับเฉพาะไฟล์ PDF หรือรูปภาพ (PNG, JPG, JPEG) ขนาดไม่เกิน 10MB เท่านั้น' };
  }
  
  if (file.size > 10 * 1024 * 1024) {
    return { valid: false, error: 'ขนาดไฟล์เอกสารแนบต้องไม่เกิน 10MB' };
  }
  
  return { valid: true };
};

const handleDashboardMouChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    const check = isValidMouFile(file);
    if (!check.valid) {
      dashboardRequestForm.value.error = check.error;
      event.target.value = '';
      dashboardRequestForm.value.mouFile = null;
      dashboardRequestForm.value.mouFileName = '';
      return;
    }
    dashboardRequestForm.value.error = '';
    dashboardRequestForm.value.mouFileName = file.name;
    const reader = new FileReader();
    reader.onload = (e) => {
      dashboardRequestForm.value.mouFile = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    dashboardRequestForm.value.mouFile = null;
    dashboardRequestForm.value.mouFileName = '';
  }
};

const handleApiMouChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    const check = isValidMouFile(file);
    if (!check.valid) {
      apiRequestForm.value.error = check.error;
      event.target.value = '';
      apiRequestForm.value.mouFile = null;
      apiRequestForm.value.mouFileName = '';
      return;
    }
    apiRequestForm.value.error = '';
    apiRequestForm.value.mouFileName = file.name;
    const reader = new FileReader();
    reader.onload = (e) => {
      apiRequestForm.value.mouFile = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    apiRequestForm.value.mouFile = null;
    apiRequestForm.value.mouFileName = '';
  }
};

const toggleAllApiFields = () => {
  const allFields = selectedDataset.value?.api_response_fields || [];
  if (apiRequestForm.value.fields.length === allFields.length) {
    apiRequestForm.value.fields = [];
  } else {
    apiRequestForm.value.fields = [...allFields];
  }
};

const submitDashboardPermissionRequest = async () => {
  if (!dashboardRequestForm.value.reason.trim()) {
    dashboardRequestForm.value.error = 'โปรดระบุวัตถุประสงค์ในการขอเข้าถึงแดชบอร์ด';
    return;
  }
  if (!dashboardRequestForm.value.mouFile || !dashboardRequestForm.value.mouFileName) {
    dashboardRequestForm.value.error = 'กรุณาแนบเอกสารประกอบคำขอ (รองรับไฟล์ PDF หรือรูปภาพ ขนาดไม่เกิน 10MB)';
    return;
  }
  
  dashboardRequestForm.value.isSubmitting = true;
  dashboardRequestForm.value.error = '';
  dashboardRequestForm.value.success = '';
  
  try {
    const userData = localStorage.getItem('user');
    const response = await apiClient.post('/requestDatasetPermission', {
      user: encodeUserData(JSON.parse(userData)),
      service_id: selectedDataset.value.id,
      request_type: 'dashboard',
      reason: dashboardRequestForm.value.reason,
      mou_file: dashboardRequestForm.value.mouFile,
      mou_filename: dashboardRequestForm.value.mouFileName,
      fields: []
    });
    
    if (response.data.status === 'success') {
      dashboardRequestForm.value.success = 'ส่งคำขอเข้าถึงแดชบอร์ดเรียบร้อยแล้ว';
      selectedDataset.value.dashboard_permission_status = 'Pending';
      dashboardRequestForm.value.reason = '';
      dashboardRequestForm.value.mouFile = null;
      dashboardRequestForm.value.mouFileName = '';
      fetchDatasetDetail();
    } else {
      dashboardRequestForm.value.error = response.data.message || 'เกิดข้อผิดพลาด';
    }
  } catch (error) {
    dashboardRequestForm.value.error = error.response?.data?.message || 'ไม่สามารถส่งคำขอได้';
  } finally {
    dashboardRequestForm.value.isSubmitting = false;
  }
};

const submitApiPermissionRequest = async () => {
  if (apiRequestForm.value.fields.length === 0) {
    apiRequestForm.value.error = 'โปรดเลือกอย่างน้อย 1 ฟิลด์ข้อมูล';
    return;
  }
  if (!apiRequestForm.value.reason.trim()) {
    apiRequestForm.value.error = 'โปรดระบุวัตถุประสงค์ในการขอเข้าถึง API';
    return;
  }
  if (!apiRequestForm.value.mouFile || !apiRequestForm.value.mouFileName) {
    apiRequestForm.value.error = 'กรุณาแนบเอกสารประกอบคำขอ (รองรับไฟล์ PDF หรือรูปภาพ ขนาดไม่เกิน 10MB)';
    return;
  }
  
  apiRequestForm.value.isSubmitting = true;
  apiRequestForm.value.error = '';
  apiRequestForm.value.success = '';
  
  try {
    const userData = localStorage.getItem('user');
    const response = await apiClient.post('/requestDatasetPermission', {
      user: encodeUserData(JSON.parse(userData)),
      service_id: selectedDataset.value.id,
      request_type: 'api',
      fields: apiRequestForm.value.fields,
      reason: apiRequestForm.value.reason,
      mou_file: apiRequestForm.value.mouFile,
      mou_filename: apiRequestForm.value.mouFileName
    });
    
    if (response.data.status === 'success') {
      apiRequestForm.value.success = 'ส่งคำขอเข้าถึง API เรียบร้อยแล้ว';
      selectedDataset.value.api_permission_status = 'Pending';
      apiRequestForm.value.fields = [];
      apiRequestForm.value.reason = '';
      apiRequestForm.value.mouFile = null;
      apiRequestForm.value.mouFileName = '';
      fetchDatasetDetail();
    } else {
      apiRequestForm.value.error = response.data.message || 'เกิดข้อผิดพลาด';
    }
  } catch (error) {
    apiRequestForm.value.error = error.response?.data?.message || 'ไม่สามารถส่งคำขอได้';
  } finally {
    apiRequestForm.value.isSubmitting = false;
  }
};

const dictIsCsv = computed(() => {
  const path = selectedDataset.value?.data_dictionary_path;
  return path ? path.toLowerCase().endsWith('.csv') : false;
});
const dictIsExcel = computed(() => {
  const path = selectedDataset.value?.data_dictionary_path;
  return path ? (path.toLowerCase().endsWith('.xls') || path.toLowerCase().endsWith('.xlsx')) : false;
});

const apiIsCsv = computed(() => {
  const path = selectedDataset.value?.file_path;
  return path ? path.toLowerCase().endsWith('.csv') : false;
});
const apiIsExcel = computed(() => {
  const p1 = selectedDataset.value?.excel_file_path;
  const p2 = selectedDataset.value?.file_path;
  const path = p1 || (p2 && (p2.toLowerCase().endsWith('.xls') || p2.toLowerCase().endsWith('.xlsx')) ? p2 : '');
  return path ? (path.toLowerCase().endsWith('.xls') || path.toLowerCase().endsWith('.xlsx')) : false;
});
const apiIsJson = computed(() => {
  const path = selectedDataset.value?.file_path;
  return path ? path.toLowerCase().endsWith('.json') : false;
});
const apiIsXml = computed(() => {
  const path = selectedDataset.value?.file_path;
  return path ? path.toLowerCase().endsWith('.xml') : false;
});

const openPreview = (format) => {
  if (selectedDataset.value) {
    let fileTypeParam = 'data';
    const fmt = String(format || '').toUpperCase();
    if (fmt === 'DICTIONARY') fileTypeParam = 'dictionary';
    else if (fmt === 'SAMPLING') fileTypeParam = 'sampling';
    else if (fmt === 'EXCEL' || fmt === 'XLS' || fmt === 'XLSX') fileTypeParam = 'excel';
    
    // Fallback: If they want data (CSV) but it's null, and dictionary exists, download dictionary instead
    if (fileTypeParam === 'data' && !selectedDataset.value.file_path && selectedDataset.value.data_dictionary_path) {
        fileTypeParam = 'dictionary';
    }
    
    // For CSV, XLS, API, etc. it corresponds to the main data file.
    window.open(`/api/downloadFile/${selectedDataset.value.id}?type=${fileTypeParam}`, '_blank');
  } else {
    alert(`กำลังเปิดดาวน์โหลดไฟล์/แสดงพรีวิวในรูปแบบ ${format}`);
  }
};

onMounted(() => {
  fetchDatasetDetail();
});

watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchDatasetDetail();
  }
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
        <p>กำลังโหลดข้อมูลรายละเอียดชุดข้อมูล...</p>
      </div>
      
      <div v-else-if="errorMessage" class="error-state">
        <p>{{ errorMessage }}</p>
        <button @click="fetchDatasetDetail" class="btn-outline">ลองใหม่อีกครั้ง</button>
      </div>
      
      <template v-else-if="selectedDataset">
        <header class="detail-header">
          <div class="header-main">
            <div class="agency-header">
              <div class="agency-logo">DEX</div>
              <span class="agency-name">{{ selectedDataset.agency }}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
              <h1 style="margin:0;">{{ selectedDataset.title }}</h1>
              <span class="id-badge font-mono">{{ selectedDataset.dataset_id }}</span>
            </div>
            
            <div class="header-meta">
              <span class="meta-badge" :class="selectedDataset.accessClass || 'access-public'">{{ selectedDataset.accessibility }}</span>
              <span class="meta-item">{{ selectedDataset.category }} / {{ selectedDataset.sub_category }}</span>
            </div>
          </div>
          
          <div class="header-actions">
            <button class="btn-outline" :class="{ 'is-active': isFavorite(selectedDataset) }" @click="toggleFavorite(selectedDataset)" title="เพิ่ม/ลบ ชุดข้อมูลนี้ในรายการโปรดของคุณ">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" :fill="isFavorite(selectedDataset) ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.921-1.103 1.821-1.891 1.118l-3.976-2.888a1 1 0 00-1.175 0l-3.976 2.888c-.788.703-2.191-.197-1.891-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              {{ isFavorite(selectedDataset) ? 'เลิกติดตาม' : 'ติดตามชุดข้อมูล' }}
            </button>
          </div>
        </header>
        
        <div class="tabs-container">
          <nav class="tabs">
            <button :class="['tab-btn', { active: activeTab === 'info' }]" @click="activeTab = 'info'">คำอธิบายข้อมูล</button>
            <button :class="['tab-btn', { active: activeTab === 'dictionary' }]" @click="activeTab = 'dictionary'">พจนานุกรมข้อมูล</button>
            <button :class="['tab-btn', { active: activeTab === 'visual' }]" @click="activeTab = 'visual'" title="ดูแดชบอร์ดสรุปผลข้อมูล">แดชบอร์ด</button title="ดูแดชบอร์ดสรุปผลข้อมูล">
            <button :class="['tab-btn', { active: activeTab === 'api' }]" @click="activeTab = 'api'" title="ดูเอกสารและการเชื่อมต่อ API">ข้อมูล API</button title="ดูเอกสารและการเชื่อมต่อ API">
          </nav>
          
          <div class="tab-content">
            <!-- Info Tab -->
            <div v-if="activeTab === 'info'" class="info-tab transition-fade">
              <div class="info-grid">
                <div class="info-main">
                  <h3>รายละเอียด</h3>
                  <p>{{ selectedDataset.description }}</p>
                  
                  <div class="metadata-table">
                    <div class="row-group-title">ข้อมูลทั่วไป</div>
                    <div class="row"><span class="label">รหัสชุดข้อมูล</span><span class="value font-mono">{{ selectedDataset.dataset_id }}</span></div>
                    <div class="row"><span class="label">หน่วยงานเจ้าของ</span><span class="value">{{ selectedDataset.agency }}</span></div>
                    <div class="row"><span class="label">ผู้ติดต่อ</span><span class="value">{{ selectedDataset.contact_name }}</span></div>
                    <div class="row"><span class="label">อีเมลติดต่อ</span><span class="value">{{ selectedDataset.contact_email }}</span></div>
                    <div class="row"><span class="label">หมวดหมู่ชุดข้อมูล</span><span class="value">{{ selectedDataset.category }} / {{ selectedDataset.sub_category }}</span></div>
                    <div class="row"><span class="label">การเข้าถึง</span><span class="value">{{ selectedDataset.access_type }}</span></div>
                    
                    <div class="row-group-title">ธรรมาภิบาลและความถี่</div>
                    <div class="row"><span class="label">ชั้นความลับ</span><span class="value">{{ selectedDataset.gov_category }}</span></div>
                    <div class="row"><span class="label">สัญญาอนุญาต</span><span class="value">{{ selectedDataset.license }}</span></div>
                    <div class="row"><span class="label">วัตถุประสงค์</span><span class="value">{{ selectedDataset.objective_type }}</span></div>
                    <div class="row"><span class="label">แหล่งที่มา</span><span class="value">{{ selectedDataset.data_source }}</span></div>
                    <div class="row"><span class="label">ความถี่การปรับปรุง</span><span class="value">{{ selectedDataset.update_freq }}</span></div>
                    <div class="row"><span class="label">ขอบเขตข้อมูล</span><span class="value">{{ selectedDataset.geo_scope }}</span></div>
                    
                    <!-- STATISTIC SPECIFIC -->
                    <template v-if="selectedDataset.dataset_type === 'statistic'">
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
                    <template v-if="selectedDataset.dataset_type === 'geospatial'">
                      <div class="row-group-title text-[var(--primary)] border-emerald-200 mt-4">ข้อมูลภูมิสารสนเทศเชิงพื้นที่</div>
                      <div class="row"><span class="label">ชื่อชุดข้อมูลภูมิศาสตร์</span><span class="value">{{ selectedDataset.geo_dataset_name || '-' }}</span></div>
                      <div class="row"><span class="label">มาตราส่วน</span><span class="value">{{ selectedDataset.geo_scale || '-' }}</span></div>
                      <div class="row"><span class="label">ขอบเขต (W, E, N, S)</span><span class="value font-mono">{{ selectedDataset.geo_west_bound || '-' }}, {{ selectedDataset.geo_east_bound || '-' }}, {{ selectedDataset.geo_north_bound || '-' }}, {{ selectedDataset.geo_south_bound || '-' }}</span></div>
                      <div class="row"><span class="label">ความถูกต้องของตำแหน่ง</span><span class="value">{{ selectedDataset.geo_position_accuracy || '-' }}</span></div>
                      <div class="row"><span class="label">เวลาอ้างอิง</span><span class="value">{{ selectedDataset.geo_reference_time || '-' }}</span></div>
                      <div class="row"><span class="label">วันที่เผยแพร่ข้อมูล</span><span class="value">{{ selectedDataset.geo_published_date || '-' }}</span></div>
                    </template>

                    <div class="row-group-title mt-4">ข้อมูลอื่นๆ</div>
                    <div class="row"><span class="label">แท็ก</span><span class="value">
                      <span v-for="tag in selectedDataset.tags.split(',')" :key="tag" class="tag-inline">{{ tag.trim() }}</span>
                    </span></div>
                  </div>
                </div>
                
                <aside class="info-sidebar">
                  
                  <!-- Data Dictionary (Public - always open) -->
                  <div class="action-card" style="margin-bottom: 16px;">
                    <h4>Data Dictionary</h4>
                    <p style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">ดาวน์โหลดพจนานุกรมอธิบายโครงสร้างข้อมูล</p>
                    <div class="download-buttons" style="margin-top: 12px; display: flex; gap: 8px;">
                      <button class="btn-download csv" :disabled="!dictIsCsv" @click="openPreview('DICTIONARY')" title="ดาวน์โหลด Data Dictionary (CSV)">CSV</button>
                      <button class="btn-download xls" :disabled="!dictIsExcel" @click="openPreview('DICTIONARY')" title="ดาวน์โหลด Data Dictionary (Excel)">Excel</button>
                    </div>
                  </div>

                  <!-- API / File download card -->
                  <div v-if="selectedDataset.has_api_access" class="action-card">
                    <h4>API & Data Files</h4>
                    <p style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">ดาวน์โหลดไฟล์ข้อมูลต้นฉบับ</p>
                    <div class="download-buttons" style="margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;">
                      <button class="btn-download csv" :disabled="!apiIsCsv" @click="openPreview('CSV')" title="ดาวน์โหลดไฟล์ในรูปแบบ CSV">CSV</button>
                      <button class="btn-download xls" :disabled="!apiIsExcel" @click="openPreview('Excel')" title="ดาวน์โหลดไฟล์ในรูปแบบ Excel">Excel</button>
                      <button v-if="apiIsXml" class="btn-download xml" @click="openPreview('XML')" title="ดาวน์โหลดไฟล์ในรูปแบบ XML">XML</button>
                      <button v-if="apiIsJson" class="btn-download json" @click="openPreview('JSON')" title="ดาวน์โหลดไฟล์ในรูปแบบ JSON">JSON</button>
                    </div>
                    
                    <button v-if="selectedDataset.data_sampling_path" class="btn-primary-outline w-full mt-4" style="width:100%; margin-top:16px;" @click="openPreview('SAMPLING')" title="ดาวน์โหลดข้อมูลตัวอย่างสำหรับทดสอบ">ดาวน์โหลดชุดข้อมูลสุ่ม (Zip File)</button>
                  </div>
                  
                  <!-- If does NOT have API access, show clean prompt in sidebar -->
                  <div v-else class="action-card">
                    <h4 style="display:flex;align-items:center;gap:6px;">🔒 ดาวน์โหลดไฟล์ & API</h4>
                    <p style="font-size:0.85rem;color:#64748b;margin-top:4px;margin-bottom:12px;">ชุดข้อมูลนี้จำกัดสิทธิ์การดาวน์โหลดไฟล์ข้อมูลและ API</p>
                    <button class="btn-primary-outline w-full" style="width:100%; font-size:0.85rem; padding:8px 12px;" @click="activeTab = 'api'">
                      ไปที่แท็บ ข้อมูล API เพื่อส่งคำขอ
                    </button>
                  </div>
                </aside>
              </div>
            </div>
            
            <!-- Dictionary Tab (Always Publicly Viewable) -->
            <div v-if="activeTab === 'dictionary'" class="dictionary-tab transition-fade">
              <div v-if="!selectedDataset.api_response_fields || selectedDataset.api_response_fields.length === 0" style="padding: 48px 24px; text-align: center; color: #64748b; background: white; border-radius: 12px; border: 1px solid #e2e8f0;">
                <svg xmlns="http://www.w3.org/2000/svg" style="width: 48px; height: 48px; margin: 0 auto 12px auto; color: #cbd5e1;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <h4 style="font-size: 1.05rem; font-weight: 600; color: #334155; margin: 0 0 6px 0;">ยังไม่มีพจนานุกรมข้อมูลสำหรับชุดข้อมูลนี้</h4>
                <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;">ชุดข้อมูลนี้ยังไม่มีการสร้าง API หรืออัปโหลดไฟล์พจนานุกรมข้อมูล (Data Dictionary)</p>
              </div>
              <table v-else class="dictionary-table">
                <thead>
                  <tr>
                    <th style="width: 10%">ลำดับ</th>
                    <th style="width: 30%">ชื่อฟิลด์</th>
                    <th style="width: 20%">ประเภท</th>
                    <th style="width: 40%">คำอธิบาย</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(field, index) in selectedDataset.api_response_fields" :key="field">
                    <td>{{ index + 1 }}</td>
                    <td class="font-mono" style="font-weight:600;">{{ field }}</td>
                    <td>VARCHAR / String</td>
                    <td>ฟิลด์ข้อมูลที่ให้บริการสำหรับชุดข้อมูลนี้</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- Visual Tab (Dashboard) -->
            <div v-if="activeTab === 'visual'" class="visual-tab transition-fade" style="padding: 0;">
              <!-- If does NOT have dashboard access, show Dashboard Permission Request / Status -->
              <div v-if="!selectedDataset.has_dashboard_access" style="padding: 32px 20px; background: white; border-radius: 16px; border: 1px solid #e2e8f0;">
                <div v-if="selectedDataset.dashboard_permission_status === 'Pending'" style="background:#fef3c7; color:#92400e; padding:32px 24px; border-radius:12px; border:1px solid #fde68a; text-align:center; max-width:640px; margin:0 auto;">
                  <div style="font-size: 40px; margin-bottom: 12px;">⏳</div>
                  <h4 style="font-size:1.15rem; font-weight:700; margin:0 0 6px 0;">คำขอเข้าถึงแดชบอร์ดอยู่ระหว่างรอการอนุมัติ</h4>
                  <p style="font-size:0.9rem; margin:0; color:#b45309;">คำขอเข้าถึงแดชบอร์ดของคุณถูกส่งเรียบร้อยแล้ว และอยู่ระหว่างการพิจารณาโดยผู้ดูแลระบบ</p>
                </div>

                <div v-else-if="selectedDataset.dashboard_permission_status === 'Rejected'" style="background:#fee2e2; color:#991b1b; padding:32px 24px; border-radius:12px; border:1px solid #fecaca; text-align:center; max-width:640px; margin:0 auto;">
                  <div style="font-size: 40px; margin-bottom: 12px;">❌</div>
                  <h4 style="font-size:1.15rem; font-weight:700; margin:0 0 6px 0;">คำขอเข้าถึงแดชบอร์ดถูกปฏิเสธ</h4>
                  <p style="font-size:0.9rem; margin:0 0 16px 0; color:#b91c1c;">คำขอเข้าถึงแดชบอร์ดของคุณไม่ผ่านการอนุมัติ คุณสามารถตรวจสอบเอกสารและส่งคำขอใหม่อีกครั้ง</p>
                  <button class="btn-primary-outline" style="padding:8px 20px;" @click="selectedDataset.dashboard_permission_status = null">ส่งคำขอเข้าถึงแดชบอร์ดใหม่</button>
                </div>

                <div v-else class="dashboard-request-form" style="max-width: 640px; margin: 0 auto; padding: 28px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;">
                  <div style="text-align: center; margin-bottom: 24px;">
                    <div style="width: 56px; height: 56px; border-radius: 50%; background: #e0f2fe; color: #0284c7; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px auto; font-size: 26px;">
                      📊
                    </div>
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0 0 8px 0;">ขอสิทธิ์เข้าถึงแดชบอร์ด (Dashboard Access Request)</h3>
                    <p style="font-size: 0.9rem; color: #64748b; margin: 0;">ชุดข้อมูลนี้จำกัดสิทธิ์การเข้าถึงแดชบอร์ด กรุณากรอกวัตถุประสงค์และแนบเอกสารเพื่อขออนุมัติสิทธิ์</p>
                  </div>

                  <div class="form-group mb-4" style="margin-bottom: 16px;">
                    <label class="font-semibold block mb-1 text-slate-700" style="font-size:0.9rem; display:block; margin-bottom: 6px; font-weight:600;">วัตถุประสงค์ในการขอเข้าถึงแดชบอร์ด <span style="color:#ef4444;">*</span></label>
                    <textarea v-model="dashboardRequestForm.reason" rows="3" style="width:100%; border:1px solid #cbd5e1; border-radius:8px; padding:10px 12px; font-size:0.9rem; resize:vertical; box-sizing:border-box;" placeholder="ระบุเหตุผลและวัตถุประสงค์ในการใช้งานแดชบอร์ดชุดข้อมูลนี้..."></textarea>
                  </div>

                  <div class="form-group mb-4" style="margin-bottom: 20px;">
                    <label class="font-semibold block mb-1 text-slate-700" style="font-size:0.9rem; display:block; margin-bottom: 4px; font-weight:600;">เอกสารประกอบคำขอ (MOU / หนังสือขอความอนุเคราะห์ / รูปภาพหลักฐาน) <span style="color:#ef4444;">* (จำเป็นต้องแนบ)</span></label>
                    <div style="font-size:0.8rem; color:#1e3a8a; margin:0 0 8px 0; background:#eff6ff; padding:8px 12px; border-radius:8px; border:1px solid #bfdbfe; display:flex; align-items:center; gap:6px;">
                      <span>📌</span>
                      <span><strong>เงื่อนไขไฟล์แนบ:</strong> รองรับไฟล์ <strong>PDF หรือรูปภาพ (PNG, JPG, JPEG)</strong> ขนาดไม่เกิน <strong>10 MB</strong> (ไม่อนุญาตไฟล์ SVG)</span>
                    </div>
                    <input type="file" @change="handleDashboardMouChange" accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg" style="width:100%; border:1px solid #cbd5e1; border-radius:8px; padding:8px 12px; font-size:0.85rem; background:white; cursor:pointer;" required>
                    <div v-if="dashboardRequestForm.mouFileName" style="margin-top:6px; font-size:0.8rem; color:#059669; display:flex; align-items:center; gap:4px;">
                      <span>📎 ไฟล์ที่เลือก: <strong>{{ dashboardRequestForm.mouFileName }}</strong></span>
                    </div>
                  </div>

                  <div v-if="dashboardRequestForm.error" style="color:#e11d48; font-size:0.85rem; margin-bottom:12px; padding:8px 12px; background:#ffe4e6; border-radius:6px;">{{ dashboardRequestForm.error }}</div>
                  <div v-if="dashboardRequestForm.success" style="color:#16a34a; font-size:0.85rem; margin-bottom:12px; padding:8px 12px; background:#dcfce7; border-radius:6px;">{{ dashboardRequestForm.success }}</div>

                  <button class="btn-primary w-full" style="width:100%; padding:12px; font-size:0.95rem; border:none; border-radius:8px; background:var(--mso-accent, var(--primary)); color:white; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;" :disabled="dashboardRequestForm.isSubmitting" @click="submitDashboardPermissionRequest">
                    <span v-if="dashboardRequestForm.isSubmitting">กำลังส่งคำขอ...</span>
                    <span v-else>ส่งคำขอเข้าถึงแดชบอร์ด</span>
                  </button>
                </div>
              </div>

              <!-- If HAS dashboard access -->
              <div v-else-if="selectedDataset.external_dashboard_url" class="dashboard-container">
                <div class="dashboard-actions mb-4 p-4 flex justify-between items-center bg-slate-50 border-b border-slate-100" style="display:flex; justify-content:space-between; align-items:center; padding:16px; background:#f8fafc; border-bottom:1px solid #cbd5e1;">
                  <div style="display:flex; align-items:center; gap:8px; color:#475569; font-weight:500;">
                    <span>External Dashboard</span>
                  </div>
                  <a :href="selectedDataset.external_dashboard_url" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; background:var(--mso-accent, var(--primary)); color:white; border-radius:8px; text-decoration:none; font-weight:600; font-size:0.875rem;">
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
              <div v-else class="dashboard-empty-container" style="padding: 40px; text-align: center; background:#f8fafc; border:1px solid #e2e8f0; border-radius:16px;">
                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto mb-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="height: 64px; width: 64px; margin: 0 auto 16px auto; color: #cbd5e1;">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p style="font-weight: bold; font-size: 1.125rem; margin-bottom: 4px; color:#475569;">ไม่มีแดชบอร์ดสำหรับชุดข้อมูลนี้</p>
                <p style="font-size: 0.875rem; color: #94a3b8; margin: 0;">ชุดข้อมูลนี้ยังไม่ได้ตั้งค่าการเชื่อมต่อแดชบอร์ด</p>
              </div>
            </div>
            
            <!-- API Tab -->
            <div v-if="activeTab === 'api'" class="api-tab transition-fade">
              <!-- If does NOT have API access, show API Permission Request / Status -->
              <div v-if="!selectedDataset.has_api_access" style="padding: 32px 20px; background: white; border-radius: 16px; border: 1px solid #e2e8f0;">
                <div v-if="selectedDataset.api_permission_status === 'Pending'" style="background:#fef3c7; color:#92400e; padding:32px 24px; border-radius:12px; border:1px solid #fde68a; text-align:center; max-width:640px; margin:0 auto;">
                  <div style="font-size: 40px; margin-bottom: 12px;">⏳</div>
                  <h4 style="font-size:1.15rem; font-weight:700; margin:0 0 6px 0;">คำขอเข้าถึง API อยู่ระหว่างรอการอนุมัติ</h4>
                  <p style="font-size:0.9rem; margin:0; color:#b45309;">คำขอเข้าถึง API ของคุณถูกส่งเรียบร้อยแล้ว และอยู่ระหว่างการพิจารณาโดยผู้ดูแลระบบ</p>
                </div>

                <div v-else-if="selectedDataset.api_permission_status === 'Rejected'" style="background:#fee2e2; color:#991b1b; padding:32px 24px; border-radius:12px; border:1px solid #fecaca; text-align:center; max-width:640px; margin:0 auto;">
                  <div style="font-size: 40px; margin-bottom: 12px;">❌</div>
                  <h4 style="font-size:1.15rem; font-weight:700; margin:0 0 6px 0;">คำขอเข้าถึง API ถูกปฏิเสธ</h4>
                  <p style="font-size:0.9rem; margin:0 0 16px 0; color:#b91c1c;">คำขอเข้าถึง API ของคุณไม่ผ่านการอนุมัติ คุณสามารถตรวจสอบข้อมูลและส่งคำขอใหม่อีกครั้ง</p>
                  <button class="btn-primary-outline" style="padding:8px 20px;" @click="selectedDataset.api_permission_status = null">ส่งคำขอเข้าถึง API ใหม่</button>
                </div>

                <div v-else class="api-request-form" style="max-width: 720px; margin: 0 auto; padding: 28px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;">
                  <div style="text-align: center; margin-bottom: 24px;">
                    <div style="width: 56px; height: 56px; border-radius: 50%; background: #ecfdf5; color: #059669; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px auto; font-size: 26px;">
                      ⚡
                    </div>
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0 0 8px 0;">ขอสิทธิ์เข้าถึง API (API Access Request)</h3>
                    <p style="font-size: 0.9rem; color: #64748b; margin: 0;">ชุดข้อมูลนี้จำกัดสิทธิ์การเข้าถึง API โปรดเลือกฟิลด์ข้อมูลที่ต้องการใช้งาน พร้อมระบุวัตถุประสงค์</p>
                  </div>

                  <!-- Field Selector with Quick Action -->
                  <div class="form-group mb-4" style="margin-bottom: 16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                      <label class="font-semibold text-slate-700" style="font-size:0.9rem; font-weight:600;">ฟิลด์ข้อมูลที่ต้องการใช้งาน (Request Fields) <span style="color:#ef4444;">*</span></label>
                      <button v-if="selectedDataset.api_response_fields && selectedDataset.api_response_fields.length > 0" type="button" @click="toggleAllApiFields" style="background:none; border:none; color:var(--mso-accent, var(--primary)); font-size:0.8rem; font-weight:600; cursor:pointer; text-decoration:underline;">
                        {{ apiRequestForm.fields.length === (selectedDataset.api_response_fields || []).length ? 'ล้างการเลือกทั้งหมด' : 'เลือกทั้งหมด' }}
                      </button>
                    </div>
                    <div v-if="!selectedDataset.api_response_fields || selectedDataset.api_response_fields.length === 0" style="padding:16px; text-align:center; background:white; border:1px solid #cbd5e1; border-radius:8px; color:#94a3b8; font-size:0.85rem;">
                      ชุดข้อมูลนี้ยังไม่มีรายการฟิลด์ข้อมูล API ที่เปิดให้บริการ
                    </div>
                    <div v-else class="field-checkbox-list" style="max-height:160px; overflow-y:auto; border:1px solid #cbd5e1; border-radius:8px; padding:10px 14px; background:white; display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 8px;">
                      <label v-for="field in selectedDataset.api_response_fields" :key="field" class="flex items-center gap-2 cursor-pointer" style="display:flex; align-items:center; gap:8px; font-size:0.85rem; cursor:pointer;">
                        <input type="checkbox" :value="field" v-model="apiRequestForm.fields" style="accent-color: var(--primary);">
                        <span class="font-mono text-slate-700">{{ field }}</span>
                      </label>
                    </div>
                    <p v-if="selectedDataset.api_response_fields && selectedDataset.api_response_fields.length > 0" style="font-size:0.75rem; color:#64748b; margin-top:4px;">เลือกแล้ว {{ apiRequestForm.fields.length }} จาก {{ (selectedDataset.api_response_fields || []).length }} ฟิลด์</p>
                  </div>

                  <div class="form-group mb-4" style="margin-bottom: 16px;">
                    <label class="font-semibold block mb-1 text-slate-700" style="font-size:0.9rem; display:block; margin-bottom: 6px; font-weight:600;">วัตถุประสงค์ในการขอเข้าถึง API <span style="color:#ef4444;">*</span></label>
                    <textarea v-model="apiRequestForm.reason" rows="3" style="width:100%; border:1px solid #cbd5e1; border-radius:8px; padding:10px 12px; font-size:0.9rem; resize:vertical; box-sizing:border-box;" placeholder="ระบุเหตุผลและวัตถุประสงค์ในการเชื่อมต่อ API ชุดข้อมูลนี้..."></textarea>
                  </div>

                  <div class="form-group mb-4" style="margin-bottom: 20px;">
                    <label class="font-semibold block mb-1 text-slate-700" style="font-size:0.9rem; display:block; margin-bottom: 4px; font-weight:600;">เอกสารประกอบคำขอ (MOU / หนังสือขอความอนุเคราะห์ / รูปภาพหลักฐาน) <span style="color:#ef4444;">* (จำเป็นต้องแนบ)</span></label>
                    <div style="font-size:0.8rem; color:#065f46; margin:0 0 8px 0; background:#ecfdf5; padding:8px 12px; border-radius:8px; border:1px solid #a7f3d0; display:flex; align-items:center; gap:6px;">
                      <span>📌</span>
                      <span><strong>เงื่อนไขไฟล์แนบ:</strong> รองรับไฟล์ <strong>PDF หรือรูปภาพ (PNG, JPG, JPEG)</strong> ขนาดไม่เกิน <strong>10 MB</strong> (ไม่อนุญาตไฟล์ SVG)</span>
                    </div>
                    <input type="file" @change="handleApiMouChange" accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg" style="width:100%; border:1px solid #cbd5e1; border-radius:8px; padding:8px 12px; font-size:0.85rem; background:white; cursor:pointer;" required>
                    <div v-if="apiRequestForm.mouFileName" style="margin-top:6px; font-size:0.8rem; color:#059669; display:flex; align-items:center; gap:4px;">
                      <span>📎 ไฟล์ที่เลือก: <strong>{{ apiRequestForm.mouFileName }}</strong></span>
                    </div>
                  </div>

                  <div v-if="apiRequestForm.error" style="color:#e11d48; font-size:0.85rem; margin-bottom:12px; padding:8px 12px; background:#ffe4e6; border-radius:6px;">{{ apiRequestForm.error }}</div>
                  <div v-if="apiRequestForm.success" style="color:#16a34a; font-size:0.85rem; margin-bottom:12px; padding:8px 12px; background:#dcfce7; border-radius:6px;">{{ apiRequestForm.success }}</div>

                  <button class="btn-primary w-full" style="width:100%; padding:12px; font-size:0.95rem; border:none; border-radius:8px; background:var(--mso-accent, var(--primary)); color:white; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px;" :disabled="apiRequestForm.isSubmitting" @click="submitApiPermissionRequest">
                    <span v-if="apiRequestForm.isSubmitting">กำลังส่งคำขอ...</span>
                    <span v-else>ส่งคำขอเข้าถึง API</span>
                  </button>
                </div>
              </div>

              <!-- If HAS API access and no endpoints available -->
              <div v-else-if="combinedApis.length === 0" style="padding:40px; text-align:center; background:#f8fafc; border:1px solid #e2e8f0; border-radius:16px;">
                <p style="font-weight:bold; font-size:1.1rem; color:#475569; margin:0 0 8px 0;">🔒 ไม่พบปลายทาง API ที่เปิดใช้งาน</p>
                <p style="font-size:0.875rem; color:#64748b; margin:0;">ชุดข้อมูลนี้ยังไม่มีการกำหนด API Endpoint สำหรับให้บริการ</p>
              </div>
              
              <!-- If has API, show details -->
              <div v-else class="api-cards" style="display: flex; flex-direction: column; gap: 1rem;">
                
                <!-- Card 1: File for API -->
                <div v-if="selectedDataset.file_path" class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white; border: 1px solid #334155;">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3 style="margin: 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                      File API (ดาวน์โหลดไฟล์ข้อมูลดิบ)
                    </h3>
                    <span style="background: rgba(148, 163, 184, 0.2); color: #cbd5e1; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(148, 163, 184, 0.3);">
                      RAW FILE (/file)
                    </span>
                  </div>
                  <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' + userApiKey)">คัดลอกเพื่อใช้งาน API</div>
                  <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem; word-break: break-all;">
                    {{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>
                  </code>
                  <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                    <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || apiBaseUrl + (selectedDataset.api_endpoint || selectedDataset.dataset_id) + '/file?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>"</pre>
                  </div>
                </div>

                <!-- Loop through all configured APIs (Original + Clones) -->
                <div v-for="(api, index) in combinedApis" :key="index">
                  <!-- General API -->
                  <div v-if="api.api_type === 'general' || api.api_type === 'public' || api.api_type === 'private' || !api.api_type" class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white; border: 1px solid #334155;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                      <h3 style="margin: 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>
                        General API (ข้อมูลทั่วไปครบทุกฟิลด์) - {{ api.api_endpoint }}
                      </h3>
                      <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);">
                        GENERAL API
                      </span>
                    </div>
                    <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + api.api_endpoint + '?apikey=' + userApiKey)">คัดลอกเพื่อใช้งาน API</div>
                    <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem; word-break: break-all;">
                      {{ selectedDataset.external_api_url || apiBaseUrl + api.api_endpoint + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>
                    </code>
                    <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                      <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || apiBaseUrl + api.api_endpoint + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>"</pre>
                    </div>
                  </div>

                  <!-- Scope API -->
                  <div v-if="api.api_type === 'scope'" class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white; border: 1px solid #0284c7;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                      <h3 style="margin: 0; color: #38bdf8; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                        Scope API (ข้อมูลเฉพาะฟิลด์/เงื่อนไขที่กำหนด) - {{ api.api_endpoint }}
                      </h3>
                      <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.4);">
                        SCOPE API (/scope/)
                      </span>
                    </div>

                    <!-- Scoped Fields Tag List -->
                    <div v-if="api.api_response_fields && api.api_response_fields.length > 0" style="margin-bottom: 14px; font-size: 0.82rem; display: flex; flex-wrap: wrap; align-items: center; gap: 6px; background: rgba(56, 189, 248, 0.08); padding: 8px 12px; border-radius: 8px; border: 1px dashed rgba(56, 189, 248, 0.3);">
                      <span style="color: #38bdf8; font-weight: 600;">🎯 ฟิลด์ใน Scope ({{ api.api_response_fields.length }} ฟิลด์):</span>
                      <span v-for="field in api.api_response_fields" :key="field" style="background: rgba(56, 189, 248, 0.2); color: #e0f2fe; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.75rem;">
                        {{ field }}
                      </span>
                    </div>

                    <div class="method-badge" style="display: inline-block; background: #0284c7; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px; cursor: pointer;" @click="copyToClipboard(selectedDataset.external_api_url || apiBaseUrl + 'scope/' + api.api_endpoint + '?apikey=' + userApiKey)">คัดลอกเพื่อใช้งาน API</div>
                    <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem; word-break: break-all;">
                      {{ selectedDataset.external_api_url || apiBaseUrl + 'scope/' + api.api_endpoint + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>
                    </code>
                    <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                      <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || apiBaseUrl + 'scope/' + api.api_endpoint + '?apikey=' }}<span class='blur-key'>{{ userApiKey }}</span>"</pre>
                    </div>
                  </div>
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
.blur-key { filter: blur(4px); transition: filter 0.3s; user-select: text; }
.blur-key:hover { filter: blur(0px); }
.endpoint-url { display: flex; align-items: center; gap: 8px; }
.copy-btn { background: #334155; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; transition: background 0.2s; }
.copy-btn:hover { background: #475569; }
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
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
  border-top-color: var(--mso-accent, var(--primary));
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
  max-width: 1200px;
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
  color: var(--mso-accent, var(--primary));
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
  background: var(--mso-pink-dark);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--mso-accent, var(--primary));
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
}

.id-badge {
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 6px;
  color: #475569;
  font-size: 0.85rem;
  border: 1px solid #e2e8f0;
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

.meta-badge.access,
.meta-badge.access-public,
.meta-badge.access-open {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.meta-badge.access-internal {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.meta-badge.access-restricted {
  background: #fff1f2;
  color: #e11d48;
  border: 1px solid #fecdd3;
}

.meta-badge.access-pii {
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
}

.meta-item {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: var(--mso-accent, var(--primary));
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
  transition: all 0.2s;
}

.btn-outline.is-active, .btn-outline:hover {
  background-color: var(--mso-pink-dark);
  color: var(--mso-accent, var(--primary));
  border-color: var(--mso-accent, var(--primary));
}

.tabs-container {
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid #f1f5f9;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #f1f5f9;
  padding: 0 24px;
  background: #fafafa;
}

.tab-btn {
  padding: 20px 24px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 0.95rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  color: var(--mso-accent, var(--primary));
  border-bottom-color: var(--mso-accent, var(--primary));
}

.tab-content {
  padding: 40px;
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
  color: var(--mso-accent, var(--primary));
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 20px 6px;
  background-color: var(--mso-pink-dark);
  border-bottom: 1px solid #cbd5e1;
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
  border: 1px solid #f1f5f9;
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
  min-width: 70px;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background-color: #e2e8f0;
  color: #94a3b8;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: not-allowed;
  transition: all 0.2s;
  text-align: center;
}

.btn-download:not(:disabled) {
  background-color: #008236;
  color: #ffffff;
  border-color: #008236;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 130, 54, 0.2);
}

.btn-download:hover:not(:disabled) {
  background-color: #00682b;
  border-color: #00682b;
  color: #ffffff;
  transform: translateY(-1px);
}

.btn-download:disabled, .btn-download.disabled {
  background-color: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
  border-color: #cbd5e1;
  opacity: 0.85;
}

.btn-primary-outline {
  background: none;
  border: 1.5px solid var(--mso-accent, var(--primary));
  color: var(--mso-accent, var(--primary));
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary-outline:hover {
  background-color: var(--mso-accent, var(--primary));
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

.transition-fade {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 1024px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  .detail-content {
    padding: 20px;
  }
}
</style>
