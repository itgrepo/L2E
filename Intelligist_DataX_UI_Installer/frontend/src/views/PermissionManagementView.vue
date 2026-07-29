<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import { postWithUser } from '../utils/api';

const roleList = ref([]);
const selectedRole = ref(null);
const menuPermissions = ref([]);
const isLoading = ref(true);
const isSaving = ref(false);
const saveStatus = ref('');
const newRoleName = ref('');
const isCreatingRole = ref(false);

const fetchInitialData = async () => {
  isLoading.value = true;
  try {
    const userStored = JSON.parse(localStorage.getItem('user') || '{}');
    
    // Fetch Roles
    const roleResponse = await postWithUser('/mgmt/getRoles', userStored);
    if (Array.isArray(roleResponse.data)) {
        roleList.value = roleResponse.data;
        if (roleList.value.length > 0) {
            selectedRole.value = roleList.value[0];
        }
    }

    // Fetch All Menu Permissions
    const menuResponse = await postWithUser('/mgmt/getMenu', userStored);
    if (menuResponse.data && menuResponse.data.data) {
        menuPermissions.value = menuResponse.data.data;
    }
  } catch (error) {
    console.error('Error fetching initial data:', error);
  } finally {
    isLoading.value = false;
  }
};

const currentPermissions = computed(() => {
  if (!selectedRole.value) return [];
  return menuPermissions.value.filter(p => p.previlage_id === selectedRole.value.previlage_id);
});

const togglePermission = async (perm) => {
  const newValue = perm.value === 'Yes' ? 'No' : 'Yes';
  const originalValue = perm.value;
  
  // Optimistic update
  perm.value = newValue;
  isSaving.value = true;
  saveStatus.value = `Saving ${perm.menu_name}...`;

  try {
    const userStored = JSON.parse(localStorage.getItem('user') || '{}');
    const response = await postWithUser('/mgmt/savePermission', userStored, {
      data: {
        ...perm,
        value: newValue
      }
    });
    
    if (response.data === 'success') {
      saveStatus.value = 'Settings saved';
      setTimeout(() => { if (saveStatus.value === 'Settings saved') saveStatus.value = ''; }, 2000);
    } else {
      perm.value = originalValue;
      alert('Failed to save: ' + (response.data.status || response.data));
    }
  } catch (error) {
    console.error('Error saving permission:', error);
    perm.value = originalValue;
    alert('Communication error with server');
  } finally {
    isSaving.value = false;
  }
};

const handleCreateRole = async () => {
  if (!newRoleName.value) return;
  isCreatingRole.value = true;
  try {
    const userStored = JSON.parse(localStorage.getItem('user') || '{}');
    const response = await postWithUser('/mgmt/addRole', userStored, {
      role_name: newRoleName.value
    });
    
    if (response.data.status === 'success') {
      newRoleName.value = '';
      // Refetch both to get new role and its initialized permissions
      await fetchInitialData(); 
      
      saveStatus.value = 'Role created successfully';
      setTimeout(() => { saveStatus.value = ''; }, 3000);
    } else {
      alert('Error creating role: ' + (response.data.message || response.data.status));
    }
  } catch (error) {
    console.error('Error creating role:', error);
  } finally {
    isCreatingRole.value = false;
  }
};

const selectRole = (role) => {
  selectedRole.value = role;
};

