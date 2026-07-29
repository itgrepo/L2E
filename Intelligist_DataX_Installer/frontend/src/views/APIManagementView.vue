<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { postWithUser } from '../utils/api';

const isLoading = ref(false);
const showKey = ref(null);
const services = ref([]);
const selectedServiceId = ref(null);
const credentials = ref([]);
const message = ref({ text: '', type: '' });
const hideRevoked = ref(true);

// Add credential form
const showAddForm = ref(false);
const availableUsers = ref([]);
const selectedUserId = ref('');
const generatedKey = ref('');

// Scope modal
const showScopeModal = ref(false);
const editingCredential = ref(null);
const scopeEntries = ref([]);
const newScopeField = ref('');
const newScopeValue = ref('');

// Expiration / UI
const selectedExpiresAt = ref('');
const showExtendModal = ref(false);
const editingExtendCredential = ref(null);
const newExpiresAt = ref('');

// Service metadata for scope fields
const selectedServiceMeta = ref(null);

const fetchServices = async () => {
  try {
    const response = await apiClient.get('/retrieveService');
    if (response.data.status === 'success') {
      services.value = response.data.data.filter(s => 
        s.api_enabled == 1 || s.api_enabled === true || s.api_enabled === '1'
      );
      if (services.value.length > 0 && !selectedServiceId.value) {
        selectedServiceId.value = services.value[0].service_id;
      }
    }
  } catch (error) {
    console.error('Error fetching services:', error);
  }
};

const fetchCredentials = async () => {
  if (!selectedServiceId.value) return;
  isLoading.value = true;
  credentials.value = [];
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const response = await postWithUser('/getApiCredentials', userData, {
      service_id: selectedServiceId.value
    });
    if (response.data.status === 'success') {
      credentials.value = response.data.data;
    }
  } catch (error) {
    console.error('Error fetching credentials:', error);
  } finally {
    isLoading.value = false;
  }
};

const fetchUsers = async () => {
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const response = await postWithUser('/getAvailableUsers', userData);
    if (response.data.status === 'success') {
      availableUsers.value = response.data.data;
    }
  } catch (error) {
    console.error('Error fetching users:', error);
  }
};

const generateKey = () => {
  const arr = new Uint8Array(16);
  crypto.getRandomValues(arr);
  generatedKey.value = Array.from(arr, b => b.toString(16).padStart(2, '0')).join('');
};

const addCredential = async () => {
  if (!selectedServiceId.value || !selectedUserId.value) {
    message.value = { text: 'กรุณาเลือกผู้ใช้', type: 'error' };
    return;
  }
  if (!generatedKey.value) generateKey();

  isLoading.value = true;
  message.value = { text: '', type: '' };
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    
    let finalDate = selectedExpiresAt.value;
    if (finalDate && finalDate.length === 16) {
        finalDate = finalDate + ':00'; // add seconds since datetime-local doesn't include it by default
    }

    const response = await postWithUser('/addApiCredential', userData, {
      service_id: selectedServiceId.value,
      target_user_id: selectedUserId.value,
      secret_key: generatedKey.value,
      expires_at: finalDate || null
    });
    if (response.data.status === 'success') {
      message.value = { text: 'สร้าง API Key สำเร็จ!', type: 'success' };
      
      // Update local storage if creating key for self
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      if (selectedUserId.value == currentUser.user_id || selectedUserId.value == '809') { // 809 is testadmin ID
          currentUser.apikey = generatedKey.value;
          localStorage.setItem('user', JSON.stringify(currentUser));
      }

      showAddForm.value = false;
      selectedUserId.value = '';
      generatedKey.value = '';
      selectedExpiresAt.value = '';
      fetchCredentials();
    } else {
      message.value = { text: response.data.status, type: 'error' };
    }
  } catch (error) {
    message.value = { text: 'เกิดข้อผิดพลาด', type: 'error' };
  } finally {
    isLoading.value = false;
  }
};

