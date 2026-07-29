<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { postWithUser } from '../utils/api';

const isLoading = ref(true);
const isLogsLoading = ref(false);
const stats = ref({
  total_requests: 0,
  success_count: 0,
  failed_count: 0,
  unique_ips: 0
});
const trend = ref([]);
const recentLogs = ref([]);
const message = ref({ text: '', type: '' });

// Filter & Pagination State
const filterRange = ref('7d'); // 'today', '7d', '30d', 'custom'
const startDate = ref('');
const endDate = ref('');
const logsOffset = ref(0);
const hasMoreLogs = ref(true);
const PAGE_SIZE = 50;

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
    return; // Custom range handled by watchers
  }

  startDate.value = start.toISOString().split('T')[0];
  endDate.value = today.toISOString().split('T')[0];
  handleFilterChange();
};

const handleFilterChange = () => {
  logsOffset.value = 0;
  recentLogs.value = [];
  hasMoreLogs.value = true;
  fetchMonitorData();
};

const fetchMonitorData = async () => {
    isLoading.value = true;
    try {
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        const payload = {
            start_date: startDate.value,
            end_date: endDate.value
        };
        
        // Fetch Summary & Trend
        const statsRes = await postWithUser('/getApiMonitorStats', userData, payload);
        if (statsRes.data.status === 'success') {
            stats.value = statsRes.data.summary;
            trend.value = statsRes.data.trend;
        }

        // Fetch initial Logs
        await fetchMoreLogs(true);
    } catch (error) {
        console.error('Error fetching monitor data:', error);
        message.value = { text: 'ไม่สามารถโหลดข้อมูล Monitor ได้', type: 'error' };
    } finally {
        isLoading.value = false;
    }
};

