<script setup>
import { ref, computed, onMounted } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData } from '../utils/api';

const groups = ref([]);
const isLoading = ref(true);

// 5 Hardcoded Subgroups according to requirement
const SUBGROUPS = [
  {
    id: 'course',
    code: 'course',
    prefix: 'CRS',
    title: 'กลุ่มข้อมูลหลักสูตร (Course Data)',
    icon: '📚'
  },
  {
    id: 'completion',
    code: 'completion',
    prefix: 'CMP',
    title: 'กลุ่มข้อมูลผลการเรียน (Completion Data)',
    icon: '🎓'
  },
  {
    id: 'competency',
    code: 'competency',
    prefix: 'COM',
    title: 'กลุ่มข้อมูลสมรรถนะบุคคล (Competency Data)',
    icon: '🏆'
  },
  {
    id: 'job_market',
    code: 'job_market',
    prefix: 'JOB',
    title: 'กลุ่มข้อมูลตลาดแรงงาน (Job / Labour Market Data)',
    icon: '💼'
  },
  {
    id: 'skill_analytics',
    code: 'skill_analytics',
    prefix: 'SKL',
    title: 'กลุ่มข้อมูลการวิเคราะห์ทักษะ (Skill Analytics Data)',
    icon: '📊'
  }
];

// Helper to determine which subgroup a dataset belongs to
const getDatasetSubgroup = (dataset) => {
  if (!dataset) return 'course';
  
  // 0. Direct subgroup or subgroup_id check
  if (dataset.subgroup) {
    const sg = dataset.subgroup.toLowerCase();
    if (sg.includes('course')) return 'course';
    if (sg.includes('completion')) return 'completion';
    if (sg.includes('competency')) return 'competency';
    if (sg.includes('job')) return 'job_market';
    if (sg.includes('skill')) return 'skill_analytics';
  }
  if (dataset.subgroup_id === 1) return 'course';
  if (dataset.subgroup_id === 2) return 'completion';
  if (dataset.subgroup_id === 3) return 'competency';
  if (dataset.subgroup_id === 4) return 'job_market';
  if (dataset.subgroup_id === 5) return 'skill_analytics';

  // 1. Check l2e_group_id (1..5)
  if (dataset.l2e_group_id === 1) return 'course';
  if (dataset.l2e_group_id === 2) return 'completion';
  if (dataset.l2e_group_id === 3) return 'competency';
  if (dataset.l2e_group_id === 4) return 'job_market';
  if (dataset.l2e_group_id === 5) return 'skill_analytics';
  
  // 2. Check dataset_id prefix
  const dsId = (dataset.dataset_id || '').toUpperCase();
  if (dsId.includes('CRS-') || dsId.includes('COURSES')) return 'course';
  if (dsId.includes('CMP-')) return 'completion';
  if (dsId.includes('COM-')) return 'competency';
  if (dsId.includes('JOB-')) return 'job_market';
  if (dsId.includes('SKL-')) return 'skill_analytics';

  // 3. Check category / sub_category
  const cat = ((dataset.category || '') + ' ' + (dataset.sub_category || '')).toLowerCase();
  if (cat.includes('course') || cat.includes('learning catalog') || cat.includes('หลักสูตร')) return 'course';
  if (cat.includes('completion') || cat.includes('learning record') || cat.includes('ผลการเรียน')) return 'completion';
  if (cat.includes('competency') || cat.includes('learner profile') || cat.includes('สมรรถนะ')) return 'competency';
  if (cat.includes('job') || cat.includes('labour') || cat.includes('labor') || cat.includes('ตลาดแรงงาน')) return 'job_market';
  if (cat.includes('skill') || cat.includes('analytics') || cat.includes('intelligence') || cat.includes('วิเคราะห์ทักษะ')) return 'skill_analytics';

  // Default fallback
  return 'course';
};

// Modal Data
const showManageModal = ref(false);
const selectedGroup = ref(null);
const assignedDatasets = ref([]);
const availableDatasets = ref([]);
const isSaving = ref(false);

// Active Subgroup inside Modal (null = show subgroup table, object = show subgroup dataset editor)
const activeSubgroup = ref(null);
const subgroupSearchQuery = ref('');

// Subgroup Datasets Helpers
const getAvailableDatasetsForSubgroup = (subgroupId) => {
  return availableDatasets.value.filter(d => getDatasetSubgroup(d) === subgroupId);
};

