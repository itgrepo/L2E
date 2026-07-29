<script setup>
import { ref, onMounted, computed } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData } from '../utils/api';

const organizations = ref([]);
const isLoading = ref(true);
const searchQuery = ref('');

// Modals
const showAddModal = ref(false);
const showEditModal = ref(false);
const isSubmitting = ref(false);

const newOrg = ref({
  org_name: '',
  org_description: ''
});

const editingOrg = ref({
  org_id: null,
  org_name: '',
  org_description: ''
});

const getUserParam = () => {
  const user = localStorage.getItem('user');
  if (user) {
    try {
      const parsedUser = JSON.parse(user);
      return encodeUserData(parsedUser);
    } catch (e) {
      return '';
    }
  }
  return '';
};

const fetchOrganizations = async () => {
  isLoading.value = true;
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/getOrganizations', { user: userParam });
    if (response.data.status === 'success') {
      organizations.value = response.data.data;
    }
  } catch (err) {
    console.error('Error fetching organizations:', err);
  } finally {
    isLoading.value = false;
  }
};

const handleAdd = async () => {
  if (!newOrg.value.org_name.trim()) return;
  
  isSubmitting.value = true;
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/addOrganization', {
      user: userParam,
      org_name: newOrg.value.org_name,
      org_description: newOrg.value.org_description
    });
    
    if (response.data.status === 'success') {
      showAddModal.value = false;
      newOrg.value = { org_name: '', org_description: '' };
      fetchOrganizations();
    } else {
      alert(response.data.status);
    }
  } catch (err) {
    console.error('Error adding organization:', err);
    alert('ไม่สามารถเพิ่มข้อมูลได้');
  } finally {
    isSubmitting.value = false;
  }
};

const openEditModal = (org) => {
  editingOrg.value = { ...org };
  showEditModal.value = true;
};

const handleUpdate = async () => {
  if (!editingOrg.value.org_name.trim()) return;
  
  isSubmitting.value = true;
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/updateOrganization', {
      user: userParam,
      org_id: editingOrg.value.org_id,
      org_name: editingOrg.value.org_name,
      org_description: editingOrg.value.org_description
    });
    
    if (response.data.status === 'success') {
      showEditModal.value = false;
      fetchOrganizations();
    } else {
      alert(response.data.status);
    }
  } catch (err) {
    console.error('Error updating organization:', err);
    alert('ไม่สามารถบันทึกข้อมูลได้');
  } finally {
    isSubmitting.value = false;
  }
};

const handleDelete = async (orgId) => {
  if (!confirm('ยืนยันบันการลบข้อมูลองค์กรนี้?')) return;
  
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/deleteOrganization', {
      user: userParam,
      org_id: orgId
    });
    
    if (response.data.status === 'success') {
      fetchOrganizations();
    } else {
      alert(response.data.status);
    }
  } catch (err) {
    console.error('Error deleting organization:', err);
    alert('ไม่สามารถลบข้อมูลได้');
  }
};

const filteredOrganizations = computed(() => {
  if (!searchQuery.value) return organizations.value;
  const query = searchQuery.value.toLowerCase();
  return organizations.value.filter(org => 
    org.org_name.toLowerCase().includes(query) || 
    (org.org_description && org.org_description.toLowerCase().includes(query))
  );
});