const toggleCredentialStatus = async (cred) => {
  if (cred.status === 'active') {
    if (!confirm('ต้องการระงับการใช้งาน API Key นี้ (Pause) ?')) return;
    try {
      const userData = JSON.parse(localStorage.getItem('user') || '{}');
      await postWithUser('/revokeApiCredential', userData, { credential_id: cred.credential_id });
      message.value = { text: 'ระงับการใช้งาน Key สำเร็จ', type: 'success' };
      fetchCredentials();
    } catch (error) {
      message.value = { text: 'เกิดข้อผิดพลาด', type: 'error' };
    }
  } else {
    if (!confirm('ต้องการยกเลิกการเพิกถอนและเปิดใช้งาน API Key นี้อีกครั้ง (Resume) ?')) return;
    try {
      const userData = JSON.parse(localStorage.getItem('user') || '{}');
      await postWithUser('/resumeApiCredential', userData, { credential_id: cred.credential_id });
      message.value = { text: 'เปิดใช้งาน Key สำเร็จ', type: 'success' };
      fetchCredentials();
    } catch (error) {
      message.value = { text: 'เกิดข้อผิดพลาด', type: 'error' };
    }
  }
};

const deleteCredential = async (credentialId) => {
  if (!confirm('ต้องการลบ API Key นี้ถาวร? การลบจะไม่สามารถกู้คืนได้')) return;
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const response = await postWithUser('/deleteApiCredential', userData, { credential_id: credentialId });
    if (response.data.status === 'success') {
      message.value = { text: 'ลบ API Key สำเร็จ', type: 'success' };
      fetchCredentials();
    } else {
      message.value = { text: 'ไม่สามารถลบได้: ' + response.data.status, type: 'error' };
    }
  } catch (error) {
    message.value = { text: 'เกิดข้อผิดพลาดในการลบ', type: 'error' };
  }
};

const isExpired = (expiresAt) => {
  if (!expiresAt) return false;
  return new Date(expiresAt) < new Date();
};

const openExtendModal = (cred) => {
  editingExtendCredential.value = cred;
  if (cred.expires_at) {
    newExpiresAt.value = cred.expires_at.replace(' ', 'T').slice(0, 16);
  } else {
    newExpiresAt.value = '';
  }
  showExtendModal.value = true;
};

const saveExtension = async () => {
  if (!editingExtendCredential.value) return;
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    let finalDate = newExpiresAt.value;
    if (finalDate && finalDate.length === 16) {
        finalDate = finalDate + ':00';
    } else if (!finalDate) {
        finalDate = null;
    }
    await postWithUser('/extendApiCredential', userData, { 
      credential_id: editingExtendCredential.value.credential_id,
      expires_at: finalDate
    });
    message.value = { text: 'ปรับเปลี่ยนวันหมดอายุสำเร็จ', type: 'success' };
    showExtendModal.value = false;
    fetchCredentials();
  } catch (error) {
    message.value = { text: 'เกิดข้อผิดพลาดในการปรับเวลา', type: 'error' };
  }
};

const openScopeModal = (cred) => {
  editingCredential.value = cred;
  // Parse existing scope_json into entries
  const scopeObj = cred.scope_json || {};
  scopeEntries.value = Object.entries(scopeObj).map(([field, values]) => ({
    field,
    values: Array.isArray(values) ? values : [values]
  }));
  
  // Load service meta for field options
  const svc = services.value.find(s => s.service_id === selectedServiceId.value);
  selectedServiceMeta.value = svc;
  
  showScopeModal.value = true;
};

const addScopeEntry = () => {
  if (!newScopeField.value || !newScopeValue.value) return;
  const existing = scopeEntries.value.find(e => e.field === newScopeField.value);
  if (existing) {
    if (!existing.values.includes(newScopeValue.value)) {
      existing.values.push(newScopeValue.value);
    }
  } else {
    scopeEntries.value.push({ field: newScopeField.value, values: [newScopeValue.value] });
  }
  newScopeValue.value = '';
};

