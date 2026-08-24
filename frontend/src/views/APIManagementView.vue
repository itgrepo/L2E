<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { postWithUser, encodeUserData } from '../utils/api';

const activeTab = ref('general');
const services = ref([]);
const isLoading = ref(false);
const message = ref({ text: '', type: '' });

// API GENERAL - Add API Modal
const showAddApiModal = ref(false);
const apiForm = ref({
  report_id: '',
  service_name: '',
  api_endpoint: '',
  service_description: '',
  api_type: 'general',
  api_enabled: 'Active = Enable',
  api_db_name: 'WAREHOUSE',
  api_source_name: '',
  request_fields: [],
  response_fields: []
});

// Manage API Access (BY USER) Modal
const showManageAccessModal = ref(false);
const selectedService = ref(null);
const credentials = ref([]);
const showKey = ref(null);

const toggleMainServiceStatus = async (svc) => {
  const isCurrentlyActive = (svc.status === 'Active' || svc.status === 'active');
  const newStatus = isCurrentlyActive ? 'Inactive' : 'Active';
  
  if (!confirm(`Are you sure you want to change the status of ${svc.service_name} to ${newStatus}?`)) return;
  
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await apiClient.post('/toggleServiceStatus', {
      user: encodeUserData(userData),
      service_id: svc.service_id,
      status: newStatus
    });
    
    if (res.data.status === 'success') {
      await fetchServices(); // Refresh list
    } else {
      alert('Error: ' + res.data.message);
    }
  } catch (e) {
    console.error(e);
    alert('An error occurred while updating the status.');
  }
};

const fetchServices = async () => {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/retrieveService');
    if (response.data.status === 'success') {
      services.value = response.data.data;
    }
  } catch (error) {
    console.error('Error fetching services:', error);
  } finally {
    isLoading.value = false;
  }
};

const openManageAccess = async (service) => {
  selectedService.value = service;
  showManageAccessModal.value = true;
  await fetchCredentials(service.service_id);
};

const fetchCredentials = async (serviceId) => {
  credentials.value = [];
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const response = await postWithUser('/getApiCredentials', userData, {
      service_id: serviceId
    });
    if (response.data.status === 'success') {
      credentials.value = response.data.data;
    }
  } catch (error) {
    console.error('Error fetching credentials:', error);
  }
};

const toggleKey = (id) => {
  showKey.value = showKey.value === id ? null : id;
};


const showEditExpiryModal = ref(false);
const editExpiryCred = ref(null);
const editExpiryDate = ref('');

const openEditExpiryForm = (cred) => {
  editExpiryCred.value = cred;
  if (cred.expires_at) {
    const d = new Date(cred.expires_at);
    const tzoffset = (new Date()).getTimezoneOffset() * 60000;
    const localISOTime = (new Date(d - tzoffset)).toISOString().slice(0, 16);
    editExpiryDate.value = localISOTime;
  } else {
    editExpiryDate.value = '';
  }
  showEditExpiryModal.value = true;
};

const saveEditExpiry = async () => {
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const payload = {
      credential_id: editExpiryCred.value.credential_id
    };
    if (editExpiryDate.value) {
      payload.expires_at = new Date(editExpiryDate.value).toISOString();
    }
    
    const res = await postWithUser('/extendApiCredential', userData, payload);
    if (res.data.status === 'success') {
      showEditExpiryModal.value = false;
      fetchServices();
      if (selectedService.value) {
        fetchCredentialsForService(selectedService.value.service_id);
      }
      if (scopeSelectedService.value) {
        fetchScopesForService(scopeSelectedService.value.service_id);
      }
    } else {
      alert('Error updating expiry: ' + res.data.status);
    }
  } catch (e) {
    console.error(e);
  }
};

const handleCredentialAction = async (endpoint, cred) => {
  if (!confirm(`Are you sure you want to ${endpoint.replace('ApiCredential', '')} this key?`)) return;
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const response = await postWithUser(`/${endpoint}`, userData, {
      credential_id: cred.credential_id
    });
    if (response.data.status === 'success') {
      alert(`Successfully performed action.`);
      // Refresh credentials
      if (selectedService.value) {
        await fetchCredentials(selectedService.value.service_id);
      } else if (scopeSelectedService.value) {
        await fetchScopesForService(scopeSelectedService.value.service_id);
      }
    } else {
      alert(`Error: ${response.data.message}`);
    }
  } catch (error) {
    console.error('Error performing action:', error);
    alert('An error occurred.');
  }
};

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleString('en-GB'); // DD/MM/YYYY, HH:MM:SS
};

onMounted(() => {
  fetchServices();
});

