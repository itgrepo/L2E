<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { encodeUserData } from '../utils/api';

const route = useRoute();
const router = useRouter();

const activeTab = ref('info');
const isLoading = ref(true);
const errorMessage = ref('');

const selectedDataset = ref(null);
const requestForm = ref({ fields: [], reason: '' });
const reqError = ref('');
const reqSuccess = ref('');
const isSubmittingReq = ref(false);

const favorites = ref(JSON.parse(localStorage.getItem('user_favorites') || '[]'));
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));

const isFavorite = (ds) => {
  return favorites.value.some(fav => fav.id === ds.id);
};

const toggleFavorite = (ds) => {
  const index = favorites.value.findIndex(fav => fav.id === ds.id);
  if (index >= 0) {
    favorites.value.splice(index, 1);
  } else {
    favorites.value.push({
      id: ds.id,
      name: ds.title,
      agency: ds.agency,
      formats: ds.formats
    });
  }
  localStorage.setItem('user_favorites', JSON.stringify(favorites.value));
};

const fetchDatasetDetail = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const userStr = localStorage.getItem('user');
    let payload = {};
    if (userStr) {
      payload.user = encodeUserData(JSON.parse(userStr));
    }
    const response = await apiClient.post('/retrieveService', payload);
    if (response.data.status === 'success') {
      const found = response.data.data.find(item => item.service_id.toString() === route.params.id.toString());
      if (found) {
        selectedDataset.value = {
          id: found.service_id,
          dataset_id: found.dataset_id,
          title: found.service_name,
          agency: found.organization || 'ไม่ระบุหน่วยงาน',
          category: found.category || 'ทั่วไป',
          sub_category: found.sub_category || '-',
          description: found.description || 'ข้อมูลชุดนี้รวบรวมเพื่อการวิเคราะห์และนำไปใช้ประโยชน์ในระดับภาครัฐและเอกชน',
          contact_name: found.contact_name || '-',
          contact_email: found.contact_email || '-',
          tags: found.tags || '',
          purpose: found.purpose || '-',
          accessibility: found.accessibility || 'Open Data',
          access_type: found.access_type || '-',
          dept_contact: found.dept_contact || '-',
          update_freq: (found.update_freq_value || '-') + ' ' + (found.update_freq_unit || ''),
          geo_scope: found.geo_scope || '-',
          data_source: found.data_source || '-',
          gov_category: found.gov_category || '-',
          license: found.license || '-',
          access_conditions: found.access_conditions || '-',
          sponsor: found.sponsor || '-',
          smallest_unit: found.smallest_unit || '-',
          languages: found.languages || '-',
          objective_type: found.objective_type || '-',
          external_dashboard_url: found.external_dashboard_url,
          external_api_url: found.external_api_url,
          has_access: found.has_access === 1 || found.has_access === '1' || found.has_access === true,
          permission_status: found.permission_status,
          api_response_fields: found.api_response_fields ? (typeof found.api_response_fields === 'string' ? JSON.parse(found.api_response_fields) : found.api_response_fields) : ['id', 'name', 'amount', 'date'],
          api_enabled: found.api_enabled == 1 || found.api_enabled === '1' || found.api_enabled === true,
          formats: found.data_format ? found.data_format.split(',') : ['CSV', 'API', 'JSON'],
          file_path: found.file_path,
          views: (Math.floor(Math.random() * 900) + 100) + 'K records',
          updated: 'ปรับปรุงเมื่อ 2 วันที่แล้ว',
          dataset_type: found.dataset_type || 'general',
          stat_year_start: found.stat_year_start,
          stat_year_latest: found.stat_year_latest,
          stat_classification: found.stat_classification,
          stat_unit: found.stat_unit,
          stat_multiplier: found.stat_multiplier,
          stat_calculation_method: found.stat_calculation_method,
          stat_standard: found.stat_standard,
          stat_official: found.stat_official,
          geo_dataset_name: found.geo_dataset_name,
          geo_scale: found.geo_scale,
          geo_west_bound: found.geo_west_bound,
          geo_east_bound: found.geo_east_bound,
          geo_north_bound: found.geo_north_bound,
          geo_south_bound: found.geo_south_bound,
          geo_position_accuracy: found.geo_position_accuracy,
          geo_reference_time: found.geo_reference_time,
          geo_published_date: found.geo_published_date
        };
      } else {
        errorMessage.value = 'ไม่พบชุดข้อมูลดังกล่าวในระบบ';
      }
    } else {
      errorMessage.value = 'ดึงข้อมูลชุดข้อมูลไม่สำเร็จ';
    }
  } catch (error) {
    console.error('Error fetching dataset detail:', error);
    errorMessage.value = 'เกิดข้อผิดพลาดในการโหลดรายละเอียดชุดข้อมูล';
  } finally {
    isLoading.value = false;
  }
};

