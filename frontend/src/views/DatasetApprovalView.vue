<script setup>
import { ref, computed, onMounted } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData } from '../utils/api';

const pendingRequests = ref([]);
const isLoading = ref(true);
const currentFilter = ref('Pending');
const currentTypeFilter = ref('all'); // 'all', 'api', 'dashboard'

const filteredRequests = computed(() => {
  if (currentTypeFilter.value === 'all') {
    return pendingRequests.value;
  }
  return pendingRequests.value.filter(req => {
    if (currentTypeFilter.value === 'dashboard') {
      return req.request_type === 'dashboard';
    }
    if (currentTypeFilter.value === 'api') {
      return req.request_type === 'api';
    }
    return true;
  });
});

const getCountByType = (type) => {
  if (type === 'all') return pendingRequests.value.length;
  return pendingRequests.value.filter(r => r.request_type === type).length;
};

const showModal = ref(false);
const selectedRequest = ref(null);
const granularForm = ref({
  allow_dictionary: true,
  allow_dashboard: true,
  allow_api: true
});

const showFieldsModal = ref(false);
const fieldsModalRequest = ref(null);
const copiedFields = ref(false);

const openFieldsModal = (req) => {
  fieldsModalRequest.value = req;
  showFieldsModal.value = true;
  copiedFields.value = false;
};

const closeFieldsModal = () => {
  showFieldsModal.value = false;
  fieldsModalRequest.value = null;
  copiedFields.value = false;
};

const copyFieldsToClipboard = async (fields) => {
  if (!fields || fields.length === 0) return;
  try {
    await navigator.clipboard.writeText(fields.join(', '));
    copiedFields.value = true;
    setTimeout(() => {
      copiedFields.value = false;
    }, 2500);
  } catch (err) {
    console.error('Failed to copy fields:', err);
  }
};

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

const isApproving = ref(false);

const openApprovalModal = (req) => {
  selectedRequest.value = req;
  const isDashboardOnly = req.request_type === 'dashboard';
  const isApiOnly = req.request_type === 'api';
  
  granularForm.value = {
    allow_dictionary: true,
    allow_dashboard: isDashboardOnly || (!isDashboardOnly && !isApiOnly),
    allow_api: isApiOnly || (!isDashboardOnly && !isApiOnly)
  };
  showModal.value = true;
};

const closeApprovalModal = () => {
  showModal.value = false;
  selectedRequest.value = null;
  isApproving.value = false;
};

