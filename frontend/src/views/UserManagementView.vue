<script setup>
import { ref, onMounted, computed } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import { postWithUser } from '../utils/api';

const users = ref([]);
const roles = ref([]);

const groups = ref([]);
const showAddModal = ref(false);
const formData = ref({
    username: '',
    email: '',
    password: '',
    previlage_id: 3,
    status_id: 1,
    groups: []
});
const isSubmitting = ref(false);

const fetchGroups = async () => {
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/getGroups', userStored);
        if (response.data && response.data.status === 'success') {
            groups.value = response.data.data;
        }
    } catch (error) {
        console.error('Error fetching groups:', error);
    }
};

const openAddModal = () => {
    formData.value = {
        username: '',
        email: '',
        password: '',
        previlage_id: 3,
        status_id: 1,
        groups: []
    };
    showAddModal.value = true;
};

const closeAddModal = () => {
    showAddModal.value = false;
};

const handleSaveUser = async () => {
    if (!formData.value.username || !formData.value.email || !formData.value.password) {
        showAlert('กรุณากรอกข้อมูล Username, Email และ Password ให้ครบถ้วน', 'error');
        return;
    }
    
    isSubmitting.value = true;
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/createUser', userStored, formData.value);
        
        if (response.data.status === 'success') {
            showAlert(`สร้างผู้ใช้ ${formData.value.username} สำเร็จ`, 'success');
            closeAddModal();
            fetchUsers();
        } else {
            showAlert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status), 'error');
        }
    } catch (error) {
        console.error('Error creating user:', error);
        showAlert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');
    } finally {
        isSubmitting.value = false;
    }
};

const isLoading = ref(true);
const searchQuery = ref('');
const alertMessage = ref({ text: '', type: '' });

const fetchUsers = async () => {
    isLoading.value = true;
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/addUser', userStored);
        if (Array.isArray(response.data)) {
            users.value = response.data;
        }
    } catch (error) {
        console.error('Error fetching users:', error);
    } finally {
        isLoading.value = false;
    }
};

const fetchRoles = async () => {
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/getRoles', userStored);
        if (Array.isArray(response.data)) {
            roles.value = response.data;
        }
    } catch (error) {
        console.error('Error fetching roles:', error);
    }
};

const handleRoleChange = async (user, newRoleId) => {
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/updateUserById', userStored, {
            target_user_id: user.user_id,
            previlage_id: newRoleId
        });
        
        if (response.data.status === 'success') {
            showAlert(`อัปเดตบทบาทของ ${user.username} สำเร็จ`, 'success');
            fetchUsers(); // Refresh list to get new role names
        } else {
            showAlert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status), 'error');
        }
    } catch (error) {
        console.error('Error updating role:', error);
        showAlert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');
    }
};

const handleDeleteUser = async (user) => {
    if (!confirm(`คุณแน่ใจหรือไม่ว่าต้องการลบผู้ใช้ "${user.username}"? การกระทำนี้ไม่สามารถกู้คืนได้`)) {
        return;
    }
    
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/deleteUser', userStored, {
            target_user_id: user.user_id
        });
        
        if (response.data.status === 'success') {
            showAlert(`ลบผู้ใช้ ${user.username} สำเร็จ`, 'success');
            fetchUsers(); // Refresh list
        } else {
            showAlert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status), 'error');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showAlert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');
    }
};

const showAlert = (text, type) => {
    alertMessage.value = { text, type };
    setTimeout(() => { alertMessage.value = { text: '', type: '' }; }, 3000);
};

const filteredUsers = computed(() => {
    if (!searchQuery.value) return users.value;
    const q = searchQuery.value.toLowerCase();
    return users.value.filter(u => 
        u.username?.toLowerCase().includes(q) || 
        u.email?.toLowerCase().includes(q)
    );
});

const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric' });
};