const submitPermissionRequest = async () => {
  if (requestForm.value.fields.length === 0) {
    reqError.value = 'โปรดเลือกอย่างน้อย 1 ฟิลด์ข้อมูล';
    return;
  }
  if (!requestForm.value.reason.trim()) {
    reqError.value = 'โปรดระบุวัตถุประสงค์ในการขอเข้าถึง';
    return;
  }
  
  isSubmittingReq.value = true;
  reqError.value = '';
  reqSuccess.value = '';
  
  try {
    const userData = localStorage.getItem('user');
    const response = await apiClient.post('/requestDatasetPermission', {
      user: encodeUserData(JSON.parse(userData)),
      service_id: selectedDataset.value.id,
      fields: requestForm.value.fields,
      reason: requestForm.value.reason
    });
    
    if (response.data.status === 'success') {
      reqSuccess.value = 'ส่งคำขอเข้าถึงข้อมูลเรียบร้อยแล้ว';
      selectedDataset.value.permission_status = 'Pending';
      requestForm.value.fields = [];
      requestForm.value.reason = '';
      fetchDatasetDetail();
    } else {
      reqError.value = response.data.message || 'เกิดข้อผิดพลาด';
    }
  } catch (error) {
    reqError.value = error.response?.data?.message || 'ไม่สามารถส่งคำขอได้';
  } finally {
    isSubmittingReq.value = false;
  }
};

const openPreview = (format) => {
  if (selectedDataset.value) {
    let fileTypeParam = 'data';
    if (format === 'DICTIONARY') fileTypeParam = 'dictionary';
    else if (format === 'SAMPLING') fileTypeParam = 'sampling';
    
    // For CSV, XLS, API, etc. it corresponds to the main data file.
    window.open(`/api/downloadFile/${selectedDataset.value.id}?type=${fileTypeParam}`, '_blank');
  } else {
    alert(`กำลังเปิดดาวน์โหลดไฟล์/แสดงพรีวิวในรูปแบบ ${format}`);
  }
};

onMounted(() => {
  fetchDatasetDetail();
});
</script>