onMounted(fetchOrganizations);
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div>
          <h1>Organization Management</h1>
          <p class="subtitle">จัดการรายชื่อองค์กรในระบบ</p>
        </div>
      </header>

      <div class="table-card">
        <div class="table-header">
          <div class="header-main">
            <h2>รายชื่อองค์กร</h2>
            <button class="btn-add" @click="showAddModal = true">
              <span class="icon">+</span> เพิ่มองค์กร
            </button>
          </div>
          
          <div class="search-bar">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="ค้นหาชื่อองค์กร หรือรายละเอียด..." 
            />
          </div>
        </div>

        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
        </div>

        <div v-else class="table-responsive">
          <table>
            <thead>
              <tr>
                <th style="width: 40%">ชื่อองค์กร</th>
                <th style="width: 45%">รายละเอียด</th>
                <th style="width: 15%; text-align: center;">จัดการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredOrganizations.length === 0">
                <td colspan="3" class="empty-state">ไม่พบข้อมูลองค์กร</td>
              </tr>
              <tr v-for="org in filteredOrganizations" :key="org.org_id">
                <td>
                  <div class="org-name-cell">
                    <div class="org-icon">🏢</div>
                    <strong>{{ org.org_name }}</strong>
                  </div>
                </td>
                <td>
                  <p class="description-text">{{ org.org_description || '-' }}</p>
                </td>
                <td>
                  <div class="action-group">
                    <button class="btn-icon edit" title="แก้ไข" @click="openEditModal(org)">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                      </svg>
                    </button>
                    <button class="btn-icon delete" title="ลบ" @click="handleDelete(org.org_id)">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /><line x1="10" y1="11" x2="10" y2="17" /><line x1="14" y1="11" x2="14" y2="17" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Add Modal -->
      <div v-if="showAddModal" class="modal-overlay">
        <div class="modal">
          <div class="modal-header">
            <h2>เพิ่มองค์กรใหม่</h2>
            <button class="btn-close" @click="showAddModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>ชื่อองค์กร</label>
              <input v-model="newOrg.org_name" type="text" placeholder="ระบุชื่อองค์กร" />
            </div>
            <div class="form-group">
              <label>รายละเอียด</label>
              <textarea v-model="newOrg.org_description" rows="4" placeholder="ระบุรายละเอียดเพิ่มเติม..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showAddModal = false">ยกเลิก</button>
            <button class="btn-save" :disabled="isSubmitting" @click="handleAdd">
              {{ isSubmitting ? 'กำลังบันทึก...' : 'บันทึกข้อมูล' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div v-if="showEditModal" class="modal-overlay">
        <div class="modal">
          <div class="modal-header">
            <h2>แก้ไขข้อมูลองค์กร</h2>
            <button class="btn-close" @click="showEditModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>ชื่อองค์กร</label>
              <input v-model="editingOrg.org_name" type="text" placeholder="ระบุชื่อองค์กร" />
            </div>
            <div class="form-group">
              <label>รายละเอียด</label>
              <textarea v-model="editingOrg.org_description" rows="4" placeholder="ระบุรายละเอียดเพิ่มเติม..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showEditModal = false">ยกเลิก</button>
            <button class="btn-save" :disabled="isSubmitting" @click="handleUpdate">
              {{ isSubmitting ? 'กำลังบันทึก...' : 'บันทึกการแก้ไข' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background-color: #f1f5f9;
}

.content {
  flex: 1;
  padding: 40px;
}

.page-header {
  margin-bottom: 32px;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
}

.subtitle {
  color: #64748b;
  margin-top: 4px;
}

.table-card {
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-header {
  padding: 32px;
  border-bottom: 1px solid #f1f5f9;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-main h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  border-left: 4px solid var(--primary);
  padding-left: 16px;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #f8fafc;
  border: 2px solid #e2e8f0;
  color: #334155;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.btn-add .icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  font-size: 1.25rem;
}

.search-bar input {
  width: 100%;
  max-width: 400px;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background-color: #f8fafc;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.search-bar input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
  background-color: white;
}

.table-responsive {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background-color: #f8fafc;
  padding: 16px 32px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: 20px 32px;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
  vertical-align: middle;
}

.org-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.org-icon {
  width: 36px;
  height: 36px;
  background-color: var(--mso-pink-dark);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.description-text {
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.action-group {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon svg {
  width: 18px;
  height: 18px;
}

.btn-icon.edit {
  background-color: #fef3c7;
  color: #d97706;
}

.btn-icon.edit:hover {
  background-color: #fde68a;
  color: #92400e;
}

.btn-icon.delete {
  background-color: #fee2e2;
  color: #ef4444;
}

.btn-icon.delete:hover {
  background-color: #fecaca;
  color: #b91c1c;
}

.loading-state {
  padding: 60px;
  display: flex;
  justify-content: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f5f9;
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
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
  max-width: 500px;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
}

.modal-body {
  padding: 32px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.form-group input, .form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
}

.form-group input:focus, .form-group textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.modal-footer {
  padding: 24px 32px;
  background-color: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.btn-cancel {
  padding: 10px 20px;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
  background: white;
  color: #64748b;
  font-weight: 600;
  cursor: pointer;
}

.btn-save {
  padding: 10px 24px;
  border-radius: 12px;
  border: none;
  background: var(--primary);
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