const getAssignedDatasetsForSubgroup = (subgroupId) => {
  return assignedDatasets.value.filter(d => getDatasetSubgroup(d) === subgroupId);
};

// Total datasets in system for this subgroup (from dataset creation)
const getSubgroupTotalCount = (subgroupId) => {
  const assigned = getAssignedDatasetsForSubgroup(subgroupId).length;
  const available = getAvailableDatasetsForSubgroup(subgroupId).length;
  return assigned + available;
};

// Assigned datasets for this specific group in this subgroup
const getSubgroupAssignedCount = (subgroupId) => {
  return getAssignedDatasetsForSubgroup(subgroupId).length;
};

// Filtered lists for currently active subgroup (with search)
const filteredAvailableForActiveSubgroup = computed(() => {
  if (!activeSubgroup.value) return [];
  const list = getAvailableDatasetsForSubgroup(activeSubgroup.value.id);
  const q = subgroupSearchQuery.value.trim().toLowerCase();
  if (!q) return list;
  return list.filter(d => 
    (d.service_name && d.service_name.toLowerCase().includes(q)) ||
    (d.organization && d.organization.toLowerCase().includes(q)) ||
    (d.dataset_id && d.dataset_id.toLowerCase().includes(q))
  );
});

const filteredAssignedForActiveSubgroup = computed(() => {
  if (!activeSubgroup.value) return [];
  const list = getAssignedDatasetsForSubgroup(activeSubgroup.value.id);
  const q = subgroupSearchQuery.value.trim().toLowerCase();
  if (!q) return list;
  return list.filter(d => 
    (d.service_name && d.service_name.toLowerCase().includes(q)) ||
    (d.organization && d.organization.toLowerCase().includes(q)) ||
    (d.dataset_id && d.dataset_id.toLowerCase().includes(q))
  );
});

const openSubgroupManage = (subgroup) => {
  activeSubgroup.value = subgroup;
  subgroupSearchQuery.value = '';
};

const backToSubgroups = () => {
  activeSubgroup.value = null;
  subgroupSearchQuery.value = '';
};

const assignAllInSubgroup = () => {
  if (!activeSubgroup.value) return;
  const toAssign = [...filteredAvailableForActiveSubgroup.value];
  toAssign.forEach(dataset => assignDataset(dataset));
};

const removeAllInSubgroup = () => {
  if (!activeSubgroup.value) return;
  const toRemove = [...filteredAssignedForActiveSubgroup.value];
  toRemove.forEach(dataset => removeDataset(dataset));
};

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
    const response = await apiClient.post('/getGroups', { user: userParam, group_type: 'dataset_group' });
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
  activeSubgroup.value = null;
  subgroupSearchQuery.value = '';
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
      assignedDatasets.value = response.data.assigned || [];
      availableDatasets.value = response.data.available || [];
    }
  } catch (err) {
    console.error('Error fetching dataset access:', err);
  }
};