const toggleCredentialStatus = async (item) => {
  if (item.status === 'revoked') return;
  const isCurrentlyActive = item.status === 'active';
  const actionName = isCurrentlyActive ? 'pause' : 'resume';
  const endpoint = isCurrentlyActive ? 'pauseApiCredential' : 'resumeApiCredential';
  
  if (!confirm(`Are you sure you want to ${actionName} this key?`)) return;
  
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await apiClient.post(`/${endpoint}`, {
      user: encodeUserData(userData),
      credential_id: item.credential_id
    });
    if (res.data.status === 'success') {
      // Refresh list
      fetchServices();
      if (scopeSelectedService.value) {
        fetchScopesForService(scopeSelectedService.value.service_id);
      }
      if (selectedService.value) {
        fetchCredentialsForService(selectedService.value.service_id);
      }
    } else {
      alert('Error: ' + res.data.status);
    }
  } catch (e) { console.error(e); }
};

const newApiColumns = ref([]);

const onReportSelect = async () => {
  const selected = services.value.find(s => s.service_id === apiForm.value.report_id);
  if (selected) {
    apiForm.value.service_name = selected.service_name || '';
    apiForm.value.api_endpoint = `API-${selected.dataset_id || selected.service_id}`;
    apiForm.value.service_description = selected.description || selected.service_name || '';
    
    try {
      const userData = JSON.parse(localStorage.getItem('user') || '{}');
      const res = await apiClient.post('/getTableColumns', {
        user: encodeUserData(userData),
        db_name: selected.db_name || 'WAREHOUSE',
        table_name: selected.source_name
      });
      if (res.data.status === 'success') {
        newApiColumns.value = res.data.data;
      }
    } catch (e) {
      console.error(e);
    }
  }
};

// ===== API SCOPES TAB - กนอ. Pattern =====
// Scopes tab: shows services list like GENERAL, click "SCOPES" opens per-service modal
const scopeSelectedService = ref(null);
const showScopesListModal = ref(false);
const scopeCredentials = ref([]);
const scopeShowKey = ref(null);

// Add/Edit scope form modal
const showScopeFormModal = ref(false);
const isEditScope = ref(false);
const editingScopeCredentialId = ref(null);
const allUsers = ref([]);
const availableColumns = ref([]);

// Add User form modal for General Access
const showAddUserFormModal = ref(false);
const addUserFormUserId = ref('');
const addUserFormExpiry = ref('');

const scopeFormUser = ref('');
const scopeFormExpiry = ref('');
const scopeConditions = ref([]);

const openScopesForService = async (service) => {
  scopeSelectedService.value = service;
  showScopesListModal.value = true;
  await fetchScopesForService(service.service_id);
};

const fetchScopesForService = async (serviceId) => {
  scopeCredentials.value = [];
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await apiClient.post('/getAllApiScopes', { user: encodeUserData(userData) });
    if (res.data.status === 'success') {
      // Filter by service_id
      scopeCredentials.value = res.data.data.filter(s => String(s.service_id) === String(serviceId));
    }
  } catch (e) { console.error(e); }
};

const toggleScopeKey = (id) => {
  scopeShowKey.value = scopeShowKey.value === id ? null : id;
};

const fetchAllUsers = async () => {
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await apiClient.post('/getAvailableUsers', { user: encodeUserData(userData) });
    if (res.data.status === 'success') {
      allUsers.value = res.data.data;
    }
  } catch (e) { console.error(e); }
};

const fetchColumnsForService = async (service) => {
  availableColumns.value = [];
  if (!service) return;
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await apiClient.post('/getTableColumns', {
      user: encodeUserData(userData),
      db_name: service.db_name || 'WAREHOUSE',
      table_name: service.source_name
    });
    if (res.data.status === 'success') {
      availableColumns.value = res.data.data;
    }
  } catch (e) { console.error(e); }
};

const openAddScopeForm = async () => {
  isEditScope.value = false;
  editingScopeCredentialId.value = null;
  scopeFormUser.value = '';
  scopeFormExpiry.value = '';
  scopeConditions.value = [{ logic: 'AND', field: '', operator: '=', value: '' }];
  
  await fetchAllUsers();
  await fetchColumnsForService(scopeSelectedService.value);
  
  showScopeFormModal.value = true;
};

const openEditScopeForm = async (scope) => {
  isEditScope.value = true;
  editingScopeCredentialId.value = scope.credential_id;
  scopeFormUser.value = scope.user_id;
  
  // Format expiry date for datetime-local input (YYYY-MM-DDThh:mm)
  if (scope.expires_at) {
    const d = new Date(scope.expires_at);
    const tzoffset = (new Date()).getTimezoneOffset() * 60000; // offset in milliseconds
    const localISOTime = (new Date(d - tzoffset)).toISOString().slice(0, 16);
    scopeFormExpiry.value = localISOTime;
  } else {
    scopeFormExpiry.value = '';
  }
  
  // Parse existing scope
  const existingScope = scope.scope_json || [];
  if (existingScope.length > 0) {
    scopeConditions.value = JSON.parse(JSON.stringify(existingScope));
  } else {
    scopeConditions.value = [{ logic: 'AND', field: '', operator: '=', value: '' }];
  }
  
  await fetchAllUsers();
  await fetchColumnsForService(scopeSelectedService.value);
  
  showScopeFormModal.value = true;
};

