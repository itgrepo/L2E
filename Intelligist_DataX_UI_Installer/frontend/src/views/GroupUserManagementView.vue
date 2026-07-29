<script setup>
import { ref, onMounted, computed } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData, postWithUser } from '../utils/api';

const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));
const groups = ref([]);
const isLoading = ref(true);
const isCreateModalOpen = ref(false);
const isMemberModalOpen = ref(false);

const newGroupName = ref('');
const selectedGroup = ref(null);

// Member Management State
const availableUsers = ref([]);
const assignedUsers = ref([]);
const memberSearchQuery = ref('');
const availableSearchQuery = ref('');

const fetchGroups = async () => {
    isLoading.value = true;
    try {
        const response = await postWithUser('/getGroups', user.value);
        if (response.data.status === 'success') {
            groups.value = response.data.data;
        }
    } catch (error) {
        console.error('Error fetching groups:', error);
    } finally {
        isLoading.value = false;
    }
};

const openCreateModal = () => {
    newGroupName.value = '';
    isCreateModalOpen.value = true;
};

const handleCreateGroup = async () => {
    if (!newGroupName.value) return;
    try {
        const response = await postWithUser('/addGroup', user.value, {
            group_name: newGroupName.value
        });
        if (response.data.status === 'success') {
            isCreateModalOpen.value = false;
            fetchGroups();
        } else {
            alert(response.data.status);
        }
    } catch (error) {
        console.error('Error adding group:', error);
    }
};

const openMemberModal = async (group) => {
    selectedGroup.value = group;
    availableUsers.value = [];
    assignedUsers.value = [];
    isMemberModalOpen.value = true;
    
    try {
        const response = await postWithUser('/getGroupMembers', user.value, {
            group_id: group.group_id
        });
        if (response.data.status === 'success') {
            assignedUsers.value = response.data.assigned;
            availableUsers.value = response.data.available;
        }
    } catch (error) {
        console.error('Error fetching members:', error);
    }
};

const assignUser = (user) => {
    availableUsers.value = availableUsers.value.filter(u => u.user_id !== user.user_id);
    assignedUsers.value.push(user);
};

const unassignUser = (user) => {
    assignedUsers.value = assignedUsers.value.filter(u => u.user_id !== user.user_id);
    availableUsers.value.push(user);
};

const handleUpdateMembers = async () => {
    try {
        const response = await postWithUser('/updateGroupMembers', user.value, {
            group_id: selectedGroup.value.group_id,
            user_ids: assignedUsers.value.map(u => u.user_id)
        });
        if (response.data.status === 'success') {
            isMemberModalOpen.value = false;
            fetchGroups();
        }
    } catch (error) {
        console.error('Error updating members:', error);
    }
};

const deleteGroup = async (group_id) => {
    if (!confirm('ยืนยันการลบกลุ่ม? สมาชิกในกลุ่มจะถูกถอนการเชื่อมโยงแต่ตัวผู้ใช้จะไม่ถูกลบ')) return;
    try {
        const response = await postWithUser('/deleteGroup', user.value, {
            group_id: group_id
        });
        if (response.data.status === 'success') {
            fetchGroups();
        }
    } catch (error) {
        console.error('Error deleting group:', error);
    }
};

// Helper for encoding (if not in utils)
function b64EncodeUnicode(str) {
    return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
        function (match, p1) {
            return String.fromCharCode('0x' + p1);
        }));
}

const filteredAvailable = computed(() => {
    if (!availableSearchQuery.value) return availableUsers.value;
    const q = availableSearchQuery.value.toLowerCase();
    return availableUsers.value.filter(u => 
        u.username.toLowerCase().includes(q) || 
        u.firstname.toLowerCase().includes(q) || 
        u.lastname.toLowerCase().includes(q)
    );
});

const filteredAssigned = computed(() => {
    if (!memberSearchQuery.value) return assignedUsers.value;
    const q = memberSearchQuery.value.toLowerCase();
    return assignedUsers.value.filter(u => 
        u.username.toLowerCase().includes(q) || 
        u.firstname.toLowerCase().includes(q) || 
        u.lastname.toLowerCase().includes(q)
    );
});

