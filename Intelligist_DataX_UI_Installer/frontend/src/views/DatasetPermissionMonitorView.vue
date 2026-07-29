<script setup>
import { ref, onMounted, computed } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { postWithUser, encodeUserData } from '../utils/api';

const activeTab = ref('users'); // 'users', 'groups', 'datasets'
const isLoading = ref(true);

// State
const users = ref([]);
const groups = ref([]);
const datasets = ref([]);

const selectedUser = ref(null);
const selectedGroup = ref(null);
const selectedDataset = ref(null);

// Specific relationship states
const userGroups = ref([]);
const userDatasets = ref([]);
const groupMembers = ref([]);
const groupDatasets = ref([]);
const datasetGroups = ref([]);
const datasetUsers = ref([]);

// Search queries
const userSearch = ref('');
const groupSearch = ref('');
const datasetSearch = ref('');

// Fetch Base Data
const fetchBaseData = async () => {
    isLoading.value = true;
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const tokenUser = encodeUserData(userStored);
        
        // Fetch Users (using existing logic from UserManagement)
        const userRes = await postWithUser('/mgmt/addUser', userStored);
        if (Array.isArray(userRes.data)) {
            users.value = userRes.data;
        }

        // Fetch Groups
        const groupRes = await apiClient.post('/getGroups', { user: tokenUser });
        if (groupRes.data?.status === 'success') {
            groups.value = groupRes.data.data;
        }

        // Fetch Datasets (Mocking datasets list or fetching from catalog if we can, but we'll extract from group dataset calls if needed. For now, fetch all catalogs)
        const catalogRes = await apiClient.post('/getCatalog', { user: tokenUser });
        if (catalogRes.data?.status === 'success') {
            datasets.value = catalogRes.data.data;
        }

    } catch (e) {
        console.error('Error fetching base data:', e);
    } finally {
        isLoading.value = false;
    }
};

const getUserParam = () => {
  const user = localStorage.getItem('user');
  if (user) {
    try {
      const parsedUser = JSON.parse(user);
      return parsedUser.token || user;
    } catch (e) {
      return user;
    }
  }
  return '';
};

// Selectors
const selectUser = async (userObj) => {
    selectedUser.value = userObj;
    userGroups.value = [];
    userDatasets.value = [];
    
    // Manual mapping since no direct /getUserDatasets API yet:
    // We will find which groups have this user, then which datasets those groups have.
    const userParam = getUserParam();
    
    let resolvedGroups = [];
    let resolvedDatasetsMap = new Map();

    for (const group of groups.value) {
        // Fetch members of this group
        try {
            const memberRes = await apiClient.post('/getGroupMembers', { user: userParam, group_id: group.group_id });
            if (memberRes.data?.status === 'success') {
                const isMember = memberRes.data.assigned.some(u => u.user_id === userObj.user_id);
                if (isMember) {
                    resolvedGroups.push(group);
                    // Fetch datasets for this group
                    const dRes = await apiClient.post('/getGroupDatasetAccess', { user: userParam, group_id: group.group_id });
                    if (dRes.data?.status === 'success') {
                        dRes.data.assigned.forEach(d => {
                            resolvedDatasetsMap.set(d.service_id, d);
                        });
                    }
                }
            }
        } catch (e) {}
    }

    userGroups.value = resolvedGroups;
    userDatasets.value = Array.from(resolvedDatasetsMap.values());
};

const selectGroup = async (groupObj) => {
    selectedGroup.value = groupObj;
    groupMembers.value = [];
    groupDatasets.value = [];
    
    const userParam = getUserParam();
    
    try {
        const memberRes = await apiClient.post('/getGroupMembers', { user: userParam, group_id: groupObj.group_id });
        if (memberRes.data?.status === 'success') {
            groupMembers.value = memberRes.data.assigned;
        }
        
        const dRes = await apiClient.post('/getGroupDatasetAccess', { user: userParam, group_id: groupObj.group_id });
        if (dRes.data?.status === 'success') {
            groupDatasets.value = dRes.data.assigned;
        }
    } catch (e) {}
};

