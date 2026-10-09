<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import { postWithUser } from '../utils/api';

const isLoading = ref(true);
const stats = ref({
  total_requests: 0,
  success_count: 0,
  failed_count: 0,
  unique_ips: 0
});
const trend = ref([]);
const recentLogs = ref([]);
const systemLogs = ref([]);
const activeTab = ref('system'); // Default to 'system' (ประวัติกิจกรรมการใช้งานระบบ)

const message = ref({ text: '', type: '' });
const searchQuery = ref('');

// Filter & Pagination State
const filterRange = ref('7d'); // 'today', '7d', '30d', '2y', 'custom'
const startDate = ref('');
const endDate = ref('');
const FETCH_LIMIT = 1000;

// Numbered Pagination
const itemsPerPage = ref(10);
const itemsPerPageOptions = [10, 20, 50, 100];
const currentSystemPage = ref(1);
const currentApiPage = ref(1);

const setRange = (range) => {
  filterRange.value = range;
  const today = new Date();
  let start = new Date();

  if (range === 'today') {
    start = today;
  } else if (range === '7d') {
    start.setDate(today.getDate() - 7);
  } else if (range === '30d') {
    start.setDate(today.getDate() - 30);
  } else if (range === '2y') {
    start.setFullYear(today.getFullYear() - 2);
  } else {
    return; // Custom range handled by Apply button
  }

  startDate.value = start.toISOString().split('T')[0];
  endDate.value = today.toISOString().split('T')[0];
  handleFilterChange();
};

const handleFilterChange = () => {
  currentSystemPage.value = 1;
  currentApiPage.value = 1;
  fetchMonitorData();
};

const fetchMonitorData = async () => {
  isLoading.value = true;
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const payload = {
      start_date: startDate.value,
      end_date: endDate.value,
      limit: FETCH_LIMIT,
      offset: 0
    };
    
    // Fetch Summary & Trend
    const statsRes = await postWithUser('/getApiMonitorStats', userData, payload);
    if (statsRes.data.status === 'success') {
      stats.value = statsRes.data.summary;
      trend.value = statsRes.data.trend || [];
    }

    // Fetch Logs
    const [apiLogsRes, sysLogsRes] = await Promise.all([
      postWithUser('/getApiMonitorLogs', userData, payload),
      postWithUser('/getSystemActivityLogs', userData, payload)
    ]);

    if (apiLogsRes.data.status === 'success') {
      recentLogs.value = apiLogsRes.data.data || [];
    }
    if (sysLogsRes.data.status === 'success') {
      systemLogs.value = sysLogsRes.data.data || [];
    }
  } catch (error) {
    console.error('Error fetching monitor data:', error);
    message.value = { text: 'ไม่สามารถโหลดข้อมูล Monitor ได้', type: 'error' };
  } finally {
    isLoading.value = false;
  }
};

const successRate = computed(() => {
  if (stats.value.total_requests === 0) return 100;
  return ((stats.value.success_count / stats.value.total_requests) * 100).toFixed(1);
});

const maxTrend = computed(() => {
  if (trend.value.length === 0) return 1;
  return Math.max(...trend.value.map(t => t.count)) || 1;
});

const parseApiDetail = (detail) => {
  if (!detail) return { result: 'Success', message: 'OK', isSuccess: true };
  try {
    if (detail.startsWith('{') && detail.endsWith('}')) {
      const obj = JSON.parse(detail);
      const isSuccess = obj.result === 'Allowed' || obj.status === 'success' || (obj.message && !obj.message.toLowerCase().includes('fail'));
      return {
        result: obj.result || (isSuccess ? 'Allowed' : 'Denied'),
        message: obj.message || obj.action || detail,
        isSuccess
      };
    }
  } catch (e) {}
  
  if (detail.includes('[200]')) return { result: '200 OK', message: detail, isSuccess: true };
  if (detail.includes('[403]') || detail.includes('[401]')) return { result: 'Unauthorized', message: detail, isSuccess: false };
  return { result: detail.includes('error') ? 'Error' : 'Info', message: detail, isSuccess: !detail.includes('error') };
};

