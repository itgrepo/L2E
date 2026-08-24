<script setup>
import { ref, onMounted } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData } from '../utils/api';

const pendingRequests = ref([]);
const isLoading = ref(true);
const currentFilter = ref('Pending');

const showModal = ref(false);
const selectedRequest = ref(null);
const granularForm = ref({
  allow_dictionary: true,
  allow_dashboard: true,
  allow_api: true
});

const fetchPendingRequests = async () => {
  isLoading.value = true;
  try {
    const userData = localStorage.getItem('user');
    const res = await apiClient.post('/getPendingDatasetRequests', {
      user: userData ? encodeUserData(JSON.parse(userData)) : null,
      status: currentFilter.value
    });
    if (res.data?.status === 'success') {
      pendingRequests.value = res.data.data || [];
    }
  } catch (error) {
    console.error("Error fetching pending requests:", error);
  } finally {
    isLoading.value = false;
  }
};

const openApprovalModal = (req) => {
  selectedRequest.value = req;
  granularForm.value = {
    allow_dictionary: true,
    allow_dashboard: true,
    allow_api: true
  };
  showModal.value = true;
};

const closeApprovalModal = () => {
  showModal.value = false;
  selectedRequest.value = null;
};

const submitApproval = async () => {
  if (!selectedRequest.value) return;
  try {
    const userData = localStorage.getItem('user');
    await apiClient.post('/approveDatasetRequest', {
      user: userData ? encodeUserData(JSON.parse(userData)) : null,
      request_id: selectedRequest.value.request_id,
      ...granularForm.value
    });
    alert('อนุมัติคำขอสำเร็จ');
    closeApprovalModal();
    fetchPendingRequests();
  } catch (error) {
    alert('เกิดข้อผิดพลาดในการอนุมัติ: ' + (error.response?.data?.message || error.message));
  }
};

const rejectRequest = async (req) => {
  if (!confirm('คุณแน่ใจหรือไม่ที่จะปฏิเสธคำขอนี้?')) return;
  try {
    const userData = localStorage.getItem('user');
    await apiClient.post('/rejectDatasetRequest', { 
      user: userData ? encodeUserData(JSON.parse(userData)) : null,
      request_id: req.request_id 
    });
    alert('ปฏิเสธคำขอสำเร็จ');
    fetchPendingRequests();
  } catch (error) {
    alert('เกิดข้อผิดพลาด: ' + (error.response?.data?.message || error.message));
  }
};

