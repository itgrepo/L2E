<script setup>
import { ref, onMounted, watch, computed, onActivated, reactive } from 'vue';
import { useRoute } from 'vue-router';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData, postWithUser } from '../utils/api';

const route = useRoute();

const activeTab = ref('create');
const tabs = [
  { id: 'create', name: 'สร้างชุดข้อมูล', icon: 'M12 4v16m8-8H4' },
  { id: 'edit', name: 'แก้ไขชุดข้อมูล', icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z' },
  { id: 'file', name: 'เพิ่มไฟล์', icon: 'M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { id: 'link', name: 'เพิ่มลิงก์', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1' },
  { id: 'api', name: 'สร้าง API', icon: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' }
];

const formData = ref({
  dataset_id: '',
  l2e_group_id: '',
  source_system_id: '',
  category: '',
  sub_category: '',
  status: 'Inactive', // Match portal default
  service_name: '',
  organization: '',
  access_type: '',
  contact_name: '', // Will be used for "ชื่อฝ่ายงานสำหรับติดต่อ"
  contact_email: '',
  tags: '',
  description: '',
  purpose: '',
  // M-Society Gap Alignment
  dept_contact: '',
  update_freq_unit: 'เลือกหน่วยความถี่',
  update_freq_value: 0,
  geo_scope: 'เลือกขอบเขตเชิงภูมิศาสตร์หรือพื้นที่',
  data_source: '',
  data_format: [],
  gov_category: 'เลือกหมวดหมู่ข้อมูลตามธรรมาภิบาลข้อมูลภาครัฐ',
  license: 'เลือกสัญญาอนุญาตให้ใช้ข้อมูล',
  access_conditions: '',
  sponsor: 'เลือกผู้สนับสนุนหรือผู้ร่วมดำเนินการ',
  smallest_unit: 'เลือกหน่วยที่ย่อยที่สุดของการจัดเก็บข้อมูล',
  url: '',
  languages: [],
  objective_type: '',
  external_dashboard_url: '',
  external_api_url: ''
});

const isSubmitting = ref(false);
const successMessage = ref('');
const errorMessage = ref('');
const editingId = ref(null);
const datasets = ref([]);
const datasetGroups = ref([]);
const sourceSystems = ref([]);

const fetchMasters = async () => {
  try {
    const userParam = getUserParam ? getUserParam() : '';
    const groupRes = await apiClient.post('/getDatasetGroups', { user: userParam });
    if (groupRes.data) {
      datasetGroups.value = groupRes.data;
    }
    const sysRes = await apiClient.post('/getSourceSystems', { user: userParam });
    if (sysRes.data) {
      sourceSystems.value = sysRes.data;
    }
  } catch (err) {
    console.error('Error fetching masters:', err);
  }
};

const fetchDatasets = async () => {
  try {
    // Use retrieveService which works without admin auth
    const response = await apiClient.get('/retrieveService');
    if (response.data && response.data.data) {
      datasets.value = response.data.data;
    } else if (Array.isArray(response.data)) {
      datasets.value = response.data;
    }
  } catch (error) {
    console.error('Fetch error:', error);
    // Fallback to getService if retrieveService fails
    try {
      const userData = localStorage.getItem('user');
      const res = await apiClient.post('/getService', {
        user: encodeUserData(JSON.parse(userData))
      });
      if (res.data.status === 'success') {
        datasets.value = res.data.data;
      }
    } catch (e) {
      console.error('Fallback fetch also failed:', e);
    }
  }
};

const checkEditQuery = () => {
  if (route.query.edit) {
    const item = datasets.value.find(d => String(d.service_id) === String(route.query.edit));
    if (item) {
      selectForEdit(item);
    }
  }
};

onMounted(async () => {
  await fetchCategories();
  fetchOrganizations();
  await fetchMasters();
  await fetchDatasets();
  checkEditQuery();
});

onActivated(() => {
  checkEditQuery();
});

watch(() => route.query.edit, () => {
  checkEditQuery();
});

const selectForEdit = (item) => {
  editingId.value = item.service_id;
  formData.value = {
    dataset_id: item.dataset_id || '',
    l2e_group_id: item.l2e_group_id || '',
    source_system_id: item.source_system_id || '',
    category: item.category || '',
    sub_category: item.sub_category || '',
    status: item.status || 'Inactive',
    service_name: item.service_name || '',
    organization: item.organization || '',
    access_type: item.access_type || '',
    contact_name: item.contact_name || '',
    contact_email: item.contact_email || '',
    tags: item.tags || '',
    description: item.description || '',
    purpose: item.purpose || '',
    dept_contact: item.dept_contact || '',
    update_freq_unit: item.update_freq_unit || 'วัน',
    update_freq_value: item.update_freq_value || 1,
    geo_scope: item.geo_scope || 'ระดับประเทศ',
    data_source: item.data_source || '',
    data_format: item.data_format ? item.data_format.split(',') : [],
    gov_category: item.gov_category || 'ข้อมูลสาธารณะ',
    license: item.license || 'Open Data Common',
    access_conditions: item.access_conditions || '',
    sponsor: item.sponsor || '',
    smallest_unit: item.smallest_unit || 'รายระเบียน',
    url: item.url || '',
    languages: item.languages ? item.languages.split(',') : ['Thai'],
    objective_type: item.objective_type || 'ภารกิจหน่วยงาน',
    external_dashboard_url: item.external_dashboard_url || '',
    external_api_url: item.external_api_url || '',
    date_start: item.date_start || '',
    date_updated: item.date_updated || '',
    is_high_value: item.is_high_value || 'ไม่ใช่',
    is_reference: item.is_reference || 'ไม่ใช่',
    dataset_type: item.dataset_type || 'record',
    stat_year_start: item.stat_year_start || '',
    stat_year_latest: item.stat_year_latest || '',
    stat_classification: item.stat_classification || '',
    stat_unit: item.stat_unit || '',
    stat_multiplier: item.stat_multiplier || '',
    stat_calculation_method: item.stat_calculation_method || '',
    stat_standard: item.stat_standard || '',
    stat_official: item.stat_official || 'ไม่ใช่',
    geo_dataset_name: item.geo_dataset_name || '',
    geo_scale: item.geo_scale || '',
    geo_west_bound: item.geo_west_bound || '',
    geo_east_bound: item.geo_east_bound || '',
    geo_north_bound: item.geo_north_bound || '',
    geo_south_bound: item.geo_south_bound || '',
    geo_position_accuracy: item.geo_position_accuracy || '',
    geo_reference_time: item.geo_reference_time || '',
    geo_published_date: item.geo_published_date || ''
  };
  activeTab.value = 'create';
};

const resetForm = () => {
  editingId.value = null;
  formData.value = {
    dataset_id: '',
    category: '',
    sub_category: '',
    status: 'Inactive',
    service_name: '',
    organization: '',
    access_type: '',
    contact_name: '',
    contact_email: '',
    tags: '',
    description: '',
    purpose: '',
    dept_contact: '',
    update_freq_unit: 'เลือกหน่วยความถี่',
    update_freq_value: 0,
    geo_scope: 'เลือกขอบเขตเชิงภูมิศาสตร์หรือพื้นที่',
    data_source: '',
    data_format: [],
    gov_category: 'เลือกหมวดหมู่ข้อมูลตามธรรมาภิบาลข้อมูลภาครัฐ',
    license: 'เลือกสัญญาอนุญาตให้ใช้ข้อมูล',
    access_conditions: '',
    sponsor: 'เลือกผู้สนับสนุนหรือผู้ร่วมดำเนินการ',
    smallest_unit: 'เลือกหน่วยที่ย่อยที่สุดของการจัดเก็บข้อมูล',
    url: '',
    languages: [],
    objective_type: '',
    external_dashboard_url: '',
    external_api_url: '',
    dataset_type: 'record',
    stat_year_start: '',
    stat_year_latest: '',
    stat_classification: '',
    stat_unit: '',
    stat_multiplier: '',
    stat_calculation_method: '',
    stat_standard: '',
    stat_official: 'ไม่ใช่',
    geo_dataset_name: '',
    geo_scale: '',
    geo_west_bound: '',
    geo_east_bound: '',
    geo_north_bound: '',
    geo_south_bound: '',
    geo_position_accuracy: '',
    geo_reference_time: '',
    geo_published_date: ''
  };
};

const selectedFile = ref(null);
const uploadDatasetId = ref('');
const fileType = ref('dictionary');

const linkType = ref('api');
const linkDatasetId = ref('');
const linkUrl = ref('');

const apiDatasetId = ref('');
const isApiEnabled = ref(true);
const apiType = ref('public');
const apiEndpoint = ref('');
const apiDbName = ref('');
const apiSourceType = ref('table');
const apiSourceName = ref('');
const apiRequestFields = ref([]);
const apiResponseFields = ref([]);

// Cascade data
const availableDatabases = ref([]);
const availableTables = ref([]);
const availableColumns = ref([]);
const isLoadingMeta = ref(false);

const fetchDatabases = async () => {
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await postWithUser('/getAvailableDatabases', userData);
    if (res.data.status === 'success') availableDatabases.value = res.data.data;
  } catch (e) { console.error('DB fetch error:', e); }
};

const fetchTables = async (dbName) => {
  if (!dbName) { availableTables.value = []; return; }
  isLoadingMeta.value = true;
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await postWithUser('/getAvailableTables', userData, { db_name: dbName });
    if (res.data.status === 'success') availableTables.value = res.data.data;
  } catch (e) { console.error('Table fetch error:', e); }
  finally { isLoadingMeta.value = false; }
};