<template>
  <div class="detail-layout">
    <AppSidebar />
    
    <main class="detail-content">
      <nav class="breadcrumb">
        <router-link to="/catalog">Catalog</router-link>
        <span class="separator">/</span>
        <span class="current">Dataset Detail</span>
      </nav>
      
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>กำลังโหลดข้อมูลรายละเอียดชุดข้อมูล...</p>
      </div>
      
      <div v-else-if="errorMessage" class="error-state">
        <p>{{ errorMessage }}</p>
        <button @click="fetchDatasetDetail" class="btn-outline">ลองใหม่อีกครั้ง</button>
      </div>
      
      <template v-else-if="selectedDataset">
        <header class="detail-header">
          <div class="header-main">
            <div class="agency-header">
              <div class="agency-logo">DEX</div>
              <span class="agency-name">{{ selectedDataset.agency }}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
              <h1 style="margin:0;">{{ selectedDataset.title }}</h1>
              <span class="id-badge font-mono">{{ selectedDataset.dataset_id }}</span>
            </div>
            
            <div class="header-meta">
              <span class="meta-badge access">{{ selectedDataset.accessibility }}</span>
              <span class="meta-item">{{ selectedDataset.category }} / {{ selectedDataset.sub_category }}</span>
              <span class="meta-item">• {{ selectedDataset.views }}</span>
            </div>
          </div>
          
          <div class="header-actions">
            <button class="btn-outline" :class="{ 'is-active': isFavorite(selectedDataset) }" @click="toggleFavorite(selectedDataset)">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" :fill="isFavorite(selectedDataset) ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.921-1.103 1.821-1.891 1.118l-3.976-2.888a1 1 0 00-1.175 0l-3.976 2.888c-.788.703-2.191-.197-1.891-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              {{ isFavorite(selectedDataset) ? 'เลิกติดตาม' : 'ติดตามชุดข้อมูล' }}
            </button>
          </div>
        </header>
        
        <div class="tabs-container">
          <nav class="tabs">
            <button :class="['tab-btn', { active: activeTab === 'info' }]" @click="activeTab = 'info'">คำอธิบายข้อมูล</button>
            <button :class="['tab-btn', { active: activeTab === 'dictionary' }]" @click="activeTab = 'dictionary'">พจนานุกรมข้อมูล</button>
            <button :class="['tab-btn', { active: activeTab === 'visual' }]" @click="activeTab = 'visual'">แดชบอร์ด</button>
            <button :class="['tab-btn', { active: activeTab === 'api' }]" @click="activeTab = 'api'">ข้อมูล API</button>
          </nav>
          
          <div class="tab-content">
            <!-- Info Tab -->
            <div v-if="activeTab === 'info'" class="info-tab transition-fade">
              <div class="info-grid">
                <div class="info-main">
                  <h3>รายละเอียด</h3>
                  <p>{{ selectedDataset.description }}</p>
                  
                  <div class="metadata-table">
                    <div class="row-group-title">ข้อมูลทั่วไป</div>
                    <div class="row"><span class="label">รหัสชุดข้อมูล</span><span class="value font-mono">{{ selectedDataset.dataset_id }}</span></div>
                    <div class="row"><span class="label">หน่วยงานเจ้าของ</span><span class="value">{{ selectedDataset.agency }}</span></div>
                    <div class="row"><span class="label">ผู้ติดต่อ</span><span class="value">{{ selectedDataset.contact_name }}</span></div>
                    <div class="row"><span class="label">อีเมลติดต่อ</span><span class="value">{{ selectedDataset.contact_email }}</span></div>
                    <div class="row"><span class="label">หมวดหมู่ชุดข้อมูล</span><span class="value">{{ selectedDataset.category }} / {{ selectedDataset.sub_category }}</span></div>
                    <div class="row"><span class="label">การเข้าถึง</span><span class="value">{{ selectedDataset.access_type }}</span></div>
                    
                    <div class="row-group-title">ธรรมาภิบาลและความถี่</div>
                    <div class="row"><span class="label">ชั้นความลับ</span><span class="value">{{ selectedDataset.gov_category }}</span></div>
                    <div class="row"><span class="label">สัญญาอนุญาต</span><span class="value">{{ selectedDataset.license }}</span></div>
                    <div class="row"><span class="label">วัตถุประสงค์</span><span class="value">{{ selectedDataset.objective_type }}</span></div>
                    <div class="row"><span class="label">แหล่งที่มา</span><span class="value">{{ selectedDataset.data_source }}</span></div>
                    <div class="row"><span class="label">ความถี่การปรับปรุง</span><span class="value">{{ selectedDataset.update_freq }}</span></div>
                    <div class="row"><span class="label">ขอบเขตข้อมูล</span><span class="value">{{ selectedDataset.geo_scope }}</span></div>
                    
                    <!-- STATISTIC SPECIFIC -->
                    <template v-if="selectedDataset.dataset_type === 'statistic'">
                      <div class="row-group-title text-sky-600 border-sky-200 mt-4">ข้อมูลเฉพาะสถิติ</div>
                      <div class="row"><span class="label">ปีข้อมูลที่เริ่มจัดทำ</span><span class="value">{{ selectedDataset.stat_year_start || '-' }}</span></div>
                      <div class="row"><span class="label">ปีข้อมูลล่าสุด</span><span class="value">{{ selectedDataset.stat_year_latest || '-' }}</span></div>
                      <div class="row"><span class="label">การจัดจำแนก</span><span class="value">{{ selectedDataset.stat_classification || '-' }}</span></div>
                      <div class="row"><span class="label">หน่วยวัด</span><span class="value">{{ selectedDataset.stat_unit || '-' }}</span></div>
                      <div class="row"><span class="label">หน่วยตัวคูณ</span><span class="value">{{ selectedDataset.stat_multiplier || '-' }}</span></div>
                      <div class="row"><span class="label">วิธีการคำนวณ</span><span class="value">{{ selectedDataset.stat_calculation_method || '-' }}</span></div>
                      <div class="row"><span class="label">มาตรฐานการจัดทำข้อมูล</span><span class="value">{{ selectedDataset.stat_standard || '-' }}</span></div>
                      <div class="row"><span class="label">สถิติทางการ</span><span class="value">{{ selectedDataset.stat_official || '-' }}</span></div>
                    </template>

                    <!-- GEOSPATIAL SPECIFIC -->
                    <template v-if="selectedDataset.dataset_type === 'geospatial'">
                      <div class="row-group-title text-[var(--primary)] border-emerald-200 mt-4">ข้อมูลภูมิสารสนเทศเชิงพื้นที่</div>
                      <div class="row"><span class="label">ชื่อชุดข้อมูลภูมิศาสตร์</span><span class="value">{{ selectedDataset.geo_dataset_name || '-' }}</span></div>
                      <div class="row"><span class="label">มาตราส่วน</span><span class="value">{{ selectedDataset.geo_scale || '-' }}</span></div>
                      <div class="row"><span class="label">ขอบเขต (W, E, N, S)</span><span class="value font-mono">{{ selectedDataset.geo_west_bound || '-' }}, {{ selectedDataset.geo_east_bound || '-' }}, {{ selectedDataset.geo_north_bound || '-' }}, {{ selectedDataset.geo_south_bound || '-' }}</span></div>
                      <div class="row"><span class="label">ความถูกต้องของตำแหน่ง</span><span class="value">{{ selectedDataset.geo_position_accuracy || '-' }}</span></div>
                      <div class="row"><span class="label">เวลาอ้างอิง</span><span class="value">{{ selectedDataset.geo_reference_time || '-' }}</span></div>
                      <div class="row"><span class="label">วันที่เผยแพร่ข้อมูล</span><span class="value">{{ selectedDataset.geo_published_date || '-' }}</span></div>
                    </template>

                    <div class="row-group-title mt-4">ข้อมูลอื่นๆ</div>
                    <div class="row"><span class="label">แท็ก</span><span class="value">
                      <span v-for="tag in selectedDataset.tags.split(',')" :key="tag" class="tag-inline">{{ tag.trim() }}</span>
                    </span></div>
                  </div>
                </div>
                
                <aside class="info-sidebar">
                  <!-- If has access, show download options -->
                  <div v-if="selectedDataset.has_access" class="action-card">
                    <h4>ดาวน์โหลดข้อมูล</h4>
                    <p>ดาวน์โหลดไฟล์ข้อมูลต้นฉบับในรูปแบบต่างๆ</p>
                    <div class="download-buttons">
                      <button class="btn-download csv" @click="openPreview('CSV')">CSV</button>
                      <button class="btn-download xls" @click="openPreview('Excel')">Excel</button>
                    </div>
                    <button v-if="selectedDataset.file_path" class="btn-primary-outline w-full mt-4" style="width:100%; margin-top:16px;" @click="openPreview('ไฟล์แนบต้นฉบับ')">ดาวน์โหลดไฟล์แนบ (API File)</button>
                    <button v-if="selectedDataset.data_sampling_path" class="btn-primary-outline w-full mt-4" style="width:100%; margin-top:16px;" @click="openPreview('ชุดข้อมูลสุ่ม (Zip File)')">ดาวน์โหลดชุดข้อมูลสุ่ม (Zip File)</button>
                  </div>
                  
                  <!-- If does NOT have access, show Request Access form -->
                  <div v-else class="action-card">
                    <h4 style="display:flex;align-items:center;gap:6px;">🔒 จำกัดสิทธิ์การใช้งาน</h4>
                    <p style="font-size:0.875rem;color:#64748b;margin-bottom:16px;">ชุดข้อมูลนี้จำกัดสิทธิ์ โปรดส่งคำขออนุญาตเพื่อดาวน์โหลดข้อมูลหรือใช้ API</p>
                    
                    <div v-if="!selectedDataset.permission_status" class="request-access-form-wrapper">
                      <!-- Field selector -->
                      <div class="form-group mb-4" style="margin-bottom: 12px;">
                        <label class="font-semibold block mb-1 text-slate-700" style="font-size:0.85rem; display:block; margin-bottom: 4px; font-weight:600;">ฟิลด์ข้อมูลที่ต้องการ *</label>
                        <div class="field-checkbox-list" style="max-height:120px;overflow-y:auto;border:1px solid #e2e8f0;border-radius:6px;padding:8px;background:#f8fafc; text-align:left;">
                          <label v-for="field in selectedDataset.api_response_fields" :key="field" class="flex items-center gap-2 mb-1 cursor-pointer" style="display:flex;align-items:center;gap:6px;font-size:0.85rem; margin-bottom: 4px; cursor:pointer;">
                            <input type="checkbox" :value="field" v-model="requestForm.fields">
                            <span>{{ field }}</span>
                          </label>
                        </div>
                      </div>
                      
                      <!-- Reason input -->
                      <div class="form-group mb-4" style="margin-bottom: 12px;">
                        <label class="font-semibold block mb-1 text-slate-700" style="font-size:0.85rem; display:block; margin-bottom: 4px; font-weight:600;">วัตถุประสงค์ในการขอเข้าถึง *</label>
                        <textarea v-model="requestForm.reason" rows="2" style="width:100%;border:1px solid #e2e8f0;border-radius:6px;padding:8px;font-size:0.85rem;resize:none; box-sizing:border-box;" placeholder="ระบุเหตุผลและวัตถุประสงค์การใช้งาน..."></textarea>
                      </div>

                      <div v-if="reqError" style="color:#e11d48;font-size:0.75rem;margin-bottom:8px;text-align:left;">{{ reqError }}</div>
                      <div v-if="reqSuccess" style="color:#16a34a;font-size:0.75rem;margin-bottom:8px;text-align:left;">{{ reqSuccess }}</div>

                      <button class="btn-primary w-full" style="padding:10px;font-size:0.9rem;width:100%; border:none; border-radius:8px; background:var(--mso-accent, var(--primary)); color:white; font-weight:600; cursor:pointer;" :disabled="isSubmittingReq" @click="submitPermissionRequest">
                        {{ isSubmittingReq ? 'กำลังส่งคำขอ...' : 'ส่งคำขอเข้าถึงข้อมูล' }}
                      </button>
                    </div>

                    <!-- If status is Pending -->
                    <div v-else-if="selectedDataset.permission_status === 'Pending'" style="background:#fef3c7; color:#92400e; padding:12px; border-radius:8px; border:1px solid #fde68a; text-align:center;">
                      <p style="font-weight:bold; margin:0 0 4px 0; font-size:0.875rem;">⏳ รอการอนุมัติสิทธิ์ (Pending Approval)</p>
                      <p style="font-size:0.75rem; margin:0; color:#b45309;">คำขอเข้าถึงข้อมูลอยู่ระหว่างการพิจารณาโดยผู้ดูแลระบบ</p>
                    </div>

                    <!-- If status is Rejected -->
                    <div v-else-if="selectedDataset.permission_status === 'Rejected'" style="background:#fee2e2; color:#991b1b; padding:12px; border-radius:8px; border:1px solid #fecaca; text-align:center;">
                      <p style="font-weight:bold; margin:0 0 4px 0; font-size:0.875rem;">❌ ปฏิเสธการขอสิทธิ์ (Rejected)</p>
                      <p style="font-size:0.75rem; margin:0 0 8px 0; color:#b91c1c;">คำขอเข้าถึงข้อมูลของคุณถูกปฏิเสธ</p>
                      <button class="btn-primary-outline w-full" style="padding:6px; font-size:0.75rem; width:100%;" @click="selectedDataset.permission_status = null">ส่งคำขอใหม่อีกครั้ง</button>
                    </div>
                  </div>
                </aside>
              </div>
            </div>
            
            <!-- Dictionary Tab -->
            <div v-if="activeTab === 'dictionary'" class="dictionary-tab transition-fade">
              <table class="dictionary-table">
                <thead>
                  <tr>
                    <th style="width: 10%">ลำดับ</th>
                    <th style="width: 30%">ชื่อฟิลด์</th>
                    <th style="width: 20%">ประเภท</th>
                    <th style="width: 40%">คำอธิบาย</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(field, index) in selectedDataset.api_response_fields" :key="field">
                    <td>{{ index + 1 }}</td>
                    <td class="font-mono" style="font-weight:600;">{{ field }}</td>
                    <td>VARCHAR / String</td>
                    <td>ฟิลด์ข้อมูลที่ให้บริการสำหรับชุดข้อมูลนี้</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- Visual Tab -->
            <div v-if="activeTab === 'visual'" class="visual-tab transition-fade" style="padding: 0;">
              <!-- If does not have access, hide dashboard visualizer -->
              <div v-if="!selectedDataset.has_access" class="visual-restricted-card" style="padding: 40px; text-align: center; background:#f8fafc; border:1px solid #e2e8f0; border-radius:16px;">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="height: 64px; width: 64px; margin: 0 auto 16px auto; color: #94a3b8;">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <p style="font-weight: bold; font-size: 1.125rem; margin-bottom: 4px; color:#1e293b;">แดชบอร์ดถูกจำกัดสิทธิ์</p>
                <p style="font-size: 0.875rem; color: #64748b; margin-bottom: 16px;">โปรดส่งคำขอเข้าถึงข้อมูลเพื่อเรียกดูแดชบอร์ดของชุดข้อมูลนี้</p>
                <button style="padding: 8px 24px; background: #1e293b; color: white; border: none; border-radius: 8px; font-weight: 500; cursor: pointer;" @click="activeTab = 'info'">
                  ส่งคำขอเข้าถึงข้อมูล
                </button>
              </div>
              <div v-else-if="selectedDataset.external_dashboard_url" class="dashboard-container">
                <div class="dashboard-actions mb-4 p-4 flex justify-between items-center bg-slate-50 border-b border-slate-100" style="display:flex; justify-content:space-between; align-items:center; padding:16px; background:#f8fafc; border-bottom:1px solid #cbd5e1;">
                  <div style="display:flex; align-items:center; gap:8px; color:#475569; font-weight:500;">
                    <span>External Dashboard</span>
                  </div>
                  <a :href="selectedDataset.external_dashboard_url" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:8px 16px; background:var(--mso-accent, var(--primary)); color:white; border-radius:8px; text-decoration:none; font-weight:600; font-size:0.875rem;">
                    เปิดในหน้าต่างใหม่
                  </a>
                </div>
                <div class="iframe-wrapper" style="height: 60vh; position: relative; background: #f8fafc;">
                  <iframe 
                    :src="selectedDataset.external_dashboard_url" 
                    width="100%" 
                    height="100%" 
                    frameborder="0" 
                    allowfullscreen
                    style="border: none;"
                  ></iframe>
                </div>
              </div>
              <div v-else class="dashboard-mockup-container bg-slate-50 p-6" style="height: 600px; overflow-y: auto; border-radius: 0 0 1rem 1rem; background:#f8fafc; padding:24px;">
                <!-- Mockup Header Stats -->
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                  <div style="padding: 16px; background: white; border-radius: 12px; border: 1px solid #f1f5f9; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <p style="font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin: 0 0 4px 0;">ปริมาณการใช้งานทั้งหมด</p>
                    <p style="font-size: 1.5rem; font-weight: 800; color: #1e293b; margin: 0;">5.47M <span style="font-size: 0.75rem; color: #10b981; font-weight: normal;">+2.4%</span></p>
                  </div>
                  <div style="padding: 16px; background: white; border-radius: 12px; border: 1px solid #f1f5f9; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <p style="font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin: 0 0 4px 0;">สัดส่วนการเชื่อมต่อ</p>
                    <p style="font-size: 1.5rem; font-weight: 800; color: #1e293b; margin: 0;">3,620 <span style="font-size: 0.75rem; color: #64748b; font-weight: normal;">ครั้ง/วัน</span></p>
                  </div>
                  <div style="padding: 16px; background: white; border-radius: 12px; border: 1px solid #f1f5f9; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <p style="font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase; margin: 0 0 4px 0;">ประสิทธิภาพ API</p>
                    <p style="font-size: 1.5rem; font-weight: 800; color: var(--primary); margin: 0;">99.85% <span style="font-size: 0.75rem; color: var(--primary); font-weight: normal;">เสถียรภาพสูง</span></p>
                  </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                  <!-- Main Bar Chart Mockup -->
                  <div style="padding:16px; background:white; border-radius:12px; border:1px solid #f1f5f9; grid-column:span 2; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <p style="font-size: 0.875rem; font-weight: 700; color: #334155; margin: 0 0 16px 0;">ปริมาณข้อมูลรายวันแยกตามประเภท</p>
                    <div style="display: flex; align-items: flex-end; gap: 0.5rem; height: 180px; padding-bottom: 20px; border-bottom: 1px solid #f1f5f9;">
                      <div style="flex: 1; height: 90%; background: var(--mso-pink-dark); border-radius: 4px 4px 0 0;"></div>
                      <div style="flex: 1; height: 45%; background: var(--mso-pink-dark); border-radius: 4px 4px 0 0;"></div>
                      <div style="flex: 1; height: 40%; background: var(--mso-pink-dark); border-radius: 4px 4px 0 0;"></div>
                      <div style="flex: 1; height: 35%; background: var(--primary); border-radius: 4px 4px 0 0;"></div>
                      <div style="flex: 1; height: 65%; background: var(--mso-pink-dark); border-radius: 4px 4px 0 0;"></div>
                      <div style="flex: 1; height: 50%; background: var(--mso-pink-dark); border-radius: 4px 4px 0 0;"></div>
                      <div style="flex: 1; height: 30%; background: var(--mso-pink-dark); border-radius: 4px 4px 0 0;"></div>
                      <div style="flex: 1; height: 25%; background: var(--mso-pink-dark); border-radius: 4px 4px 0 0;"></div>
                      <div style="flex: 1; height: 55%; background: var(--mso-pink-dark); border-radius: 4px 4px 0 0;"></div>
                      <div style="flex: 1; height: 20%; background: var(--mso-pink-dark); border-radius: 4px 4px 0 0;"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- API Tab -->
            <div v-if="activeTab === 'api'" class="api-tab transition-fade">
              <!-- If does not have API enabled -->
              <div v-if="!selectedDataset.api_enabled" style="padding:40px; text-align:center; background:#f8fafc; border:1px solid #e2e8f0; border-radius:16px;">
                <p style="font-weight:bold; font-size:1.1rem; color:#475569; margin:0 0 8px 0;">🔒 ข้อมูล API เฉพาะ Private API</p>
                <p style="font-size:0.875rem; color:#64748b; margin:0;">ชุดข้อมูลนี้ยังไม่เปิดบริการเรียกใช้ผ่านช่องทาง API สำหรับระดับสิทธิ์ของคุณ</p>
              </div>
              
              <!-- If has API, show details -->
              <div v-else class="api-cards" style="display: flex; flex-direction: column; gap: 1rem;">
                
                <!-- Card 1: File for API -->
                <div class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white;">
                  <h3 style="margin: 0 0 16px 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                    File for API
                  </h3>
                  <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px;">GET</div>
                  <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem;">
                    {{ selectedDataset.external_api_url || 'https://api.datax.go.th/v1/datasets/' + selectedDataset.dataset_id + '/file' }}
                  </code>
                  <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                    <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || 'https://api.datax.go.th/v1/datasets/' + selectedDataset.dataset_id + '/file' }}" \
  -H "Authorization: Bearer YOUR_API_KEY"</pre>
                  </div>
                </div>

                <!-- Card 2: Public API -->
                <div class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white;">
                  <h3 style="margin: 0 0 16px 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>
                    Public API (General)
                  </h3>
                  <div class="method-badge" style="display: inline-block; background: var(--primary, #059669); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px;">GET</div>
                  <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem;">
                    {{ selectedDataset.external_api_url || 'https://api.datax.go.th/v1/datasets/' + selectedDataset.dataset_id }}
                  </code>
                  <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                    <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X GET "{{ selectedDataset.external_api_url || 'https://api.datax.go.th/v1/datasets/' + selectedDataset.dataset_id }}" \
  -H "Authorization: Bearer YOUR_API_KEY"</pre>
                  </div>
                </div>

                <!-- Card 3: Scope API -->
                <div class="api-doc" style="background: #0f172a; padding: 24px; border-radius: 16px; color: white;">
                  <h3 style="margin: 0 0 16px 0; color: #f8fafc; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                    Scope API (Granular Access)
                  </h3>
                  <div class="method-badge" style="display: inline-block; background: #2563eb; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 12px;">POST</div>
                  <code class="endpoint" style="display: block; font-family: monospace; color: #94a3b8; margin-bottom: 16px; font-size:0.9rem;">
                    {{ selectedDataset.external_api_url || 'https://api.datax.go.th/v1/datasets/' + selectedDataset.dataset_id + '/query' }}
                  </code>
                  <div class="code-block" style="background: #1e293b; padding: 16px; border-radius: 8px; font-family: monospace;">
                    <pre style="margin: 0; color: #e2e8f0; font-size:0.85rem; overflow-x:auto;">
