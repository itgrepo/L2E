<script setup>
import { ref, onMounted, computed } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData } from '../utils/api';

const activeTab = ref('users'); // 'users' or 'datasets'
const pendingUsers = ref([]);
const pendingDatasets = ref([]);
const isLoading = ref(true);
const isDatasetsLoading = ref(false);
const actionLoading = ref(null);
const successMessage = ref('');
const errorMessage = ref('');

const getUserData = () => {
  return JSON.parse(localStorage.getItem('user') || '{}');
};

const fetchPendingUsers = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const userData = getUserData();
    const response = await apiClient.post('/getPendingUsers', {
      user: encodeUserData(userData)
    });
    if (response.data.status === 'success') {
      pendingUsers.value = response.data.data || [];
    } else {
      errorMessage.value = response.data.message || response.data.status;
    }
  } catch (err) {
    console.error('Error fetching pending users:', err);
    errorMessage.value = 'ไม่สามารถโหลดข้อมูลได้';
  } finally {
    isLoading.value = false;
  }
};

const fetchPendingDatasets = async () => {
  isDatasetsLoading.value = true;
  errorMessage.value = '';
  try {
    const userData = getUserData();
    const response = await apiClient.post('/getPendingDatasetRequests', {
      user: encodeUserData(userData)
    });
    if (response.data.status === 'success') {
      pendingDatasets.value = response.data.data || [];
    } else {
      errorMessage.value = response.data.message || response.data.status;
    }
  } catch (err) {
    console.error('Error fetching pending datasets:', err);
    errorMessage.value = 'ไม่สามารถโหลดข้อมูลคำขอเข้าถึงข้อมูลได้';
  } finally {
    isDatasetsLoading.value = false;
  }
};

const approveUser = async (userId, username) => {
  console.log(`[Approve] Starting approval for user: ${username} (ID: ${userId})`);
  actionLoading.value = userId;
  errorMessage.value = '';
  try {
    const userData = getUserData();
    const encodedUser = encodeUserData(userData);
    
    const payload = {
      user: encodedUser,
      target_user_id: userId
    };
    
    const response = await apiClient.post('/approveUser', payload);
    
    if (response.data.status === 'success') {
      successMessage.value = response.data.message || `อนุมัติผู้ใช้ "${username}" สำเร็จ`;
      pendingUsers.value = pendingUsers.value.filter(u => u.user_id !== userId);
      setTimeout(() => successMessage.value = '', 5000);
    } else {
      errorMessage.value = response.data.message || response.data.status || 'เกิดข้อผิดพลาดจาก Backend';
    }
  } catch (err) {
    console.error('[Approve] Network/Exception error:', err);
    const errMsg = err.response?.data?.message || err.message || 'ไม่สามารถเชื่อมต่อ Backend ได้';
    errorMessage.value = `ไม่สามารถอนุมัติได้: ${errMsg}`;
  } finally {
    actionLoading.value = null;
  }
};

const rejectUser = async (userId, username) => {
  actionLoading.value = userId;
  errorMessage.value = '';
  try {
    const userData = getUserData();
    const response = await apiClient.post('/rejectUser', {
      user: encodeUserData(userData),
      target_user_id: userId
    });
    
    if (response.data.status === 'success') {
      successMessage.value = `ปฏิเสธผู้ใช้ "${username}" แล้ว`;
      pendingUsers.value = pendingUsers.value.filter(u => u.user_id !== userId);
      setTimeout(() => successMessage.value = '', 5000);
    } else {
      errorMessage.value = response.data.message || response.data.status || 'เกิดข้อผิดพลาด';
    }
  } catch (err) {
    console.error('[Reject] Network/Exception error:', err);
    const errMsg = err.response?.data?.message || err.message || 'ไม่สามารถเชื่อมต่อ Backend ได้';
    errorMessage.value = `ไม่สามารถปฏิเสธได้: ${errMsg}`;
  } finally {
    actionLoading.value = null;
  }
};