onMounted(() => {
    fetchGroups();
});
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div class="header-main">
          <h1>Group User Management</h1>
          <p class="subtitle">จัดการกลุ่มผู้ใช้งานและการแบ่งปันข้อมูลภายในกลุ่มแบบรวมศูนย์</p>
        </div>
        <button class="btn-primary" @click="openCreateModal">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          Create New Group
        </button>
      </header>

      <!-- Stats Summary -->
      <div class="stats-grid">
        <div class="stat-card glass-card">
          <div class="stat-icon bg-blue-soft">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <p class="stat-label">Total Groups</p>
            <p class="stat-value">{{ groups.length }}</p>
          </div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-icon bg-green-soft">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <p class="stat-label">Total Members</p>
            <p class="stat-value">{{ groups.reduce((acc, g) => acc + g.member_count, 0) }}</p>
          </div>
        </div>
      </div>

      <!-- Groups Table -->
      <div class="table-card glass-card shadow-premium">
        <div class="table-header">
          <h2>รายชื่อกลุ่มผู้ใช้งานในระบบ</h2>
          <div class="table-actions">
            <!-- Search placeholder -->
          </div>
        </div>
        
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th width="40%">Group Name</th>
                <th width="20%">Members</th>
                <th width="20%">Created Date</th>
                <th width="20%">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="isLoading">
                <td colspan="4" class="text-center py-10">กำลังโหลดข้อมูล...</td>
              </tr>
              <tr v-else-if="groups.length === 0">
                <td colspan="4" class="text-center py-10">ยังไม่มีกลุ่มผู้ใช้งานในระบบ</td>
              </tr>
              <tr v-for="group in groups" :key="group.group_id" class="group-row">
                <td>
                  <div class="group-name-cell">
                    <div class="group-avatar">{{ group.group_name.charAt(0).toUpperCase() }}</div>
                    <div class="group-name-info">
                      <strong>{{ group.group_name }}</strong>
                      <span>ID: #{{ group.group_id }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="member-badge">{{ group.member_count }} Members</span>
                </td>
                <td>{{ new Date(group.create_at).toLocaleDateString() }}</td>
                <td>
                  <div class="actions">
                    <button class="action-btn manage" @click="openMemberModal(group)">
                      Manage
                    </button>
                    <button class="action-btn delete" @click="deleteGroup(group.group_id)">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Create Group Modal -->
      <div v-if="isCreateModalOpen" class="modal-overlay" @click.self="isCreateModalOpen = false">
        <div class="modal-container glass-modal shadow-premium">
          <div class="modal-header">
            <h3>Create New User Group</h3>
            <button class="close-btn" @click="isCreateModalOpen = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Group Name</label>
              <input type="text" v-model="newGroupName" placeholder="เช่น ทีมวิเคราะห์ข้อมูลประชากร" @keyup.enter="handleCreateGroup">
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="isCreateModalOpen = false">Cancel</button>
            <button class="btn-submit" @click="handleCreateGroup" :disabled="!newGroupName">Confirm Create</button>
          </div>
        </div>
      </div>

      <!-- Manage Members Modal -->
      <div v-if="isMemberModalOpen" class="modal-overlay" @click.self="isMemberModalOpen = false">
        <div class="modal-container member-modal glass-modal shadow-premium">
          <div class="modal-header">
            <div>
              <h3>จัดการสมาชิกกลุ่ม: {{ selectedGroup?.group_name }}</h3>
              <p class="modal-subtitle">เพิ่มหรือลดชื่อผู้ใช้งานออกจากกลุ่มนี้</p>
            </div>
            <button class="close-btn" @click="isMemberModalOpen = false">&times;</button>
          </div>
          
          <div class="modal-body assignment-layout">
            <!-- Left: Available -->
            <div class="assignment-panel">
              <div class="panel-header">
                <h4>ผู้ใช้งานในระบบ ({{ filteredAvailable.length }})</h4>
                <div class="search-box">
                  <input type="text" v-model="availableSearchQuery" placeholder="ค้นหาตามชื่อ...">
                </div>
              </div>
              <div class="user-list">
                <div v-for="u in filteredAvailable" :key="u.user_id" class="user-item available">
                  <div class="u-info">
                    <p class="u-name">{{ u.firstname }} {{ u.lastname }}</p>
                    <p class="u-user">@{{ u.username }}</p>
                  </div>
                  <button class="add-btn" @click="assignUser(u)">
                    Add
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div class="assignment-divider">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            </div>

            <!-- Right: Assigned -->
            <div class="assignment-panel assigned">
              <div class="panel-header">
                <h4>สมาชิกปัจจุบัน ({{ filteredAssigned.length }})</h4>
                <div class="search-box">
                  <input type="text" v-model="memberSearchQuery" placeholder="ค้นหาตามชื่อ...">
                </div>
              </div>
              <div class="user-list">
                <div v-if="assignedUsers.length === 0" class="empty-state">
                  ยังไม่มีสมาชิกในกลุ่มนี้
                </div>
                <div v-for="u in filteredAssigned" :key="u.user_id" class="user-item assigned">
                  <div class="u-info">
                    <p class="u-name">{{ u.firstname }} {{ u.lastname }}</p>
                    <p class="u-user">@{{ u.username }}</p>
                  </div>
                  <button class="remove-btn" @click="unassignUser(u)">
                    Remove
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="isMemberModalOpen = false">Cancel</button>
            <button class="btn-submit save" @click="handleUpdateMembers">Save Changes</button>
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
  padding: 40px 60px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