curl -X POST "{{ selectedDataset.external_api_url || 'https://api.datax.go.th/v1/datasets/' + selectedDataset.dataset_id + '/query' }}" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"columns":["field1","field2"], "filters":{"status":"active"}}'</pre>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px;
  text-align: center;
  gap: 16px;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f1f5f9;
  border-top-color: var(--mso-accent, var(--primary));
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.detail-layout {
  display: flex;
  background-color: #f8fafc;
  min-height: 100vh;
}

.detail-content {
  flex: 1;
  padding: 40px;
  max-width: 1200px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 24px;
}

.breadcrumb a {
  color: var(--mso-accent, var(--primary));
  text-decoration: none;
}

.separator {
  color: #cbd5e1;
}

.current {
  color: #94a3b8;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}

.agency-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.agency-logo {
  width: 32px;
  height: 32px;
  background: var(--mso-pink-dark);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--mso-accent, var(--primary));
}

.agency-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
}

h1 {
  font-size: 2.25rem;
  font-weight: 800;
  color: #1e293b;
}

.id-badge {
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 6px;
  color: #475569;
  font-size: 0.85rem;
  border: 1px solid #e2e8f0;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.meta-badge {
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 700;
}

.meta-badge.access {
  background: #ecfdf5;
  color: #065f46;
}