const submitApproval = async () => {
  if (!selectedRequest.value || isApproving.value) return;
  isApproving.value = true;
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
  } finally {
    isApproving.value = false;
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

      <!-- Primary Category Tabs: API / Dashboard / All -->
      <div class="category-tabs">
        <button 
          :class="['category-tab-btn', currentTypeFilter === 'all' ? 'active' : '']" 
          @click="currentTypeFilter = 'all'"
        >
          <span style="font-size: 1.1rem;">🌐</span>
          <span>คำขอทั้งหมด</span>
          <span class="count-badge">{{ getCountByType('all') }}</span>
        </button>

        <button 
          :class="['category-tab-btn', currentTypeFilter === 'api' ? 'active' : '']" 
          @click="currentTypeFilter = 'api'"
        >
          <span style="font-size: 1.1rem;">⚡</span>
          <span>คำขอข้อมูล API</span>
          <span class="count-badge">{{ getCountByType('api') }}</span>
        </button>

        <button 
          :class="['category-tab-btn', currentTypeFilter === 'dashboard' ? 'active' : '']" 
          @click="currentTypeFilter = 'dashboard'"
        >
          <span style="font-size: 1.1rem;">📊</span>
          <span>คำขอแดชบอร์ด</span>
          <span class="count-badge">{{ getCountByType('dashboard') }}</span>
        </button>
      </div>

      <!-- Status Sub-tabs: Pending / Approved / Rejected -->
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
        <div v-if="filteredRequests.length === 0" class="no-data">
          <p v-if="currentTypeFilter === 'api'">
            ไม่มีคำขอข้อมูล API ในสถานะ {{ currentFilter === 'Pending' ? 'รอการอนุมัติ' : (currentFilter === 'Approved' ? 'อนุมัติแล้ว' : 'ถูกปฏิเสธ') }}
          </p>
          <p v-else-if="currentTypeFilter === 'dashboard'">
            ไม่มีคำขอแดชบอร์ดในสถานะ {{ currentFilter === 'Pending' ? 'รอการอนุมัติ' : (currentFilter === 'Approved' ? 'อนุมัติแล้ว' : 'ถูกปฏิเสธ') }}
          </p>
          <p v-else>
            ไม่มีคำขอในสถานะ {{ currentFilter === 'Pending' ? 'รอการอนุมัติ' : (currentFilter === 'Approved' ? 'อนุมัติแล้ว' : 'ถูกปฏิเสธ') }}
          </p>
        </div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>รหัสคำขอ</th>
              <th>ประเภทที่ขอ</th>
              <th>ชื่อ-นามสกุลจริง</th>
              <th>อีเมลสังกัด</th>
              <th>ชื่อหน่วยงาน</th>
              <th>ชุดข้อมูลที่ขอ</th>
              <th>เหตุผลที่ขอ</th>
              <th>เอกสารแนบ / ฟิลด์ข้อมูล</th>
              <th>วันที่ขอ</th>
              <th>จัดการ</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in filteredRequests" :key="req.request_id">
              <td>#{{ req.request_id }}</td>
              <td>
                <span v-if="req.request_type === 'dashboard'" class="badge-type badge-dashboard">📊 แดชบอร์ด</span>
                <span v-else-if="req.request_type === 'api'" class="badge-type badge-api">⚡ ข้อมูล API</span>
                <span v-else class="badge-type badge-all">🌐 ทั้งหมด</span>
                <div v-if="req.request_type === 'api' && req.fields && req.fields.length > 0" style="font-size: 0.75rem; color: #047857; margin-top: 4px; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" :title="req.fields.join(', ')">
                  {{ req.fields.length }} ฟิลด์: {{ req.fields.join(', ') }}
                </div>
              </td>
              <td>{{ req.firstname }} {{ req.lastname }}</td>
              <td>{{ req.email }}</td>
              <td>{{ req.organization || '-' }}</td>
              <td>{{ req.service_name || req.service_id }}</td>
              <td style="max-width: 180px; white-space: normal; font-size: 0.85rem;">{{ req.reason || '-' }}</td>
              <td>
                <div style="display: flex; flex-direction: column; gap: 6px; align-items: flex-start;">
                  <a v-if="req.mou_file_path" :href="`/api/downloadRequestMou/${req.request_id}`" target="_blank" class="btn-mou-download" title="คลิกเพื่อดูหรือดาวน์โหลดเอกสารแนบ">
                    📄 ดูไฟล์แนบ
                  </a>
                  <button 
                    v-if="req.request_type === 'api' || (req.fields && req.fields.length > 0)" 
                    class="btn-fields-popup" 
                    @click="openFieldsModal(req)" 
                    title="คลิกเพื่อดูรายการฟิลด์ที่ขอทั้งหมด"
                  >
                    ⚡ ดูฟิลด์ที่ขอ ({{ req.fields?.length || 0 }})
                  </button>
                  <span v-if="!req.mou_file_path && !(req.request_type === 'api' || (req.fields && req.fields.length > 0))" style="color: #94a3b8; font-size: 0.85rem;">-</span>
                </div>
              </td>
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

    <!-- Modal แสดงรายการฟิลด์ที่ขอ (API Fields Popup) -->
    <div v-if="showFieldsModal" class="modal-backdrop" @click.self="closeFieldsModal">
      <div class="modal-card fields-modal-card">
        <div class="fields-modal-header">
          <div style="display: flex; align-items: center; gap: 10px;">
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">⚡</div>
            <div>
              <h3 style="margin: 0; font-size: 1.15rem; color: #1e293b;">รายการฟิลด์ที่ขอเข้าถึง (API Fields)</h3>
              <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #64748b;">
                คำขอ #{{ fieldsModalRequest?.request_id }} โดย {{ fieldsModalRequest?.firstname }} {{ fieldsModalRequest?.lastname }} ({{ fieldsModalRequest?.organization || fieldsModalRequest?.email }})
              </p>
            </div>
          </div>
          <button class="btn-close-modal" @click="closeFieldsModal" title="ปิดหน้าต่าง">✕</button>
        </div>

        <div class="fields-modal-body">
          <div class="fields-summary-bar">
            <div>
              <span style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 600;">ชุดข้อมูลเป้าหมาย</span>
              <strong style="color: #1e293b; display: block; font-size: 0.95rem;">{{ fieldsModalRequest?.service_name || fieldsModalRequest?.service_id }}</strong>
            </div>
            <div style="text-align: right;">
              <span style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 600;">จำนวนฟิลด์</span>
              <div>
                <span class="fields-count-badge">{{ fieldsModalRequest?.fields?.length || 0 }} ฟิลด์</span>
              </div>
            </div>
          </div>

          <div v-if="fieldsModalRequest?.fields && fieldsModalRequest.fields.length > 0" class="fields-list-container">
            <div class="fields-tags-grid">
              <div 
                v-for="(field, index) in fieldsModalRequest.fields" 
                :key="field"
                class="field-tag-card"
              >
                <span class="field-num">{{ index + 1 }}</span>
                <span class="field-name">{{ field }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-fields-notice">
            <p style="margin: 0; font-size: 0.9rem; color: #64748b;">ไม่ได้ระบุฟิลด์เฉพาะเจาะจง (คำขอนี้ขอสิทธิ์ทุกฟิลด์ในชุดข้อมูล)</p>
          </div>
        </div>

        <div class="fields-modal-footer">
          <button 
            v-if="fieldsModalRequest?.fields && fieldsModalRequest.fields.length > 0"
            class="btn-copy-fields"
            @click="copyFieldsToClipboard(fieldsModalRequest.fields)"
          >
            <span v-if="copiedFields">✅ คัดลอกสำเร็จ!</span>
            <span v-else>📋 คัดลอกรายชื่อฟิลด์</span>
          </button>
          <button class="btn-cancel" @click="closeFieldsModal">ปิดหน้าต่าง</button>
        </div>
      </div>
    </div>

    <!-- Modal ตรวจสอบและอนุมัติสิทธิ์ (Approval Modal) -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeApprovalModal">
      <div class="modal-card approval-modal-card">
        <div class="approval-modal-header">
          <div style="display: flex; align-items: center; gap: 10px;">
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">
              <span v-if="selectedRequest?.request_type === 'dashboard'">📊</span>
              <span v-else-if="selectedRequest?.request_type === 'api'">⚡</span>
              <span v-else>🌐</span>
            </div>
            <div>
              <h3 style="margin: 0; font-size: 1.15rem; color: #1e293b;">อนุมัติคำขอเข้าถึงข้อมูล</h3>
              <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #64748b;">
                คำขอ #{{ selectedRequest?.request_id }} โดย {{ selectedRequest?.firstname }} {{ selectedRequest?.lastname }}
              </p>
            </div>
          </div>
          <button class="btn-close-modal" @click="closeApprovalModal" title="ปิดหน้าต่าง">✕</button>
        </div>

        <div class="approval-modal-body">
          <!-- Request Meta Summary -->
          <div class="approval-meta-grid">
            <div class="meta-item">
              <span class="meta-label">ชุดข้อมูล</span>
              <strong class="meta-value">{{ selectedRequest?.service_name || selectedRequest?.service_id }}</strong>
            </div>
            <div class="meta-item">
              <span class="meta-label">ประเภทสิทธิ์ที่ขอ</span>
              <div>
                <span v-if="selectedRequest?.request_type === 'dashboard'" class="badge-type badge-dashboard">📊 คำขอแดชบอร์ด</span>
                <span v-else-if="selectedRequest?.request_type === 'api'" class="badge-type badge-api">⚡ คำขอข้อมูล API</span>
                <span v-else class="badge-type badge-all">🌐 คำขอทั้งหมด</span>
              </div>
            </div>
            <div class="meta-item">
              <span class="meta-label">ผู้ขอเข้าถึง</span>
              <span class="meta-value">{{ selectedRequest?.firstname }} {{ selectedRequest?.lastname }} ({{ selectedRequest?.email }})</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">หน่วยงาน</span>
              <span class="meta-value">{{ selectedRequest?.organization || '-' }}</span>
            </div>
          </div>

          <!-- Purpose / Reason -->
          <div v-if="selectedRequest?.reason" class="approval-section-card">
            <div class="section-card-title">📝 วัตถุประสงค์ในการขอเข้าถึง:</div>
            <div class="section-card-content">{{ selectedRequest.reason }}</div>
          </div>

          <!-- Document Attachment (เอกสารแนบประกอบคำขอ) -->
          <div v-if="selectedRequest?.mou_file_path" class="approval-doc-card">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 1.5rem;">📄</span>
              <div>
                <div style="font-weight: 600; font-size: 0.85rem; color: #1e293b;">เอกสารประกอบคำขอ</div>
                <div style="font-size: 0.75rem; color: #64748b;">{{ selectedRequest?.mou_filename || 'เอกสารแนบประกอบคำขอ' }}</div>
              </div>
            </div>
            <a :href="`/api/downloadRequestMou/${selectedRequest?.request_id}`" target="_blank" class="btn-view-doc" title="คลิกเพื่อเปิดดูเอกสารแนบในแท็บใหม่">
              📄 เปิดดูเอกสาร
            </a>
          </div>

          <!-- Requested Fields for API (ถ้าเป็น API แสดงฟิลด์ที่ขอ) -->
          <div v-if="selectedRequest?.request_type === 'api' || (selectedRequest?.fields && selectedRequest?.fields.length > 0)" class="approval-fields-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <strong style="color: #065f46; font-size: 0.85rem;">
                ⚡ ฟิลด์ข้อมูลที่ขอใช้งาน ({{ selectedRequest.fields?.length || 0 }} ฟิลด์):
              </strong>
              <button 
                v-if="selectedRequest.fields && selectedRequest.fields.length > 0"
                class="btn-copy-sm"
                @click="copyFieldsToClipboard(selectedRequest.fields)"
                title="คัดลอกรายชื่อฟิลด์"
              >
                <span v-if="copiedFields">✅ คัดลอกแล้ว</span>
                <span v-else>📋 คัดลอก</span>
              </button>
            </div>
            <div v-if="selectedRequest.fields && selectedRequest.fields.length > 0" class="approval-fields-grid">
              <span v-for="(f, i) in selectedRequest.fields" :key="f" class="approval-field-chip">
                <span class="chip-num">{{ i + 1 }}</span>
                <span class="chip-name">{{ f }}</span>
              </span>
            </div>
            <div v-else style="font-size: 0.8rem; color: #64748b; font-style: italic;">
              คำขอนี้ขอสิทธิ์ทุกฟิลด์ในชุดข้อมูล
            </div>
          </div>

          <!-- Direct Grant Notice -->
          <div class="approval-notice-banner">
            <span style="font-size: 1.1rem;">💡</span>
            <span v-if="selectedRequest?.request_type === 'dashboard'">
              การอนุมัติจะให้สิทธิ์ผู้ใช้เข้าถึงหน้าแดชบอร์ดของชุดข้อมูลนี้ทันที
            </span>
            <span v-else-if="selectedRequest?.request_type === 'api'">
              การอนุมัติจะให้สิทธิ์ผู้ใช้เรียกใช้งาน API สำหรับฟิลด์ข้อมูลที่เลือกทันที
            </span>
            <span v-else>
              การอนุมัติจะให้สิทธิ์ผู้ใช้เข้าถึงทั้งแดชบอร์ดและ API ของชุดข้อมูลนี้ทันที
            </span>
          </div>
        </div>

        <div class="approval-modal-footer">
          <button class="btn-cancel" @click="closeApprovalModal" :disabled="isApproving">ยกเลิก</button>
          <button class="btn-confirm-approve" @click="submitApproval" :disabled="isApproving">
            <span v-if="isApproving">กำลังอนุมัติ...</span>
            <span v-else>✓ อนุมัติคำขอ</span>
          </button>
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
  background: var(--mso-accent, #008236);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-mou-download {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #008236;
  font-weight: 600;
  font-size: 0.8rem;
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.2s;
}
.btn-mou-download:hover {
  background: #e2e8f0;
  border-color: #008236;
}

.category-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.category-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  color: #475569;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.category-tab-btn:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
  color: #1e293b;
}

.category-tab-btn.active {
  background: #008236;
  border-color: #008236;
  color: white;
  box-shadow: 0 4px 6px -1px rgba(0, 130, 54, 0.25);
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 0.75rem;
  background: #f1f5f9;
  color: #475569;
  font-weight: 700;
}

.category-tab-btn.active .count-badge {
  background: rgba(255, 255, 255, 0.25);
  color: white;
}

.badge-type {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}
.badge-dashboard {
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
}
.badge-api {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}
.badge-all {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}

/* API Fields Popup Styles */
.btn-fields-popup {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #047857;
  font-weight: 600;
  font-size: 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.btn-fields-popup:hover {
  background: #d1fae5;
  border-color: #059669;
  color: #065f46;
}

.fields-modal-card {
  width: 580px;
  max-width: 92vw;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.fields-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 14px;
  border-bottom: 1px solid #e2e8f0;
}

.btn-close-modal {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  line-height: 1;
}
.btn-close-modal:hover {
  background: #f1f5f9;
  color: #475569;
}

.fields-modal-body {
  padding: 16px 0;
  overflow-y: auto;
  flex: 1;
}

.fields-summary-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.fields-count-badge {
  display: inline-block;
  background: #008236;
  color: white;
  font-weight: 700;
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 12px;
  margin-top: 2px;
}

.fields-list-container {
  max-height: 320px;
  overflow-y: auto;
  padding: 2px;
}

.fields-tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 8px;
}

.field-tag-card {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.15s;
}
.field-tag-card:hover {
  background: #f0fdf4;
  border-color: #86efac;
}

.field-num {
  font-size: 0.7rem;
  font-weight: 700;
  color: #64748b;
  background: #e2e8f0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}

.field-name {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.85rem;
  font-weight: 600;
  color: #0f766e;
  word-break: break-all;
}

.empty-fields-notice {
  text-align: center;
  padding: 24px;
  color: #64748b;
  background: #f8fafc;
  border-radius: 8px;
}

.fields-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid #e2e8f0;
}

.btn-copy-fields {
  background: #047857;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}
.btn-copy-fields:hover {
  background: #065f46;
}

/* Approval Modal Styles */
.approval-modal-card {
  width: 600px;
  max-width: 95vw;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
}

.approval-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.approval-modal-body {
  padding: 16px 0;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.approval-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 14px;
  border-radius: 8px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.meta-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
}

.meta-value {
  font-size: 0.9rem;
  color: #1e293b;
  word-break: break-word;
}

.approval-section-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 12px 14px;
  border-radius: 8px;
}

.section-card-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #475569;
  margin-bottom: 4px;
}

