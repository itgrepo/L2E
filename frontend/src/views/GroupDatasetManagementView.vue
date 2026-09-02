<script setup>
import { ref, onMounted } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData } from '../utils/api';

const groups = ref([]);
const isLoading = ref(true);

// Modal Data
const showManageModal = ref(false);
const selectedGroup = ref(null);
const assignedDatasets = ref([]);
const availableDatasets = ref([]);
const isSaving = ref(false);

const showAddGroupModal = ref(false);
const newGroupName = ref('');
const isAddingGroup = ref(false);

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

const fetchGroups = async () => {
  isLoading.value = true;
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/getGroups', { user: userParam });
    if (response.data.status === 'success') {
      groups.value = response.data.data;
    }
  } catch (err) {
    console.error('Error fetching groups:', err);
  } finally {
    isLoading.value = false;
  }
};

const openManageModal = async (group) => {
  selectedGroup.value = group;
  showManageModal.value = true;
  assignedDatasets.value = [];
  availableDatasets.value = [];
  
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/getGroupDatasetAccess', {
      user: userParam,
      group_id: group.group_id
    });
    
    if (response.data.status === 'success') {
      assignedDatasets.value = response.data.assigned;
      availableDatasets.value = response.data.available;
    }
  } catch (err) {
    console.error('Error fetching dataset access:', err);
  }
};

const closeManageModal = () => {
  showManageModal.value = false;
  selectedGroup.value = null;
};

const assignDataset = (dataset) => {
  availableDatasets.value = availableDatasets.value.filter(d => d.service_id !== dataset.service_id);
  assignedDatasets.value.push(dataset);
};

const removeDataset = (dataset) => {
  assignedDatasets.value = assignedDatasets.value.filter(d => d.service_id !== dataset.service_id);
  availableDatasets.value.push(dataset);
};

const saveDatasetAccess = async () => {
  isSaving.value = true;
  try {
    const userParam = getUserParam();
    const serviceIds = assignedDatasets.value.map(d => d.service_id);
    
    const response = await apiClient.post('/updateGroupDatasetAccess', {
      user: userParam,
      group_id: selectedGroup.value.group_id,
      service_ids: serviceIds
    });
    
    if (response.data.status === 'success') {
      alert('บันทึกข้อมูลเรียบร้อยแล้ว');
      closeManageModal();
      fetchGroups(); // Refresh count
    } else {
      alert('Error: ' + response.data.status);
    }
  } catch (err) {
    console.error('Error saving access:', err);
    alert('ไม่สามารถบันทึกข้อมูลได้ กรุณาลองใหม่');
  } finally {
    isSaving.value = false;
  }
};

const handleAddGroup = async () => {
  if (!newGroupName.value.trim()) return;
  
  isAddingGroup.value = true;
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/addGroup', {
      user: userParam,
      group_name: newGroupName.value.trim()
    });
    
    if (response.data.status === 'success') {
      showAddGroupModal.value = false;
      newGroupName.value = '';
      fetchGroups();
    } else {
      alert(response.data.status || 'เกิดข้อผิดพลาดในการสร้างกลุ่ม');
    }
  } catch (err) {
    console.error('Error adding group:', err);
    alert('ไม่สามารถสร้างกลุ่มได้ กรุณาลองใหม่');
  } finally {
    isAddingGroup.value = false;
  }
};

const deleteGroup = async (group) => {
  if (!confirm(`คุณต้องการลบกลุ่ม "${group.group_name}" หรือไม่?\n\nข้อมูลสมาชิกและชุดข้อมูลที่กำหนดไว้ในกลุ่มนี้จะถูกลบทั้งหมด`)) {
    return;
  }
  
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/deleteGroup', {
      user: userParam,
      group_id: group.group_id
    });
    
    if (response.data.status === 'success') {
      alert('ลบกลุ่มเรียบร้อยแล้ว');
      fetchGroups();
    } else {
      alert('Error: ' + (response.data.message || 'ไม่สามารถลบกลุ่มได้'));
    }
  } catch (err) {
    console.error('Error deleting group:', err);
    alert('ไม่สามารถลบกลุ่มได้ กรุณาลองใหม่');
  }
};