const selectDataset = async (datasetObj) => {
    selectedDataset.value = datasetObj;
    datasetGroups.value = [];
    datasetUsers.value = [];
    
    const userParam = getUserParam();
    let resolvedGroups = [];
    let resolvedUsersMap = new Map();

    for (const group of groups.value) {
        try {
            const dRes = await apiClient.post('/getGroupDatasetAccess', { user: userParam, group_id: group.group_id });
            if (dRes.data?.status === 'success') {
                const hasAccess = dRes.data.assigned.some(d => String(d.service_id) === String(datasetObj.service_id));
                if (hasAccess) {
                    resolvedGroups.push(group);
                    
                    // Fetch users in this group
                    const memberRes = await apiClient.post('/getGroupMembers', { user: userParam, group_id: group.group_id });
                    if (memberRes.data?.status === 'success') {
                        memberRes.data.assigned.forEach(u => {
                            resolvedUsersMap.set(u.user_id, u);
                        });
                    }
                }
            }
        } catch (e) {}
    }
    
    datasetGroups.value = resolvedGroups;
    datasetUsers.value = Array.from(resolvedUsersMap.values());
};

// Filters
const filteredUsers = computed(() => {
    if (!userSearch.value) return users.value;
    const q = userSearch.value.toLowerCase();
    return users.value.filter(u => u.username?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q));
});

const filteredGroups = computed(() => {
    if (!groupSearch.value) return groups.value;
    const q = groupSearch.value.toLowerCase();
    return groups.value.filter(g => g.group_name?.toLowerCase().includes(q));
});

const filteredDatasets = computed(() => {
    if (!datasetSearch.value) return datasets.value;
    const q = datasetSearch.value.toLowerCase();
    return datasets.value.filter(d => d.service_name?.toLowerCase().includes(q));
});