const addScopeCondition = () => {
  scopeConditions.value.push({ logic: 'AND', field: '', operator: '=', value: '' });
};

const removeScopeCondition = (index) => {
  scopeConditions.value.splice(index, 1);
};

const saveScopeForm = async () => {
  if (!scopeFormUser.value) {
    alert('กรุณาเลือก User');
    return;
  }
  
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const validConditions = scopeConditions.value.filter(c => c.field && c.value);
    
    const payload = {
      user: encodeUserData(userData),
      service_id: scopeSelectedService.value.service_id,
      target_user_id: scopeFormUser.value,
      scope_json: validConditions
    };
    if (scopeFormExpiry.value) {
      // Convert local datetime back to standard format for backend
      const utcDate = new Date(scopeFormExpiry.value).toISOString();
      payload.expires_at = utcDate;
    }
    
    const res = await apiClient.post('/saveApiScopeForUser', payload);
    
    
    if (res.data.status === 'success') {
      if (res.data.secret_key) {
        alert('SUCCESS! Please copy this API Key now, it will not be shown again:\n\n' + res.data.secret_key);
      }
      showScopeFormModal.value = false;

      await fetchScopesForService(scopeSelectedService.value.service_id);
    } else {
      alert('Error saving scope: ' + res.data.status);
    }
  } catch (e) {
    console.error(e);
  }
};

const openAddUserForm = async () => {
  addUserFormUserId.value = '';
  addUserFormExpiry.value = '';
  await fetchAllUsers();
  showAddUserFormModal.value = true;
};

const saveAddUserForm = async () => {
  if (!addUserFormUserId.value) {
    alert('กรุณาเลือก User');
    return;
  }
  
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const payload = {
      user: encodeUserData(userData),
      service_id: selectedService.value.service_id,
      target_user_id: addUserFormUserId.value
    };
    if (addUserFormExpiry.value) {
      payload.expires_at = new Date(addUserFormExpiry.value).toISOString();
    }
    
    const res = await apiClient.post('/addApiCredential', payload);
    
    if (res.data.status === 'success') {
      if (res.data.secret_key) {
        alert('SUCCESS! Please copy this API Key now, it will not be shown again:\n\n' + res.data.secret_key);
      }
      showAddUserFormModal.value = false;
      await fetchCredentialsForService(selectedService.value.service_id);
    } else {
      alert('Error adding user: ' + res.data.status);
    }
  } catch (e) {
    console.error(e);
  }
};

const deleteScopeEntry = async (scope) => {
  if (!confirm("Are you sure you want to delete this scope?")) return;
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const res = await apiClient.post('/deleteApiScopeForUser', { 
      user: encodeUserData(userData),
      credential_id: scope.credential_id
    });
    if (res.data.status === 'success') {
      await fetchScopesForService(scopeSelectedService.value.service_id);
    }
  } catch (e) { console.error(e); }
};

const formatScopeJson = (scopeJson) => {
  if (!scopeJson || !Array.isArray(scopeJson) || scopeJson.length === 0) return '{}';
  const obj = {};
  for (const cond of scopeJson) {
    if (cond.field) {
      if (!obj[cond.field]) obj[cond.field] = [];
      obj[cond.field].push(cond.value);
    }
  }
  return JSON.stringify(obj);
};
</script>

