<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { postWithUser } from '../utils/api';

const router = useRouter();
const datasets = ref([]);
const isLoading = ref(true);
const searchQuery = ref('');
const filterCategory = ref('');
const filterStatus = ref('');
const alertMessage = ref({ text: '', type: '' });

const stats = ref({
    total: 0,
    active: 0,
    inactive: 0,
    highValue: 0
});

// Access Modal State
const isAccessModalOpen = ref(false);
const accessMode = ref('select'); // 'select', 'group', 'user'
const currentDataset = ref(null);
const assignedItems = ref([]);
const availableItems = ref([]);
const isProcessingAccess = ref(false);
const modalSearchQuery = ref('');

const fetchDatasets = async () => {
    isLoading.value = true;
    try {
        const userData = localStorage.getItem('user');
        const response = await apiClient.post('/getService', {
            user: btoa(userData)
        });
        
        if (response.data.status === 'success') {
            datasets.value = response.data.data;
            updateStats();
        }
    } catch (error) {
        console.error('Error fetching datasets:', error);
        showAlert('ไม่สามารถโหลดข้อมูลชุดข้อมูลได้', 'error');
    } finally {
        isLoading.value = false;
    }
};

const updateStats = () => {
    stats.value = {
        total: datasets.value.length,
        active: datasets.value.filter(d => d.status === 'Active').length,
        inactive: datasets.value.filter(d => d.status !== 'Active').length,
        highValue: datasets.value.filter(d => d.is_high_value === 'ใช่').length
    };
};

const filteredDatasets = computed(() => {
    let result = datasets.value;
    
    if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase();
        result = result.filter(d => 
            (d.service_name && d.service_name.toLowerCase().includes(q)) || 
            (d.dataset_id && d.dataset_id.toLowerCase().includes(q))
        );
    }
    
    if (filterCategory.value) {
        result = result.filter(d => d.category === filterCategory.value);
    }
    
    if (filterStatus.value) {
        result = result.filter(d => d.status === filterStatus.value);
    }
    
    return result;
});

const categories = computed(() => {
    const cats = datasets.value.map(d => d.category).filter(Boolean);
    return [...new Set(cats)];
});