onMounted(() => {
    fetchBaseData();
});
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div class="header-main">
          <h1>Permission Monitor</h1>
          <p class="subtitle">ตรวจสอบความสัมพันธ์และการเข้าถึงข้อมูล (Users ↔ Groups ↔ Datasets)</p>
        </div>
      </header>

      <!-- Segmented Tabs -->
      <div class="tabs-container">
          <div class="tab-slider" :class="activeTab"></div>
          <button class="tab-btn" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">
              <span class="icon">👤</span> หมวดผู้ใช้งาน
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'groups' }" @click="activeTab = 'groups'">
              <span class="icon">👥</span> หมวดกลุ่มผู้ใช้งาน
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'datasets' }" @click="activeTab = 'datasets'">
              <span class="icon">📊</span> หมวดชุดข้อมูล
          </button>
      </div>

      <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>กำลังรวบรวมข้อมูลสิทธิ์...</p>
      </div>

      <!-- Tab: Users -->
      <div v-if="!isLoading && activeTab === 'users'" class="monitor-grid">
          <!-- Selection Panel -->
          <div class="panel list-panel">
              <div class="panel-header">
                  <h3>เลือกผู้ใช้งาน</h3>
                  <input type="text" v-model="userSearch" placeholder="ค้นหาชื่อผู้ใช้..." class="search-input">
              </div>
              <div class="item-list">
                  <div v-for="u in filteredUsers" :key="u.user_id" 
                       class="list-item" :class="{ active: selectedUser?.user_id === u.user_id }"
                       @click="selectUser(u)">
                      <div class="item-avatar">{{ u.username.charAt(0).toUpperCase() }}</div>
                      <div class="item-info">
                          <strong>{{ u.username }}</strong>
                          <small>{{ u.email || 'No email' }}</small>
                      </div>
                  </div>
              </div>
          </div>

          <!-- Flow / Relationship Visualization -->
          <div class="panel flow-panel" v-if="selectedUser">
              <div class="flow-header">
                  <h2>การเข้าถึงข้อมูลของ <span>@{{ selectedUser.username }}</span></h2>
              </div>
              
              <div class="flow-container">
                  <!-- User Node -->
                  <div class="node user-node">
                      <div class="node-icon">👤</div>
                      <div>{{ selectedUser.username }}</div>
                  </div>
                  
                  <div class="flow-path"></div>

                  <!-- Group Nodes -->
                  <div class="node-column">
                      <h4 class="col-title">สังกัดกลุ่ม ({{ userGroups.length }})</h4>
                      <div v-if="userGroups.length === 0" class="empty-text">ไม่มีกลุ่ม</div>
                      <div v-for="g in userGroups" :key="g.group_id" class="sub-node group-node">
                          {{ g.group_name }}
                      </div>
                  </div>
                  
                  <div class="flow-path"></div>

                  <!-- Dataset Nodes -->
                  <div class="node-column">
                      <h4 class="col-title">ชุดข้อมูลที่เข้าถึงได้ ({{ userDatasets.length }})</h4>
                      <div v-if="userDatasets.length === 0" class="empty-text">ไม่มีข้อมูล</div>
                      <div v-for="d in userDatasets" :key="d.service_id" class="sub-node dataset-node">
                          {{ d.service_name }}
                      </div>
                  </div>
              </div>
          </div>
          <div class="panel empty-panel" v-else>
              <div class="empty-icon">👈</div>
              <h3>กรุณาเลือกผู้ใช้งานจากเมนูด้านซ้าย</h3>
          </div>
      </div>

      <!-- Tab: Groups -->
      <div v-if="!isLoading && activeTab === 'groups'" class="monitor-grid">
          <div class="panel list-panel">
              <div class="panel-header">
                  <h3>เลือกกลุ่มผู้ใช้งาน</h3>
                  <input type="text" v-model="groupSearch" placeholder="ค้นหาชื่อกลุ่ม..." class="search-input">
              </div>
              <div class="item-list">
                  <div v-for="g in filteredGroups" :key="g.group_id" 
                       class="list-item group-style" :class="{ active: selectedGroup?.group_id === g.group_id }"
                       @click="selectGroup(g)">
                      <div class="item-icon">👥</div>
                      <div class="item-info">
                          <strong>{{ g.group_name }}</strong>
                      </div>
                  </div>
              </div>
          </div>

          <div class="panel flow-panel dual-flow" v-if="selectedGroup">
              <div class="flow-header">
                  <h2>การเชื่อมโยงของกลุ่ม <span>{{ selectedGroup.group_name }}</span></h2>
              </div>
              
              <div class="flow-container bidirectional">
                  <!-- Users Column -->
                  <div class="node-column">
                      <h4 class="col-title">สมาชิก ({{ groupMembers.length }})</h4>
                      <div class="card-grid">
                          <div v-for="m in groupMembers" :key="m.user_id" class="sub-node user-node-small">
                              <span class="icon">👤</span> {{ m.username }}
                          </div>
                      </div>
                  </div>
                  
                  <!-- Center Node -->
                  <div class="center-connector">
                      <div class="node group-node">
                          <div class="node-icon">👥</div>
                          <div>{{ selectedGroup.group_name }}</div>
                      </div>
                  </div>

                  <!-- Datasets Column -->
                  <div class="node-column">
                      <h4 class="col-title">สิทธิ์เข้าถึง ({{ groupDatasets.length }})</h4>
                      <div class="card-grid">
                          <div v-for="d in groupDatasets" :key="d.service_id" class="sub-node dataset-node-small">
                              <span class="icon">📊</span> {{ d.service_name }}
                          </div>
                      </div>
                  </div>
              </div>
          </div>
          <div class="panel empty-panel" v-else>
              <div class="empty-icon">👈</div>
              <h3>กรุณาเลือกกลุ่มผู้ใช้งานจากเมนูด้านซ้าย</h3>
          </div>
      </div>

      <!-- Tab: Datasets -->
      <div v-if="!isLoading && activeTab === 'datasets'" class="monitor-grid reverse-flow">
          <div class="panel list-panel">
              <div class="panel-header">
                  <h3>เลือกชุดข้อมูล</h3>
                  <input type="text" v-model="datasetSearch" placeholder="ค้นหาชุดข้อมูล..." class="search-input">
              </div>
              <div class="item-list">
                  <div v-for="d in filteredDatasets" :key="d.service_id" 
                       class="list-item dataset-style" :class="{ active: selectedDataset?.service_id === d.service_id }"
                       @click="selectDataset(d)">
                      <div class="item-icon">📊</div>
                      <div class="item-info">
                          <strong>{{ d.service_name }}</strong>
                      </div>
                  </div>
              </div>
          </div>

          <div class="panel flow-panel" v-if="selectedDataset">
              <div class="flow-header">
                  <h2>ผู้เข้าถึงชุดข้อมูล <span>{{ selectedDataset.service_name }}</span></h2>
              </div>
              
              <div class="flow-container right-to-left">
                  <!-- Users -->
                  <div class="node-column end-col">
                      <h4 class="col-title">ผู้สืบทอดสิทธิ์ ({{ datasetUsers.length }})</h4>
                      <div v-for="u in datasetUsers" :key="u.user_id" class="sub-node user-node">
                          {{ u.username }}
                      </div>
                  </div>
                  
                  <div class="flow-path"></div>

                  <!-- Groups -->
                  <div class="node-column">
                      <h4 class="col-title">กลุ่มที่ได้รับอนุญาต ({{ datasetGroups.length }})</h4>
                      <div v-if="datasetGroups.length === 0" class="empty-text">ไม่มีกลุ่ม</div>
                      <div v-for="g in datasetGroups" :key="g.group_id" class="sub-node group-node">
                          {{ g.group_name }}
                      </div>
                  </div>
                  
                  <div class="flow-path"></div>

                  <!-- Dataset Node -->
                  <div class="node dataset-node-large">
                      <div class="node-icon">📊</div>
                      <div>{{ selectedDataset.service_name }}</div>
                  </div>
              </div>
          </div>
          <div class="panel empty-panel" v-else>
              <div class="empty-icon">👈</div>
              <h3>กรุณาเลือกชุดข้อมูลจากเมนูด้านซ้าย</h3>
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
  margin-bottom: 32px;
}