const approveDatasetRequest = async (requestId, username, datasetName) => {
  actionLoading.value = `dataset-${requestId}`;
  errorMessage.value = '';
  try {
    const userData = getUserData();
    const response = await apiClient.post('/approveDatasetRequest', {
      user: encodeUserData(userData),
      request_id: requestId
    });
    if (response.data.status === 'success') {
      successMessage.value = `อนุมัติการเข้าถึงข้อมูล "${datasetName}" ให้กับผู้ใช้ "${username}" สำเร็จ`;
      pendingDatasets.value = pendingDatasets.value.filter(req => req.request_id !== requestId);
      setTimeout(() => successMessage.value = '', 5000);
    } else {
      errorMessage.value = response.data.message || response.data.status;
    }
  } catch (err) {
    console.error('Error approving dataset request:', err);
    errorMessage.value = err.response?.data?.message || 'เกิดข้อผิดพลาดในการอนุมัติ';
  } finally {
    actionLoading.value = null;
  }
};

const rejectDatasetRequest = async (requestId, username, datasetName) => {
  actionLoading.value = `dataset-${requestId}`;
  errorMessage.value = '';
  try {
    const userData = getUserData();
    const response = await apiClient.post('/rejectDatasetRequest', {
      user: encodeUserData(userData),
      request_id: requestId
    });
    if (response.data.status === 'success') {
      successMessage.value = `ปฏิเสธการเข้าถึงข้อมูล "${datasetName}" สำหรับผู้ใช้ "${username}" เรียบร้อย`;
      pendingDatasets.value = pendingDatasets.value.filter(req => req.request_id !== requestId);
      setTimeout(() => successMessage.value = '', 5000);
    } else {
      errorMessage.value = response.data.message || response.data.status;
    }
  } catch (err) {
    console.error('Error rejecting dataset request:', err);
    errorMessage.value = err.response?.data?.message || 'เกิดข้อผิดพลาดในการปฏิเสธ';
  } finally {
    actionLoading.value = null;
  }
};