onMounted(() => {
  fetchPendingRequests();
});
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div class="header-main">
          <h1>จัดการคำขออนุมัติชุดข้อมูล</h1>
          <p class="subtitle">ตรวจสอบและอนุมัติการเข้าถึงชุดข้อมูลของผู้ใช้งาน</p>
        </div>
      </header>

      <div class="filter-tabs" style="display: flex; gap: 16px; margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 0;">
        <button 
          :class="['filter-tab', currentFilter === 'Pending' ? 'active' : '']" 
          @click="currentFilter = 'Pending'; fetchPendingRequests()"
          style="padding: 12px 16px; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; color: #64748b; background: none; border: none; border-bottom-width: 2px; border-bottom-style: solid; font-size: 1rem;"
          :style="currentFilter === 'Pending' ? 'border-bottom-color: #10b981; color: #10b981;' : ''"
        >รายการที่รออนุมัติ</button>
        
        <button 
          :class="['filter-tab', currentFilter === 'Approved' ? 'active' : '']" 
          @click="currentFilter = 'Approved'; fetchPendingRequests()"
          style="padding: 12px 16px; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; color: #64748b; background: none; border: none; border-bottom-width: 2px; border-bottom-style: solid; font-size: 1rem;"
          :style="currentFilter === 'Approved' ? 'border-bottom-color: #10b981; color: #10b981;' : ''"
        >รายการที่อนุมัติแล้ว</button>
        
        <button 
          :class="['filter-tab', currentFilter === 'Rejected' ? 'active' : '']" 
          @click="currentFilter = 'Rejected'; fetchPendingRequests()"
          style="padding: 12px 16px; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; color: #64748b; background: none; border: none; border-bottom-width: 2px; border-bottom-style: solid; font-size: 1rem;"
          :style="currentFilter === 'Rejected' ? 'border-bottom-color: #10b981; color: #10b981;' : ''"
        >รายการที่ปฏิเสธ</button>
      </div>

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>กำลังโหลดคำขอ...</p>
      </div>

      <div v-else class="requests-container">
        <div v-if="pendingRequests.length === 0" class="no-data">
          <p v-if="currentFilter === 'Pending'">ไม่มีคำขอที่รอการอนุมัติในขณะนี้</p>
          <p v-else-if="currentFilter === 'Approved'">ไม่มีรายการที่อนุมัติแล้ว</p>
          <p v-else-if="currentFilter === 'Rejected'">ไม่มีรายการที่ถูกปฏิเสธ</p>
          <p v-else>ไม่มีข้อมูล</p>
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>รหัสคำขอ</th>
              <th>ผู้ใช้งาน</th>
              <th>ชุดข้อมูลที่ขอ</th>
              <th>เหตุผลที่ขอ</th>
              <th>วันที่ขอ</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in pendingRequests" :key="req.request_id">
              <td>#{{ req.request_id }}</td>
              <td>{{ req.username }}</td>
              <td>{{ req.service_name || req.service_id }}</td>
              <td>{{ req.reason || '-' }}</td>
              <td>{{ req.created_at }}</td>
              <td>
                <div v-if="req.status === 'Pending'" class="action-buttons">
                  <button class="btn-approve" @click="openApprovalModal(req)">อนุมัติ</button>
                  <button class="btn-reject" @click="rejectRequest(req)">ปฏิเสธ</button>
                </div>
                <div v-else style="font-weight: 600; color: #475569;">
                  <span v-if="req.status === 'Approved'" style="color: #10b981;">อนุมัติแล้ว</span>
                  <span v-else-if="req.status === 'Rejected'" style="color: #ef4444;">ปฏิเสธแล้ว</span>
                  <span v-else>{{ req.status }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <!-- Modal อนุมัติสิทธิ์ -->
    <div v-if="showModal" class="modal-backdrop">
      <div class="modal-card">
        <h3>อนุมัติสิทธิ์การเข้าถึงข้อมูล</h3>
        <p class="mb-4 text-sm text-slate-500">เลือกกำหนดระดับการเข้าถึงข้อมูลให้กับ <strong>{{ selectedRequest?.username }}</strong> สำหรับชุดข้อมูล <strong>{{ selectedRequest?.service_name || selectedRequest?.service_id }}</strong></p>
        
        <div class="form-group checkbox-group">
          <label>
            <input type="checkbox" v-model="granularForm.allow_dictionary">
            สิทธิ์ดูพจนานุกรมและข้อมูลตัวอย่าง (Data Dictionary & Preview)
          </label>
        </div>
        <div class="form-group checkbox-group">
          <label>
            <input type="checkbox" v-model="granularForm.allow_dashboard">
            สิทธิ์ดู Dashboard (Visualizations)
          </label>
        </div>
        <div class="form-group checkbox-group">
          <label>
            <input type="checkbox" v-model="granularForm.allow_api">
            สิทธิ์เรียกใช้ API และดาวน์โหลด (API Access & Download)
          </label>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" @click="closeApprovalModal">ยกเลิก</button>
          <button class="btn-confirm" @click="submitApproval">ยืนยันการอนุมัติ</button>
        </div>
      </div>
    </div>
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
  padding: 32px 48px;
  overflow-y: auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.subtitle {
  color: #64748b;
  font-size: 1rem;
}

.loading-state, .no-data {
  text-align: center;
  padding: 48px;
  color: #64748b;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--mso-accent, #2563eb);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
}

.data-table th, .data-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.data-table th {
  background: #f1f5f9;
  font-weight: 600;
  color: #475569;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-approve {
  background: #10b981;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.btn-approve:hover { background: #059669; }

.btn-reject {
  background: #ef4444;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.btn-reject:hover { background: #dc2626; }

/* Modal Styles */
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-card {
  background: white;
  width: 500px;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
}

.modal-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.checkbox-group {
  margin-bottom: 12px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel {
  background: white;
  border: 1px solid #cbd5e1;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.btn-confirm {
  background: var(--mso-accent, #2563eb);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}
</style>