h1 {
  font-size: 2.25rem;
  font-weight: 800;
  color: #0f172a;
  background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.subtitle {
  color: #64748b;
  font-size: 1.05rem;
}

/* Tabs */
.tabs-container {
    display: flex;
    position: relative;
    background: #e2e8f0;
    padding: 6px;
    border-radius: 16px;
    width: fit-content;
    margin-bottom: 32px;
}

.tab-slider {
    position: absolute;
    top: 6px;
    bottom: 6px;
    width: calc(33.333% - 4px);
    background: white;
    border-radius: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.tab-slider.users { left: 6px; }
.tab-slider.groups { left: calc(33.333% + 2px); }
.tab-slider.datasets { left: calc(66.666% - 2px); }

.tab-btn {
    position: relative;
    z-index: 10;
    background: none;
    border: none;
    padding: 12px 24px;
    font-size: 0.95rem;
    font-weight: 700;
    color: #64748b;
    cursor: pointer;
    transition: color 0.3s;
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 180px;
    justify-content: center;
}

.tab-btn.active {
    color: #0f172a;
}

/* Grid Layout */
.monitor-grid {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 24px;
    height: 600px;
}

.panel {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 24px;
    box-shadow: 0 10px 30px -5px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* List Panel */
.list-panel .panel-header {
    padding: 20px;
    border-bottom: 1px solid #f1f5f9;
    background: white;
}

.list-panel h3 {
    margin: 0 0 16px 0;
    color: #1e293b;
}

.search-input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background: #f8fafc;
    outline: none;
    transition: all 0.2s;
}

.search-input:focus {
    border-color: #3b82f6;
    background: white;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.item-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.list-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 16px;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s;
}

.list-item:hover {
    background: #f1f5f9;
}

.list-item.active {
    background: white;
    border-color: #e2e8f0;
    box-shadow: 0 4px 10px rgba(0,0,0,0.02);
}

/* User Selection Theme */
.list-item.active { border-left: 4px solid #3b82f6; }
.group-style.active { border-left: 4px solid var(--primary); }
.dataset-style.active { border-left: 4px solid #8b5cf6; }

.item-avatar {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    font-weight: 800;
}

.item-icon {
    width: 40px;
    height: 40px;
    background: #f1f5f9;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    font-size: 1.2rem;
}

.item-info strong {
    display: block;
    color: #1e293b;
    font-size: 0.95rem;
}

.item-info small {
    display: block;
    color: #94a3b8;
    font-size: 0.8rem;
}

/* Flow Panel */
.flow-panel {
    padding: 0;
}

.flow-header {
    padding: 24px 32px;
    border-bottom: 1px solid #f1f5f9;
    background: white;
}

.flow-header h2 {
    margin: 0;
    font-size: 1.4rem;
    color: #1e293b;
}

.flow-header h2 span {
    color: #3b82f6;
}

.flow-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 40px;
    overflow-x: auto;
    background: #fafaf9;
}

.node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 20px 32px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 20px -5px rgba(0,0,0,0.1);
    font-weight: 800;
    color: #1e293b;
    z-index: 2;
}

.node-icon {
    font-size: 2.5rem;
}

.node-column {
    display: flex;
    flex-direction: column;
    gap: 12px;
    flex: 1;
    min-width: 220px;
    max-height: 400px;
    overflow-y: auto;
    padding: 10px;
}

.col-title {
    text-align: center;
    margin: 0 0 10px 0;
    color: #64748b;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.sub-node {
    padding: 14px 20px;
    background: white;
    border-radius: 14px;
    font-weight: 600;
    color: #334155;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    border: 1px solid #f1f5f9;
    transition: all 0.3s;
    text-align: center;
}

.sub-node:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
}

.group-node { border-left: 4px solid var(--primary); }
.dataset-node { border-left: 4px solid #8b5cf6; }
.user-node { border-left: 4px solid #3b82f6; }

.flow-path {
    height: 2px;
    background: #cbd5e1;
    flex: 0.5;
    min-width: 40px;
    position: relative;
    border-style: dashed;
    border-width: 2px;
    border-color: #cbd5e1;
    background: transparent;
}

.flow-path::after {
    content: '▶';
    position: absolute;
    right: -10px;
    top: -9px;
    color: #94a3b8;
}

/* Dual Flow (Bidirectional) */
.bidirectional {
    justify-content: center;
    gap: 40px;
}
.center-connector {
    position: relative;
    z-index: 5;
}
.center-connector::before, .center-connector::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 40px;
    height: 2px;
    border-top: 2px dashed #cbd5e1;
}
.center-connector::before { right: 100%; }
.center-connector::after { left: 100%; }

.card-grid {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.user-node-small { border-right: 4px solid #3b82f6; border-left: none; text-align: right; }
.dataset-node-small { border-left: 4px solid #8b5cf6; text-align: left; }

.right-to-left {
    flex-direction: row;
}
.end-col { order: -1; }

.dataset-node-large { border-left: 8px solid #8b5cf6; }

/* Empty States */
.empty-panel {
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    background: #f8fafc;
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 16px;
    opacity: 0.5;
}

.empty-text {
    text-align: center;
    color: #94a3b8;
    font-style: italic;
    padding: 20px;
    background: #f1f5f9;
    border-radius: 12px;
}

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: 16px;
    color: #64748b;
    font-weight: 600;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e2e8f0;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>