const removeScopeValue = (fieldIdx, valIdx) => {
  scopeEntries.value[fieldIdx].values.splice(valIdx, 1);
  if (scopeEntries.value[fieldIdx].values.length === 0) {
    scopeEntries.value.splice(fieldIdx, 1);
  }
};

const saveScopeChanges = async () => {
  if (!editingCredential.value) return;
  const scopeObj = {};
  scopeEntries.value.forEach(entry => {
    scopeObj[entry.field] = entry.values;
  });

  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    await postWithUser('/updateApiScope', userData, {
      credential_id: editingCredential.value.credential_id,
      scope_json: scopeObj
    });
    message.value = { text: 'บันทึก Scope สำเร็จ', type: 'success' };
    showScopeModal.value = false;
    fetchCredentials();
  } catch (error) {
    message.value = { text: 'เกิดข้อผิดพลาดในการบันทึก Scope', type: 'error' };
  }
};

const toggleKey = (id) => {
  showKey.value = showKey.value === id ? null : id;
};

const selectedServiceType = computed(() => {
  const svc = services.value.find(s => s.service_id === selectedServiceId.value);
  return svc?.api_type || 'public';
});

const requestFieldOptions = computed(() => {
  const svc = services.value.find(s => s.service_id === selectedServiceId.value);
  if (!svc?.api_request_fields) return [];
  try {
    const fields = typeof svc.api_request_fields === 'string' ? JSON.parse(svc.api_request_fields) : svc.api_request_fields;
    return Array.isArray(fields) ? fields : [];
  } catch { return []; }
});

const filteredCredentials = computed(() => {
  if (!hideRevoked.value) return credentials.value;
  return credentials.value.filter(cred => cred.status === 'active');
});

watch(selectedServiceId, () => {
  fetchCredentials();
});

onMounted(() => {
  fetchServices();
  fetchUsers();
});
</script>