.meta-item {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: var(--mso-accent, var(--primary));
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.btn-outline {
  background: white;
  color: #475569;
  border: 1px solid #e2e8f0;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline.is-active, .btn-outline:hover {
  background-color: var(--mso-pink-dark);
  color: var(--mso-accent, var(--primary));
  border-color: var(--mso-accent, var(--primary));
}

.tabs-container {
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid #f1f5f9;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #f1f5f9;
  padding: 0 24px;
  background: #fafafa;
}

.tab-btn {
  padding: 20px 24px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 0.95rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  color: var(--mso-accent, var(--primary));
  border-bottom-color: var(--mso-accent, var(--primary));
}

.tab-content {
  padding: 40px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 40px;
}

.info-main h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #334155;
  margin-bottom: 16px;
}

.info-main p {
  line-height: 1.7;
  color: #64748b;
  margin-bottom: 32px;
}

.metadata-table {
  display: flex;
  flex-direction: column;
  gap: 0;
  background-color: #fff;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  overflow: hidden;
}

.row-group-title {
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--mso-accent, var(--primary));
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 20px 6px;
  background-color: var(--mso-pink-dark);
  border-bottom: 1px solid #cbd5e1;
}

.metadata-table .row {
  display: grid;
  grid-template-columns: 180px 1fr;
  border-bottom: 1px solid #f1f5f9;
}