const fetchColumns = async (dbName, tableName) => {
  if (!dbName || !tableName) { availableColumns.value = []; return; }
  isLoadingMeta.value = true;
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await postWithUser('/getTableColumns', userData, { db_name: dbName, table_name: tableName });
    if (res.data.status === 'success') availableColumns.value = res.data.data;
  } catch (e) { console.error('Column fetch error:', e); }
  finally { isLoadingMeta.value = false; }
};

watch(apiDbName, (val) => {
  apiSourceName.value = '';
  availableColumns.value = [];
  apiRequestFields.value = [];
  apiResponseFields.value = [];
  fetchTables(val);
});

watch(apiSourceName, (val) => {
  apiRequestFields.value = [];
  apiResponseFields.value = [];
  if (val && apiDbName.value) {
    const t = availableTables.value.find(t => t.name === val);
    if (t) apiSourceType.value = t.type;
    fetchColumns(apiDbName.value, val);
  }
});

watch(apiDatasetId, (newId) => {
  if (newId) {
    const ds = datasets.value.find(d => d.service_id === newId);
    isApiEnabled.value = ds ? (ds.api_enabled == true || ds.api_enabled == 1) : false;
    apiType.value = ds?.api_type || 'public';
    apiEndpoint.value = ds?.api_endpoint || '';
    apiDbName.value = ds?.api_db_name || '';
    apiSourceType.value = ds?.api_source_type || 'table';
    apiSourceName.value = ds?.api_source_name || '';
    try {
      apiRequestFields.value = ds?.api_request_fields ? (typeof ds.api_request_fields === 'string' ? JSON.parse(ds.api_request_fields) : ds.api_request_fields) : [];
      apiResponseFields.value = ds?.api_response_fields ? (typeof ds.api_response_fields === 'string' ? JSON.parse(ds.api_response_fields) : ds.api_response_fields) : [];
    } catch { apiRequestFields.value = []; apiResponseFields.value = []; }
    if (ds?.api_db_name) fetchDatabases();
  }
});

const toggleRequestField = (name) => {
  const idx = apiRequestFields.value.indexOf(name);
  if (idx >= 0) apiRequestFields.value.splice(idx, 1);
  else apiRequestFields.value.push(name);
};
const toggleResponseField = (name) => {
  const idx = apiResponseFields.value.indexOf(name);
  if (idx >= 0) apiResponseFields.value.splice(idx, 1);
  else apiResponseFields.value.push(name);
};

const handleApiConfigSubmit = async () => {
  if (!apiDatasetId.value) {
    errorMessage.value = 'กรุณาเลือกชุดข้อมูล';
    return;
  }
  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await postWithUser('/saveApiConfig', userData, {
      service_id: apiDatasetId.value,
      api_enabled: isApiEnabled.value,
      api_type: apiType.value,
      api_endpoint: apiEndpoint.value,
      api_db_name: apiDbName.value,
      api_source_type: apiSourceType.value,
      api_source_name: apiSourceName.value,
      api_request_fields: apiRequestFields.value,
      api_response_fields: apiResponseFields.value
    });
    if (res.data.status === 'success') {
      successMessage.value = 'บันทึกการตั้งค่า API เรียบร้อยแล้ว';
      fetchDatasets();
    } else {
      errorMessage.value = res.data.status || 'เกิดข้อผิดพลาด';
    }
  } catch(e) {
    console.error('API config error:', e);
    errorMessage.value = 'เกิดข้อผิดพลาดในการบันทึก';
  } finally {
    isSubmitting.value = false;
  }
};

const handleLinkSubmit = async () => {
  if (!linkDatasetId.value || !linkUrl.value) {
    errorMessage.value = 'โปรดเลือกชุดข้อมูลและกรอก URL';
    return;
  }
  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    const userData = localStorage.getItem('user');
    const fd = new FormData();
    fd.append('user', encodeUserData(JSON.parse(userData)));
    fd.append('service_id', linkDatasetId.value);
    
    // We only update the specific link field
    if (linkType.value === 'api') {
      fd.append('external_api_url', linkUrl.value);
    } else {
      fd.append('external_dashboard_url', linkUrl.value);
    }

    const response = await apiClient.put('/addService', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    if (response.data.status.includes('success')) {
      successMessage.value = 'บันทึกลิงก์สำเร็จ!';
      linkUrl.value = '';
      linkDatasetId.value = '';
    } else {
      errorMessage.value = response.data.status || 'เกิดข้อผิดพลาดในการบันทึก';
    }
  } catch (error) {
    console.error('Link update error:', error);
    errorMessage.value = 'ไม่สามารถบันทึกลิงก์ได้';
  } finally {
    isSubmitting.value = false;
  }
};

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
  }
};

const triggerFileUpload = () => {
  document.getElementById('fileInput').click();
};