onMounted(() => {
  fetchGroups();
});
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div>
          <h1>Group Dataset Management</h1>
          <p class="subtitle">จัดการสิทธิ์การเข้าถึงชุดข้อมูลของแต่ละกลุ่มผู้ใช้</p>
        </div>
        <button class="btn-primary" @click="showAddGroupModal = true">+ สร้างกลุ่มใหม่</button>
      </header>

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
      </div>

      <div v-else class="card-grid">
        <div v-if="groups.length === 0" class="empty-state-card" style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; background: white; border-radius: 20px; border: 2px dashed #e2e8f0;">
          <div style="font-size: 3rem; margin-bottom: 16px;">📂</div>
          <h3 style="color: #475569; margin-bottom: 8px;">ยังไม่มีกลุ่มในระบบ</h3>
          <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 24px;">กรุณาสร้างกลุ่มใหม่เพื่อเริ่มต้นการจัดการสิทธิ์ชุดข้อมูล</p>
          <button class="btn-primary" @click="showAddGroupModal = true">สร้างกลุ่มใหม่</button>
        </div>
        
        <div v-for="group in groups" :key="group.group_id" class="card">
          <div class="card-icon">🔐</div>
          <h3>{{ group.group_name }}</h3>
          <p class="owner">สร้างเมื่อ: {{ group.create_at }}</p>
          <div class="card-stats">
            <div class="stat">
              <span class="stat-value">{{ group.member_count }}</span>
              <span class="stat-label">สมาชิก</span>
            </div>
            <div class="stat">
              <span class="stat-value">{{ group.dataset_count || 0 }}</span>
              <span class="stat-label">ชุดข้อมูล</span>
            </div>
          </div>
          <div class="card-footer">
            <button class="btn-manage" @click="openManageModal(group)">
              <span>⚙️</span> จัดการชุดข้อมูล
            </button>
            <button class="btn-delete-group" @click="deleteGroup(group)" title="ลบกลุ่ม">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
              ลบกลุ่ม
            </button>
          </div>
        </div>
      </div>

      <!-- Manage Dataset Access Modal -->
      <div v-if="showManageModal" class="modal-overlay">
        <div class="modal">
          <div class="modal-header">
            <h2>จัดการชุดข้อมูล - {{ selectedGroup?.group_name }}</h2>
            <button class="btn-close" @click="closeManageModal">✕</button>
          </div>
          
          <div class="modal-body access-layout">
            <div class="access-panel">
              <div class="panel-header">
                <h3>ชุดข้อมูลทั้งหมด ({{ availableDatasets.length }})</h3>
              </div>
              <div class="panel-list">
                <div v-if="availableDatasets.length === 0" class="empty-state">ไม่มีชุดข้อมูลเพิ่มเติม</div>
                <div v-for="dataset in availableDatasets" :key="dataset.service_id" class="list-item">
                  <div class="item-info">
                    <strong>{{ dataset.service_name }}</strong>
                    <small>{{ dataset.provider_name || 'N/A' }}</small>
                  </div>
                  <button class="btn-action add" @click="assignDataset(dataset)">+</button>
                </div>
              </div>
            </div>

            <div class="access-panel assigned-panel">
              <div class="panel-header">
                <h3>ชุดข้อมูลที่เข้าถึงได้ ({{ assignedDatasets.length }})</h3>
              </div>
              <div class="panel-list">
                <div v-if="assignedDatasets.length === 0" class="empty-state">ยังไม่มีชุดข้อมูลที่กำหนด</div>
                <div v-for="dataset in assignedDatasets" :key="dataset.service_id" class="list-item assigned">
                  <div class="item-info">
                    <strong>{{ dataset.service_name }}</strong>
                    <small>{{ dataset.provider_name || 'N/A' }}</small>
                  </div>
                  <button class="btn-action remove" @click="removeDataset(dataset)">✕</button>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="closeManageModal">ยกเลิก</button>
            <button class="btn-save" @click="saveDatasetAccess" :disabled="isSaving">
              {{ isSaving ? 'กำลังบันทึก...' : 'บันทึกการเปลี่ยนแปลง' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Add Group Modal -->
      <div v-if="showAddGroupModal" class="modal-overlay">
        <div class="modal" style="max-width: 500px;">
          <div class="modal-header">
            <h2>สร้างกลุ่มใหม่</h2>
            <button class="btn-close" @click="showAddGroupModal = false">✕</button>
          </div>
          
          <div class="modal-body">
            <div class="form-group" style="display: flex; flex-direction: column; gap: 8px;">
              <label for="group-name" style="font-weight: 600; color: #475569;">ชื่อกลุ่ม (Group Name)</label>
              <input 
                id="group-name" 
                v-model="newGroupName" 
                type="text" 
                placeholder="เช่น: ฝ่ายสิ่งแวดล้อม, พนักงานขาย" 
                style="padding: 12px; border: 1px solid #cbd5e1; border-radius: 10px; font-size: 1rem;"
                @keyup.enter="handleAddGroup"
              />
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="showAddGroupModal = false">ยกเลิก</button>
            <button class="btn-save" @click="handleAddGroup" :disabled="isAddingGroup || !newGroupName.trim()">
              {{ isAddingGroup ? 'กำลังสร้าง...' : 'สร้างกลุ่ม' }}
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
  background-color: #f8fafc;
}

.content {
  flex: 1;
  padding: 40px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.btn-primary {
  background-color: var(--primary, #4f46e5);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.card {
  background: white;
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: 16px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef2ff;
  border-radius: 14px;
}

h3 {
  margin: 0 0 4px;
  color: #1e293b;
  font-size: 1.25rem;
}

.owner {
  color: #94a3b8;
  font-size: 0.85rem;
  margin-bottom: 20px;
}

.card-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-footer {
  margin-top: auto;
  display: flex;
  gap: 8px;
}

.btn-manage {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #3b82f6;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-manage:hover {
  background-color: #eff6ff;
  border-color: #bfdbfe;
}

.btn-delete-group {
  padding: 12px;
  border-radius: 12px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 0.85rem;
  white-space: nowrap;
}

.btn-delete-group:hover {
  background-color: #fee2e2;
  border-color: #f87171;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 24px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #1e293b;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
}

.btn-close:hover {
  color: #ef4444;
}

.modal-body {
  padding: 32px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.access-layout {
  display: flex;
  gap: 24px;
}

.access-panel {
  flex: 1;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  max-height: 500px;
}

.assigned-panel {
  border-color: #bbf7d0;
  background-color: #eef2ff;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  background-color: #f8fafc;
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
}

.assigned-panel .panel-header {
  background-color: #eef2ff;
  border-bottom-color: #bbf7d0;
}

.panel-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #475569;
}

.assigned-panel .panel-header h3 {
  color: #166534;
}

.panel-list {
  padding: 12px;
  overflow-y: auto;
  flex: 1;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  margin-bottom: 8px;
  transition: all 0.2s;
}

.list-item:hover {
  border-color: #cbd5e1;
}

.list-item.assigned {
  border-color: #bbf7d0;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-info strong {
  font-size: 0.95rem;
  color: #1e293b;
}

.item-info small {
  font-size: 0.8rem;
  color: #64748b;
}

.btn-action {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action.add {
  background-color: #eff6ff;
  color: #3b82f6;
}

.btn-action.add:hover {
  background-color: #3b82f6;
  color: white;
}

.btn-action.remove {
  background-color: #fef2f2;
  color: #ef4444;
}

.btn-action.remove:hover {
  background-color: #ef4444;
  color: white;
}

.empty-state {
  padding: 32px;
  text-align: center;
  color: #94a3b8;
  font-size: 0.9rem;
}

.modal-footer {
  padding: 24px 32px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  background-color: #f8fafc;
}

.btn-cancel {
  padding: 12px 24px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  color: #64748b;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #f1f5f9;
}

.btn-save {
  padding: 12px 24px;
  background: #3b82f6;
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* ============================================
   RESPONSIVE: Tablet (≤ 1024px)
   ============================================ */
@media (max-width: 1024px) {
  .content { padding: 24px; }
  .access-layout { flex-direction: column; min-height: 0; }
  .access-panel { max-height: none; height: 350px; flex: none; min-height: 350px; }
  .table-wrapper { overflow-x: auto; }
}

/* ============================================
   RESPONSIVE: Mobile (≤ 768px)
   ============================================ */
@media (max-width: 768px) {
  .content { padding: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .header-actions { width: 100%; justify-content: flex-start; }
  .search-wrapper { width: 100%; max-width: none; }
  .search-wrapper input { width: 100%; }
}

/* ============================================
   RESPONSIVE: Small Mobile (≤ 480px)
   ============================================ */
@media (max-width: 480px) {
  .content { padding: 12px; }
  .modal { width: 95%; padding: 0; }
  .modal-header { padding: 16px; }
  .modal-body { padding: 16px; }
  .modal-footer { padding: 16px; flex-direction: column; }
  .btn-save, .btn-cancel { width: 100%; }
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  vertical-align: middle;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  transition: .4s;
}
.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}
input:checked + .slider {
  background-color: #10b981;
}
input:checked + .slider:before {
  transform: translateX(20px);
}
.slider.round {
  border-radius: 24px;
}
.slider.round:before {
  border-radius: 50%;
}
</style>