const approveAll = async () => {
  for (const user of [...pendingUsers.value]) {
    await approveUser(user.user_id, user.username);
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch {
    return dateStr;
  }
};

const refreshData = () => {
  if (activeTab.value === 'users') {
    fetchPendingUsers();
  } else {
    fetchPendingDatasets();
  }
};

onMounted(() => {
  fetchPendingUsers();
  fetchPendingDatasets();
});
</script>

<template>
  <div class="page-layout">
    <AppSidebar />
    <main class="main-content">
      <div class="page-header">
        <div>
          <h1>{{ activeTab === 'users' ? 'อนุมัติสมาชิก' : 'อนุมัติสิทธิ์เข้าถึงข้อมูล' }}</h1>
          <p class="header-subtitle">
            {{ activeTab === 'users' ? 'จัดการคำขอสมัครสมาชิกใหม่ที่รอการอนุมัติ' : 'จัดการคำขอสิทธิ์การใช้งานข้อมูลเพื่อใช้งาน API และดาวน์โหลด' }}
          </p>
        </div>
        <div class="header-actions">
          <button class="btn-refresh" @click="refreshData">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            รีเฟรช
          </button>
          <button v-if="activeTab === 'users' && pendingUsers.length > 0" class="btn-approve-all" @click="approveAll">
            ✓ อนุมัติทั้งหมด ({{ pendingUsers.length }})
          </button>
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div class="tabs-navigation" style="display: flex; gap: 16px; margin-bottom: 24px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
        <button 
          class="tab-link" 
          @click="activeTab = 'users'"
          style="background: none; border: none; font-size: 1rem; font-weight: 600; padding: 8px 16px; cursor: pointer; color: #64748b; border-bottom: 3px solid transparent; transition: all 0.2s; outline: none;"
          :style="activeTab === 'users' ? 'color: var(--primary); border-bottom-color: var(--primary);' : ''"
        >
          👤 อนุมัติสมาชิก ({{ pendingUsers.length }})
        </button>
        <button 
          class="tab-link" 
          @click="activeTab = 'datasets'"
          style="background: none; border: none; font-size: 1rem; font-weight: 600; padding: 8px 16px; cursor: pointer; color: #64748b; border-bottom: 3px solid transparent; transition: all 0.2s; outline: none;"
          :style="activeTab === 'datasets' ? 'color: var(--primary); border-bottom-color: var(--primary);' : ''"
        >
          📂 อนุมัติสิทธิ์การเข้าถึงข้อมูล ({{ pendingDatasets.length }})
        </button>
      </div>

      <!-- Success Toast -->
      <transition name="slide">
        <div v-if="successMessage" class="toast-success">
          ✅ {{ successMessage }}
        </div>
      </transition>

      <!-- Error -->
      <div v-if="errorMessage" class="error-alert">
        ❌ {{ errorMessage }}
        <button @click="errorMessage = ''" class="close-btn">×</button>
      </div>

      <!-- Users Approval Content -->
      <div v-if="activeTab === 'users'">
        <!-- Summary cards -->
        <div class="summary-cards">
          <div class="stat-card pending">
            <div class="stat-value">{{ pendingUsers.length }}</div>
            <div class="stat-label">รอการอนุมัติ</div>
            <div class="stat-icon">⏳</div>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>กำลังโหลดข้อมูล...</p>
        </div>

        <!-- Empty state -->
        <div v-else-if="pendingUsers.length === 0" class="empty-state">
          <div class="empty-icon">🎉</div>
          <h3>ไม่มีคำขอที่รอการอนุมัติ</h3>
          <p>สมาชิกที่สมัครใหม่และยืนยันอีเมลแล้วจะแสดงที่นี่</p>
        </div>

        <!-- Table -->
        <div v-else class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>ชื่อ-นามสกุล</th>
                <th>Username</th>
                <th>อีเมล</th>
                <th>หน่วยงาน</th>
                <th>สมัครเมื่อ</th>
                <th>การดำเนินการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(user, index) in pendingUsers" :key="user.user_id">
                <td>{{ index + 1 }}</td>
                <td>
                  <div class="user-cell">
                    <div class="user-avatar">{{ (user.firstname || user.username || '?').charAt(0).toUpperCase() }}</div>
                    <div>
                      <div class="user-fullname">{{ user.firstname || '-' }} {{ user.lastname || '' }}</div>
                    </div>
                  </div>
                </td>
                <td><code>{{ user.username }}</code></td>
                <td>{{ user.email || '-' }}</td>
                <td>{{ user.usage_objective || '-' }}</td>
                <td>{{ formatDate(user.create_at) }}</td>
                <td>
                  <div class="action-btns">
                    <button 
                      class="btn-action approve" 
                      @click="approveUser(user.user_id, user.username)"
                      :disabled="actionLoading === user.user_id"
                    >
                      <span v-if="actionLoading === user.user_id" class="mini-spinner"></span>
                      <span v-else>✓ อนุมัติ</span>
                    </button>
                    <button 
                      class="btn-action reject" 
                      @click="rejectUser(user.user_id, user.username)"
                      :disabled="actionLoading === user.user_id"
                    >
                      ✕ ปฏิเสธ
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Datasets Approval Content -->
      <div v-if="activeTab === 'datasets'">
        <!-- Summary cards -->
        <div class="summary-cards">
          <div class="stat-card pending" style="border-left-color: var(--primary);">
            <div class="stat-value">{{ pendingDatasets.length }}</div>
            <div class="stat-label">คำขอเข้าถึงข้อมูลที่ค้างอยู่</div>
            <div class="stat-icon">📂</div>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="isDatasetsLoading" class="loading-state">
          <div class="spinner"></div>
          <p>กำลังโหลดข้อมูลคำขอเข้าถึงข้อมูล...</p>
        </div>

        <!-- Empty state -->
        <div v-else-if="pendingDatasets.length === 0" class="empty-state">
          <div class="empty-icon">🎉</div>
          <h3>ไม่มีคำขอเข้าถึงข้อมูลที่รอการอนุมัติ</h3>
          <p>คำขอใหม่จากบัญชีข้อมูลจะแสดงที่นี่</p>
        </div>

        <!-- Table -->
        <div v-else class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>ผู้ขอสิทธิ์</th>
                <th>ชุดข้อมูลที่ขอสิทธิ์</th>
                <th>ฟิลด์ที่ขอสิทธิ์</th>
                <th>วัตถุประสงค์ / เหตุผล</th>
                <th>ส่งเมื่อ</th>
                <th>การดำเนินการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(req, index) in pendingDatasets" :key="req.request_id">
                <td>{{ index + 1 }}</td>
                <td>
                  <div class="user-cell">
                    <div class="user-avatar" style="background: linear-gradient(135deg, var(--primary), #0284c7);">
                      {{ (req.username || '?').charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <div class="user-fullname">{{ req.firstname || '-' }} {{ req.lastname || '' }}</div>
                      <div style="font-size:0.75rem; color:#64748b;">@{{ req.username }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="font-semibold text-slate-800">{{ req.service_name }}</div>
                  <div style="font-size:0.75rem; color:#64748b;" class="font-mono">{{ req.dataset_id }}</div>
                </td>
                <td>
                  <div style="display:flex; flex-wrap:wrap; gap:4px; max-width:240px;">
                    <span v-for="f in req.fields" :key="f" style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-size:0.75rem; font-weight:500;">
                      {{ f }}
                    </span>
                  </div>
                </td>
                <td style="max-width:300px; word-wrap:break-word; white-space:normal;">
                  {{ req.reason || '-' }}
                </td>
                <td>{{ formatDate(req.created_at) }}</td>
                <td>
                  <div class="action-btns">
                    <button 
                      class="btn-action approve" 
                      @click="approveDatasetRequest(req.request_id, req.username, req.service_name)"
                      :disabled="actionLoading === `dataset-${req.request_id}`"
                    >
                      <span v-if="actionLoading === `dataset-${req.request_id}`" class="mini-spinner"></span>
                      <span v-else>✓ อนุมัติ</span>
                    </button>
                    <button 
                      class="btn-action reject" 
                      @click="rejectDatasetRequest(req.request_id, req.username, req.service_name)"
                      :disabled="actionLoading === `dataset-${req.request_id}`"
                    >
                      ✕ ปฏิเสธ
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f1f5f9;
}

.main-content {
  flex: 1;
  padding: 32px;
  overflow-x: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px;
}

.header-subtitle {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  color: #475569;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  border-color: #94a3b8;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.btn-approve-all {
  padding: 10px 20px;
  background: var(--mso-accent);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-approve-all:hover {
  background: var(--primary);
  transform: translateY(-1px);
}

/* Toast */
.toast-success {
  background: #fdf2f8;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 14px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-weight: 500;
  animation: slideIn 0.3s ease;
}

.error-alert {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 14px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #b91c1c;
}

/* Summary */
.summary-cards {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px 28px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 200px;
}

.stat-card.pending {
  border-left: 4px solid #f59e0b;
}

.stat-value {
  font-size: 2rem;
  font-weight: 800;
  color: #1e293b;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
}

.stat-icon {
  font-size: 1.5rem;
  margin-left: auto;
}

/* Loading & Empty */
.loading-state {
  text-align: center;
  padding: 60px;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--mso-accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.empty-state {
  text-align: center;
  padding: 80px 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #1e293b;
  font-size: 1.25rem;
  margin-bottom: 8px;
}

.empty-state p {
  color: #64748b;
  font-size: 0.9rem;
}

/* Table */
.table-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8fafc;
  padding: 14px 16px;
  text-align: left;
  font-weight: 600;
  color: #475569;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e2e8f0;
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
  font-size: 0.9rem;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover td {
  background: #f8fafc;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--mso-accent), var(--primary));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.user-fullname {
  font-weight: 600;
  color: #1e293b;
}

code {
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #475569;
}

.action-btns {
  display: flex;
  gap: 8px;
}

.btn-action {
  padding: 8px 14px;
  border: none;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action.approve {
  background: #fce7f3;
  color: #166534;
}

.btn-action.approve:hover {
  background: var(--mso-accent);
  color: white;
}

.btn-action.reject {
  background: #fef2f2;
  color: #b91c1c;
}

.btn-action.reject:hover {
  background: #ef4444;
  color: white;
}

.btn-action:disabled {
  opacity: 0.6;
  cursor: wait;
}

.mini-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-bottom-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.slide-enter-active, .slide-leave-active {
  transition: all 0.3s;
}

.slide-enter-from, .slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