const handleFileUpload = async () => {
  if (!uploadDatasetId.value || !selectedFile.value) {
    errorMessage.value = 'โปรดเลือกชุดข้อมูลและไฟล์ที่ต้องการอัปโหลด';
    return;
  }

  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';

  try {
    const userData = localStorage.getItem('user');
    const fd = new FormData();
    fd.append('user', encodeUserData(JSON.parse(userData)));
    fd.append('service_id', uploadDatasetId.value);
    fd.append('data_file', selectedFile.value);
    fd.append('file_type', fileType.value);

    const response = await apiClient.put('/addService', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    if (response.data.status.includes('success')) {
      successMessage.value = 'อัปโหลดไฟล์สำเร็จ!';
      selectedFile.value = null;
      uploadDatasetId.value = '';
    } else {
      errorMessage.value = response.data.status || 'เกิดข้อผิดพลาดในการอัปโหลด';
    }
  } catch (error) {
    console.error('Upload error:', error);
    errorMessage.value = 'ไม่สามารถอัปโหลดไฟล์ได้';
  } finally {
    isSubmitting.value = false;
  }
};

const handleSubmit = async () => {
  isSubmitting.value = true;
  successMessage.value = '';
  errorMessage.value = '';
  
  try {
    const userData = localStorage.getItem('user');
    const fd = new FormData();
    fd.append('user', encodeUserData(JSON.parse(userData))); 
    
    // Add all metadata fields
    Object.keys(formData.value).forEach(key => {
      let value = formData.value[key];
      if (Array.isArray(value)) value = value.join(',');
      fd.append(key, value);
    });
    
    // Compatibility fields
    fd.append('service_url', '#');
    fd.append('service_status', formData.value.status);
    
    if (editingId.value) {
      fd.append('service_id', editingId.value);
    }

    const endpoint = '/addService';
    const method = editingId.value ? 'put' : 'post';
    
    const response = await apiClient[method](endpoint, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    if (response.data.status.includes('success')) {
      successMessage.value = editingId.value ? 'อัปเดตข้อมูลสำเร็จ!' : 'บันทึกข้อมูลชุดข้อมูลสำเร็จ!';
      if (!editingId.value) resetForm();
      fetchDatasets();
    } else {
      errorMessage.value = response.data.status || 'เกิดข้อผิดพลาดในการบันทึก';
    }
  } catch (error) {
    console.error('Submit error:', error);
    errorMessage.value = 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้';
  } finally {
    isSubmitting.value = false;
  }
};

// L2E Category Mapping
const categoryMap = reactive({
  'Learning Catalog': ['Course / Learning Offerings'],
  'Learning Record': ['Course Completion / Credit Earned'],
  'Learner Profile': ['Competency / Profile / Career Interest'],
  'Job Market': ['Vacancy / Labour Demand'],
  'Skill Intelligence': ['Skill Demand / Gap / Salary Insight']
});

const showAddSubCatModal = ref(false);
const newSubCatName = ref('');

const modalSelectedCategory = ref('');

const handleAddSubCategory = async () => {
  if (!newSubCatName.value.trim()) return;
  const cat = modalSelectedCategory.value;
  if (!cat) {
    alert('กรุณาเลือกหมวดหมู่หลักก่อนเพิ่มหมวดหมู่ย่อย');
    return;
  }
  
  const subName = newSubCatName.value.trim();
  
  try {
    const userData = localStorage.getItem('user') || '';
    const res = await apiClient.post('/addSubCategory', {
      user: userData ? encodeUserData(JSON.parse(userData)) : '',
      category_name: cat,
      sub_category_name: subName
    });
    
    if (res.data && res.data.status === 'success') {
      await fetchCategories();
  fetchOrganizations(); // Refresh list
      formData.value.category = cat;
      setTimeout(() => {
        formData.value.sub_category = subName;
      }, 100);
      showAddSubCatModal.value = false;
      newSubCatName.value = '';
    } else {
      alert('Error: ' + (res.data.status || 'Failed'));
    }
  } catch (err) {
    console.error(err);
    alert('Failed to add sub-category');
  }
};

const organizations = ref([]);
const categoriesList = ref([]);


const fetchOrganizations = async () => {
  try {
    const userData = localStorage.getItem('user');
    const userParam = userData ? encodeUserData(JSON.parse(userData)) : '';
    const response = await apiClient.post('/getOrganizations', { user: userParam });
    if (response.data.status === 'success') {
      organizations.value = response.data.data;
    }
  } catch (error) {
    console.error('Error fetching organizations:', error);
  }
};

const availableOrganizations = computed(() => {
  return organizations.value.filter(org => org.is_active || (formData.value.organization && org.org_name === formData.value.organization));
});

const fetchCategories = async () => {
  try {
    const response = await apiClient.get('/retrieveCategories');
    if (response.data && response.data.status === 'success' && Array.isArray(response.data.data)) {
      categoriesList.value = response.data.data.map(c => c.name || c.category_name);
    }
    
    // Fetch Sub Categories
    const subRes = await apiClient.get('/retrieveSubCategories');
    if (subRes.data && subRes.data.status === 'success' && Array.isArray(subRes.data.data)) {
      // Clear and rebuild map
      for (let key in categoryMap) {
        delete categoryMap[key];
      }
      subRes.data.data.forEach(item => {
        if (!categoryMap[item.category_name]) categoryMap[item.category_name] = [];
        if (!categoryMap[item.category_name].includes(item.sub_category_name)) {
          categoryMap[item.category_name].push(item.sub_category_name);
        }
      });
    }
  } catch (error) {
    console.error('Fetch categories error:', error);
  }
};

const availableSubCategories = computed(() => {
  return categoryMap[formData.value.category] || [];
});

const onCategoryChange = () => {
  const subs = categoryMap[formData.value.category];
  if (subs && subs.length > 0) {
    formData.value.sub_category = subs[0];
  } else {
    formData.value.sub_category = '';
  }
};

const updateDatasetPrefix = () => {
  if (editingId.value) return; // ห้ามเขียนทับ Dataset ID เดิมอัตโนมัติ
  const selectedGroup = datasetGroups.value.find(g => g.id === formData.value.l2e_group_id);
  if (selectedGroup) {
    formData.value.dataset_id = selectedGroup.prefix;
  }
};

</script>

<template>
  <div class="config-layout">
    <AppSidebar />
    
    <main class="config-content">
      <header class="config-header">
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
            <li>
              <router-link to="/catalog" style="color: #64748b; text-decoration: none; transition: color 0.2s;" onmouseover="this.style.color='var(--primary)'" onmouseout="this.style.color='#64748b'">
                บัญชีข้อมูล
              </router-link>
            </li>
            <li>/</li>
            <li style="font-weight: 500; color: #1e293b;" aria-current="page">
              {{ editingId ? 'แก้ไขบัญชีข้อมูล' : 'ตั้งค่าบัญชีข้อมูล' }}
            </li>
          </ol>
        </nav>

        <div class="header-titles">
          <h1>Dataset Configuration</h1>
          <p>จัดการและตั้งค่าชุดข้อมูลในระบบ Intelligist DataX Portal</p>
        </div>
      </header>

      <div class="config-container">
        <div class="tabs-nav">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.icon" />
            </svg>
            {{ tab.name }}
          </button>
        </div>

        <div class="tab-content card">
          <!-- CREATE TAB -->
          <div v-if="activeTab === 'create'" class="form-section">
            <div class="section-header">
              <h2 class="section-title">{{ editingId ? 'แก้ไขชุดข้อมูล' : 'สร้างชุดข้อมูลใหม่' }}</h2>
              <button v-if="editingId" @click="resetForm" class="btn-cancel-mini">คืนค่าสถานะสร้างใหม่</button>
            </div>
            
            <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

            <form @submit.prevent="handleSubmit" class="config-form">
              <div class="dataset-type-selector mt-4 mb-6">
                <label class="block text-slate-700 font-semibold mb-2" style="font-size: 1.1rem; border-bottom: 2px solid var(--primary); padding-bottom: 0.5rem; display: inline-block;">ประเภทชุดข้อมูล (Dataset Type) *</label>
                <div class="flex flex-wrap gap-2 mt-2" style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                  <button 
                    type="button"
                    v-for="type in [
                      { id: 'record', name: 'ข้อมูลระเบียน' },
                      { id: 'statistic', name: 'ข้อมูลสถิติ' },
                      { id: 'geospatial', name: 'ข้อมูลภูมิสารสนเทศเชิงพื้นที่' },
                      { id: 'various', name: 'ข้อมูลหลากหลายประเภท' },
                      { id: 'other', name: 'ข้อมูลประเภทอื่นๆ' }
                    ]" 
                    :key="type.id"
                    @click="formData.dataset_type = type.id"
                    style="padding: 0.5rem 1rem; border-radius: 0.375rem; border: 1px solid #cbd5e1; font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: all 0.2s;"
                    :style="formData.dataset_type === type.id ? 'background-color: var(--primary); color: white; border-color: var(--primary);' : 'background-color: white; color: #475569;'"
                  >
                    {{ type.name }}
                  </button>
                </div>
              </div>

              <!-- Section 1: Basic Information -->
              <div class="form-section-block">
                <h3 class="block-title">1. ข้อมูลพื้นฐานชุดข้อมูล (Core Info)</h3>
                <div class="form-row">
                  <div class="form-group">
                    <label>กลุ่มชุดข้อมูล (Dataset Group) *</label>
                    <select v-model="formData.l2e_group_id" @change="updateDatasetPrefix" class="form-select-custom" required>
                      <option value="">เลือกกลุ่มชุดข้อมูล</option>
                      <option v-for="group in datasetGroups" :key="group.id" :value="group.id">{{ group.name }}</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>รหัสชุดข้อมูล * (Dataset ID)</label>
                    <input type="text" v-model="formData.dataset_id" placeholder="ตัวอย่าง Prefix ตามกลุ่มชุดข้อมูล เช่น CRS-" required>
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>ชื่อชุดข้อมูล * (Dataset Name)</label>
                    <input type="text" v-model="formData.service_name" placeholder="ชื่อภาษาไทย หรือ ภาษาอังกฤษ" required>
                  </div>
                  <div class="form-group">
                    <label>สถานะการเผยแพร่ *</label>
                    <select v-model="formData.status" class="form-select-custom" required>
                      <option value="Inactive">เลือกสถานะการใช้งาน(Inactive = ไม่แสดงผล / Active = แสดงผล )</option>
                      <option value="Active">Active</option>
                      <option value="Inactive">Inactive</option>
                    </select>
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>หมวดหมู่หลัก *</label>
                    <select v-model="formData.category" @change="onCategoryChange" required class="form-select-custom">
                      <option value="">เลือกหมวดหมู่ข้อมูลในหน้าหลัก</option>
                      <option v-for="cat in categoriesList" :key="cat" :value="cat">{{ cat }}</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>หมวดหมู่ย่อย *</label>
                    <div style="display: flex; gap: 8px;">
                      <select v-model="formData.sub_category" class="form-select-custom" required style="flex: 1;">
                        <option value="">เลือกหมวดหมู่ข้อมูลย่อยในหน้าหลัก</option>
                        <option v-for="sub in availableSubCategories" :key="sub" :value="sub">{{ sub }}</option>
                      </select>
                      <button type="button" class="btn-add" @click="showAddSubCatModal = true; modalSelectedCategory = formData.category" style="padding: 0 16px; border-radius: 8px; height: 42px;">
                        <span class="icon" style="margin-right: 0;">+</span>
                      </button>
                    </div>
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>หน่วยงานที่รับผิดชอบ (Organization Owner) *</label>
                    <select v-model="formData.organization" required class="form-select-custom">
                      <option value="">เลือกหน่วยงาน</option>
                      <option v-for="org in availableOrganizations" :key="org.org_id" :value="org.org_name">{{ org.org_name }}</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>ระบบต้นทาง (Source System) *</label>
                    <select v-model="formData.source_system_id" required class="form-select-custom">
                      <option value="">เลือกระบบต้นทาง</option>
                      <option v-for="sys in sourceSystems" :key="sys.id" :value="sys.id">{{ sys.name }}</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label>การเข้าถึง (Sensitivity) *</label>
                  <select v-model="formData.access_type" class="form-select-custom" required>
                    <option value="" disabled selected>เลือกการเข้าถึง</option>
                    <option value="public">สาธารณะ (Public)</option>
                    <option value="internal">ภายในหน่วยงาน (Internal)</option>
                    <option value="restricted">จำกัดสิทธิ์ (Restricted)</option>
                    <option value="pii">ข้อมูลส่วนบุคคล (PII)</option>
                  </select>
                  <small class="text-gray-500 mt-1 block">ระบุระดับความอ่อนไหวของข้อมูลเพื่อใช้บังคับสิทธิ์การเข้าถึง</small>
                </div>

                <div class="form-group">
                  <label>รายละเอียดชุดข้อมูล (Description)</label>
                  <textarea v-model="formData.description" rows="3" placeholder="อธิบายเกี่ยวกับชุดข้อมูลนี้..."></textarea>
                </div>
              </div>

              <!-- Section 2: Data Governance & Usage -->
              <div class="form-section-block mt-8">
                <h3 class="block-title">2. การธรรมาภิบาลและการใช้งาน (Governance)</h3>
                <div class="form-row">
                  <div class="form-group">
                    <label>หมวดหมู่ข้อมูลตามธรรมาภิบาลข้อมูลภาครัฐ *</label>
                    <select v-model="formData.gov_category" class="form-select-custom" required>
                      <option>เลือกหมวดหมู่ข้อมูลตามธรรมาภิบาลข้อมูลภาครัฐ</option>
                      <option>ข้อมูลส่วนบุคคล</option>
                      <option>ข้อมูลสาธารณะ</option>
                      <option>ข้อมูลลับ</option>
                      <option>ข้อมูลความมั่นคง</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>สัญญาอนุญาตให้ใช้ข้อมูล *</label>
                    <select v-model="formData.license" class="form-select-custom" required>
                      <option>เลือกสัญญาอนุญาตให้ใช้ข้อมูล</option>
                      <option>Open Data Common</option>
                      <option>Creative Commons Attribution</option>
                      <option>Creative Commons Attribution-ShareAlike</option>
                      <option>Creative Commons Attribution-NoDerivs</option>
                      <option>Creative Commons Attribution-NonCommercial</option>
                    </select>
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>ชุดข้อมูลที่มีคุณค่าสูง (High Value Dataset) *</label>
                    <select v-model="formData.is_high_value" class="form-select-custom" required>
                      <option>ใช่</option>
                      <option>ไม่ใช่</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>ข้อมูลอ้างอิง (Reference Data) *</label>
                    <select v-model="formData.is_reference" class="form-select-custom" required>
                      <option>ใช่</option>
                      <option>ไม่ใช่</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label>เงื่อนไขในการเข้าใช้ข้อมูล (Access Conditions)</label>
                  <textarea v-model="formData.access_conditions" rows="2" placeholder="เงื่อนไขเพื่อให้สามารถเข้าถึงหรือใช้ข้อมูลได้..."></textarea>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>วันที่เริ่มต้นสร้าง *</label>
                    <input type="date" v-model="formData.date_start" class="form-input-custom" required>
                  </div>
                  <div class="form-group">
                    <label>วันที่ปรับปรุงข้อมูลล่าสุด *</label>
                    <input type="date" v-model="formData.date_updated" class="form-input-custom" required>
                  </div>
                </div>

              <!-- DYNAMIC SECTION: RECORD / VARIOUS / OTHER -->
              <div v-if="['record', 'various', 'other'].includes(formData.dataset_type)">
                <div class="form-row">
                  <div class="form-group">
                    <label>ความถี่ที่เกี่ยวกับข้อมูล *</label>
                    <select v-model="formData.update_freq_unit" class="form-select-custom" required>
                      <option>เลือกหน่วยความถี่</option>
                      <option>ไม่ทราบ</option>
                      <option>รายวัน</option>
                      <option>รายสัปดาห์</option>
                      <option>รายเดือน</option>
                      <option>รายไตรมาส</option>
                      <option>รายครึ่งปี</option>
                      <option>รายปี</option>
                      <option>วันทำการ</option>
                      <option>ทุกครั้งที่มีการเปลี่ยนข้อมูล</option>
                      <option>อื่นๆ</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>เลขจำนวนที่ประกอบกับหน่วยความถี่ (ครั้ง/หน่วยความถี่) *</label>
                    <input type="number" v-model="formData.update_freq_value" placeholder="เลขจำนวนที่ประกอบกับหน่วยความถี่" required>
                  </div>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>ขอบเขตเชิงภูมิศาสตร์หรือพื้นที่ *</label>
                    <select v-model="formData.geo_scope" class="form-select-custom" required>
                      <option>เลือกขอบเขตเชิงภูมิศาสตร์หรือพื้นที่</option>
                      <option>ไม่มี</option>
                      <option>ระดับเมือง</option>
                      <option>ระดับตำบล</option>
                      <option>ระดับอำเภอ</option>
                      <option>ระดับจังหวัด</option>
                      <option>ระดับลุ่มน้ำ/ระดับกลุ่มจังหวัด</option>
                      <option>ระดับประเทศ</option>
                      <option>ระดับภูมิภาค</option>
                      <option>ระดับระหว่างประเทศ</option>
                      <option>อื่นๆ</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>หน่วยที่ย่อยที่สุดของการจัดเก็บข้อมูล *</label>
                    <select v-model="formData.smallest_unit" class="form-select-custom" required>
                      <option>เลือกหน่วยที่ย่อยที่สุดของการจัดเก็บข้อมูล</option>
                      <option>ไม่มี</option>
                      <option>รายระเบียน</option>
                      <option>รายบุคคล</option>
                      <option>รายครัวเรือน</option>
                      <option>รายองค์กร</option>
                      <option>อื่นๆ</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label>ผู้สนับสนุนหรือผู้ร่วมดำเนินการ *</label>
                  <select v-model="formData.sponsor" class="form-select-custom" required>
                    <option>เลือกผู้สนับสนุนหรือผู้ร่วมดำเนินการ</option>
                    <option>ไม่มี</option>
                    <option>กระทรวงดิจิทัลเพื่อเศรษฐกิจและสังคม</option>
                    <option>อื่นๆ</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>วัตถุประสงค์ *</label>
                  <div class="radio-vertical-list">
                    <label v-for="obj in [
                      'ยุทธศาสตร์ชาติ', 'แผนพัฒนาเศรษฐกิจและสังคมแห่งชาติ', 'แผนความมั่นคงแห่งชาติ',
                      'แผนแม่บทภายใต้ยุทธศาสตร์ชาติ', 'แผนปฏิรูปประเทศ', 'แผนระดับที่ 3 (มติครม. 4 ธ.ค. 2560)',
                      'นโยบายรัฐบาล/ข้อสั่งการนายกรัฐมนตรี', 'มติคณะรัฐมนตรี', 'เพื่อการให้บริการประชาชน',
                      'กฎหมายที่เกี่ยวข้อง', 'พันธกิจหน่วยงาน', 'ดัชนี/ตัวชี้วัดระดับนานาชาติ', 'ไม่ทราบ', 'อื่นๆ'
                    ]" :key="obj" class="radio-label-v">
                      <input type="radio" :value="obj" v-model="formData.objective_type" required> <span>{{ obj }}</span>
                    </label>
                  </div>
                </div>

                <div class="form-group">
                  <label>รูปแบบการเก็บข้อมูล *</label>
                  <div class="checkbox-grid-3">
                    <label v-for="fmt in [
                      'csv', 'xlsx', 'ฐานข้อมูล', 'image', 'video', 'audio', 'text', 'json', 'html',
                      'xls', 'pdf', 'rdf', 'nosql', 'arcInfoCoverage', 'shapefile', 'geoTiff', 'gml', 'ไม่ทราบ'
                    ]" :key="fmt" class="checkbox-label">
                      <input type="checkbox" :value="fmt" v-model="formData.data_format"> <span>{{ fmt }}</span>
                    </label>
                  </div>
                </div>
              </div>

              </div>

              <!-- DYNAMIC SECTION: STATISTIC -->
              <div v-if="formData.dataset_type === 'statistic'" class="form-section-block mt-8" style="border-left: 4px solid #0ea5e9; padding-left: 1rem;">
                <h3 class="block-title text-sky-600">ข้อมูลเฉพาะ: ข้อมูลสถิติ</h3>
                <div class="form-row">
                  <div class="form-group">
                    <label>ปีข้อมูลที่เริ่มต้นจัดทำ *</label>
                    <input type="text" v-model="formData.stat_year_start" class="form-input-custom" placeholder="เช่น 2560" required>
                  </div>
                  <div class="form-group">
                    <label>ปีข้อมูลล่าสุดที่เผยแพร่ *</label>
                    <input type="text" v-model="formData.stat_year_latest" class="form-input-custom" placeholder="เช่น 2566" required>
                  </div>
                </div>
                <div class="form-group">
                  <label>การจัดจำแนก *</label>
                  <input type="text" v-model="formData.stat_classification" class="form-input-custom" placeholder="ระบุการจัดจำแนก" required>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>หน่วยวัด *</label>
                    <input type="text" v-model="formData.stat_unit" class="form-input-custom" placeholder="เช่น คน, บาท, ราย" required>
                  </div>
                  <div class="form-group">
                    <label>หน่วยตัวคูณ *</label>
                    <input type="text" v-model="formData.stat_multiplier" class="form-input-custom" placeholder="เช่น พัน, ล้าน" required>
                  </div>
                </div>
                <div class="form-group">
                  <label>วิธีการคำนวณ *</label>
                  <textarea v-model="formData.stat_calculation_method" rows="2" placeholder="อธิบายสูตรหรือวิธีการคำนวณ..." required></textarea>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>มาตรฐานการจัดทำข้อมูล *</label>
                    <input type="text" v-model="formData.stat_standard" class="form-input-custom" placeholder="ระบุมาตรฐานที่ใช้อ้างอิง" required>
                  </div>
                  <div class="form-group">
                    <label>สถิติทางการ *</label>
                    <select v-model="formData.stat_official" class="form-select-custom" required>
                      <option>ใช่</option>
                      <option>ไม่ใช่</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- DYNAMIC SECTION: GEOSPATIAL -->
              <div v-if="formData.dataset_type === 'geospatial'" class="form-section-block mt-8" style="border-left: 4px solid var(--primary); padding-left: 1rem;">
                <h3 class="block-title text-[var(--primary)]">ข้อมูลเฉพาะ: ข้อมูลภูมิสารสนเทศเชิงพื้นที่</h3>
                <div class="form-row">
                  <div class="form-group">
                    <label>ชุดข้อมูลภูมิศาสตร์ *</label>
                    <input type="text" v-model="formData.geo_dataset_name" class="form-input-custom" placeholder="ชื่อชุดข้อมูลภูมิศาสตร์" required>
                  </div>
                  <div class="form-group">
                    <label>มาตราส่วน *</label>
                    <input type="text" v-model="formData.geo_scale" class="form-input-custom" placeholder="เช่น 1:50000" required>
                  </div>
                </div>
                
                <h4 class="font-semibold text-slate-700 mb-2 mt-4" style="font-size: 0.95rem;">กรอบพื้นที่ (Bounding Box) *</h4>
                <div class="form-row" style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; margin-bottom: 1rem;">
                  <div class="form-group">
                    <label>ทิศตะวันตก (West)</label>
                    <input type="text" v-model="formData.geo_west_bound" class="form-input-custom" placeholder="Longitude" required>
                  </div>
                  <div class="form-group">
                    <label>ทิศตะวันออก (East)</label>
                    <input type="text" v-model="formData.geo_east_bound" class="form-input-custom" placeholder="Longitude" required>
                  </div>
                  <div class="form-group">
                    <label>ทิศเหนือ (North)</label>
                    <input type="text" v-model="formData.geo_north_bound" class="form-input-custom" placeholder="Latitude" required>
                  </div>
                  <div class="form-group">
                    <label>ทิศใต้ (South)</label>
                    <input type="text" v-model="formData.geo_south_bound" class="form-input-custom" placeholder="Latitude" required>
                  </div>
                </div>

                <div class="form-group">
                  <label>ความถูกต้องของตำแหน่ง *</label>
                  <input type="text" v-model="formData.geo_position_accuracy" class="form-input-custom" placeholder="ระบุความคลาดเคลื่อน (ถ้ามี)" required>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>เวลาอ้างอิง *</label>
                    <input type="text" v-model="formData.geo_reference_time" class="form-input-custom" placeholder="ระบุเวลาอ้างอิงของข้อมูลพิกัด" required>
                  </div>
                  <div class="form-group">
                    <label>วันที่เผยแพร่ข้อมูล *</label>
                    <input type="date" v-model="formData.geo_published_date" class="form-input-custom" required>
                  </div>
                </div>
              </div>

              <!-- Section 3: Contact & Additional Tech -->
              <div class="form-section-block mt-8">
                <h3 class="block-title">3. ช่องทางติดต่อและข้อมูลเชิงเทคนิค (Support & Technical)</h3>
                <div class="form-row">
                  <div class="form-group">
                    <label>ชื่อฝ่ายงานสำหรับติดต่อ * (Contact Department)</label>
                    <input type="text" v-model="formData.contact_name" placeholder="ชื่อหน่วยงานหรือกลุ่มงาน" required>
                  </div>
                  <div class="form-group">
                    <label>อีเมลติดต่อ * (Contact Email)</label>
                    <input type="email" v-model="formData.contact_email" placeholder="department@org.go.th" required>
                  </div>
                </div>

                <div class="form-group">
                    <label>คำสำคัญ * (Tags)</label>
                    <input type="text" v-model="formData.tags" placeholder="คั่นด้วยเครื่องหมายจุลภาค เช่น เศรษฐกิจ, สุขภาพจิต (เลือกได้สูงสุด 10 แท็ก)" required>
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>แหล่งที่มาเพิ่มเติม (Legacy Data Source Fallback)</label>
                    <input type="text" v-model="formData.data_source" placeholder="ข้อมูลแหล่งที่มาเพิ่มเติม (หากไม่มีใน Dropdown ระบบต้นทาง)">
                  </div>
                  <div class="form-group">
                    <label>URL รายละเอียดชุดข้อมูล *</label>
                    <input type="url" v-model="formData.url" placeholder="URL ที่สามารถเข้าถึงรายละเอียดของชุดข้อมูลได้" required>
                  </div>
                </div>

                <div class="form-group">
                  <label>ภาษาที่ใช้ *</label>
                  <div class="checkbox-grid-3">
                    <label v-for="lang in ['ไทย', 'อังกฤษ', 'จีน', 'มลายู', 'พม่า', 'ลาว', 'เขมร', 'ญี่ปุ่น', 'เกาหลี', 'ฝรั่งเศษ']" :key="lang" class="checkbox-label">
                      <input type="checkbox" :value="lang" v-model="formData.languages"> <span>{{ lang }}</span>
                    </label>
                  </div>
                </div>
              </div>

              <!-- Section 4: Dashboards & External APIs -->
              <div class="form-section-block mt-8">
                <h3 class="block-title">4. แดชบอร์ดและ API หน้าบ้าน (Visualization & API)</h3>
                <div class="form-group">
                  <label>ลิงก์ Dashboard (Tableau, PowerBI, ฯลฯ)</label>
                  <input type="url" v-model="formData.external_dashboard_url" placeholder="https://public.tableau.com/...">
                </div>
                <div class="form-group">
                  <label>ลิงก์ API ภายนอก</label>
                  <input type="url" v-model="formData.external_api_url" placeholder="https://api.org.go.th/...">
                </div>
              </div>

              <div class="form-actions">
                <button type="button" @click="resetForm" class="btn-cancel">ล้างค่า</button>
                <button type="submit" class="btn-save" :disabled="isSubmitting">
                  {{ isSubmitting ? 'กำลังบันทึก...' : (editingId ? 'บันทึกการแก้ไข' : 'สร้างชุดข้อมูล') }}
                </button>
              </div>
            </form>
          </div>

          <!-- EDIT TAB -->
          <div v-else-if="activeTab === 'edit'" class="edit-section">
            <div class="section-header">
              <h2 class="section-title">แก้ไขชุดข้อมูล</h2>
              <div class="search-box-mini">
                <input type="text" placeholder="ค้นหาชุดข้อมูล...">
              </div>
            </div>
            
            <div class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Dataset ID</th>
                    <th>ชื่อชุดข้อมูล</th>
                    <th>หมวดหมู่</th>
                    <th>สถานะ</th>
                    <th class="text-center">จัดการ</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in datasets" :key="item.service_id">
                    <td class="font-mono">{{ item.dataset_id || '-' }}</td>
                    <td class="font-bold">{{ item.service_name }}</td>
                    <td>{{ item.category || '-' }}</td>
                    <td><span class="status-badge" :class="item.status?.toLowerCase()">{{ item.status }}</span></td>
                    <td class="text-center">
                      <button @click="selectForEdit(item)" class="btn-icon-edit">แก้ไข</button>
                    </td>
                  </tr>
                  <tr v-if="datasets.length === 0">
                    <td colspan="5" class="text-center py-8 text-slate-400">ไม่พบข้อมูลชุดข้อมูล</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- FILE TAB -->
          <div v-else-if="activeTab === 'file'" class="file-section">
            <h2 class="section-title">เพิ่มไฟล์ข้อมูล</h2>
            
            <div class="form-group" style="max-width: 600px; margin-bottom: 24px;">
              <label>เลือกชุดข้อมูลที่ต้องการเพิ่มไฟล์ *</label>
              <select v-model="uploadDatasetId" class="form-select-custom">
                <option value="">-- เลือกชุดข้อมูล --</option>
                <option v-for="ds in datasets" :key="ds.service_id" :value="ds.service_id">
                  {{ ds.service_name }} ({{ ds.dataset_id || ds.service_id }})
                </option>
              </select>
            </div>

            <div class="file-type-selector">
              <label class="radio-card">
                <input type="radio" value="dictionary" v-model="fileType">
                <div class="radio-card-content">
                  <span class="radio-circle"></span>
                  <span>Add Data Dictionary</span>
                </div>
              </label>
              <label class="radio-card">
                <input type="radio" value="excel" v-model="fileType">
                <div class="radio-card-content">
                  <span class="radio-circle"></span>
                  <span>Add Excel File For API</span>
                </div>
              </label>
              <label class="radio-card">
                <input type="radio" value="zip" v-model="fileType">
                <div class="radio-card-content">
                  <span class="radio-circle"></span>
                  <span>Add Zip File (Data Sampling)</span>
                </div>
              </label>
            </div>

            <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

            <div class="upload-zone" @click="triggerFileUpload">
              <input type="file" id="fileInput" @change="handleFileSelect" style="display: none;">
              <div class="upload-inner">
                <svg xmlns="http://www.w3.org/2000/svg" style="width: 48px; height: 48px; margin: 0 auto; color: #475569;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p v-if="!selectedFile">ลากไฟล์มาวางที่นี่ หรือ <span>คลิกเพื่อเลือกไฟล์</span></p>
                <p v-else class="text-green-600 font-bold">เลือกไฟล์แล้ว: {{ selectedFile.name }}</p>
                <span class="text-xs text-slate-400">รองรับไฟล์ CSV, XLS, XLSX, ZIP (สูงสุด 500MB)</span>
              </div>
            </div>

            <div class="form-actions">
              <button @click="handleFileUpload" class="btn-save" :disabled="isSubmitting || !selectedFile">
                {{ isSubmitting ? 'กำลังอัปโหลด...' : 'อัปโหลดไฟล์' }}
              </button>
            </div>
          </div>

          <!-- LINK TAB -->
          <div v-else-if="activeTab === 'link'" class="link-section" style="max-width: 800px; padding-top: 2rem;">
            <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

            <div class="flex items-center p-1 bg-slate-100 rounded-xl w-fit mb-10 mt-2 border border-slate-200 shadow-inner">
              <button 
                @click="linkType = 'api'" 
                class="flex items-center gap-2 px-6 py-2.5 rounded-lg font-bold transition-all duration-200"
                :class="linkType === 'api' 
                  ? 'bg-white text-emerald-700 shadow-sm ring-1 ring-slate-200' 
                  : 'text-slate-500 hover:text-slate-700'"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                เพิ่มลิงก์ API
              </button>
              <button 
                @click="linkType = 'dashboard'" 
                class="flex items-center gap-2 px-6 py-2.5 rounded-lg font-bold transition-all duration-200"
                :class="linkType === 'dashboard' 
                  ? 'bg-white text-emerald-700 shadow-sm ring-1 ring-slate-200' 
                  : 'text-slate-500 hover:text-slate-700'"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                เพิ่มลิงก์ DashBoard
              </button>
            </div>

            <div class="form-group mb-10">
              <label class="text-sm text-slate-700 font-bold mb-2">รหัสชุดข้อมูล</label>
              <select v-model="linkDatasetId" class="w-full bg-transparent border border-slate-200 rounded-xl focus:ring-0 focus:border-slate-400 text-slate-800 py-3 px-4 transition-colors" style="outline: none;">
                <option value="">รหัสชุดข้อมูล</option>
                <option v-for="ds in datasets" :key="ds.service_id" :value="ds.service_id">
                  {{ ds.dataset_id }} - {{ ds.service_name }}
                </option>
              </select>
            </div>

            <div class="form-group mb-12">
              <label class="text-sm text-slate-700 font-bold mb-2">{{ linkType === 'api' ? 'ลิงก์ API' : 'ลิงก์ DashBoard' }}</label>
              <input type="url" v-model="linkUrl" class="w-full bg-transparent border border-slate-200 rounded-xl focus:ring-0 focus:border-slate-400 text-slate-800 py-3 px-4 transition-colors" style="outline: none;" placeholder="https://example.com/api/v1/data">
            </div>

            <div class="flex justify-start">
              <button @click="handleLinkSubmit" class="flex items-center gap-2 px-6 py-2 rounded-lg border border-slate-200 text-[var(--primary)] bg-white hover:bg-slate-50 font-medium transition-all shadow-sm" :disabled="isSubmitting">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                </svg>
                <span style="font-weight: 600;">บันทึก</span>
              </button>
            </div>
          </div>

          <!-- API TAB -->
          <div v-else-if="activeTab === 'api'" class="api-section">
            <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>
            <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

            <div class="form-group mb-8">
              <label class="text-xs text-slate-500 font-bold tracking-wide uppercase">รหัสชุดข้อมูล</label>
              <select v-model="apiDatasetId" @change="fetchDatabases()" style="width:100%;padding:10px 16px;border:1.5px solid #e2e8f0;border-radius:10px;font-size:0.9375rem;outline:none;">
                <option value="">-- เลือกชุดข้อมูล --</option>
                <option v-for="ds in datasets" :key="ds.service_id" :value="ds.service_id">
                  {{ ds.dataset_id }} - {{ ds.service_name }}
                </option>
              </select>
            </div>

            <div v-if="apiDatasetId">
              <h2 class="section-title">ตั้งค่า API สำหรับชุดข้อมูล</h2>

              <!-- Toggle -->
              <div class="api-setup-card" style="margin-bottom:24px;">
                <div class="api-opt-item">
                  <div class="toggle-container">
                    <input type="checkbox" id="apiToggle" v-model="isApiEnabled">
                    <label for="apiToggle" class="toggle-slider"></label>
                  </div>
                  <span style="font-weight:600;color:#1e293b;">{{ isApiEnabled ? 'เปิดใช้งาน API Access แล้ว' : 'ปิดใช้งาน API Access' }}</span>
                </div>
              </div>

              <div v-if="isApiEnabled" class="api-setup-card" style="max-width:100%;">
                <!-- API Type -->
                <div class="form-row">
                  <div class="form-group">
                    <label>ประเภท API *</label>
                    <select v-model="apiType" style="padding:10px 16px;border:1.5px solid #e2e8f0;border-radius:10px;">
                      <option value="public">Public API (เปิดเผยข้อมูลสาธารณะ ไม่ต้องใช้ API Key)</option>
                      <option value="private">Private API (ต้องยืนยันตัวตนด้วย API Key และต้องผ่านการอนุมัติสิทธิ์)</option>
                      <option value="scope">Scope API (จำกัดขอบเขตข้อมูลตามเงื่อนไขผู้ใช้รายบุคคล)</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>API Endpoint Path *</label>
                    <input type="text" v-model="apiEndpoint" placeholder="เช่น my_dataset_api" style="padding:10px 16px;border:1.5px solid #e2e8f0;border-radius:10px;">
                  </div>
                </div>

                <!-- Data Source -->
                <h3 class="block-title" style="margin-top:16px;">แหล่งข้อมูล (Data Source)</h3>
                <div class="form-row">
                  <div class="form-group">
                    <label>Database *</label>
                    <select v-model="apiDbName" style="padding:10px 16px;border:1.5px solid #e2e8f0;border-radius:10px;">
                      <option value="">-- เลือก Database --</option>
                      <option v-for="db in availableDatabases" :key="db" :value="db">{{ db }}</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Table / View *</label>
                    <select v-model="apiSourceName" :disabled="!apiDbName || isLoadingMeta" style="padding:10px 16px;border:1.5px solid #e2e8f0;border-radius:10px;">
                      <option value="">{{ isLoadingMeta ? 'กำลังโหลด...' : '-- เลือก Table/View --' }}</option>
                      <option v-for="t in availableTables" :key="t.name" :value="t.name">
                        {{ t.name }} ({{ t.type }})
                      </option>
                    </select>
                  </div>
                </div>

                <!-- Field Selection -->
                <div v-if="availableColumns.length > 0">
                  <h3 class="block-title" style="margin-top:16px;">เลือกฟิลด์ (Field Selection)</h3>
                  <div class="form-row" style="gap:32px;">
                    <div>
                      <label style="font-weight:700;color:#475569;margin-bottom:12px;display:block;">Request Fields (ฟิลด์ที่ใช้ Filter)</label>
                      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:16px;max-height:300px;overflow-y:auto;">
                        <label v-for="col in availableColumns" :key="'req_'+col.name" style="display:flex;align-items:center;gap:8px;padding:6px 0;cursor:pointer;font-size:0.875rem;color:#475569;">
                          <input type="checkbox" :checked="apiRequestFields.includes(col.name)" @change="toggleRequestField(col.name)">
                          <span>{{ col.name }}</span>
                          <span style="color:#94a3b8;font-size:0.75rem;margin-left:auto;">({{ col.type }})</span>
                        </label>
                      </div>
                    </div>
                    <div>
                      <label style="font-weight:700;color:#475569;margin-bottom:12px;display:block;">Response Fields (ฟิลด์ที่แสดงผล)</label>
                      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:16px;max-height:300px;overflow-y:auto;">
                        <label v-for="col in availableColumns" :key="'res_'+col.name" style="display:flex;align-items:center;gap:8px;padding:6px 0;cursor:pointer;font-size:0.875rem;color:#475569;">
                          <input type="checkbox" :checked="apiResponseFields.includes(col.name)" @change="toggleResponseField(col.name)">
                          <span>{{ col.name }}</span>
                          <span style="color:#94a3b8;font-size:0.75rem;margin-left:auto;">({{ col.type }})</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="form-actions" style="border:none;margin-top:24px;">
                  <button @click="handleApiConfigSubmit" class="btn-save" :disabled="isSubmitting">
                    {{ isSubmitting ? 'กำลังบันทึก...' : 'บันทึกการตั้งค่า API' }}
                  </button>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center" style="padding:48px 0;color:#94a3b8;">
              <svg xmlns="http://www.w3.org/2000/svg" style="width:48px;height:48px;margin:0 auto 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
              </svg>
              <p>กรุณาเลือกชุดข้อมูลด้านบนเพื่อจัดการการเข้าถึง API</p>
            </div>
          </div>
        </div>
      </div>
      <!-- Add Sub Category Modal -->
      <div v-if="showAddSubCatModal" class="modal-overlay">
        <div class="modal">
          <div class="modal-header">
            <h2>เพิ่มหมวดหมู่ย่อยใหม่</h2>
            <button class="btn-close" @click="showAddSubCatModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>หมวดหมู่หลัก</label>
              <select v-model="modalSelectedCategory" class="form-select-custom">
                <option value="">-- เลือกหมวดหมู่หลัก --</option>
                <option v-for="cat in categoriesList" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>
            <div class="form-group" style="margin-top: 16px;">
              <label>ชื่อหมวดหมู่ย่อย</label>
              <input v-model="newSubCatName" type="text" placeholder="ระบุชื่อหมวดหมู่ย่อย" class="form-input-custom" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showAddSubCatModal = false">ยกเลิก</button>
            <button class="btn-save" @click="handleAddSubCategory">บันทึกข้อมูล</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.config-layout {
  display: flex;
  background-color: #f8fafc;
  min-height: 100vh;
}