h1 {
  font-size: 2.25rem;
  font-weight: 800;
  background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.subtitle {
  color: #64748b;
  font-size: 1.1rem;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.15);
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(15, 23, 42, 0.2);
}

/* Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 320px);
  gap: 24px;
  margin-bottom: 40px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-blue-soft { background-color: #eff6ff; }
.bg-green-soft { background-color: var(--mso-pink-dark); }

.stat-label {
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 800;
  color: #0f172a;
}

/* Glassmorphism Styles */
.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 20px;
}

.shadow-premium {
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 10px -2px rgba(0, 0, 0, 0.02);
}

/* Table Styles */
.table-card {
  padding: 0;
  border-radius: 24px;
  overflow: hidden;
}

.table-header {
  padding: 28px 32px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background-color: #f8fafc;
  padding: 16px 32px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  color: #94a3b8;
  letter-spacing: 0.05em;
}

.group-row:hover {
  background-color: #f1f5f9;
}

.data-table td {
  padding: 24px 32px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}

.group-name-cell {
  display: flex;
  align-items: center;
  gap: 16px;
}

.group-avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.1rem;
  box-shadow: 0 4px 10px -2px rgba(37, 99, 235, 0.3);
}

.group-name-info strong {
  display: block;
  font-size: 1.05rem;
  color: #0f172a;
}

.group-name-info span {
  font-size: 0.8rem;
  color: #94a3b8;
}

.member-badge {
  background-color: #f1f5f9;
  color: #475569;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
}

.actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.manage {
  background-color: #eff6ff;
  color: #2563eb;
  border: 1px solid #dbeafe;
}

.action-btn.manage:hover {
  background-color: #2563eb;
  color: white;
}

.action-btn.delete {
  background-color: #fef2f2;
  color: #ef4444;
  border: 1px solid #fee2e2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn.delete:hover {
  background-color: #ef4444;
  color: white;
}

/* Modals */
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

.modal-container {
  width: 100%;
  max-width: 500px;
  border-radius: 28px;
  padding: 32px;
}

.glass-modal {
  background: white;
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.modal-header h3 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
}

.modal-subtitle {
  color: #64748b;
  font-size: 0.9rem;
  margin-top: 4px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
}

.form-group label {
  display: block;
  font-weight: 700;
  color: #334155;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.form-group input {
  width: 100%;
  padding: 14px 18px;
  border: 2px solid #f1f5f9;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.2s;
}

.form-group input:focus {
  border-color: #3b82f6;
  outline: none;
  background-color: #fff;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 32px;
}

.btn-cancel {
  padding: 12px 24px;
  border-radius: 12px;
  background: #f1f5f9;
  color: #64748b;
  border: none;
  font-weight: 700;
  cursor: pointer;
}

.btn-submit {
  padding: 12px 28px;
  border-radius: 12px;
  background: #0f172a;
  color: white;
  border: none;
  font-weight: 700;
  cursor: pointer;
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Membership Assignment Layout */
.member-modal {
  max-width: 900px;
}

.assignment-layout {
  display: flex;
  gap: 32px;
  align-items: stretch;
}

.assignment-panel {
  flex: 1;
  background-color: #f8fafc;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  max-height: 500px;
}

.panel-header {
  margin-bottom: 16px;
}

.panel-header h4 {
  font-size: 1rem;
  font-weight: 800;
  color: #334155;
  margin-bottom: 12px;
}

.search-box input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.9rem;
}

.user-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-right: 4px;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  background-color: white;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
  transition: all 0.2s;
}

.u-name {
  font-weight: 700;
  color: #1e293b;
  font-size: 0.95rem;
}

.u-user {
  font-size: 0.8rem;
  color: #94a3b8;
}

.add-btn, .remove-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  border: none;
}

.add-btn {
  background-color: var(--mso-pink-dark);
  color: var(--primary);
}
.add-btn:hover { background-color: var(--primary); color: white; }

.remove-btn {
  background-color: #fef2f2;
  color: #ef4444;
}
.remove-btn:hover { background-color: #ef4444; color: white; }

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #94a3b8;
  font-style: italic;
}

.assignment-divider {
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-submit.save {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
}

/* Custom Scrollbar */
.user-list::-webkit-scrollbar {
  width: 6px;
}
.user-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
</style>