const formatThaiTime = (utcString) => {
  if (!utcString) return '-';
  try {
    const date = new Date(utcString.replace(' ', 'T') + 'Z');
    return date.toLocaleString('th-TH', { 
      year: 'numeric', month: '2-digit', day: '2-digit', 
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      hour12: false
    }).replace(/\//g, '-');
  } catch (e) {
    return utcString;
  }
};

// Filtered Lists
const filteredSystemLogs = computed(() => {
  if (!searchQuery.value.trim()) return systemLogs.value;
  const q = searchQuery.value.trim().toLowerCase();
  return systemLogs.value.filter(l => 
    (l.username && l.username.toLowerCase().includes(q)) ||
    (l.path && l.path.toLowerCase().includes(q)) ||
    (l.type && l.type.toLowerCase().includes(q)) ||
    (l.log_detail && l.log_detail.toLowerCase().includes(q)) ||
    (l.ip && l.ip.toLowerCase().includes(q))
  );
});

const filteredApiLogs = computed(() => {
  if (!searchQuery.value.trim()) return recentLogs.value;
  const q = searchQuery.value.trim().toLowerCase();
  return recentLogs.value.filter(l => 
    (l.username && l.username.toLowerCase().includes(q)) ||
    (l.path && l.path.toLowerCase().includes(q)) ||
    (l.log_detail && l.log_detail.toLowerCase().includes(q)) ||
    (l.ip && l.ip.toLowerCase().includes(q))
  );
});

// Watch search query to reset pagination
watch(searchQuery, () => {
  currentSystemPage.value = 1;
  currentApiPage.value = 1;
});

// Pagination Computeds
const totalSystemPages = computed(() => {
  return Math.ceil(filteredSystemLogs.value.length / itemsPerPage.value) || 1;
});

const totalApiPages = computed(() => {
  return Math.ceil(filteredApiLogs.value.length / itemsPerPage.value) || 1;
});

const paginatedSystemLogs = computed(() => {
  const start = (currentSystemPage.value - 1) * itemsPerPage.value;
  return filteredSystemLogs.value.slice(start, start + itemsPerPage.value);
});

const paginatedApiLogs = computed(() => {
  const start = (currentApiPage.value - 1) * itemsPerPage.value;
  return filteredApiLogs.value.slice(start, start + itemsPerPage.value);
});

const goToSystemPage = (page) => {
  if (page < 1 || page > totalSystemPages.value) return;
  currentSystemPage.value = page;
};

const goToApiPage = (page) => {
  if (page < 1 || page > totalApiPages.value) return;
  currentApiPage.value = page;
};

const getPaginationRange = (currentPage, totalPages) => {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }
  const delta = 2;
  const range = [];
  const rangeWithDots = [];
  let l;

  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - delta && i <= currentPage + delta)) {
      range.push(i);
    }
  }

  for (let i of range) {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1);
      } else if (i - l !== 1) {
        rangeWithDots.push('...');
      }
    }
    rangeWithDots.push(i);
    l = i;
  }

  return rangeWithDots;
};

onMounted(() => {
  setRange('7d');
});
</script>