.config-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.config-header {
  padding: 40px 64px 20px;
  background-color: white;
  border-bottom: 1px solid #f1f5f9;
}

.header-titles h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.header-titles p {
  color: #64748b;
  font-size: 0.9375rem;
}

.config-container {
  padding: 32px 64px;
}

.tabs-nav {
  display: flex;
  background-color: var(--primary);
  border-radius: 12px 12px 0 0;
  overflow: hidden;
  padding: 8px 8px 0;
  gap: 4px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: transparent;
  border: none;
  color: #cbd5e1;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.2s;
}

.tab-btn:hover {
  background-color: rgba(255,255,255,0.1);
  color: white;
}

.tab-btn.active {
  background-color: white;
  color: var(--primary);
}

.card {
  background-color: white;
  border-radius: 0 0 16px 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  padding: 40px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 32px;
}

.config-form {
  max-width: 900px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
}

.form-group input, 
.form-group select, 
.form-group textarea {
  padding: 12px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.9375rem;
  transition: border-color 0.2s;
  outline: none;
}

.form-group input:focus, 
.form-group select:focus, 
.form-group textarea:focus {
  border-color: var(--primary);
}

.form-select-custom {
  background-color: white;
}

.radio-group {
  display: flex;
  gap: 32px;
  padding: 12px 0;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.9375rem;
  color: #475569;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 40px;
  padding-top: 32px;
  border-top: 1px solid #f1f5f9;
}