const handleToggleStatus = async (dataset) => {
    const newStatus = dataset.status === 'Active' ? 'Inactive' : 'Active';
    try {
        const userData = localStorage.getItem('user');
        const fd = new FormData();
        fd.append('user', btoa(userData));
        fd.append('service_id', dataset.service_id);
        fd.append('service_status', newStatus);
        
        const response = await apiClient.put('/addService', fd, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        if (response.data.status && response.data.status.includes('success')) {
            showAlert(`อัปเดตสถานะของ ${dataset.service_name} สำเร็จ`, 'success');
            fetchDatasets();
        } else {
            showAlert('เกิดข้อผิดพลาดในการอัปเดตสถานะ', 'error');
        }
    } catch (error) {
        console.error('Error toggling status:', error);
        showAlert('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');
    }
};

const handleDelete = async (dataset) => {
    if (!confirm(`คุณแน่ใจหรือไม่ว่าต้องการลบชุดข้อมูล "${dataset.service_name}"?`)) return;
    
    try {
        const userData = localStorage.getItem('user');
        const fd = new FormData();
        fd.append('user', btoa(userData));
        fd.append('service_id', dataset.service_id);
        fd.append('service_status', 'Deleted'); // Soft delete pattern
        
        const response = await apiClient.put('/addService', fd, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        if (response.data.status && response.data.status.includes('success')) {
            showAlert(`ลบชุดข้อมูลสำเร็จ`, 'success');
            fetchDatasets();
        }
    } catch (error) {
        console.error('Delete error:', error);
        showAlert('เกิดข้อผิดพลาดในการลบ', 'error');
    }
};

const goToEdit = (dataset) => {
    router.push({ 
        path: '/dataset-config', 
        query: { edit: dataset.service_id } 
    });
};

const showAlert = (text, type) => {
    alertMessage.value = { text, type };
    setTimeout(() => { alertMessage.value = { text: '', type: '' }; }, 3000);
};

// Access Management Methods
const openAccessModal = (dataset) => {
    currentDataset.value = dataset;
    accessMode.value = 'select';
    isAccessModalOpen.value = true;
};

const closeAccessModal = () => {
    isAccessModalOpen.value = false;
    currentDataset.value = null;
    modalSearchQuery.value = '';
};

const fetchAccessData = async (mode) => {
    accessMode.value = mode;
    isProcessingAccess.value = true;
    try {
        const userData = localStorage.getItem('user');
        const endpoint = mode === 'group' ? '/getDatasetAccessGroups' : '/getDatasetAccessUsers';
        const response = await apiClient.post(endpoint, {
            user: btoa(userData),
            service_id: currentDataset.value.service_id
        });
        
        if (response.data.status === 'success') {
            assignedItems.value = response.data.assigned;
            availableItems.value = response.data.available;
        }
    } catch (error) {
        console.error(`Error fetching ${mode} access:`, error);
        showAlert('ไม่สามารถโหลดข้อมูลสิทธิ์ได้', 'error');
    } finally {
        isProcessingAccess.value = false;
    }
};

const handleAssign = (item) => {
    availableItems.value = availableItems.value.filter(i => (i.group_id || i.user_id) !== (item.group_id || item.user_id));
    assignedItems.value.push(item);
};

const handleUnassign = (item) => {
    assignedItems.value = assignedItems.value.filter(i => (i.group_id || i.user_id) !== (item.group_id || item.user_id));
    availableItems.value.push(item);
};

const saveAccessChanges = async () => {
    isProcessingAccess.value = true;
    try {
        const userData = localStorage.getItem('user');
        const endpoint = accessMode.value === 'group' ? '/updateDatasetAccessGroups' : '/updateDatasetAccessUsers';
        const payload = {
            user: btoa(userData),
            service_id: currentDataset.value.service_id
        };
        
        if (accessMode.value === 'group') {
            payload.group_ids = assignedItems.value.map(i => i.group_id);
        } else {
            payload.user_ids = assignedItems.value.map(i => i.user_id);
        }
        
        const response = await apiClient.post(endpoint, payload);
        if (response.data.status === 'success') {
            showAlert('อัปเดตสิทธิ์การเข้าถึงสำเร็จ', 'success');
            closeAccessModal();
        }
    } catch (error) {
        console.error('Error saving access:', error);
        showAlert('เกิดข้อผิดพลาดในการบันทึกสิทธิ์', 'error');
    } finally {
        isProcessingAccess.value = false;
    }
};

const filteredAssigned = computed(() => {
    if (!modalSearchQuery.value) return assignedItems.value;
    const q = modalSearchQuery.value.toLowerCase();
    return assignedItems.value.filter(i => 
        (i.group_name && i.group_name.toLowerCase().includes(q)) ||
        (i.firstname && i.firstname.toLowerCase().includes(q)) ||
        (i.username && i.username.toLowerCase().includes(q))
    );
});

const filteredAvailable = computed(() => {
    if (!modalSearchQuery.value) return availableItems.value;
    const q = modalSearchQuery.value.toLowerCase();
    return availableItems.value.filter(i => 
        (i.group_name && i.group_name.toLowerCase().includes(q)) ||
        (i.firstname && i.firstname.toLowerCase().includes(q)) ||
        (i.username && i.username.toLowerCase().includes(q))
    );
});

onMounted(() => {
    fetchDatasets();
});
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div class="header-left">
          <h1>Dataset Management</h1>
          <p class="subtitle">บริหารจัดการรหัสชุดข้อมูลและทรัพยากรในระบบ</p>
        </div>
        <div class="header-actions">
          <router-link to="/dataset-config" class="btn-primary">
            <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            เพิ่มชุดข้อมูลใหม่
          </router-link>
        </div>
      </header>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon total">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">Total Datasets</p>
            <h3 class="stat-value">{{ stats.total }}</h3>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon active">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">Active</p>
            <h3 class="stat-value text-green">{{ stats.active }}</h3>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon inactive">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
            </svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">Inactive</p>
            <h3 class="stat-value text-slate">{{ stats.inactive }}</h3>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon high-value">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
          <div class="stat-info">
            <p class="stat-label">High Value</p>
            <h3 class="stat-value text-amber">{{ stats.highValue }}</h3>
          </div>
        </div>
      </div>

      <!-- Filters & Search -->
      <div class="filter-bar card shadow-sm">
        <div class="search-box">
          <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input type="text" v-model="searchQuery" placeholder="ค้นหาชื่อชุดข้อมูล หรือ ID...">
        </div>
        <div class="filter-group">
          <select v-model="filterCategory" class="filter-select">
            <option value="">ทุกหมวดหมู่</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <select v-model="filterStatus" class="filter-select">
            <option value="">ทุกสถานะ</option>
            <option value="Active">เปิดใช้งาน (Active)</option>
            <option value="Inactive">ปิดใช้งาน (Inactive)</option>
          </select>
        </div>
      </div>

      <!-- Alert -->
      <transition name="fade">
        <div v-if="alertMessage.text" :class="['alert-banner', alertMessage.type]">
          {{ alertMessage.text }}
        </div>
      </transition>

      <!-- Table Section -->
      <div class="card shadow-premium">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>กำลังโหลดข้อมูลชุดข้อมูล...</p>
        </div>
        
        <div v-else class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Dataset ID</th>
                <th>ชุดข้อมูล</th>
                <th>หมวดหมู่ / หน่วยงาน</th>
                <th>สถานะ</th>
                <th>ประเภทข้อมูล</th>
                <th>ดำเนินการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in filteredDatasets" :key="d.service_id">
                <td class="id-cell">{{ d.dataset_id || '-' }}</td>
                <td>
                  <div class="dataset-cell">
                    <div class="dataset-name">{{ d.service_name }}</div>
                    <div class="dataset-tags" v-if="d.is_high_value === 'ใช่'">
                      <span class="tag-high-value">High Value</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="meta-cell">
                    <span class="category-text">{{ d.category || 'ไม่ระบุ' }}</span>
                    <span class="org-text">{{ d.organization || '-' }}</span>
                  </div>
                </td>
                <td>
                  <span class="status-badge" :class="d.status?.toLowerCase()">
                    {{ d.status }}
                  </span>
                </td>
                <td>
                  <span class="type-badge">{{ d.dataset_type || 'record' }}</span>
                </td>
                <td>
                  <div class="actions">
                    <button class="action-btn access" @click="openAccessModal(d)" title="จัดการสิทธิ์">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                    </button>
                    <button class="action-btn edit" @click="goToEdit(d)" title="แก้ไข">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button class="action-btn toggle" @click="handleToggleStatus(d)" :title="d.status === 'Active' ? 'ปิดใช้งาน' : 'เปิดใช้งาน'">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                      </svg>
                    </button>
                    <button class="action-btn delete" @click="handleDelete(d)" title="ลบ">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredDatasets.length === 0">
                <td colspan="6" class="no-data">ไม่พบข้อมูลชุดข้อมูลที่ค้นหา</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- Access Management Modal -->
    <Teleport to="body">
      <transition name="fade">
        <div v-if="isAccessModalOpen" class="modal-overlay" @click.self="closeAccessModal">
          <div class="modal-container">
            <header class="modal-header">
              <div class="modal-title-group">
                <span class="modal-icon-badge">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </span>
                <div>
                  <h2>จัดการสิทธิ์การเข้าถึง</h2>
                  <p class="modal-subtitle">{{ currentDataset?.service_name }} ({{ currentDataset?.dataset_id }})</p>
                </div>
              </div>
              <button class="btn-close" @click="closeAccessModal">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </header>

            <div class="modal-body scrollbar-custom">
              <!-- Mode Selection -->
              <div v-if="accessMode === 'select'" class="selection-grid transition-fade">
                <button class="selection-card group" @click="fetchAccessData('group')">
                  <div class="selection-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <div class="selection-info">
                    <h3>BY GROUP</h3>
                    <p>จัดการสิทธิ์ให้กลุ่มผู้ใช้งาน</p>
                  </div>
                </button>
                
                <button class="selection-card user" @click="fetchAccessData('user')">
                  <div class="selection-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div class="selection-info">
                    <h3>BY USER</h3>
                    <p>จัดการสิทธิ์รายบุคคล</p>
                  </div>
                </button>
              </div>

              <!-- Dual List Interface -->
              <div v-else class="dual-list-container transition-fade">
                <div class="dual-header">
                  <button class="btn-back" @click="accessMode = 'select'">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    ย้อนกลับ
                  </button>
                  <div class="modal-search">
                    <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <input type="text" v-model="modalSearchQuery" placeholder="ค้นหาข้อมูลในรายการ...">
                  </div>
                </div>

                <div class="lists-wrapper">
                  <!-- Assigned Column -->
                  <div class="list-column assigned">
                    <div class="column-title">
                      <span class="dot red"></span>
                      {{ accessMode === 'group' ? 'กลุ่มที่ได้รับสิทธิ์' : 'ผู้ใช้ที่ได้รับสิทธิ์' }}
                      <span class="count-badge">{{ assignedItems.length }}</span>
                    </div>
                    <div class="list-items scrollbar-custom">
                      <div v-for="item in filteredAssigned" :key="item.group_id || item.user_id" class="list-item">
                        <div class="item-info">
                          <span class="item-name">{{ item.group_name || `${item.firstname} ${item.lastname}` }}</span>
                          <span class="item-sub">{{ item.username || item.group_id }}</span>
                        </div>
                        <button class="item-action remove" @click="handleUnassign(item)">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </button>
                      </div>
                      <div v-if="filteredAssigned.length === 0" class="empty-list">ไม่มีรายการที่ถูกเลือก</div>
                    </div>
                  </div>

                  <!-- Available Column -->
                  <div class="list-column available">
                    <div class="column-title">
                      <span class="dot green"></span>
                      เพิ่มรายการ
                      <span class="count-badge gray">{{ availableItems.length }}</span>
                    </div>
                    <div class="list-items scrollbar-custom">
                      <div v-for="item in filteredAvailable" :key="item.group_id || item.user_id" class="list-item">
                        <div class="item-info">
                          <span class="item-name">{{ item.group_name || `${item.firstname} ${item.lastname}` }}</span>
                          <span class="item-sub">{{ item.username || item.group_id }}</span>
                        </div>
                        <button class="item-action add" @click="handleAssign(item)">
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </button>
                      </div>
                      <div v-if="filteredAvailable.length === 0" class="empty-list">ไม่พบรายการให้เลือกเพิ่ม</div>
                    </div>
                  </div>
                </div>

                <div class="modal-footer">
                  <button class="btn-outline" @click="closeAccessModal">ยกเลิก</button>
                  <button class="btn-primary" @click="saveAccessChanges" :disabled="isProcessingAccess">
                    <span v-if="isProcessingAccess" class="spinner-small"></span>
                    บันทึกข้อมูล
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
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
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

h1 {
  font-size: 1.875rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 4px;
}

.subtitle {
  color: #64748b;
  font-size: 0.9375rem;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: #0f172a;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
  cursor: pointer;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1e293b;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-icon {
  width: 20px;
  height: 20px;
}

/* Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.stat-icon svg { width: 24px; height: 24px; }

.stat-icon.total { background: #f1f5f9; color: #475569; }
.stat-icon.active { background: #fdf2f8; color: var(--primary); }
.stat-icon.inactive { background: #f8fafc; color: #94a3b8; }
.stat-icon.high-value { background: #fffbeb; color: #d97706; }

.stat-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
}

.text-green { color: var(--primary); }
.text-slate { color: #64748b; }
.text-amber { color: #d97706; }

/* Filter Bar */
.filter-bar {
  background: white;
  padding: 20px 24px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 20px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #94a3b8;
}

.search-box input {
  width: 100%;
  padding: 10px 14px 10px 42px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  outline: none;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.search-box input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.05);
}

.filter-group {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 10px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  font-size: 0.875rem;
  color: #475569;
  outline: none;
  background: #f8fafc;
  cursor: pointer;
}

/* Alerts */
.alert-banner {
  padding: 12px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  font-weight: 600;
  font-size: 0.875rem;
}

.alert-banner.success { background: #fdf2f8; color: #166534; border: 1px solid #fce7f3; }
.alert-banner.error { background: #fef2f2; color: #991b1b; border: 1px solid #fee2e2; }

/* Table Section */
.card { background: white; border-radius: 20px; overflow: hidden; }
.shadow-premium { box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04); }

.table-container { overflow-x: auto; }

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
  letter-spacing: 0.05em;
  border-bottom: 1.5px solid #f1f5f9;
}

.data-table td {
  padding: 20px 24px;
  border-bottom: 1px solid #f8fafc;
  vertical-align: middle;
}

.data-table tr:hover td { background-color: #fbfcfe; }

.id-cell { font-family: monospace; color: #64748b; font-size: 0.8125rem; }

.dataset-cell { display: flex; flex-direction: column; gap: 4px; }
.dataset-name { font-weight: 700; color: #1e293b; font-size: 0.9375rem; }

.tag-high-value {
  display: inline-block;
  padding: 2px 8px;
  background: #fffbeb;
  color: #d97706;
  font-size: 0.6875rem;
  font-weight: 700;
  border-radius: 4px;
  text-transform: uppercase;
}

.meta-cell { display: flex; flex-direction: column; }
.category-text { font-size: 0.875rem; font-weight: 600; color: #475569; }
.org-text { font-size: 0.75rem; color: #94a3b8; }

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: capitalize;
}

.status-badge.active { background: #fdf2f8; color: var(--primary); }
.status-badge.inactive { background: #f1f5f9; color: #64748b; }
.status-badge.deleted { background: #fef2f2; color: #ef4444; }

.type-badge {
  font-size: 0.75rem;
  color: #6366f1;
  background: #eef2ff;
  padding: 2px 10px;
  border-radius: 6px;
  font-weight: 600;
}

.actions { display: flex; gap: 8px; }

.action-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1.5px solid #e2e8f0;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: #64748b;
  padding: 6px;
}

.action-btn svg { width: 18px; height: 18px; }

.action-btn.edit:hover { border-color: #3b82f6; color: #3b82f6; background: #eff6ff; }
.action-btn.toggle:hover { border-color: #db2777; color: #db2777; background: #fdf2f8; }
.action-btn.delete:hover { border-color: #ef4444; color: #ef4444; background: #fef2f2; }
.action-btn.access:hover { border-color: #6366f1; color: #6366f1; background: #eef2ff; }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  width: 100%;
  max-width: 900px;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-header {
  padding: 24px 32px;
  background: #0f172a;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-icon-badge {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}

.modal-icon-badge svg { width: 24px; height: 24px; }

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.modal-subtitle {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.modal-body {
  padding: 32px;
  flex: 1;
  overflow-y: auto;
  background: #f8fafc;
}

/* Selection Cards */
.selection-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  height: 100%;
  padding: 40px 0;
}

.selection-card {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 20px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.selection-card:hover {
  border-color: #3b82f6;
  transform: translateY(-4px);
  box-shadow: 0 12px 20px -5px rgba(59, 130, 246, 0.1);
}

.selection-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px;
}

.selection-card.group .selection-icon { background: #eff6ff; color: #1d4ed8; }
.selection-card.user .selection-icon { background: #fdf2f8; color: #166534; }

.selection-info { text-align: center; }
.selection-info h3 { font-weight: 800; color: #1e293b; margin-bottom: 4px; }
.selection-info p { font-size: 0.875rem; color: #64748b; }

/* Dual List Layout */
.dual-list-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.dual-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: #64748b;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-back:hover { color: #1e293b; }

.modal-search {
  position: relative;
  width: 300px;
}

.modal-search input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.8125rem;
  outline: none;
}

.modal-search .search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #94a3b8;
}

.lists-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  min-height: 400px;
}

.list-column {
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.column-title {
  padding: 16px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
}

.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.red { background: #ef4444; }
.dot.green { background: #db2777; }

.count-badge {
  background: #0f172a;
  color: white;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 0.75rem;
  margin-left: auto;
}

.count-badge.gray { background: #e2e8f0; color: #64748b; }

.list-items {
  flex: 1;
  padding: 8px;
  overflow-y: auto;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 12px;
  transition: all 0.2s;
}

.list-item:hover { background: #f8fafc; }

.item-info { display: flex; flex-direction: column; gap: 2px; }
.item-name { font-weight: 600; color: #1e293b; font-size: 0.875rem; }
.item-sub { font-size: 0.75rem; color: #94a3b8; }

.item-action {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px;
  transition: all 0.2s;
}

.item-action.remove { background: #fef2f2; color: #ef4444; }
.item-action.remove:hover { background: #ef4444; color: white; }

.item-action.add { background: #fdf2f8; color: #db2777; }
.item-action.add:hover { background: #db2777; color: white; }

.empty-list {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 0.8125rem;
  font-style: italic;
}

.modal-footer {
  padding: 24px 32px;
  background: white;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-outline {
  padding: 10px 24px;
  background: white;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
}

.btn-outline:hover { border-color: #1e293b; color: #1e293b; }

/* Spinner */
.loading-state {
  padding: 100px 0;
  text-align: center;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.spinner-small {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Custom Scrollbar */
.scrollbar-custom::-webkit-scrollbar { width: 6px; }
.scrollbar-custom::-webkit-scrollbar-track { background: transparent; }
.scrollbar-custom::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
.scrollbar-custom::-webkit-scrollbar-thumb:hover { background: #cbd5e1; }

.no-data {
  padding: 60px;
  text-align: center;
  color: #94a3b8;
  font-style: italic;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