onMounted(() => {
  fetchInitialData();
});
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div class="header-main">
          <h1>Permission Management</h1>
          <p class="subtitle">ควบคุมสิทธิ์การใช้งานระดับสูงสำหรับแต่ละกลุ่มบทบาท (Roles)</p>
        </div>
        <div class="header-status" v-if="saveStatus">
            <span class="status-badge" :class="{ 'saving': isSaving }">
                <span v-if="isSaving" class="dot"></span>
                {{ saveStatus }}
            </span>
        </div>
      </header>

      <div class="permission-gateway" v-if="!isLoading">
        <!-- Sidebar: Roles -->
        <div class="role-sidebar glass-panel shadow-premium">
          <div class="sidebar-header">
            <h3>บทบาทผู้ใช้งาน (Roles)</h3>
          </div>
          <div class="role-list">
            <button 
              v-for="role in roleList" 
              :key="role.previlage_id"
              class="role-item"
              :class="{ 'active': selectedRole?.previlage_id === role.previlage_id }"
              @click="selectRole(role)"
            >
              <div class="role-icon-box">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div class="role-info">
                <span class="role-name">{{ role.previlage_name }}</span>
                <span class="role-id">ID: #{{ role.previlage_id }}</span>
              </div>
              <div class="active-indicator" v-if="selectedRole?.previlage_id === role.previlage_id"></div>
            </button>
          </div>

          <div class="create-role-box glass-panel">
            <input 
              type="text" 
              v-model="newRoleName" 
              placeholder="สร้างบทบาทใหม่..."
              @keyup.enter="handleCreateRole"
            >
            <button 
              class="add-role-btn" 
              @click="handleCreateRole" 
              :disabled="isCreatingRole || !newRoleName"
            >
              <span v-if="isCreatingRole">...</span>
              <span v-else>+ เพิ่ม</span>
            </button>
          </div>
        </div>

        <!-- Main: Permissions List -->
        <div class="permission-main">
          <div class="panel-header">
            <div class="role-detail">
              <h2 class="role-title">การตั้งค่าสิทธิ์สำหรับ: <span>{{ selectedRole?.previlage_name }}</span></h2>
              <p>เปิดหรือปิดความสามารถในการเข้าถึงฟีเจอร์ต่างๆ ภายในระบบ</p>
            </div>
          </div>

          <div class="settings-grid">
            <div 
              v-for="perm in currentPermissions" 
              :key="perm.menu_name_id"
              class="permission-card glass-panel"
              :class="{ 'enabled': perm.value === 'Yes' }"
            >
              <div class="card-content">
                <div class="feature-icon">
                  <svg v-if="perm.menu_name.includes('Catalog')" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                  <svg v-else-if="perm.menu_name.includes('Analytics')" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div class="feature-info">
                  <h4>{{ perm.menu_name }}</h4>
                  <p>อนุญาตให้บทบาทนี้เข้าถึงเมนูและทำงานที่เกี่ยวข้องได้</p>
                </div>
                <div class="feature-control">
                  <label class="switch">
                    <input type="checkbox" :checked="perm.value === 'Yes'" @change="togglePermission(perm)">
                    <span class="slider round"></span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="loading-state">
        <div class="spinner"></div>
        <p>กำลังเตรียมข้อมูลบทบาทและสิทธิ์การใช้งาน...</p>
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

/* Status Badge */
.status-badge {
    padding: 8px 16px;
    border-radius: 20px;
    background-color: var(--mso-pink-dark);
    color: #166534;
    font-size: 0.85rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
    border: 1px solid var(--mso-pink-dark);
    animation: fadeIn 0.3s ease;
}

.status-badge.saving {
    background-color: #eff6ff;
    color: #1e40af;
    border-color: #dbeafe;
}

.dot {
    width: 8px;
    height: 8px;
    background-color: #3b82f6;
    border-radius: 50%;
    animation: pulse 1s infinite;
}

/* Main Layout Grid */
.permission-gateway {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 32px;
  align-items: start;
}

/* Glass Panel Utility */
.glass-panel {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 24px;
}

.shadow-premium {
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.05);
}

/* Role Sidebar */
.role-sidebar {
  padding: 24px;
}

.sidebar-header h3 {
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 24px;
  padding-left: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.role-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.role-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  width: 100%;
}

.role-item:hover {
  transform: translateX(4px);
  border-color: #cbd5e1;
}

.role-item.active {
  background-color: #0f172a;
  border-color: #0f172a;
  color: white;
  box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.3);
}

.create-role-box {
  margin-top: 24px;
  padding: 12px;
  display: flex;
  gap: 8px;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
}

.create-role-box input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 8px;
  font-size: 0.9rem;
  outline: none;
  color: #1e293b;
}

.add-role-btn {
  background-color: #0f172a;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.add-role-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-role-btn:hover:not(:disabled) {
  background-color: #334155;
  transform: translateY(-1px);
}

.role-icon-box {
  width: 44px;
  height: 44px;
  background-color: #f1f5f9;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  transition: all 0.3s;
}

.role-item.active .role-icon-box {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.role-name {
  display: block;
  font-weight: 700;
  font-size: 1rem;
}

.role-id {
  display: block;
  font-size: 0.75rem;
  opacity: 0.6;
}

.active-indicator {
  position: absolute;
  right: 16px;
  width: 6px;
  height: 6px;
  background-color: #f472b6;
  border-radius: 50%;
  box-shadow: 0 0 10px #f472b6;
}

/* Permission Main Content */
.permission-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.panel-header {
  padding: 8px;
}

.role-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 4px;
}

.role-title span {
  color: #3b82f6;
}

.role-detail p {
  color: #94a3b8;
  font-size: 0.95rem;
}

/* Settings Grid */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.permission-card {
  padding: 24px;
  transition: all 0.3s;
}

.permission-card.enabled {
  background: white;
  border-color: var(--mso-pink-dark);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.feature-icon {
  width: 52px;
  height: 52px;
  background-color: #f8fafc;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  transition: all 0.3s;
}

.enabled .feature-icon {
  background-color: var(--mso-pink-dark);
  color: var(--mso-accent);
}

.feature-info {
  flex: 1;
}

.feature-info h4 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.feature-info p {
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.4;
}

/* Toggle Switch Styling */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 28px;
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
  background-color: #e2e8f0;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

input:checked + .slider {
  background-color: var(--mso-accent);
}

input:checked + .slider:before {
  transform: translateX(22px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f5f9;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes pulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.7; }
    100% { transform: scale(1); opacity: 1; }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