.form-section-block {
  background: #fff;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  padding: 24px;
}

.block-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--mso-pink-dark);
}

.input-inline {
  display: flex;
  gap: 12px;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 8px 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9375rem;
  color: #475569;
  cursor: pointer;
}

.mt-8 { margin-top: 2rem; }

.radio-vertical-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
}

.radio-label-v {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  font-size: 0.9375rem;
  color: #475569;
  transition: color 0.2s;
}

.radio-label-v:hover {
  color: var(--primary);
}

.checkbox-grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
}

@media (max-width: 1023px) {
  .checkbox-grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 767px) {
  .checkbox-grid-3 {
    grid-template-columns: 1fr;
  }
}

.btn-save {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save:hover:not(:disabled) {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: white;
  color: #64748b;
  border: 1.5px solid #e2e8f0;
  padding: 12px 32px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}

.btn-cancel-mini {
  background-color: #f1f5f9;
  color: #475569;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.alert {
  padding: 16px;
  border-radius: 10px;
  margin-bottom: 24px;
  font-weight: 500;
}

.alert-success {
  background-color: var(--mso-pink-dark);
  color: var(--primary);
  border: 1px solid #bbf7d0;
}

.alert-danger {
  background-color: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.placeholder-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #94a3b8;
  text-align: center;
}

.placeholder-tab h3 {
  margin-top: 24px;
  color: #1e293b;
}

/* Tab Specific Styles */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.search-box-mini input {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  width: 240px;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  background-color: #f8fafc;
  color: #64748b;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid #f1f5f9;
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
  color: #1e293b;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.active {
  background-color: var(--mso-pink-dark);
  color: var(--primary);
}

.btn-icon-edit {
  background-color: #f1f5f9;
  color: #475569;
  border: none;
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.file-type-selector {
  display: flex;
  gap: 20px;
  margin-bottom: 32px;
}

.radio-card {
  flex: 1;
  cursor: pointer;
}

.radio-card input {
  display: none;
}

.radio-card-content {
  padding: 20px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  transition: all 0.2s;
}

.radio-card input:checked + .radio-card-content {
  border-color: var(--primary);
  background-color: var(--mso-pink-dark);
  color: var(--primary);
}

.radio-circle {
  width: 18px;
  height: 18px;
  border: 2px solid #e2e8f0;
  border-radius: 50%;
  position: relative;
}

.radio-card input:checked + .radio-card-content .radio-circle::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 8px;
  height: 8px;
  background-color: var(--primary);
  border-radius: 50%;
}

.upload-zone {
  border: 2px dashed #e2e8f0;
  border-radius: 16px;
  padding: 60px;
  text-align: center;
  background-color: #f8fafc;
  transition: all 0.2s;
}

.upload-zone:hover {
  border-color: var(--primary);
  background-color: #f1f5f9;
}

.upload-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-inner p {
  color: #475569;
}

.upload-inner p span {
  color: var(--primary);
  font-weight: 600;
  text-decoration: underline;
}

.api-setup-card {
  max-width: 600px;
  background-color: #f8fafc;
  border-radius: 16px;
  padding: 32px;
}

.api-header-card {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.api-icon {
  width: 48px;
  height: 48px;
  background-color: var(--primary);
  color: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.api-header-card h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.api-desc {
  font-size: 0.9375rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 24px;
}

.toggle-container {
  position: relative;
  width: 44px;
  height: 24px;
}

.toggle-container input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  transition: .4s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--mso-accent);
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

.api-opt-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  color: #1e293b;
}

.text-center { text-align: center; }
.font-mono { font-family: monospace; }
.font-bold { font-weight: 700; }

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  .config-container {
    padding: 24px;
  }
}
/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  width: 90%;
  max-width: 400px;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #64748b;
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 16px 24px;
  background-color: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
}

.btn-add {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  background-color: var(--primary-hover);
}
</style>
