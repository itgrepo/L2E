<script setup>
import { ref, onMounted, computed } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import { postWithUser } from '../utils/api';

const users = ref([]);
const roles = ref([]);
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
        <div class="search-container">
            <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input type="text" v-model="searchQuery" placeholder="ค้นหาด้วย Username หรือ Email...">
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
          <table class="data-table">
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
</style>