.section-card-content {
  font-size: 0.85rem;
  color: #334155;
  line-height: 1.4;
  white-space: pre-line;
}

.approval-doc-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  padding: 12px 14px;
  border-radius: 8px;
}

.btn-view-doc {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #008236;
  color: white;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 130, 54, 0.2);
}

.btn-view-doc:hover {
  background: #00662a;
}

.approval-fields-card {
  background: #f0fdf4;
  border: 1px solid #a7f3d0;
  padding: 12px 14px;
  border-radius: 8px;
}

.btn-copy-sm {
  background: white;
  border: 1px solid #a7f3d0;
  color: #047857;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-copy-sm:hover {
  background: #ecfdf5;
  border-color: #059669;
}

.approval-fields-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 160px;
  overflow-y: auto;
  padding-top: 4px;
}

.approval-field-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: white;
  border: 1px solid #bbf7d0;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
}

.chip-num {
  background: #dcfce7;
  color: #166534;
  font-size: 0.65rem;
  font-weight: 700;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.chip-name {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-weight: 600;
  color: #0f766e;
}

.approval-notice-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.825rem;
  line-height: 1.4;
}

.approval-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid #e2e8f0;
}

.btn-confirm-approve {
  background: #10b981;
  color: white;
  border: none;
  padding: 9px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.25);
  transition: all 0.2s;
}

.btn-confirm-approve:hover:not(:disabled) {
  background: #059669;
  box-shadow: 0 4px 6px rgba(16, 185, 129, 0.35);
}

.btn-confirm-approve:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