<template>
  <div class="api-layout">
    <AppSidebar />
    
    <main class="api-content">
      <header class="content-header">
        <div class="header-titles">
          <h1>API Management</h1>
          <p>จัดการ API Key และ Scope สำหรับผู้ใช้งาน</p>
        </div>
        
        <div class="service-selector">
          <span>Service:</span>
          <select v-model="selectedServiceId" @change="fetchCredentials">
            <option v-for="svc in services" :key="svc.service_id" :value="svc.service_id">
              {{ svc.service_name }} ({{ svc.api_type || 'public' }})
            </option>
          </select>
        </div>
      </header>

      <div v-if="message.text" :class="['alert-message', message.type]">
        {{ message.text }}
      </div>

      <!-- Service Type Badge -->
      <div v-if="selectedServiceId" class="type-badge-row">
        <div class="flex items-center gap-4">
          <span class="type-badge" :class="selectedServiceType">
            {{ selectedServiceType === 'public' ? '🔓 Public API' : selectedServiceType === 'private' ? '🔐 Private API' : '🔐 Private API - Scope Based' }}
          </span>
          <label class="toggle-revoked flex items-center gap-2 text-sm cursor-pointer select-none">
            <input type="checkbox" v-model="hideRevoked">
            <span class="text-slate-600">ซ่อนรายการที่ถูกยกเลิก (Hide Revoked)</span>
          </label>
        </div>
        <button @click="showAddForm = true; fetchUsers()" class="btn-add-key">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          เพิ่ม API Key
        </button>
      </div>

      <!-- Add Key Panel -->
      <div v-if="showAddForm" class="card add-key-panel">
        <h3>สร้าง API Key ใหม่</h3>
        <div class="add-key-form">
          <div class="form-group">
            <label>เลือกผู้ใช้</label>
            <select v-model="selectedUserId">
              <option value="">-- เลือก --</option>
              <option v-for="u in availableUsers" :key="u.user_id" :value="u.user_id">
                {{ u.username }} ({{ u.firstname }} {{ u.lastname }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Secret Key</label>
            <div class="key-gen-row">
              <input type="text" v-model="generatedKey" placeholder="คลิก Generate เพื่อสร้าง" readonly>
              <button @click="generateKey" class="btn-gen">Generate</button>
            </div>
          </div>
          <div class="form-group">
            <label>วันหมดอายุ (เว้นว่างหากใช้งานได้ตลอด)</label>
            <input type="datetime-local" v-model="selectedExpiresAt">
          </div>
          <div class="add-key-actions">
            <button @click="showAddForm = false" class="btn-cancel-sm">ยกเลิก</button>
            <button @click="addCredential" class="btn-primary" :disabled="isLoading">
              {{ isLoading ? 'กำลังสร้าง...' : 'สร้าง Key' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Credentials Table -->
      <div class="card api-card">
        <div class="api-header">
          <h3>API Credentials</h3>
          <p>รายการ API Key สำหรับ Service ที่เลือก</p>
        </div>
        
        <div v-if="isLoading && credentials.length === 0" class="loading-inline">
          กำลังโหลด...
        </div>
        
        <table v-else class="api-table">
          <thead>
            <tr>
              <th>ผู้ใช้</th>
              <th>Secret Key</th>
              <th>สถานะ</th>
              <th v-if="selectedServiceType === 'scope'">Scope</th>
              <th>อายุการใช้งาน</th>
              <th class="text-center">เพิกถอน (Pause)</th>
              <th class="text-right">จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cred in filteredCredentials" :key="cred.credential_id">
              <td class="name-cell">
                <strong>{{ cred.username }}</strong>
                <div class="text-sm text-muted">{{ cred.firstname }} {{ cred.lastname }}</div>
              </td>
              <td class="key-cell">
                <code>{{ showKey === cred.credential_id ? cred.secret_key : '••••••••••••••••' }}</code>
                <button class="toggle-btn" @click="toggleKey(cred.credential_id)">
                  {{ showKey === cred.credential_id ? 'ซ่อน' : 'แสดง' }}
                </button>
              </td>
              <td>
                <span v-if="cred.status === 'active' && isExpired(cred.expires_at)" class="status-badge expired">
                  Expired
                </span>
                <span v-else :class="['status-badge', cred.status]">
                  {{ cred.status === 'active' ? 'Active' : 'Revoked' }}
                </span>
              </td>
              <td v-if="selectedServiceType === 'scope'">
                <button v-if="cred.status === 'active'" @click="openScopeModal(cred)" class="btn-scope">
                  {{ cred.scope_json && Object.keys(cred.scope_json).length > 0 ? '✏️ แก้ไข Scope' : '➕ เพิ่ม Scope' }}
                </button>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-sm">
                <div>สร้าง: <span class="text-muted">{{ cred.created_at?.split(' ')[0] || '-' }}</span></div>
                <div style="margin-top:4px; font-weight:600;" :style="{ color: isExpired(cred.expires_at) ? '#ef4444' : '#1e293b' }">
                  หมด: {{ cred.expires_at ? cred.expires_at.split(' ')[0] : 'ไม่มีกำหนด' }}
                </div>
              </td>
              <td class="text-center">
                <label class="toggle-switch" :title="cred.status === 'active' ? 'กำลังใช้งาน (คลิกเพื่อระงับ)' : 'ถูกระงับ (คลิกเพื่อเปิดใช้งาน)'">
                  <input type="checkbox" :checked="cred.status === 'active'" @click.prevent="toggleCredentialStatus(cred)">
                  <span class="slider round"></span>
                </label>
              </td>
              <td class="text-right">
                <div class="action-buttons-wrap">
                  <button v-if="cred.status === 'active'" @click="openExtendModal(cred)" class="btn-warning-sm" title="ปรับวันหมดอายุ">📅 ขยายเวลา</button>
                  <button @click="deleteCredential(cred.credential_id)" class="btn-delete" title="ลบถาวร">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    ลบ
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredCredentials.length === 0">
              <td :colspan="selectedServiceType === 'scope' ? 7 : 6" style="text-align:center;padding:48px;color:#94a3b8;">
                {{ hideRevoked ? 'ไม่มี API Key ที่ใช้งานอยู่ (เปิด "แสดงรายการที่ถูกยกเลิก" เพื่อดูทั้งหมด)' : 'ยังไม่มี API Key สำหรับ Service นี้' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Scope Modal -->
      <div v-if="showScopeModal" class="modal-overlay" @click.self="showScopeModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>จัดการ Scope — {{ editingCredential?.username }}</h3>
            <button @click="showScopeModal = false" class="modal-close">&times;</button>
          </div>
          <div class="modal-body">
            <p style="color:#64748b;margin-bottom:20px;">
              กำหนดค่าที่อนุญาตให้ผู้ใช้คนนี้เข้าถึง เช่น <code>{"province": ["กรุงเทพ"]}</code>
            </p>

            <!-- Existing entries -->
            <div v-for="(entry, idx) in scopeEntries" :key="idx" class="scope-entry">
              <div class="scope-field-name">{{ entry.field }}</div>
              <div class="scope-values">
                <span v-for="(val, vidx) in entry.values" :key="vidx" class="scope-chip">
                  {{ val }}
                  <button @click="removeScopeValue(idx, vidx)" class="chip-remove">&times;</button>
                </span>
              </div>
            </div>

            <!-- Add new -->
            <div class="scope-add-row">
              <select v-model="newScopeField" style="flex:1;">
                <option value="">-- เลือก Field --</option>
                <option v-for="f in requestFieldOptions" :key="f" :value="f">{{ f }}</option>
              </select>
              <input type="text" v-model="newScopeValue" placeholder="ค่าที่อนุญาต" style="flex:1;" @keyup.enter="addScopeEntry">
              <button @click="addScopeEntry" class="btn-add-sm">เพิ่ม</button>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showScopeModal = false" class="btn-cancel-sm">ยกเลิก</button>
            <button @click="saveScopeChanges" class="btn-primary">บันทึก Scope</button>
          </div>
        </div>
      </div>

      <!-- Extend Time Modal -->
      <div v-if="showExtendModal" class="modal-overlay" @click.self="showExtendModal = false">
        <div class="modal-content" style="max-width:400px;">
          <div class="modal-header">
            <h3>ปรับวันหมดอายุ (ขยายเวลา)</h3>
            <button @click="showExtendModal = false" class="modal-close">&times;</button>
          </div>
          <div class="modal-body" style="display: flex; flex-direction: column; gap:16px;">
            <p style="color:#64748b;">
              ต่ออายุแอปพลิเคชันหรือแก้ไขวันหมดอายุให้กับผู้ใช้ <strong>{{ editingExtendCredential?.username }}</strong>
            </p>
            <div class="form-group" style="display: flex; flex-direction: column; gap:6px;">
              <label style="font-weight:600;font-size:14px;color:#475569;">วันหมดอายุใหม่</label>
              <input type="datetime-local" v-model="newExpiresAt" style="padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 0.9375rem; outline: none; width: 100%;">
              <span style="font-size:12px;color:#94a3b8;margin-top:4px;">ปล่อยว่างไว้หากต้องการให้คีย์นี้ใช้งานได้ตลอดไปโดยไม่มีวันหมดอายุ</span>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showExtendModal = false" class="btn-cancel-sm">ยกเลิก</button>
            <button @click="saveExtension" class="btn-primary">บันทึก</button>
          </div>
        </div>
      </div>

      <!-- Info Section -->
      <section class="security-info">
        <h3>Security Best Practices</h3>
        <div class="info-grid">
          <div class="info-item">
            <div class="icon-circle">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h4>ห้ามแชร์ API Key</h4>
            <p>เก็บ Key ไว้เป็นความลับ หากถูก expose ให้เพิกถอนทันที</p>
          </div>
          <div class="info-item">
            <div class="icon-circle">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h4>Scope = Row-Level Security</h4>
            <p>ใช้ Scope API เพื่อจำกัดข้อมูลตามผู้ใช้แต่ละคน</p>
          </div>
          <div class="info-item">
            <div class="icon-circle">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <h4>หมุนเวียน Key ทุก 90 วัน</h4>
            <p>เปลี่ยน Key เป็นประจำเพื่อความปลอดภัยสูงสุด</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.api-layout { display: flex; background-color: #f8fafc; min-height: 100vh; }
.api-content { flex: 1; padding: 40px; }
.content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
.header-titles h1 { font-size: 1.875rem; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.header-titles p { color: #64748b; font-size: 0.9375rem; }

.service-selector { display: flex; align-items: center; gap: 12px; }
.service-selector span { font-weight: 600; color: #475569; }
.service-selector select { padding: 8px 16px; border-radius: 10px; border: 1px solid #e2e8f0; background: white; font-weight: 600; color: #1e293b; outline: none; }

.type-badge-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.type-badge { padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 0.875rem; }
.type-badge.general, .type-badge.public { background: #e0f2fe; color: #0369a1; }
.type-badge.private { background: #fee2e2; color: #991b1b; }
.type-badge.scope { background: #fef3c7; color: #92400e; }

.btn-add-key { display: flex; align-items: center; gap: 8px; padding: 10px 20px; background: var(--primary); color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-add-key:hover { background: var(--primary-hover); transform: translateY(-1px); }

.alert-message { padding: 14px 20px; border-radius: 10px; margin-bottom: 20px; font-weight: 600; text-align: center; }
.alert-message.success { background-color: #fce7f3; color: #166534; border: 1px solid #bbf7d0; }
.alert-message.error { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

.card { background: white; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }

.add-key-panel { padding: 28px; margin-bottom: 24px; }
.add-key-panel h3 { font-size: 1.125rem; font-weight: 700; color: #1e293b; margin-bottom: 20px; }
.add-key-form { display: flex; flex-direction: column; gap: 16px; }
.add-key-form .form-group { display: flex; flex-direction: column; gap: 6px; }
.add-key-form label { font-size: 0.875rem; font-weight: 600; color: #475569; }
.add-key-form select, .add-key-form input { padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 0.9375rem; outline: none; }
.key-gen-row { display: flex; gap: 8px; }
.key-gen-row input { flex: 1; font-family: monospace; font-size: 0.8125rem; }
.btn-gen { padding: 10px 20px; background: #475569; color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer; }
.add-key-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 8px; }

.api-card { padding: 32px; margin-bottom: 40px; }
.api-header { margin-bottom: 24px; }
.api-header h3 { font-size: 1.25rem; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.api-header p { color: #64748b; }

.loading-inline { padding: 40px; text-align: center; color: #94a3b8; }

.api-table { width: 100%; border-collapse: collapse; }
.api-table th { text-align: left; padding: 14px 16px; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; border-bottom: 2px solid #f1f5f9; }
.api-table td { padding: 18px 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.9375rem; vertical-align: middle; }
.name-cell strong { color: #1e293b; display: block; }
.text-sm { font-size: 0.8125rem; }
.text-muted { color: #94a3b8; }
.text-center { text-align: center; }
.text-right { text-align: right; }

.key-cell { display: flex; align-items: center; gap: 12px; }
.key-cell code { background: #f8fafc; padding: 6px 10px; border-radius: 6px; font-family: monospace; color: #475569; font-size: 0.8125rem; }
.toggle-btn { background: none; border: none; color: var(--primary); font-weight: 600; cursor: pointer; font-size: 0.8125rem; }

.status-badge { padding: 4px 10px; border-radius: 100px; font-size: 0.75rem; font-weight: 700; }
.status-badge.active { background: #fce7f3; color: #166534; }
.status-badge.revoked { background: #fee2e2; color: #ef4444; }
.status-badge.expired { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

.btn-scope { background: #f0f9ff; color: #0369a1; border: 1px solid #bae6fd; padding: 6px 14px; border-radius: 8px; font-size: 0.8125rem; font-weight: 600; cursor: pointer; }
.btn-scope:hover { background: #e0f2fe; }
.action-buttons-wrap { display: flex; gap: 8px; justify-content: flex-end; align-items: center; }

/* Toggle Switch Styles */
.toggle-switch { position: relative; display: inline-block; width: 44px; height: 24px; flex-shrink: 0; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.toggle-switch .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; transition: .3s; }
.toggle-switch .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .3s; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
.toggle-switch input:checked + .slider { background-color: #10b981; }
.toggle-switch input:focus + .slider { box-shadow: 0 0 1px #10b981; }
.toggle-switch input:checked + .slider:before { transform: translateX(20px); }
.toggle-switch .slider.round { border-radius: 24px; }
.toggle-switch .slider.round:before { border-radius: 50%; }

.btn-warning-sm { background: none; color: #d97706; border: 1px solid #fcd34d; padding: 6px 14px; border-radius: 8px; font-size: 0.8125rem; font-weight: 600; cursor: pointer; }
.btn-warning-sm:hover { background: #fef3c7; }

.btn-primary { background: var(--primary); color: white; border: none; padding: 10px 24px; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-delete { background: none; color: #64748b; border: 1px solid #e2e8f0; padding: 6px 14px; border-radius: 8px; font-size: 0.8125rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 4px; }
.btn-delete:hover { background: #fee2e2; color: #ef4444; border-color: #fecaca; }
.btn-cancel-sm { background: white; color: #64748b; border: 1px solid #e2e8f0; padding: 10px 24px; border-radius: 10px; font-weight: 600; cursor: pointer; }
.btn-add-sm { background: var(--primary); color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; white-space: nowrap; }

/* Modal */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; border-radius: 20px; width: 90%; max-width: 600px; max-height: 80vh; overflow-y: auto; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 28px; border-bottom: 1px solid #f1f5f9; }
.modal-header h3 { font-size: 1.125rem; font-weight: 700; color: #1e293b; }
.modal-close { background: none; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
.modal-body { padding: 24px 28px; }
.modal-footer { padding: 16px 28px; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; gap: 12px; }

.scope-entry { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
.scope-field-name { font-weight: 700; color: #475569; margin-bottom: 8px; font-size: 0.875rem; }
.scope-values { display: flex; flex-wrap: wrap; gap: 8px; }
.scope-chip { display: inline-flex; align-items: center; gap: 6px; background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 20px; font-size: 0.8125rem; font-weight: 600; }
.chip-remove { background: none; border: none; color: #1e40af; cursor: pointer; font-size: 1rem; line-height: 1; }

.scope-add-row { display: flex; gap: 8px; margin-top: 16px; }
.scope-add-row select, .scope-add-row input { padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 0.875rem; outline: none; }

/* Security Info */
.security-info h3 { font-size: 1.5rem; font-weight: 700; color: #1e293b; margin-bottom: 32px; }
.info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; }
.icon-circle { width: 48px; height: 48px; background: #fdf2f8; color: var(--mso-accent); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
.icon-circle svg { width: 24px; height: 24px; }
.info-item h4 { font-size: 1.125rem; font-weight: 700; color: #1e293b; margin-bottom: 12px; }
.info-item p { color: #64748b; line-height: 1.6; }

@media (max-width: 768px) {
  .info-grid { grid-template-columns: 1fr; }
  .content-header { flex-direction: column; gap: 16px; }
}
</style>