const fetchMoreLogs = async (reset = false) => {
    if (isLogsLoading.value) return;
    isLogsLoading.value = true;
    try {
        const userData = JSON.parse(localStorage.getItem('user') || '{}');
        const payload = {
            start_date: startDate.value,
            end_date: endDate.value,
            limit: PAGE_SIZE,
            offset: logsOffset.value
        };

        const logsRes = await postWithUser('/getApiMonitorLogs', userData, payload);
        if (logsRes.data.status === 'success') {
            const newLogs = logsRes.data.data;
            if (reset) {
                recentLogs.value = newLogs;
            } else {
                recentLogs.value = [...recentLogs.value, ...newLogs];
            }
            
            if (newLogs.length < PAGE_SIZE) {
                hasMoreLogs.value = false;
            } else {
                logsOffset.value += PAGE_SIZE;
            }
        }
    } catch (error) {
        console.error('Error fetching logs:', error);
    } finally {
        isLogsLoading.value = false;
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

const getStatusClass = (detail) => {
  if (detail.includes('[200]')) return 'status-success';
  if (detail.includes('[403]') || detail.includes('[401]')) return 'status-warning';
  return 'status-error';
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
          <h1>API Monitor</h1>
          <p>ตรวจสอบสถิติและการเรียกใช้งาน API ย้อนหลังได้สูงสุด 2 ปี</p>
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

          <button @click="fetchMonitorData" class="btn-refresh" :disabled="isLoading">
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

      <!-- Real-time / Historical Logs -->
      <div class="card table-card shadow-premium">
        <div class="card-header">
          <h3>Detailed Activity Logs</h3>
          <div class="header-actions">
            <span v-if="filterRange === 'today'" class="live-indicator">
              <span class="pulse"></span> LIVE
            </span>
            <span v-else class="text-muted text-xs">Viewing Historical Data</span>
          </div>
        </div>
        
        <div class="table-responsive">
          <table class="monitor-table">
            <thead>
              <tr>
                <th>Timestamp (Local)</th>
                <th>Result Detail</th>
                <th>Endpoint Path</th>
                <th>Client IP</th>
                <th>Region</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in recentLogs" :key="log.log_id">
                <td class="time-cell">{{ formatThaiTime(log.create_at) }}</td>
                <td>
                  <span :class="['status-chip', getStatusClass(log.log_detail)]">
                    {{ log.log_detail }}
                  </span>
                </td>
                <td class="path-cell"><code>{{ log.path }}</code></td>
                <td>{{ log.ip }}</td>
                <td><span class="country-cell">{{ log.country === 'None' ? 'Thailand' : log.country }}</span></td>
              </tr>
              <tr v-if="recentLogs.length === 0 && !isLoading && !isLogsLoading">
                <td colspan="5" class="no-data-table">
                  ไม่พบข้อมูลการเรียกใช้งานในช่วงเวลานี้
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-if="hasMoreLogs" class="load-more">
            <button @click="fetchMoreLogs(false)" :disabled="isLogsLoading" class="btn-load-more">
              <span v-if="isLogsLoading" class="spinner-small"></span>
              {{ isLogsLoading ? 'Loading Logs...' : 'Show More Logs' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.monitor-layout { display: flex; background-color: #f1f5f9; min-height: 100vh; }
.monitor-content { flex: 1; padding: 40px; max-width: 1400px; margin: 0 auto; overflow-y: auto; height: 100vh; }

.content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; gap: 20px; }
.header-titles h1 { font-size: 1.875rem; font-weight: 800; color: #0f172a; margin-bottom: 4px; letter-spacing: -0.025em; }
.header-titles p { color: #64748b; font-size: 0.9375rem; }

.header-filters { display: flex; align-items: center; gap: 16px; }

.range-presets { display: flex; background: white; padding: 4px; border-radius: 12px; border: 1px solid #e2e8f0; }
.range-presets button { padding: 6px 14px; border: none; background: none; border-radius: 8px; font-size: 0.8125rem; font-weight: 600; color: #64748b; cursor: pointer; transition: all 0.2s; }
.range-presets button:hover { color: #0f172a; background: #f8fafc; }
.range-presets button.active { background: #0f172a; color: white; }

.date-inputs { display: flex; align-items: center; gap: 8px; background: white; padding: 6px 12px; border-radius: 12px; border: 1px solid #e2e8f0; }
.date-inputs input { border: none; font-size: 0.8125rem; color: #0f172a; outline: none; }
.date-inputs span { color: #94a3b8; font-size: 0.75rem; font-weight: 600; }
.btn-apply { background: #0f172a; color: white; border: none; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; cursor: pointer; }

.btn-refresh { padding: 8px; background: white; border: 1px solid #e2e8f0; border-radius: 10px; color: #64748b; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.btn-refresh:hover { color: var(--mso-accent); border-color: var(--mso-accent); }

.alert-message { padding: 14px 20px; border-radius: 12px; margin-bottom: 24px; font-weight: 600; }
.alert-message.error { background: #fee2e2; color: #b91c1c; }

.metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 32px; }
.metric-card { background: white; padding: 24px; border-radius: 20px; display: flex; gap: 16px; align-items: flex-start; }
.shadow-premium { box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); }

.metric-icon-small { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.metric-icon-small svg { width: 22px; height: 22px; }
.metric-icon-small.total { background: #eff6ff; color: #3b82f6; }
.metric-icon-small.success { background: var(--mso-pink-dark); color: var(--mso-accent); }
.metric-icon-small.error { background: #fef2f2; color: #ef4444; }
.metric-icon-small.user { background: #faf5ff; color: #a855f7; }

.metric-label { font-size: 0.8125rem; font-weight: 600; color: #64748b; margin-bottom: 6px; }
.metric-value { font-size: 1.5rem; font-weight: 800; color: #0f172a; margin: 0; }

.simple-progress { width: 100%; height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.progress-bar { height: 100%; background: var(--mso-accent); border-radius: 3px; }

.charts-row { margin-bottom: 32px; }
.card { background: white; border-radius: 24px; padding: 32px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.card h3 { font-size: 1.125rem; font-weight: 800; color: #0f172a; }

.bar-chart-container { height: 240px; display: flex; align-items: flex-end; padding-top: 20px; }
.bar-chart { display: flex; width: 100%; height: 100%; gap: 8px; align-items: flex-end; }
.bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 12px; height: 100%; justify-content: flex-end; min-width: 0; }
.bar-outer { width: 100%; max-width: 40px; height: 180px; background: #f8fafc; border-radius: 6px; display: flex; align-items: flex-end; position: relative; }
.bar-inner { width: 100%; background: linear-gradient(180deg, #f472b6 0%, var(--mso-accent) 100%); border-radius: 6px; transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1); position: relative; }
.bar-inner:hover { filter: brightness(1.1); }
.bar-tooltip { position: absolute; top: -34px; left: 50%; transform: translateX(-50%); background: #0f172a; color: white; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; opacity: 0; pointer-events: none; transition: opacity 0.2s; white-space: nowrap; z-index: 10; }
.bar-inner:hover .bar-tooltip { opacity: 1; }
.bar-label { font-size: 0.6875rem; color: #94a3b8; font-weight: 700; }

.live-indicator { display: flex; align-items: center; gap: 8px; font-size: 0.75rem; font-weight: 800; color: #ef4444; background: #fef2f2; padding: 4px 10px; border-radius: 20px; }
.pulse { width: 8px; height: 8px; background: #ef4444; border-radius: 50%; animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); } 70% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); } 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); } }

.monitor-table { width: 100%; border-collapse: collapse; }
.monitor-table th { text-align: left; padding: 16px; font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; border-bottom: 2px solid #f1f5f9; letter-spacing: 0.05em; }
.monitor-table td { padding: 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.875rem; color: #475569; }
.time-cell { font-family: 'JetBrains Mono', monospace; font-size: 0.8125rem; color: #64748b; }
.path-cell code { background: #f1f5f9; padding: 4px 8px; border-radius: 6px; font-size: 0.8125rem; color: #0f172a; font-weight: 500; }
.status-chip { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.status-success { background: var(--mso-pink-dark); color: var(--primary); }
.status-warning { background: #fffbeb; color: #d97706; }
.status-error { background: #fef2f2; color: #ef4444; }
.country-cell { font-weight: 600; color: #0f172a; }

.load-more { padding: 32px; text-align: center; }
.btn-load-more { background: white; border: 1.5px solid #e2e8f0; padding: 10px 24px; border-radius: 12px; color: #0f172a; font-weight: 600; font-size: 0.875rem; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }
.btn-load-more:hover:not(:disabled) { border-color: #0f172a; background: #f8fafc; }
.btn-load-more:disabled { opacity: 0.5; cursor: not-allowed; }

.spinning { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.spinner-small { width: 16px; height: 16px; border: 2px solid #e2e8f0; border-top-color: #0f172a; border-radius: 50%; animation: spin 1s linear infinite; }

.transition-fade { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

.scrollbar-custom::-webkit-scrollbar { width: 6px; }
.scrollbar-custom::-webkit-scrollbar-track { background: transparent; }
.scrollbar-custom::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }

.no-data-table { text-align: center; padding: 60px !important; color: #94a3b8; font-style: italic; }
</style>