const closeManageModal = () => {
  showManageModal.value = false;
  selectedGroup.value = null;
  activeSubgroup.value = null;
  subgroupSearchQuery.value = '';
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
      // Update group card count
      fetchGroups();
      // If inside subgroup view, go back to table with updated counts
      if (activeSubgroup.value) {
        backToSubgroups();
      } else {
        closeManageModal();
      }
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
      group_name: newGroupName.value.trim(),
      group_type: 'dataset_group'
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

// Access Management Modal State (BY GROUP / BY USER from user diagram)
const showAccessModal = ref(false);
const selectedAccessGroup = ref(null);
const accessMode = ref('select'); // 'select' | 'group' | 'user'
const isProcessingAccess = ref(false);
const modalSearchQuery = ref('');
const assignedItems = ref([]);
const availableItems = ref([]);

const openAccessModal = (group) => {
  selectedAccessGroup.value = group;
  accessMode.value = 'select';
  modalSearchQuery.value = '';
  assignedItems.value = [];
  availableItems.value = [];
  showAccessModal.value = true;
};

const closeAccessModal = () => {
  showAccessModal.value = false;
  selectedAccessGroup.value = null;
  accessMode.value = 'select';
  modalSearchQuery.value = '';
  assignedItems.value = [];
  availableItems.value = [];
};

const fetchAccessData = async (mode) => {
  accessMode.value = mode;
  isProcessingAccess.value = true;
  modalSearchQuery.value = '';
  assignedItems.value = [];
  availableItems.value = [];

  try {
    const userParam = getUserParam();
    if (mode === 'user') {
      const response = await apiClient.post('/getGroupMembers', {
        user: userParam,
        group_id: selectedAccessGroup.value.group_id
      });
      if (response.data.status === 'success') {
        assignedItems.value = response.data.assigned || [];
        availableItems.value = response.data.available || [];
      } else {
        alert(response.data.status || 'ไม่สามารถโหลดรายชื่อผู้ใช้ได้');
      }
    } else if (mode === 'group') {
      const response = await apiClient.post('/getGroupDatasetAccess', {
        user: userParam,
        group_id: selectedAccessGroup.value.group_id
      });
      if (response.data.status === 'success') {
        assignedItems.value = response.data.assigned || [];
        availableItems.value = response.data.available || [];
      } else {
        alert(response.data.status || 'ไม่สามารถโหลดข้อมูลชุดข้อมูลของกลุ่มได้');
      }
    }
  } catch (error) {
    console.error(`Error fetching ${mode} access:`, error);
    alert('ไม่สามารถโหลดข้อมูลสิทธิ์ได้ กรุณาลองใหม่');
  } finally {
    isProcessingAccess.value = false;
  }
};

const handleAssign = (item) => {
  if (accessMode.value === 'user') {
    availableItems.value = availableItems.value.filter(i => i.user_id !== item.user_id);
    assignedItems.value.push(item);
  } else {
    availableItems.value = availableItems.value.filter(i => i.service_id !== item.service_id);
    assignedItems.value.push(item);
  }
};

const handleUnassign = (item) => {
  if (accessMode.value === 'user') {
    assignedItems.value = assignedItems.value.filter(i => i.user_id !== item.user_id);
    availableItems.value.push(item);
  } else {
    assignedItems.value = assignedItems.value.filter(i => i.service_id !== item.service_id);
    availableItems.value.push(item);
  }
};

const saveAccessChanges = async () => {
  if (!selectedAccessGroup.value) return;
  isProcessingAccess.value = true;
  try {
    const userParam = getUserParam();
    if (accessMode.value === 'user') {
      const userIds = assignedItems.value.map(i => i.user_id);
      const response = await apiClient.post('/updateGroupMembers', {
        user: userParam,
        group_id: selectedAccessGroup.value.group_id,
        user_ids: userIds
      });
      if (response.data.status === 'success') {
        alert('บันทึกข้อมูลสมาชิกกลุ่มเรียบร้อยแล้ว');
        fetchGroups();
        accessMode.value = 'select';
      } else {
        alert('Error: ' + (response.data.status || 'ไม่สามารถบันทึกได้'));
      }
    } else if (accessMode.value === 'group') {
      const serviceIds = assignedItems.value.map(i => i.service_id);
      const response = await apiClient.post('/updateGroupDatasetAccess', {
        user: userParam,
        group_id: selectedAccessGroup.value.group_id,
        service_ids: serviceIds
      });
      if (response.data.status === 'success') {
        alert('บันทึกสิทธิ์ชุดข้อมูลของกลุ่มเรียบร้อยแล้ว');
        fetchGroups();
        accessMode.value = 'select';
      } else {
        alert('Error: ' + (response.data.status || 'ไม่สามารถบันทึกได้'));
      }
    }
  } catch (error) {
    console.error('Error saving access changes:', error);
    alert('ไม่สามารถบันทึกข้อมูลได้ กรุณาลองใหม่');
  } finally {
    isProcessingAccess.value = false;
  }
};

const filteredAssigned = computed(() => {
  if (!modalSearchQuery.value) return assignedItems.value;
  const q = modalSearchQuery.value.trim().toLowerCase();
  return assignedItems.value.filter(item => {
    if (accessMode.value === 'user') {
      const name = `${item.firstname || ''} ${item.lastname || ''}`.toLowerCase();
      const username = (item.username || '').toLowerCase();
      const email = (item.email || '').toLowerCase();
      return name.includes(q) || username.includes(q) || email.includes(q);
    } else {
      const sName = (item.service_name || '').toLowerCase();
      const dsId = (item.dataset_id || '').toLowerCase();
      const org = (item.organization || '').toLowerCase();
      return sName.includes(q) || dsId.includes(q) || org.includes(q);
    }
  });
});

const filteredAvailable = computed(() => {
  if (!modalSearchQuery.value) return availableItems.value;
  const q = modalSearchQuery.value.trim().toLowerCase();
  return availableItems.value.filter(item => {
    if (accessMode.value === 'user') {
      const name = `${item.firstname || ''} ${item.lastname || ''}`.toLowerCase();
      const username = (item.username || '').toLowerCase();
      const email = (item.email || '').toLowerCase();
      return name.includes(q) || username.includes(q) || email.includes(q);
    } else {
      const sName = (item.service_name || '').toLowerCase();
      const dsId = (item.dataset_id || '').toLowerCase();
      const org = (item.organization || '').toLowerCase();
      return sName.includes(q) || dsId.includes(q) || org.includes(q);
    }
  });
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
            <div class="stat" :title="'จำนวนสมาชิกทั้งหมดในกลุ่ม โดยไม่นับจำนวนสมาชิกเนื่องจาก 1 user สามารถถืออยู่ได้มากกว่า 1 Group User'">
              <span class="stat-value">{{ group.member_count }}</span>
              <span class="stat-label">
                สมาชิก
                <span class="stat-info-badge" :title="'จำนวนสมาชิกทั้งหมดในกลุ่ม โดยไม่นับจำนวนสมาชิกเนื่องจาก 1 user สามารถถืออยู่ได้มากกว่า 1 Group User'">ℹ️</span>
              </span>
            </div>
            <div class="stat" :title="'จำนวนชุดข้อมูลทั้งหมดในกลุ่ม (ชุดข้อมูลสามารถถืออยู่ได้ 1 กลุ่มโดยถูกบังคับให้เลือก Group & Subgroup ตั้งแต่ตอนสร้างแต่สามารถมาปรับแก้ไขได้ภายหลังที่ Group manage)'">
              <span class="stat-value">{{ group.dataset_count || 0 }}</span>
              <span class="stat-label">
                ชุดข้อมูล
                <span class="stat-info-badge" :title="'จำนวนชุดข้อมูลทั้งหมดในกลุ่ม (ชุดข้อมูลสามารถถืออยู่ได้ 1 กลุ่มโดยถูกบังคับให้เลือก Group & Subgroup ตั้งแต่ตอนสร้างแต่สามารถมาปรับแก้ไขได้ภายหลังที่ Group manage)'">ℹ️</span>
              </span>
            </div>
          </div>
          <div class="card-footer">
            <button class="btn-card-action btn-manage-access" @click="openAccessModal(group)" title="จัดการ user และกลุ่ม user">
              <svg xmlns="http://www.w3.org/2000/svg" class="action-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              <span>จัดการ user และกลุ่ม user</span>
            </button>
            <button class="btn-card-action btn-manage-subgroup" @click="openManageModal(group)" title="จัดการกลุ่มย่อย">
              <svg xmlns="http://www.w3.org/2000/svg" class="action-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span>จัดการกลุ่มย่อย</span>
            </button>
            <button class="btn-delete-group" @click="deleteGroup(group)" title="ลบกลุ่ม">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
              <span>ลบกลุ่ม</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Manage Dataset Access Modal -->
      <div v-if="showManageModal" class="modal-overlay">
        <div class="modal">
          <div class="modal-header">
            <div>
              <h2 v-if="!activeSubgroup">จัดการกลุ่มข้อมูลย่อย (Subgroup) - {{ selectedGroup?.group_name }}</h2>
              <h2 v-else>จัดการชุดข้อมูล: {{ activeSubgroup.title }}</h2>
              <p class="modal-subtitle" v-if="activeSubgroup">กลุ่มผู้ใช้: {{ selectedGroup?.group_name }}</p>
            </div>
            <button class="btn-close" @click="closeManageModal">✕</button>
          </div>
          
          <div class="modal-body">
            <!-- 1. SUBGROUP TABLE VIEW (Default) -->
            <div v-if="!activeSubgroup" class="subgroup-table-view">
              <div class="subgroup-header-info">
                <p class="subgroup-desc">
                  จัดการสิทธิ์เข้าถึงชุดข้อมูลของกลุ่ม <strong>"{{ selectedGroup?.group_name }}"</strong> โดยจำแนกตามกลุ่มข้อมูลย่อย (Subgroup) ทั้ง 5 กลุ่ม
                </p>
              </div>

              <div class="subgroup-table-card">
                <table class="subgroup-table">
                  <thead>
                    <tr>
                      <th style="width: 45%;">ชื่อ subgroup (5 ตัวเลือก)</th>
                      <th style="width: 30%; text-align: center;">จำนวนชุดข้อมูล</th>
                      <th style="width: 25%; text-align: center;">จัดการเพิ่มชุดข้อมูล</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="subgroup in SUBGROUPS" :key="subgroup.id">
                      <td>
                        <div class="subgroup-name-cell">
                          <span class="subgroup-icon">{{ subgroup.icon }}</span>
                          <div class="subgroup-title-wrap">
                            <span class="subgroup-title">{{ subgroup.title }}</span>
                            <span class="subgroup-prefix-badge">Prefix: {{ subgroup.prefix }}-*</span>
                          </div>
                        </div>
                      </td>
                      <td style="text-align: center;">
                        <div class="count-badge-wrap">
                          <span class="count-total">{{ getSubgroupTotalCount(subgroup.id) }} ชุดข้อมูล</span>
                          <span class="count-assigned" v-if="getSubgroupAssignedCount(subgroup.id) > 0">
                            (กำหนดสิทธิ์แล้ว {{ getSubgroupAssignedCount(subgroup.id) }} ชุด)
                          </span>
                          <span class="count-zero" v-else>
                            (ยังไม่ได้กำหนดสิทธิ์)
                          </span>
                        </div>
                      </td>
                      <td style="text-align: center;">
                        <button class="btn-subgroup-action" @click="openSubgroupManage(subgroup)">
                          <span>⚙️ จัดการชุดข้อมูล</span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 2. SUBGROUP DATASET MANAGEMENT VIEW (Drill-down) -->
            <div v-else class="subgroup-detail-view">
              <div class="subgroup-nav-bar">
                <button class="btn-back-subgroup" @click="backToSubgroups">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                  กลับไปรายการ Subgroup
                </button>
                <div class="active-subgroup-stat-pill">
                  กำหนดสิทธิ์แล้ว <strong>{{ getSubgroupAssignedCount(activeSubgroup.id) }}</strong> / {{ getSubgroupTotalCount(activeSubgroup.id) }} ชุด
                </div>
              </div>

              <!-- Search in Subgroup -->
              <div class="subgroup-search-box">
                <input 
                  v-model="subgroupSearchQuery" 
                  type="text" 
                  placeholder="🔍 ค้นหาชุดข้อมูลในกลุ่มย่อยนี้..." 
                  class="subgroup-search-input"
                />
              </div>

              <!-- Dual Listbox for Active Subgroup -->
              <div class="access-layout">
                <div class="access-panel">
                  <div class="panel-header">
                    <h3>ชุดข้อมูลที่เลือกได้ ({{ filteredAvailableForActiveSubgroup.length }})</h3>
                    <button 
                      v-if="filteredAvailableForActiveSubgroup.length > 0" 
                      class="btn-bulk-action" 
                      @click="assignAllInSubgroup"
                    >
                      + เพิ่มทั้งหมด
                    </button>
                  </div>
                  <div class="panel-list">
                    <div v-if="filteredAvailableForActiveSubgroup.length === 0" class="empty-state">
                      ไม่มีชุดข้อมูลเพิ่มเติมในกลุ่มย่อยนี้
                    </div>
                    <div v-for="dataset in filteredAvailableForActiveSubgroup" :key="dataset.service_id" class="list-item">
                      <div class="item-info">
                        <strong>{{ dataset.service_name }}</strong>
                        <small>
                          {{ dataset.organization || 'N/A' }} 
                          <span v-if="dataset.dataset_id" class="item-ds-id">({{ dataset.dataset_id }})</span>
                        </small>
                      </div>
                      <button class="btn-action add" @click="assignDataset(dataset)" title="เพิ่มสิทธิ์ชุดข้อมูล">+</button>
                    </div>
                  </div>
                </div>

                <div class="access-panel assigned-panel">
                  <div class="panel-header">
                    <h3>ชุดข้อมูลที่เข้าถึงได้ ({{ filteredAssignedForActiveSubgroup.length }})</h3>
                    <button 
                      v-if="filteredAssignedForActiveSubgroup.length > 0" 
                      class="btn-bulk-action remove" 
                      @click="removeAllInSubgroup"
                    >
                      ✕ ลบทั้งหมด
                    </button>
                  </div>
                  <div class="panel-list">
                    <div v-if="filteredAssignedForActiveSubgroup.length === 0" class="empty-state">
                      ยังไม่มีชุดข้อมูลที่กำหนดในกลุ่มย่อยนี้
                    </div>
                    <div v-for="dataset in filteredAssignedForActiveSubgroup" :key="dataset.service_id" class="list-item assigned">
                      <div class="item-info">
                        <strong>{{ dataset.service_name }}</strong>
                        <small>
                          {{ dataset.organization || 'N/A' }} 
                          <span v-if="dataset.dataset_id" class="item-ds-id">({{ dataset.dataset_id }})</span>
                        </small>
                      </div>
                      <button class="btn-action remove" @click="removeDataset(dataset)" title="ยกเลิกสิทธิ์ชุดข้อมูล">✕</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <template v-if="!activeSubgroup">
              <button class="btn-save" @click="closeManageModal">ปิดหน้าต่าง</button>
            </template>
            <template v-else>
              <button class="btn-cancel" @click="backToSubgroups">กลับ</button>
              <button class="btn-save" @click="saveDatasetAccess" :disabled="isSaving">
                {{ isSaving ? 'กำลังบันทึก...' : 'บันทึกการเปลี่ยนแปลง' }}
              </button>
            </template>
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

      <!-- Manage Access Modal (BY GROUP & BY USER) -->
      <div v-if="showAccessModal" class="modal-overlay">
        <div class="modal modal-access">
          <header class="modal-header">
            <div class="modal-title-wrap">
              <div class="title-with-badge">
                <span class="modal-title-icon">🔐</span>
                <h2>จัดการสิทธิ์การเข้าถึง</h2>
              </div>
              <p class="modal-subtitle">({{ selectedAccessGroup?.group_name }})</p>
            </div>
            <button class="btn-close" @click="closeAccessModal">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </header>

          <div class="modal-body scrollbar-custom">
            <!-- Mode Selection: 2 Cards (BY USER & BY DATASET) -->
            <div v-if="accessMode === 'select'" class="selection-grid transition-fade">
              <button class="selection-card user" @click="fetchAccessData('user')">
                <div class="selection-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <div class="selection-info">
                  <h3>BY USER</h3>
                  <p>จัดการสมาชิกผู้ใช้งานในกลุ่มนี้</p>
                </div>
              </button>

              <button class="selection-card group" @click="fetchAccessData('group')">
                <div class="selection-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                  </svg>
                </div>
                <div class="selection-info">
                  <h3>BY DATASET</h3>
                  <p>จัดการชุดข้อมูลในกลุ่มนี้</p>
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
                  <input type="text" v-model="modalSearchQuery" :placeholder="accessMode === 'user' ? 'ค้นหาชื่อผู้ใช้หรืออีเมล...' : 'ค้นหาชื่อชุดข้อมูลหรือรหัส...'">
                </div>
              </div>

              <div v-if="isProcessingAccess" class="loading-state" style="padding: 60px 0;">
                <div class="spinner"></div>
                <p style="color: #64748b; margin-top: 12px;">กำลังโหลดข้อมูล...</p>
              </div>

              <div v-else class="lists-wrapper">
                <!-- Assigned Column -->
                <div class="list-column assigned">
                  <div class="column-title">
                    <span class="dot red"></span>
                    {{ accessMode === 'user' ? 'ผู้ใช้ที่ได้รับสิทธิ์ในกลุ่ม' : 'ชุดข้อมูลที่ได้รับสิทธิ์ในกลุ่ม' }}
                    <span class="count-badge">{{ assignedItems.length }}</span>
                  </div>
                  <div class="list-items scrollbar-custom">
                    <div v-for="item in filteredAssigned" :key="item.user_id || item.service_id" class="list-item">
                      <div class="item-info">
                        <span class="item-name">{{ accessMode === 'user' ? `${item.firstname || ''} ${item.lastname || ''}` : item.service_name }}</span>
                        <span class="item-sub">{{ accessMode === 'user' ? (item.username || item.email) : (item.dataset_id || item.organization) }}</span>
                      </div>
                      <button class="item-action remove" @click="handleUnassign(item)" :title="accessMode === 'user' ? 'ลบผู้ใช้' : 'ลบชุดข้อมูล'">
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
                    {{ accessMode === 'user' ? 'เพิ่มผู้ใช้งานในระบบ' : 'เพิ่มชุดข้อมูล' }}
                    <span class="count-badge gray">{{ availableItems.length }}</span>
                  </div>
                  <div class="list-items scrollbar-custom">
                    <div v-for="item in filteredAvailable" :key="item.user_id || item.service_id" class="list-item">
                      <div class="item-info">
                        <span class="item-name">{{ accessMode === 'user' ? `${item.firstname || ''} ${item.lastname || ''}` : item.service_name }}</span>
                        <span class="item-sub">{{ accessMode === 'user' ? (item.username || item.email) : (item.dataset_id || item.organization) }}</span>
                      </div>
                      <button class="item-action add" @click="handleAssign(item)" :title="accessMode === 'user' ? 'เพิ่มเข้ากลุ่ม' : 'เพิ่มชุดข้อมูลเข้ากลุ่ม'">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </button>
                    </div>
                    <div v-if="filteredAvailable.length === 0" class="empty-list">ไม่พบรายการให้เลือกเพิ่ม</div>
                  </div>
                </div>
              </div>

              <div v-if="!isProcessingAccess" class="modal-footer" style="padding: 16px 0 0; background: none; border-top: 1px solid #e2e8f0; margin-top: 16px;">
                <button class="btn-cancel" @click="accessMode = 'select'">ยกเลิก</button>
                <button class="btn-save" @click="saveAccessChanges" :disabled="isProcessingAccess">
                  บันทึกข้อมูล
                </button>
              </div>
            </div>
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
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-card-action {
  flex: 1 1 130px;
  padding: 10px 12px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  white-space: nowrap;
}

.btn-manage-access {
  background-color: #f0fdf4;
  border: 1.5px solid #bbf7d0;
  color: #166534;
}

.btn-manage-access:hover {
  background-color: #dcfce7;
  border-color: #86efac;
  transform: translateY(-1px);
}

.btn-manage-subgroup {
  background-color: #eff6ff;
  border: 1.5px solid #bfdbfe;
  color: #1d4ed8;
}

.btn-manage-subgroup:hover {
  background-color: #dbeafe;
  border-color: #93c5fd;
  transform: translateY(-1px);
}

.action-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.btn-delete-group {
  padding: 10px 12px;
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
  gap: 4px;
  font-size: 0.8rem;
  white-space: nowrap;
}

.btn-delete-group:hover {
  background-color: #fee2e2;
  border-color: #f87171;
  transform: translateY(-1px);
}

.stat-info-badge {
  display: inline-block;
  margin-left: 4px;
  font-size: 0.8rem;
  opacity: 0.6;
  cursor: help;
  transition: opacity 0.2s;
}

.stat-info-badge:hover {
  opacity: 1;
}

/* Access Modal Specific Styles */
.modal-access {
  max-width: 860px;
  width: 95%;
}

.modal-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 10px;
}

.modal-title-icon {
  font-size: 1.5rem;
}

.selection-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  padding: 24px 0;
}

.selection-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px 24px;
  border-radius: 20px;
  border: 2px solid #e2e8f0;
  background: white;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.selection-card:hover {
  border-color: #3b82f6;
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -6px rgba(59, 130, 246, 0.15);
}

.selection-card.group:hover {
  border-color: #3b82f6;
}

.selection-card.user:hover {
  border-color: #10b981;
}

.selection-icon {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px;
}

.selection-icon svg {
  width: 36px;
  height: 36px;
}

.selection-card.group .selection-icon {
  background: #eff6ff;
  color: #1d4ed8;
}

.selection-card.user .selection-icon {
  background: #ecfdf5;
  color: #10b981;
}

.selection-info {
  text-align: center;
}

.selection-info h3 {
  font-weight: 800;
  font-size: 1.25rem;
  color: #1e293b;
  margin-bottom: 6px;
}

.selection-info p {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
}

/* Dual List Layout */
.dual-list-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-back:hover {
  color: #1e293b;
  background: #f1f5f9;
}

.modal-search {
  position: relative;
  width: 280px;
}

.modal-search input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  font-size: 0.8125rem;
  outline: none;
  transition: border-color 0.2s;
}