onMounted(() => {
    fetchUsers();
    fetchRoles();
    fetchGroups();
});
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div>
          <h1>User Management</h1>
          <p class="subtitle">จัดการข้อมูลผู้ใช้และกำหนดบทบาทการเข้าถึงระบบ</p>
        </div>
        
        <div class="header-actions">
            <button class="btn-primary" @click="openAddModal">
                <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add User
            </button>
            <div class="search-container">
                <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input type="text" v-model="searchQuery" placeholder="ค้นหาด้วย Username หรือ Email...">
            </div>
        </div>
      </header>

      <!-- Alert Message -->
      <transition name="fade">
        <div v-if="alertMessage.text" :class="['alert-banner', alertMessage.type]">
            {{ alertMessage.text }}
        </div>
      </transition>

      <div class="card shadow-premium">
        <div v-if="isLoading" class="loading-state">
            <div class="spinner"></div>
            <p>กำลังโหลดรายชื่อผู้ใช้...</p>
        </div>

        <div v-else class="table-container">
          <div class="mobile-cards-view">
            <div v-for="(u, idx) in filteredUsers" :key="u.user_id" class="mobile-card">
              <div class="mc-header">
                <div class="user-info">
                  <div class="user-avatar">{{ u.username.charAt(0).toUpperCase() }}</div>
                  <div>
                      <div class="username-text">{{ u.username }}</div>
                      <div class="user-id-text">ID: #{{ u.user_id }}</div>
                  </div>
                </div>
                <div class="actions-group">
                  <button class="delete-btn" @click="handleDeleteUser(u)" title="ลบผู้ใช้">
                    <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              <div class="mc-body">
                <div class="mc-row">
                  <span class="mc-label">อีเมล</span>
                  <span class="mc-value">{{ u.email || '-' }}</span>
                </div>
                <div class="mc-row">
                  <span class="mc-label">วันที่เข้าร่วม</span>
                  <span class="mc-value">{{ formatDate(u.create_at) }}</span>
                </div>
                <div class="mc-row">
                  <span class="mc-label">บทบาท</span>
                  <div class="role-selector-box mobile-select">
                    <select 
                        :value="u.previlage_id" 
                        @change="handleRoleChange(u, $event.target.value)"
                        class="role-select"
                    >
                        <option v-for="role in roles" :key="role.previlage_id" :value="role.previlage_id">
                            {{ role.previlage_name }}
                        </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <table class="data-table desktop-table-view">
            <thead>
              <tr>
                <th>#</th>
                <th>ผู้ใช้งาน</th>
                <th>อีเมล</th>
                <th>วันที่เข้าร่วม</th>
                <th>บทบาทปัจจุบัน</th>
                <th>ดำเนินการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(u, idx) in filteredUsers" :key="u.user_id">
                <td>{{ idx + 1 }}</td>
                <td>
                  <div class="user-info">
                    <div class="user-avatar">{{ u.username.charAt(0).toUpperCase() }}</div>
                    <div>
                        <div class="username-text">{{ u.username }}</div>
                        <div class="user-id-text">ID: #{{ u.user_id }}</div>
                    </div>
                  </div>
                </td>
                <td>{{ u.email || '-' }}</td>
                <td>{{ formatDate(u.create_at) }}</td>
                <td>
                  <span class="role-badge" :class="u.previlage_name?.toLowerCase()">
                    {{ u.previlage_name || 'No Role' }}
                  </span>
                </td>
                <td>
                  <div class="actions-group">
                    <div class="role-selector-box">
                      <select 
                          :value="u.previlage_id" 
                          @change="handleRoleChange(u, $event.target.value)"
                          class="role-select"
                      >
                          <option v-for="role in roles" :key="role.previlage_id" :value="role.previlage_id">
                              {{ role.previlage_name }}
                          </option>
                      </select>
                    </div>
                    <button class="delete-btn" @click="handleDeleteUser(u)" title="ลบผู้ใช้">
                      <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="filteredUsers.length === 0" class="no-results">
            ไม่พบข้อมูลผู้ใช้ที่ค้นหา
          </div>
        </div>
      </div>
    
      <!-- Add User Modal (Dark Theme) -->
      <transition name="fade">
        <div class="modal-overlay" v-if="showAddModal" @click="closeAddModal">
          <div class="modal-content dark-card" @click.stop>
            <div class="modal-header">
              <h2>Add New User</h2>
              <button class="close-btn" @click="closeAddModal">&times;</button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Username <span class="required">*</span></label>
                <input type="text" v-model="formData.username" class="dark-input" placeholder="Enter username" />
              </div>
              <div class="form-group">
                <label>Email <span class="required">*</span></label>
                <input type="email" v-model="formData.email" class="dark-input" placeholder="Enter email" />
              </div>
              <div class="form-group">
                <label>Password <span class="required">*</span></label>
                <input type="password" v-model="formData.password" class="dark-input" placeholder="Enter password" />
              </div>
              
              <div class="form-row">
                <div class="form-group half">
                  <label>Role</label>
                  <select v-model="formData.previlage_id" class="dark-input">
                    <option v-for="role in roles" :key="role.previlage_id" :value="role.previlage_id">
                      {{ role.previlage_name }}
                    </option>
                  </select>
                </div>
                <div class="form-group half">
                  <label>Status</label>
                  <select v-model="formData.status_id" class="dark-input">
                    <option :value="1">Active</option>
                    <option :value="4">Pending Verification</option>
                    <option :value="3">Suspended</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Groups</label>
                <select multiple v-model="formData.groups" class="dark-input multi-select">
                  <option v-for="group in groups" :key="group.group_id" :value="group.group_id">
                    {{ group.group_name }}
                  </option>
                </select>
                <small class="help-text">Hold Cmd/Ctrl to select multiple</small>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="closeAddModal">Cancel</button>
              <button class="btn-save" @click="handleSaveUser" :disabled="isSubmitting">
                {{ isSubmitting ? 'Saving...' : 'Save User' }}
              </button>
            </div>
          </div>
        </div>
      </transition>

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
  align-items: flex-end;
  margin-bottom: 32px;
}

h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 4px;
}

.subtitle {
  color: #64748b;
  font-size: 1rem;
}

/* Search Box */
.search-container {
    position: relative;
    width: 350px;
}

.search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    color: #94a3b8;
}

.search-container input {
    width: 100%;
    padding: 12px 14px 12px 42px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    outline: none;
    transition: all 0.2s;
    font-size: 0.95rem;
}