<template>
  <div class="api-layout">
    <AppSidebar />
    
    <main class="api-content">
      <header class="content-header">
        <div class="header-titles">
          <h1>API MANAGEMENT</h1>
          <p>จัดการการเชื่อมต่อและการเข้าถึงข้อมูล</p>
        </div>
      </header>

      <div class="card api-card">
        <div class="tabs-container">
          <button 
            :class="['tab-btn', { active: activeTab === 'general' }]"
            @click="activeTab = 'general'"
          >
            API GENERAL
          </button>
          <button 
            :class="['tab-btn', { active: activeTab === 'scopes' }]"
            @click="activeTab = 'scopes'"
          >
            API SCOPES
          </button>
        </div>

        <!-- ============ API GENERAL TAB ============ -->
        <div v-if="activeTab === 'general'" class="tab-content">
          <div class="table-actions">
            <button @click="showAddApiModal = true" class="btn-primary">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              ADD API
            </button>
          </div>

          <table class="api-table">
            <thead>
              <tr>
                <th>API SERVICE NAME</th>
                <th>API ENDPOINT</th>
                <th>API DESCRIPTION</th>
                <th>ACTIVE</th>
                <th>STATUS</th>
                <th class="text-center">SELECT</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="svc in services" :key="svc.service_id">
                <td><strong>{{ svc.service_name }}</strong></td>
                <td>{{ svc.api_endpoint }}</td>
                <td>{{ svc.service_description || svc.service_name }}</td>
                <td>
                  <label class="toggle-switch" title="Toggle Service Status" @click.prevent="toggleMainServiceStatus(svc)">
                    <input type="checkbox" :checked="svc.status === 'Active' || svc.status === 'active'">
                    <span class="slider"></span>
                  </label>
                </td>
                <td>
                  <span :class="['status-badge', (svc.status || 'inactive').toLowerCase()]">{{ svc.status || 'INACTIVE' }}</span>
                </td>
                <td class="text-center">
                  <button @click="openManageAccess(svc)" class="btn-outline">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    BY USER
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ============ API SCOPES TAB ============ -->
        <div v-if="activeTab === 'scopes'" class="tab-content">
          <div class="table-actions">
            <button @click="showAddApiModal = true" class="btn-primary">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              ADD API
            </button>
          </div>
          <table class="api-table">
            <thead>
              <tr>
                <th>API SERVICE NAME</th>
                <th>API ENDPOINT</th>
                <th>API DESCRIPTION</th>
                <th>ACTIVE</th>
                <th>STATUS</th>
                <th class="text-center">SELECT</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="svc in services" :key="svc.service_id">
                <td><strong>{{ svc.service_name }}</strong></td>
                <td>{{ svc.api_endpoint }}</td>
                <td>{{ svc.service_description || svc.service_name }}</td>
                <td>
                  <label class="toggle-switch" title="Toggle Service Status" @click.prevent="toggleMainServiceStatus(svc)">
                    <input type="checkbox" :checked="svc.status === 'Active' || svc.status === 'active'">
                    <span class="slider"></span>
                  </label>
                </td>
                <td>
                  <span :class="['status-badge', (svc.status || 'inactive').toLowerCase()]">{{ svc.status || 'INACTIVE' }}</span>
                </td>
                <td class="text-center">
                  <button @click="openScopesForService(svc)" class="btn-outline">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    SCOPES
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ============ Add API Modal (GENERAL) ============ -->
      <div v-if="showAddApiModal" class="modal-overlay" @click.self="showAddApiModal = false">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <h3>ADD API</h3>
            <button @click="showAddApiModal = false" class="modal-close">&times;</button>
          </div>
          <div class="modal-body form-grid">
            <div class="form-row">
              <label>Report ID <span class="required">*</span></label>
              <select v-model="apiForm.report_id" @change="onReportSelect">
                <option value="">-- เลือก Report ID --</option>
                <option v-for="srv in services" :key="srv.service_id" :value="srv.service_id">
                  {{ srv.dataset_id || srv.service_id }} - {{ srv.service_name }}
                </option>
              </select>
            </div>
            <div class="form-row">
              <label>API Name <span class="required">*</span></label>
              <input type="text" v-model="apiForm.service_name" placeholder="ชื่อ API">
            </div>
            <div class="form-row">
              <label>API SERVICES <span class="required">*</span></label>
              <input type="text" v-model="apiForm.api_endpoint" placeholder="API-XXX">
            </div>
            <div class="form-row">
              <label>API Description</label>
              <input type="text" v-model="apiForm.service_description" placeholder="รายละเอียด API">
            </div>
            <div class="form-row">
              <label>API Type <span class="required">*</span></label>
              <select v-model="apiForm.api_type">
                <option value="general">general</option>
                <option value="scope">scope</option>
              </select>
            </div>
            <div class="form-row">
              <label>Status <span class="required">*</span></label>
              <select v-model="apiForm.api_enabled">
                <option value="Active = Enable">Active = Enable</option>
              </select>
            </div>
            <div class="form-row">
              <label>Database <span class="required">*</span></label>
              <select v-model="apiForm.api_db_name">
                <option value="WAREHOUSE">WAREHOUSE</option>
              </select>
            </div>
            <div class="form-row">
              <label>Table / View <span class="required">*</span></label>
              <select v-model="apiForm.api_source_name">
                <option value="FACT.fact_cargo_transaction">FACT.fact_cargo_transaction</option>
              </select>
            </div>
            
            <div class="checkbox-sections">
              <div class="checkbox-col">
                <h4>Please select for Request*</h4>
                <div style="max-height: 150px; overflow-y: auto; border: 1px solid #cbd5e1; padding: 8px; border-radius: 4px;">
                  <label v-for="col in newApiColumns" :key="col.column_name" class="checkbox-label">
                    <input type="checkbox" :value="col.column_name" v-model="apiForm.request_fields"> {{ col.column_name }}
                  </label>
                </div>
              </div>
              <div class="checkbox-col">
                <h4>Please select for Response*</h4>
                <div style="max-height: 150px; overflow-y: auto; border: 1px solid #cbd5e1; padding: 8px; border-radius: 4px;">
                  <label v-for="col in newApiColumns" :key="col.column_name" class="checkbox-label">
                    <input type="checkbox" :value="col.column_name" v-model="apiForm.response_fields"> {{ col.column_name }}
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer justify-end">
            <button class="btn-primary" @click="showAddApiModal = false">SAVE</button>
          </div>
        </div>
      </div>

      <!-- ============ Manage API Access (BY USER) Modal ============ -->
      <div v-if="showManageAccessModal" class="modal-overlay" @click.self="showManageAccessModal = false">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <h3>MANAGE API ACCESS</h3>
            <button @click="showManageAccessModal = false" class="modal-close">&times;</button>
          </div>
          <div class="modal-body">
            <div class="table-actions text-right mb-4">
              <button class="btn-outline-primary" @click="openAddUserForm">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
                ADD USER
              </button>
            </div>
            <div class="table-scroll-wrapper">
              <table class="api-table">
                <thead>
                  <tr>
                    <th>USERNAME</th>
                    <th>PUBLIC KEY ID</th>
                    <th>API KEY (Last 4)</th>
                    <th>EXPIRES AT</th>
                    <th>STATUS</th>
                    <th style="text-align:center;">ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="cred in credentials" :key="cred.credential_id">
                    <td style="font-weight:600;">{{ cred.username }}</td>
                    <td><span class="mono-cell">{{ cred.public_key_id }}</span></td>
                    <td class="key-cell">
                      <span class="secret-box">••••••••{{ cred.key_last_four }}</span>
                    </td>
                    <td>{{ formatDateTime(cred.expires_at) }}</td>
                    <td>
                      <span :class="['status-badge', cred.status]">{{ cred.status }}</span>
                    </td>
                    <td>
                      <div class="action-btns">
                        <label class="toggle-switch" title="Toggle Status" @click.prevent="toggleCredentialStatus(cred)" v-if="cred.status !== 'revoked'">
                          <input type="checkbox" :checked="cred.status === 'active'">
                          <span class="slider"></span>
                        </label>
                        <button v-if="cred.status !== 'revoked'" class="btn-icon-clean" @click="openEditExpiryForm(cred)" title="ตั้งวันหมดอายุ">
                          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="1.5"/><line x1="16" y1="2" x2="16" y2="6" stroke-width="1.5"/><line x1="8" y1="2" x2="8" y2="6" stroke-width="1.5"/><line x1="3" y1="10" x2="21" y2="10" stroke-width="1.5"/></svg>
                        </button>
                        <button v-if="cred.status !== 'revoked'" class="btn-icon-clean btn-icon-clean--danger" @click="handleCredentialAction('revokeApiCredential', cred)" title="เพิกถอน">
                          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><circle cx="12" cy="12" r="10" stroke-width="1.5"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07" stroke-width="1.5"/></svg>
                        </button>
                        <button class="btn-icon-clean btn-icon-clean--danger" @click="handleCredentialAction('deleteApiCredential', cred)" title="ลบ">
                          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><polyline points="3 6 5 6 21 6" stroke-width="1.5"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" stroke-width="1.5"/></svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="credentials.length === 0">
                    <td colspan="6" class="text-center text-muted py-4">ไม่มีข้อมูลผู้ใช้งาน</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    
      <!-- ============ SCOPES List Modal (กนอ. Pattern) ============ -->
      <div v-if="showScopesListModal" class="modal-overlay" @click.self="showScopesListModal = false">
        <div class="modal-content modal-xl">
          <div class="modal-header">
            <h3>SCOPES : {{ scopeSelectedService?.dataset_id || scopeSelectedService?.service_id }}</h3>
            <button @click="showScopesListModal = false" class="modal-close">&times;</button>
          </div>
          <div class="modal-body">
            <div class="table-actions text-right mb-4">
              <button class="btn-outline-primary" @click="openAddScopeForm">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
                ADD SCOPES
              </button>
            </div>
            <table class="api-table">
              <thead>
                <tr>
                  <th>USERNAME</th>
                  <th>PUBLIC KEY ID</th>
                  <th>API KEY (Last 4)</th>
                  <th>API NAME</th>
                  <th>SCOPES</th>
                  <th>EXPIRES AT</th>
                  <th>STATUS</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="sc in scopeCredentials" :key="sc.credential_id">
                  <td>{{ sc.username }}</td>
                  <td>
                    <div class="mono-cell">{{ sc.public_key_id }}</div>
                  </td>
                  <td class="key-cell">
                    <span class="secret-box">••••••••••••{{ sc.key_last_four }}</span>
                  </td>
                  <td><strong>{{ sc.dataset_id || sc.service_id }}</strong></td>
                  <td>
                    <span class="scope-badge">{{ formatScopeJson(sc.scope_json) }}</span>
                  </td>
                  <td>{{ formatDateTime(sc.expires_at) }}</td>
                  <td>
                    <span :class="['status-badge', sc.status]">{{ sc.status }}</span>
                  </td>
                  <td>
                    <div class="action-btns">
                      <button class="btn-icon" @click="openEditScopeForm(sc)" title="Edit">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>
                      <button v-if="sc.status !== 'revoked'" class="btn-icon" @click="openEditExpiryForm(sc)" title="ตั้งวันหมดอายุ">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="2"/><line x1="16" y1="2" x2="16" y2="6" stroke-width="2"/><line x1="8" y1="2" x2="8" y2="6" stroke-width="2"/><line x1="3" y1="10" x2="21" y2="10" stroke-width="2"/></svg>
                      </button>
                      <label class="toggle-switch" title="Toggle Status" @click.prevent="toggleCredentialStatus(sc)" v-if="sc.status !== 'revoked'">
                        <input type="checkbox" :checked="sc.status === 'active'">
                        <span class="slider"></span>
                      </label>
                      <button v-if="sc.status !== 'revoked'" class="btn-icon btn-icon-danger" @click="handleCredentialAction('revokeApiCredential', sc)" title="Revoke">
                        🚫
                      </button>
                      <button class="btn-icon btn-icon-danger" @click="handleCredentialAction('deleteApiCredential', sc)" title="Delete">
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="scopeCredentials.length === 0">
                  <td colspan="8" class="text-center text-muted py-4">ไม่มีข้อมูล Scope สำหรับ API นี้</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ============ Add User Form Modal (GENERAL API) ============ -->
      <div v-if="showAddUserFormModal" class="modal-overlay" @click.self="showAddUserFormModal = false">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <h3>ADD USER</h3>
            <button @click="showAddUserFormModal = false" class="modal-close">&times;</button>
          </div>
          <div class="modal-body form-grid">
            <div class="form-row">
              <label>API / Dataset</label>
              <input type="text" :value="(selectedService?.dataset_id || selectedService?.service_id) + ' - ' + selectedService?.service_name" disabled style="background:#f1f5f9; color:#475569;">
            </div>

            <div class="form-row">
              <label>User <span class="required">*</span></label>
              <select v-model="addUserFormUserId">
                <option value="">-- เลือก User --</option>
                <option v-for="usr in allUsers" :key="usr.user_id" :value="usr.user_id">
                  {{ usr.username }} ({{ usr.firstname }} {{ usr.lastname }})
                </option>
              </select>
            </div>

            <div class="form-row">
              <label>Expires At</label>
              <input type="datetime-local" v-model="addUserFormExpiry">
            </div>
          </div>
          <div class="modal-footer justify-end">
            <button class="btn-cancel" @click="showAddUserFormModal = false" style="margin-right:8px;">CANCEL</button>
            <button class="btn-primary" @click="saveAddUserForm">SAVE</button>
          </div>
        </div>
      </div>

            <!-- ============ Edit Expiry Form Modal ============ -->
      <div v-if="showEditExpiryModal" class="modal-overlay" @click.self="showEditExpiryModal = false">
        <div class="modal-content modal-md">
          <div class="modal-header">
            <h3>SET EXPIRES AT</h3>
            <button @click="showEditExpiryModal = false" class="modal-close">&times;</button>
          </div>
          <div class="modal-body form-grid">
            <div class="form-row">
              <label>User / API</label>
              <input type="text" :value="editExpiryCred?.username || editExpiryCred?.dataset_id || editExpiryCred?.service_id" disabled style="background:#f1f5f9; color:#475569;">
            </div>
            <div class="form-row">
              <label>Expires At (Leave blank for no expiry)</label>
              <input type="datetime-local" v-model="editExpiryDate">
            </div>
          </div>
          <div class="modal-footer justify-end">
            <button class="btn-cancel" @click="showEditExpiryModal = false" style="margin-right:8px;">CANCEL</button>
            <button class="btn-primary" @click="saveEditExpiry">SAVE</button>
          </div>
        </div>
      </div>

      <!-- ============ Add/Edit Scope Form Modal ============ -->
      <div v-if="showScopeFormModal" class="modal-overlay" @click.self="showScopeFormModal = false">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <h3>{{ isEditScope ? 'EDIT SCOPE' : 'ADD SCOPES' }}</h3>
            <button @click="showScopeFormModal = false" class="modal-close">&times;</button>
          </div>
          <div class="modal-body form-grid">
            <!-- API Info (read-only) -->
            <div class="form-row">
              <label>API / Dataset</label>
              <input type="text" :value="(scopeSelectedService?.dataset_id || scopeSelectedService?.service_id) + ' - ' + scopeSelectedService?.service_name" disabled style="background:#f1f5f9; color:#475569;">
            </div>

            <!-- User dropdown -->
            <div class="form-row">
              <label>User <span class="required">*</span></label>
              <select v-model="scopeFormUser" :disabled="isEditScope">
                <option value="">-- เลือก User --</option>
                <option v-for="usr in allUsers" :key="usr.user_id" :value="usr.user_id">
                  {{ usr.username }} ({{ usr.firstname }} {{ usr.lastname }})
                </option>
              </select>
            </div>

            <div class="form-row">
              <label>Expires At</label>
              <input type="datetime-local" v-model="scopeFormExpiry">
            </div>

            <!-- Scope Conditions (WHERE) -->
            <div class="scope-section">
              <h4 class="scope-section-title">Scope Conditions (WHERE)</h4>
              <div v-for="(cond, index) in scopeConditions" :key="index" class="scope-row">
                <select v-if="index > 0" v-model="cond.logic" class="scope-logic">
                  <option value="AND">AND</option>
                  <option value="OR">OR</option>
                </select>
                <span v-else class="scope-where-label">WHERE</span>
                <select v-model="cond.field" class="scope-field">
                  <option value="">-- เลือก Field --</option>
                  <option v-for="col in availableColumns" :key="col.column_name" :value="col.column_name">{{ col.column_name }}</option>
                </select>
                <select v-model="cond.operator" class="scope-operator">
                  <option value="=">=</option>
                  <option value="!=">!=</option>
                  <option value=">">&gt;</option>
                  <option value="<">&lt;</option>
                  <option value="LIKE">LIKE</option>
                  <option value="IN">IN</option>
                </select>
                <input type="text" v-model="cond.value" class="scope-value" placeholder="Value">
                <button @click="removeScopeCondition(index)" class="scope-remove" title="ลบ">✕</button>
              </div>
              <button @click="addScopeCondition" class="btn-outline-primary" style="margin-top:8px;">+ Add Condition</button>
            </div>
          </div>
          <div class="modal-footer" style="display:flex; justify-content:space-between;">
            <button class="btn-cancel" @click="showScopeFormModal = false">CANCEL</button>
            <button class="btn-primary" @click="saveScopeForm">SAVE</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.api-layout { display: flex; background-color: #f8fafc; min-height: 100vh; }
.api-content { flex: 1; padding: 40px; }
.content-header { margin-bottom: 32px; }
.header-titles h1 { font-size: 2rem; font-weight: 700; color: var(--primary); margin-bottom: 4px; text-transform: uppercase; }
.header-titles p { color: #64748b; font-size: 1rem; }

.api-card { background: white; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); border: 1px solid #e2e8f0; overflow: hidden; }

.tabs-container { display: flex; border-bottom: 1px solid #e2e8f0; }
.tab-btn { flex: 1; padding: 16px; background: none; border: none; font-size: 1.125rem; font-weight: 700; color: #94a3b8; cursor: pointer; border-bottom: 3px solid transparent; text-transform: uppercase; }
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); }

.tab-content { padding: 24px; }
.table-actions { display: flex; justify-content: flex-end; margin-bottom: 16px; }

.btn-primary { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); color: white; border: none; padding: 10px 24px; border-radius: 10px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.2); }
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(15, 23, 42, 0.3); }
.btn-outline { background: white; color: #0f172a; border: 1.5px solid #e2e8f0; padding: 8px 18px; border-radius: 10px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; font-size: 0.875rem; text-transform: uppercase; transition: all 0.2s; }
.btn-outline:hover { border-color: #0f172a; background: #f8fafc; }
.btn-outline-primary { background: white; color: #0f172a; border: 1.5px solid #e2e8f0; padding: 8px 18px; border-radius: 10px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s; }
.btn-outline-primary:hover { border-color: #0f172a; background: #f8fafc; }
.btn-cancel { background: #fff; border: 1.5px solid #e2e8f0; color: #475569; padding: 10px 24px; border-radius: 10px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-cancel:hover { border-color: #94a3b8; background: #f8fafc; }

.api-table { width: 100%; border-collapse: separate; border-spacing: 0; }
.api-table th { text-align: left; padding: 14px 16px; font-size: 0.75rem; font-weight: 700; color: #94a3b8; border-bottom: 2px solid #f1f5f9; background: transparent; text-transform: uppercase; letter-spacing: 0.05em; }
.api-table td { padding: 14px 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.875rem; color: #334155; vertical-align: middle; transition: background 0.15s; }
.api-table tbody tr:hover td { background: #f8fafc; }
.api-table th.text-center, .api-table td.text-center { text-align: center; }

.status-badge { padding: 5px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; }
.status-badge.active { background: #dcfce7; color: #166534; }
.status-badge.paused { background: #fef3c7; color: #92400e; }
.status-badge.revoked { background: #fee2e2; color: #991b1b; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; animation: fadeInOverlay 0.2s ease; }
@keyframes fadeInOverlay { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUpModal { from { opacity: 0; transform: translateY(20px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-content { background: white; border-radius: 20px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; display: flex; flex-direction: column; box-shadow: 0 25px 60px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.05); animation: slideUpModal 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-content.modal-md { max-width: 520px; }
.modal-content.modal-lg { max-width: 860px; }
.modal-content.modal-xl { max-width: 1060px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px; background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); color: white; border-radius: 20px 20px 0 0; }
.modal-header h3 { font-size: 1.125rem; font-weight: 700; letter-spacing: 0.03em; text-transform: uppercase; margin: 0; }
.modal-close { background: rgba(255,255,255,0.15); border: none; font-size: 1.25rem; color: white; cursor: pointer; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; line-height: 1; }
.modal-close:hover { background: rgba(255,255,255,0.3); transform: rotate(90deg); }
.modal-body { padding: 28px; background: #f8fafc; }
.modal-footer { padding: 16px 28px; background: white; border-top: 1px solid #e2e8f0; display: flex; border-radius: 0 0 20px 20px; }
.justify-end { justify-content: flex-end; }

.form-grid { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: flex; align-items: center; }
.form-row label { width: 140px; font-size: 0.875rem; font-weight: 600; color: #475569; text-align: right; padding-right: 16px; }
.form-row .required { color: #ef4444; }
.form-row input, .form-row select { flex: 1; padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 0.9375rem; transition: all 0.2s; outline: none; }
.form-row input:focus, .form-row select:focus { border-color: #0f172a; box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.08); }

.checkbox-sections { display: flex; gap: 40px; padding-left: 140px; margin-top: 24px; }
.checkbox-col { flex: 1; display: flex; flex-direction: column; gap: 12px; }
.checkbox-col h4 { font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px; }
.checkbox-label { display: flex; align-items: center; gap: 8px; font-size: 0.9375rem; color: #1e293b; cursor: pointer; }

.key-cell { display: flex; align-items: center; gap: 8px; }
.secret-box { background: #f1f5f9; padding: 6px 12px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.8125rem; color: #475569; letter-spacing: 0.02em; }
.toggle-btn, .btn-icon { background: none; border: none; color: #94a3b8; cursor: pointer; padding: 6px; border-radius: 8px; transition: all 0.2s; font-size: 1rem; }
.toggle-btn:hover, .btn-icon:hover { color: #475569; background: #f1f5f9; }
.btn-icon-primary { color: #3b82f6 !important; }
.btn-icon-primary:hover { color: #2563eb !important; background: #eff6ff !important; }
.btn-icon-danger { color: #ef4444 !important; }
.btn-icon-danger:hover { color: #dc2626 !important; background: #fef2f2 !important; }
.text-right { text-align: right; }
.mb-4 { margin-bottom: 16px; }
.py-4 { padding-top: 16px; padding-bottom: 16px; }

.mono-cell { font-family: 'JetBrains Mono', monospace; font-size: 0.8125em; background: #f1f5f9; padding: 4px 10px; border-radius: 6px; display: inline-block; color: #475569; }
.scope-badge { font-family: 'JetBrains Mono', monospace; font-size: 0.8125em; background: #f1f5f9; padding: 4px 10px; border-radius: 6px; display: inline-block; color: #475569; word-break: break-all; max-width: 200px; }
.action-btns { display: flex; gap: 6px; align-items: center; justify-content: center; }

.table-scroll-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 0 -4px; padding: 0 4px; }

.btn-icon-clean { background: none; border: 1px solid #e2e8f0; color: #64748b; cursor: pointer; padding: 6px; border-radius: 8px; transition: all 0.2s; display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; }
.btn-icon-clean:hover { color: #0f172a; border-color: #cbd5e1; background: #f8fafc; }
.btn-icon-clean--danger { color: #94a3b8; border-color: #e2e8f0; }
.btn-icon-clean--danger:hover { color: #ef4444; border-color: #fecaca; background: #fef2f2; }
.scope-section { margin-top: 8px; padding: 16px; background: white; border-radius: 6px; border: 1px solid #e2e8f0; }
.scope-section-title { font-size: 0.9375rem; font-weight: 700; color: var(--primary); margin-bottom: 12px; }
.scope-row { display: flex; gap: 8px; margin-bottom: 8px; align-items: center; }
.scope-logic { width: 80px; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.875rem; }
.scope-where-label { width: 80px; text-align: center; font-weight: 700; color: var(--primary); font-size: 0.875rem; }
.scope-field { flex: 2; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.875rem; }
.scope-operator { width: 80px; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.875rem; }
.scope-value { flex: 2; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.875rem; }
.scope-remove { background: none; border: none; color: #ef4444; cursor: pointer; font-size: 1rem; padding: 4px 8px; font-weight: bold; }
.scope-remove:hover { color: #dc2626; }

/* Toggle Switch */
.toggle-switch { position: relative; display: inline-block; width: 44px; height: 24px; margin-right: 8px; vertical-align: middle; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; transition: .3s; border-radius: 24px; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .3s; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
input:checked + .slider { background-color: #10b981; }
input:checked + .slider:before { transform: translateX(20px); }
input:disabled + .slider { opacity: 0.5; cursor: not-allowed; }
</style>