.modal-search input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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
  gap: 20px;
  min-height: 380px;
}

.list-column {
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: 440px;
}

.column-title {
  padding: 14px 18px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.red { background: #ef4444; }
.dot.green { background: #10b981; }

.count-badge {
  background: #0f172a;
  color: white;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 0.75rem;
  margin-left: auto;
}

.count-badge.gray {
  background: #e2e8f0;
  color: #64748b;
}

.list-items {
  flex: 1;
  padding: 8px;
  overflow-y: auto;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: 10px;
  transition: all 0.15s;
  border-bottom: 1px solid #f1f5f9;
}

.list-item:hover {
  background: #f8fafc;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
  padding-right: 8px;
}

.item-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-sub {
  font-size: 0.75rem;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

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
  flex-shrink: 0;
}

.item-action.remove {
  background: #fef2f2;
  color: #ef4444;
}

.item-action.remove:hover {
  background: #ef4444;
  color: white;
}

.item-action.add {
  background: #ecfdf5;
  color: #10b981;
}

.item-action.add:hover {
  background: #10b981;
  color: white;
}

.empty-list {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 0.8125rem;
  font-style: italic;
}

.transition-fade {
  animation: fadeIn 0.25s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.scrollbar-custom::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-custom::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-custom::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}

.scrollbar-custom::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
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

/* ============================================
   SUBGROUP TABLE & DETAIL STYLES
   ============================================ */
.modal-subtitle {
  color: #64748b;
  font-size: 0.875rem;
  margin: 4px 0 0 0;
}

.subgroup-table-view {
  width: 100%;
}

.subgroup-header-info {
  margin-bottom: 20px;
  padding: 14px 18px;
  background: #f8fafc;
  border-radius: 12px;
  border-left: 4px solid var(--primary, #4f46e5);
}

.subgroup-desc {
  margin: 0;
  font-size: 0.95rem;
  color: #475569;
  line-height: 1.5;
}

.subgroup-table-card {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  overflow: hidden;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.subgroup-table {
  width: 100%;
  border-collapse: collapse;
}

.subgroup-table th {
  background: #f8fafc;
  padding: 14px 20px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
  border-bottom: 1px solid #e2e8f0;
}

.subgroup-table td {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.subgroup-table tbody tr:last-child td {
  border-bottom: none;
}

.subgroup-table tbody tr:hover {
  background: #fcfcfd;
}

.subgroup-name-cell {
  display: flex;
  align-items: center;
  gap: 14px;
}

.subgroup-icon {
  font-size: 1.5rem;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef2ff;
  border-radius: 10px;
  flex-shrink: 0;
}

.subgroup-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.subgroup-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.95rem;
}

.subgroup-prefix-badge {
  font-size: 0.75rem;
  color: #64748b;
  font-family: monospace;
}

.count-badge-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.count-total {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}

.count-assigned {
  font-size: 0.8rem;
  color: #16a34a;
  font-weight: 600;
}

.count-zero {
  font-size: 0.8rem;
  color: #94a3b8;
}

.btn-subgroup-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #15803d;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-subgroup-action:hover {
  background: #dcfce7;
  border-color: #86efac;
  transform: translateY(-1px);
}

.subgroup-detail-view {
  width: 100%;
}

.subgroup-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.btn-back-subgroup {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  color: #475569;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back-subgroup:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.active-subgroup-stat-pill {
  padding: 6px 14px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #1e40af;
}

.subgroup-search-box {
  margin-bottom: 16px;
}

.subgroup-search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  font-size: 0.95rem;
  box-sizing: border-box;
}

.subgroup-search-input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-bulk-action {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #3b82f6;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-bulk-action:hover {
  background: #eff6ff;
  border-color: #93c5fd;
}

.btn-bulk-action.remove {
  color: #dc2626;
}

.btn-bulk-action.remove:hover {
  background: #fef2f2;
  border-color: #fca5a5;
}

.item-ds-id {
  font-family: monospace;
  color: #94a3b8;
  font-size: 0.75rem;
}
</style>