<template>
  <div class="monitor-layout">
    <AppSidebar />
    
    <main class="monitor-content scrollbar-custom">
      <header class="content-header">
        <div class="header-titles">
          <h1>Monitor & Activity Logs</h1>
          <p>ตรวจสอบประวัติกิจกรรมการใช้งานระบบ และสถิติการเรียกใช้งาน API ย้อนหลัง</p>
        </div>
        
        <div class="header-filters">
          <div class="range-presets">
            <button :class="{ active: filterRange === 'today' }" @click="setRange('today')">Today</button>
            <button :class="{ active: filterRange === '7d' }" @click="setRange('7d')">7 Days</button>
            <button :class="{ active: filterRange === '30d' }" @click="setRange('30d')">30 Days</button>
            <button :class="{ active: filterRange === '2y' }" @click="setRange('2y')">2 Years</button>
            <button :class="{ active: filterRange === 'custom' }" @click="filterRange = 'custom'">Custom</button>
          </div>
          
          <div v-if="filterRange === 'custom'" class="date-inputs transition-fade">
            <input type="date" v-model="startDate">
            <span>to</span>
            <input type="date" v-model="endDate">
            <button class="btn-apply" @click="handleFilterChange">Apply</button>
          </div>

          <button @click="fetchMonitorData" class="btn-refresh" :disabled="isLoading" title="รีเฟรชข้อมูล">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" :class="{ 'spinning': isLoading }">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </header>

      <div v-if="message.text" :class="['alert-message', message.type]">
        {{ message.text }}
      </div>

      <!-- Quick Metrics -->
      <div class="metrics-grid">
        <div class="metric-card shadow-premium">
          <div class="metric-icon-small total">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <p class="metric-label">Total API Hits</p>
            <div class="metric-main">
              <h2 class="metric-value">{{ stats.total_requests.toLocaleString() }}</h2>
            </div>
            <p class="text-xs text-muted">ในช่วงเวลาที่เลือก</p>
          </div>
        </div>

        <div class="metric-card shadow-premium">
          <div class="metric-icon-small success">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="metric-label">Success Rate</p>
            <div class="metric-main">
              <h2 class="metric-value">{{ successRate }}%</h2>
            </div>
            <div class="simple-progress mt-2">
                <div class="progress-bar" :style="{ width: successRate + '%' }"></div>
            </div>
          </div>
        </div>

        <div class="metric-card shadow-premium">
          <div class="metric-icon-small error">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <p class="metric-label">API Errors</p>
            <div class="metric-main">
              <h2 class="metric-value" :class="{ 'text-error': stats.failed_count > 0 }">{{ stats.failed_count.toLocaleString() }}</h2>
            </div>
            <p class="text-xs text-error" v-if="stats.failed_count > 0">พบข้อผิดพลาดในการเรียกใช้</p>
            <p class="text-xs text-muted" v-else>ไม่มีข้อผิดพลาด</p>
          </div>
        </div>

        <div class="metric-card shadow-premium">
          <div class="metric-icon-small user">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div>
            <p class="metric-label">Unique Consumers</p>
            <div class="metric-main">
              <h2 class="metric-value">{{ stats.unique_ips.toLocaleString() }}</h2>
            </div>
            <p class="text-xs text-muted">ไอพีที่แตกต่างกัน</p>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-row">
        <div class="card chart-card shadow-premium">
          <div class="card-header">
            <h3>Traffic Growth Trend</h3>
            <span class="text-sm text-muted">จำนวนการถูกเรียกใช้งานแบ่งตามวัน</span>
          </div>
          <div class="bar-chart-container">
            <div v-if="trend.length === 0" class="no-data">No data for this period</div>
            <div v-else class="bar-chart">
              <div v-for="t in trend" :key="t.date" class="bar-group">
                <div class="bar-outer">
                  <div class="bar-inner" :style="{ height: (t.count / maxTrend * 100) + '%' }">
                    <span class="bar-tooltip">{{ t.count }} hits</span>
                  </div>
                </div>
                <span class="bar-label">{{ t.date.split('-').slice(1).reverse().join('/') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Logs Section -->
      <div class="card table-card shadow-premium">
        <div class="card-header" style="display: flex; flex-direction: column; align-items: flex-start; gap: 16px;">
          <div class="table-toolbar">
            <div class="tabs-container">
              <button :class="['tab-button', { active: activeTab === 'system' }]" @click="activeTab = 'system'">
                📋 ประวัติกิจกรรมการใช้งานระบบ (System Activity Logs)
                <span class="tab-badge" v-if="filteredSystemLogs.length > 0">{{ filteredSystemLogs.length }}</span>
              </button>
              <button :class="['tab-button', { active: activeTab === 'api' }]" @click="activeTab = 'api'">
                ⚡ บันทึกการเรียกใช้งาน API (API Logs)
                <span class="tab-badge" v-if="filteredApiLogs.length > 0">{{ filteredApiLogs.length }}</span>
              </button>
            </div>
            
            <div class="search-input-box">
              <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="ค้นหาชื่อผู้ใช้, กิจกรรม, เมนู หรือ IP..." 
              />
              <button v-if="searchQuery" class="clear-search" @click="searchQuery = ''">✕</button>
            </div>
          </div>
        </div>

        <!-- System Activity Logs Table (Default) -->
        <div class="table-responsive" v-if="activeTab === 'system'">
          <table class="monitor-table">
            <thead>
              <tr>
                <th style="width: 60px;">ลำดับ</th>
                <th style="width: 170px;">วันเวลา (Timestamp)</th>
                <th style="width: 180px;">ผู้กระทำ (User)</th>
                <th style="width: 180px;">เมนู/โมดูล</th>
                <th style="width: 120px;">ประเภท</th>
                <th>รายละเอียดกิจกรรม</th>
                <th style="width: 130px;">IP Address</th>
                <th style="width: 100px;">อุปกรณ์</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(log, index) in paginatedSystemLogs" :key="log.log_id">
                <td class="text-center font-mono text-muted">{{ (currentSystemPage - 1) * itemsPerPage + index + 1 }}</td>
                <td class="time-cell">{{ formatThaiTime(log.create_at) }}</td>
                <td>
                  <div class="user-badge">
                    <span class="user-avatar">👤</span>
                    <span class="username-text">{{ log.username || 'System' }}</span>
                  </div>
                </td>
                <td class="path-cell"><code>{{ log.path || '-' }}</code></td>
                <td>
                  <span :class="['status-chip', log.type === 'alert' || log.type === 'error' ? 'status-error' : log.type === 'warning' ? 'status-warning' : 'status-success']">
                    {{ log.type || 'info' }}
                  </span>
                </td>
                <td class="detail-cell">{{ log.log_detail }}</td>
                <td class="ip-cell font-mono">{{ log.ip }}</td>
                <td class="device-cell">{{ log.device || '-' }}</td>
              </tr>
              <tr v-if="filteredSystemLogs.length === 0 && !isLoading">
                <td colspan="8" class="no-data-table">
                  {{ searchQuery ? 'ไม่พบข้อมูลที่ตรงกับการค้นหา' : 'ไม่พบข้อมูลประวัติการใช้งานในช่วงเวลานี้' }}
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Numbered Pagination Footer for System Logs -->
          <div class="pagination-container" v-if="filteredSystemLogs.length > 0">
            <div class="pagination-info">
              <span>แสดง {{ (currentSystemPage - 1) * itemsPerPage + 1 }} - {{ Math.min(currentSystemPage * itemsPerPage, filteredSystemLogs.length) }} จากทั้งหมด {{ filteredSystemLogs.length }} รายการ</span>
              <div class="per-page-selector">
                <label>แสดง:</label>
                <select v-model="itemsPerPage" @change="currentSystemPage = 1; currentApiPage = 1;">
                  <option v-for="opt in itemsPerPageOptions" :key="opt" :value="opt">{{ opt }} / หน้า</option>
                </select>
              </div>
            </div>

            <div class="pagination-controls" v-if="totalSystemPages > 1">
              <button 
                class="page-nav-btn" 
                :disabled="currentSystemPage === 1" 
                @click="goToSystemPage(1)"
                title="หน้าแรก"
              >
                «
              </button>
              <button 
                class="page-nav-btn" 
                :disabled="currentSystemPage === 1" 
                @click="goToSystemPage(currentSystemPage - 1)"
                title="ก่อนหน้า"
              >
                ‹
              </button>

              <template v-for="(p, idx) in getPaginationRange(currentSystemPage, totalSystemPages)" :key="idx">
                <span v-if="p === '...'" class="page-dots">...</span>
                <button 
                  v-else 
                  :class="['page-number-btn', { active: currentSystemPage === p }]"
                  @click="goToSystemPage(p)"
                >
                  {{ p }}
                </button>
              </template>

              <button 
                class="page-nav-btn" 
                :disabled="currentSystemPage === totalSystemPages" 
                @click="goToSystemPage(currentSystemPage + 1)"
                title="ถัดไป"
              >
                ›
              </button>
              <button 
                class="page-nav-btn" 
                :disabled="currentSystemPage === totalSystemPages" 
                @click="goToSystemPage(totalSystemPages)"
                title="หน้าสุดท้าย"
              >
                »
              </button>
            </div>
          </div>
        </div>

        <!-- API Logs Table -->
        <div class="table-responsive" v-if="activeTab === 'api'">
          <table class="monitor-table">
            <thead>
              <tr>
                <th style="width: 60px;">ลำดับ</th>
                <th style="width: 170px;">วันเวลา (Timestamp)</th>
                <th style="width: 160px;">ผู้เรียกใช้</th>
                <th>Endpoint Path</th>
                <th style="width: 130px;">สถานะ</th>
                <th>ผลลัพธ์ / รายละเอียด</th>
                <th style="width: 130px;">Client IP</th>
                <th style="width: 100px;">ภูมิภาค</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(log, index) in paginatedApiLogs" :key="log.log_id">
                <td class="text-center font-mono text-muted">{{ (currentApiPage - 1) * itemsPerPage + index + 1 }}</td>
                <td class="time-cell">{{ formatThaiTime(log.create_at) }}</td>
                <td>
                  <div class="user-badge">
                    <span class="user-avatar">🔑</span>
                    <span class="username-text">{{ log.username || (log.user_id ? 'User #' + log.user_id : 'API Key') }}</span>
                  </div>
                </td>
                <td class="path-cell"><code>{{ log.path }}</code></td>
                <td>
                  <span :class="['status-chip', parseApiDetail(log.log_detail).isSuccess ? 'status-success' : 'status-error']">
                    {{ parseApiDetail(log.log_detail).result }}
                  </span>
                </td>
                <td class="detail-cell">{{ parseApiDetail(log.log_detail).message }}</td>
                <td class="ip-cell font-mono">{{ log.ip }}</td>
                <td><span class="country-cell">{{ log.country === 'None' || !log.country ? 'Thailand' : log.country }}</span></td>
              </tr>
              <tr v-if="filteredApiLogs.length === 0 && !isLoading">
                <td colspan="8" class="no-data-table">
                  {{ searchQuery ? 'ไม่พบข้อมูลที่ตรงกับการค้นหา' : 'ไม่พบข้อมูลการเรียกใช้งานในช่วงเวลานี้' }}
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Numbered Pagination Footer for API Logs -->
          <div class="pagination-container" v-if="filteredApiLogs.length > 0">
            <div class="pagination-info">
              <span>แสดง {{ (currentApiPage - 1) * itemsPerPage + 1 }} - {{ Math.min(currentApiPage * itemsPerPage, filteredApiLogs.length) }} จากทั้งหมด {{ filteredApiLogs.length }} รายการ</span>
              <div class="per-page-selector">
                <label>แสดง:</label>
                <select v-model="itemsPerPage" @change="currentSystemPage = 1; currentApiPage = 1;">
                  <option v-for="opt in itemsPerPageOptions" :key="opt" :value="opt">{{ opt }} / หน้า</option>
                </select>
              </div>
            </div>

            <div class="pagination-controls" v-if="totalApiPages > 1">
              <button 
                class="page-nav-btn" 
                :disabled="currentApiPage === 1" 
                @click="goToApiPage(1)"
                title="หน้าแรก"
              >
                «
              </button>
              <button 
                class="page-nav-btn" 
                :disabled="currentApiPage === 1" 
                @click="goToApiPage(currentApiPage - 1)"
                title="ก่อนหน้า"
              >
                ‹
              </button>

              <template v-for="(p, idx) in getPaginationRange(currentApiPage, totalApiPages)" :key="idx">
                <span v-if="p === '...'" class="page-dots">...</span>
                <button 
                  v-else 
                  :class="['page-number-btn', { active: currentApiPage === p }]"
                  @click="goToApiPage(p)"
                >
                  {{ p }}
                </button>
              </template>

              <button 
                class="page-nav-btn" 
                :disabled="currentApiPage === totalApiPages" 
                @click="goToApiPage(currentApiPage + 1)"
                title="ถัดไป"
              >
                ›
              </button>
              <button 
                class="page-nav-btn" 
                :disabled="currentApiPage === totalApiPages" 
                @click="goToApiPage(totalApiPages)"
                title="หน้าสุดท้าย"
              >
                »
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.monitor-layout { display: flex; background-color: #f1f5f9; min-height: 100vh; width: 100%; box-sizing: border-box; }
.monitor-content { flex: 1; padding: 32px 40px; max-width: 1440px; margin: 0 auto; width: 100%; box-sizing: border-box; min-width: 0; }

.content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; gap: 20px; flex-wrap: wrap; }
.header-titles h1 { font-size: 1.875rem; font-weight: 800; color: #0f172a; margin-bottom: 4px; letter-spacing: -0.025em; }
.header-titles p { color: #64748b; font-size: 0.9375rem; }

.header-filters { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }

.range-presets { display: flex; background: white; padding: 4px; border-radius: 12px; border: 1px solid #e2e8f0; }
.range-presets button { padding: 6px 14px; border: none; background: none; border-radius: 8px; font-size: 0.8125rem; font-weight: 600; color: #64748b; cursor: pointer; transition: all 0.2s; }
.range-presets button:hover { color: #0f172a; background: #f8fafc; }
.range-presets button.active { background: #0f172a; color: white; }

.date-inputs { display: flex; align-items: center; gap: 8px; background: white; padding: 6px 12px; border-radius: 12px; border: 1px solid #e2e8f0; }
.date-inputs input { border: none; font-size: 0.8125rem; color: #0f172a; outline: none; }
.date-inputs span { color: #94a3b8; font-size: 0.75rem; font-weight: 600; }
.btn-apply { background: #0f172a; color: white; border: none; padding: 5px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; cursor: pointer; }

.btn-refresh { padding: 8px; background: white; border: 1px solid #e2e8f0; border-radius: 10px; color: #64748b; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.btn-refresh:hover { color: var(--primary); border-color: var(--primary); }

.alert-message { padding: 14px 20px; border-radius: 12px; margin-bottom: 24px; font-weight: 600; }
.alert-message.error { background: #fee2e2; color: #b91c1c; }

.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 28px; }
.metric-card { background: white; padding: 20px; border-radius: 18px; display: flex; gap: 16px; align-items: flex-start; border: 1px solid #e2e8f0; }
.shadow-premium { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); }

.metric-icon-small { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.metric-icon-small svg { width: 22px; height: 22px; }
.metric-icon-small.total { background: #eff6ff; color: #3b82f6; }
.metric-icon-small.success { background: #dcfce7; color: #15803d; }
.metric-icon-small.error { background: #fef2f2; color: #ef4444; }
.metric-icon-small.user { background: #faf5ff; color: #a855f7; }

.metric-label { font-size: 0.8125rem; font-weight: 600; color: #64748b; margin-bottom: 4px; }
.metric-value { font-size: 1.5rem; font-weight: 800; color: #0f172a; margin: 0; }
.text-error { color: #ef4444; }

.simple-progress { width: 100%; height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.progress-bar { height: 100%; background: var(--primary); border-radius: 3px; }

.charts-row { margin-bottom: 28px; }
.card { background: white; border-radius: 20px; padding: 24px 28px; border: 1px solid #e2e8f0; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.card h3 { font-size: 1.125rem; font-weight: 800; color: #0f172a; margin: 0; }

.bar-chart-container { height: 220px; display: flex; align-items: flex-end; padding-top: 16px; overflow-x: auto; }
.bar-chart { display: flex; width: 100%; height: 100%; gap: 8px; align-items: flex-end; min-width: 600px; }
.bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 10px; height: 100%; justify-content: flex-end; min-width: 0; }
.bar-outer { width: 100%; max-width: 40px; height: 160px; background: #f8fafc; border-radius: 6px; display: flex; align-items: flex-end; position: relative; }
.bar-inner { width: 100%; background: linear-gradient(180deg, #6ee7b7 0%, var(--primary) 100%); border-radius: 6px; transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1); position: relative; }
.bar-inner:hover { filter: brightness(1.1); }
.bar-tooltip { position: absolute; top: -34px; left: 50%; transform: translateX(-50%); background: #0f172a; color: white; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; opacity: 0; pointer-events: none; transition: opacity 0.2s; white-space: nowrap; z-index: 10; }
.bar-inner:hover .bar-tooltip { opacity: 1; }
.bar-label { font-size: 0.6875rem; color: #94a3b8; font-weight: 700; }

.table-toolbar { display: flex; justify-content: space-between; align-items: center; width: 100%; gap: 16px; flex-wrap: wrap; }
.tabs-container { display: flex; gap: 6px; background: #f1f5f9; padding: 4px; border-radius: 12px; flex-wrap: wrap; }
.tab-button { padding: 8px 16px; border: none; background: transparent; border-radius: 8px; font-weight: 700; font-size: 0.875rem; color: #64748b; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }
.tab-button:hover { color: #0f172a; }
.tab-button.active { background: white; color: #0f172a; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }
.tab-badge { background: #e2e8f0; color: #475569; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 700; }
.tab-button.active .tab-badge { background: var(--primary); color: white; }

.search-input-box { position: relative; display: flex; align-items: center; min-width: 280px; }
.search-icon { position: absolute; left: 12px; width: 16px; height: 16px; color: #94a3b8; pointer-events: none; }
.search-input-box input { width: 100%; padding: 8px 32px 8px 36px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 0.875rem; background: #f8fafc; outline: none; transition: all 0.2s; }
.search-input-box input:focus { background: white; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.12); }
.clear-search { position: absolute; right: 10px; background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 0.8rem; padding: 2px 6px; }

.monitor-table { width: 100%; border-collapse: collapse; min-width: 850px; }
.table-responsive { overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 12px; }
.monitor-table th { text-align: left; padding: 14px 16px; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; background-color: #f8fafc; border-bottom: 2px solid #e2e8f0; letter-spacing: 0.05em; }
.monitor-table td { padding: 14px 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.875rem; color: #334155; vertical-align: middle; }
.time-cell { font-family: 'JetBrains Mono', monospace; font-size: 0.8125rem; color: #64748b; white-space: nowrap; }
.path-cell code { background: #f1f5f9; padding: 4px 8px; border-radius: 6px; font-size: 0.8125rem; color: #0f172a; font-weight: 600; }
.user-badge { display: inline-flex; align-items: center; gap: 6px; font-weight: 600; color: #0f172a; }
.user-avatar { font-size: 0.9rem; }
.username-text { font-size: 0.875rem; }
.status-chip { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: capitalize; }
.status-success { background: #dcfce7; color: #15803d; }
.status-warning { background: #fffbeb; color: #d97706; }
.status-error { background: #fee2e2; color: #b91c1c; }
.detail-cell { max-width: 320px; word-break: break-word; font-size: 0.85rem; color: #475569; }
.ip-cell { font-size: 0.8125rem; color: #64748b; }
.country-cell { font-weight: 600; color: #0f172a; font-size: 0.8125rem; }
.device-cell { font-size: 0.78rem; color: #64748b; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Numbered Pagination Styles */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 8px 8px;
  margin-top: 16px;
  border-top: 1px solid #f1f5f9;
  flex-wrap: wrap;
  gap: 16px;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 0.875rem;
  color: #64748b;
  flex-wrap: wrap;
}

.per-page-selector {
  display: flex;
  align-items: center;
  gap: 6px;
}

.per-page-selector select {
  padding: 4px 8px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background-color: white;
  font-size: 0.8125rem;
  color: #334155;
  outline: none;
  cursor: pointer;
}

.per-page-selector select:focus {
  border-color: var(--primary);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-nav-btn, .page-number-btn {
  min-width: 34px;
  height: 34px;
  padding: 0 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #334155;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.page-nav-btn:hover:not(:disabled), .page-number-btn:hover:not(.active) {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #0f172a;
}

.page-nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  border-color: #f1f5f9;
}

.page-number-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.page-dots {
  padding: 0 6px;
  color: #94a3b8;
  font-weight: bold;
}

.spinning { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.no-data-table { text-align: center; padding: 48px !important; color: #94a3b8; font-style: italic; }

@media (max-width: 1023px) {
  .monitor-content { padding: 24px; max-width: 100%; }
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .content-header { flex-direction: column; align-items: flex-start; }
}

@media (max-width: 767px) {
  .monitor-content { padding: 16px; margin-bottom: 60px; }
  .metrics-grid { grid-template-columns: 1fr; }
  .header-filters { flex-direction: column; width: 100%; align-items: stretch; }
  .table-toolbar { flex-direction: column; align-items: stretch; }
  .search-input-box { width: 100%; min-width: 0; }
  .pagination-container { flex-direction: column; align-items: stretch; }
  .pagination-controls { justify-content: center; }
}
</style>