.search-container input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

/* Alert Banner */
.alert-banner {
    padding: 14px 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    font-weight: 600;
    font-size: 0.95rem;
}

.alert-banner.success {
    background: #fdf2f8;
    color: #166534;
    border: 1px solid #fce7f3;
}

.alert-banner.error {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fee2e2;
}

/* Table Card */
.card {
  background: white;
  border-radius: 24px;
  overflow: hidden;
}

.shadow-premium {
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.05);
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 16px 24px;
  background: #f8fafc;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-bottom: 1px solid #f1f5f9;
}

.data-table td {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.data-table tr:hover td {
    background-color: #fbfcfe;
}

/* User Identity Cell */
.user-info {
    display: flex;
    align-items: center;
    gap: 16px;
}

.user-avatar {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
    color: white;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.2rem;
}

.username-text {
    font-weight: 700;
    color: #1e293b;
    font-size: 1rem;
}

.user-id-text {
    font-size: 0.75rem;
    color: #94a3b8;
}

/* Role Badge */
.role-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
}

.role-badge.rootadmin { background: #fee2e2; color: #991b1b; }
.role-badge.admin { background: #dbeafe; color: #1e40af; }
.role-badge.user { background: #f1f5f9; color: #475569; }

/* Select Dropdown */
/* Actions */
.actions-group {
    display: flex;
    align-items: center;
    gap: 12px;
}

.role-selector-box {
    flex: 1;
}

.delete-btn {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #fff;
    border: 1px solid #fee2e2;
    border-radius: 10px;
    color: #ef4444;
    cursor: pointer;
    transition: all 0.2s;
}

.delete-btn:hover {
    background: #fef2f2;
    border-color: #fca5a5;
    transform: scale(1.05);
}

.btn-icon {
    width: 18px;
    height: 18px;
}

.role-select {
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background-color: #fff;
    font-size: 0.85rem;
    color: #475569;
    cursor: pointer;
    outline: none;
    transition: all 0.2s;
}

.role-select:hover {
    border-color: #cbd5e1;
    background-color: #f8fafc;
}

.role-select:focus {
    border-color: #3b82f6;
}

/* Loading & Empty states */
.loading-state {
    padding: 80px;
    text-align: center;
    color: #64748b;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f1f5f9;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
}

.no-results {
    padding: 40px;
    text-align: center;
    color: #94a3b8;
    font-style: italic;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.fade-enter-active, .fade-leave-active {
    transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
    opacity: 0;
}

/* Modal Styles (Dark Game-like Theme) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-content.dark-card {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 20px;
  width: 500px;
  max-width: 90vw;
  color: #f8fafc;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255,255,255,0.05);
  overflow: hidden;
}

.modal-header {
  padding: 24px 30px;
  border-bottom: 1px solid #1e293b;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #0b1120;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #ef4444;
}

.modal-body {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-group.half {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #94a3b8;
}

.required {
  color: #ef4444;
}

.dark-input {
  width: 100%;
  padding: 12px 16px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  color: #f8fafc;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.dark-input:focus {
  border-color: #004f3b;
  box-shadow: 0 0 0 3px rgba(0, 79, 59, 0.2);
}

.multi-select {
  height: 120px;
  padding: 8px;
}

.multi-select option {
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 2px;
}

.multi-select option:checked {
  background: #004f3b linear-gradient(0deg, #004f3b 0%, #004f3b 100%);
  color: white;
}

.help-text {
  display: block;
  margin-top: 6px;
  font-size: 0.75rem;
  color: #64748b;
}

.modal-footer {
  padding: 20px 30px;
  background: #0b1120;
  border-top: 1px solid #1e293b;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  padding: 10px 20px;
  border-radius: 10px;
  background: transparent;
  color: #94a3b8;
  border: 1px solid #334155;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #1e293b;
  color: #f8fafc;
}

.btn-save {
  padding: 10px 24px;
  border-radius: 10px;
  background: #004f3b;
  color: white;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 79, 59, 0.3);
}

.btn-save:hover:not(:disabled) {
  background: #003d2d;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 79, 59, 0.4);
}

.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.actions {
  display: flex;
  align-items: center;
  margin-right: 16px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #004f3b;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 79, 59, 0.2);
}

.btn-primary:hover {
  background: #003d2d;
  transform: translateY(-1px);
}


/* Responsive Overrides for User Management */
.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}
.search-container {
  width: auto;
  min-width: 350px;
}
.mobile-cards-view {
  display: none;
}

@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    margin-top: 16px;
  }
  .search-container {
    min-width: 0;
    width: 100%;
  }
  .search-container input {
    width: 100%;
  }

  .desktop-table-view {
    display: none !important;
  }
  .mobile-cards-view {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .mobile-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
  .mc-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 12px;
    margin-bottom: 12px;
  }
  .mc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
  }
  .mc-label {
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 500;
  }
  .mc-value {
    font-size: 0.9rem;
    font-weight: 500;
    color: #334155;
  }
  .mobile-select select {
    padding: 4px 8px;
    font-size: 0.85rem;
  }
  .content {
    padding: 16px !important;
  }
}
</style>