.metadata-table .row:last-child {
  border-bottom: none;
}

.metadata-table .label {
  background-color: #f8fafc;
  padding: 10px 20px;
  font-weight: 600;
  color: #64748b;
  font-size: 0.8125rem;
  border-right: 1px solid #f1f5f9;
}

.metadata-table .value {
  padding: 10px 20px;
  color: #1e293b;
  font-size: 0.8125rem;
}

.tag-inline {
  display: inline-block;
  background-color: #f1f5f9;
  color: #475569;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  margin-right: 4px;
  margin-bottom: 4px;
}

.action-card {
  background-color: #f8fafc;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #f1f5f9;
}

.action-card h4 {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.action-card p {
  font-size: 0.8125rem;
  color: #64748b;
  margin-bottom: 20px;
}

.download-buttons {
  display: flex;
  gap: 12px;
}

.btn-download {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background-color: white;
  font-size: 0.8125rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-download:hover {
  border-color: var(--mso-accent, var(--primary));
  color: var(--mso-accent, var(--primary));
}

.btn-primary-outline {
  background: none;
  border: 1.5px solid var(--mso-accent, var(--primary));
  color: var(--mso-accent, var(--primary));
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary-outline:hover {
  background-color: var(--mso-accent, var(--primary));
  color: white;
}

.dictionary-table {
  width: 100%;
  border-collapse: collapse;
}

.dictionary-table th {
  text-align: left;
  padding: 16px;
  background-color: #f8fafc;
  color: #475569;
  font-weight: 700;
  font-size: 0.875rem;
  border-bottom: 2px solid #f1f5f9;
}

.dictionary-table td {
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
  color: #1e293b;
}

.transition-fade {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 1024px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  .detail-content {
    padding: 20px;
  }
}
</style>
