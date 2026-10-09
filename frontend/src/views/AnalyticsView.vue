<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import { postWithUser } from '../utils/api';

const isLoading = ref(true);
const selectedPeriod = ref('30d');
const periods = [
  { key: 'today', label: 'วันนี้ (Today)' },
  { key: '7d', label: '7 วันล่าสุด (7 Days)' },
  { key: '30d', label: '30 วันล่าสุด (30 Days)' },
  { key: '1y', label: '1 ปีล่าสุด (1 Year)' },
  { key: 'all', label: 'ทั้งหมด (All Time)' },
  { key: 'custom', label: 'กำหนดเอง (Custom)' }
];

const customStartDate = ref('');
const customEndDate = ref('');

const metrics = ref([]);
const consumptionTimeline = ref([]);
const categoryDistribution = ref([]);
const orgDistribution = ref([]);
const topDatasets = ref([]);
const activeDistributionTab = ref('category'); // 'category' | 'org'

// Search & Pagination for Datasets Table
const searchQuery = ref('');
const itemsPerPage = ref(10);
const itemsPerPageOptions = [10, 20, 50];
const currentPage = ref(1);

// Hovered Timeline Bar for Tooltip
const hoveredBar = ref(null);

const fetchAnalytics = async () => {
  isLoading.value = true;
  try {
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    const payload = {
      period: selectedPeriod.value,
      start_date: customStartDate.value,
      end_date: customEndDate.value
    };

    const response = await postWithUser('/api/analytics/usage', userData, payload);
    if (response.data && response.data.status === 'success') {
      metrics.value = response.data.metrics || [];
      consumptionTimeline.value = response.data.consumption_timeline || [];
      categoryDistribution.value = response.data.category_distribution || [];
      orgDistribution.value = response.data.org_distribution || [];
      topDatasets.value = response.data.topDatasets || [];
    }
  } catch (e) {
    console.error('Failed to fetch analytics', e);
  } finally {
    isLoading.value = false;
  }
};

const setPeriod = (pKey) => {
  selectedPeriod.value = pKey;
  if (pKey !== 'custom') {
    fetchAnalytics();
  }
};

const applyCustomDate = () => {
  if (!customStartDate.value || !customEndDate.value) {
    alert('โปรดเลือกวันที่เริ่มต้นและวันที่สิ้นสุด');
    return;
  }
  fetchAnalytics();
};

// Max value for Timeline chart height scaling
const maxTimelineValue = computed(() => {
  if (consumptionTimeline.value.length === 0) return 10;
  const max = Math.max(...consumptionTimeline.value.map(t => t.total || (t.api_calls + t.downloads)));
  return max > 0 ? max : 10;
});

// Sparkline SVG generators
const generateSparkline = (points) => {
  if (!points || points.length === 0) return 'M0,15 L100,15';
  if (points.length === 1) return `M0,15 L100,15`;
  const max = Math.max(...points);
  const min = Math.min(...points);
  const range = (max - min) || 1;
  const step = 100 / (points.length - 1);
  
  return points.map((val, idx) => {
    const x = (idx * step).toFixed(1);
    const y = (26 - ((val - min) / range) * 22).toFixed(1);
    return `${idx === 0 ? 'M' : 'L'}${x},${y}`;
  }).join(' ');
};

const generateSparklineArea = (points) => {
  if (!points || points.length === 0) return '';
  const linePath = generateSparkline(points);
  return `${linePath} L100,30 L0,30 Z`;
};

// Donut Chart Computeds
const currentDistributionList = computed(() => {
  return activeDistributionTab.value === 'category' 
    ? categoryDistribution.value 
    : orgDistribution.value;
});

const totalDistributionDatasets = computed(() => {
  return currentDistributionList.value.reduce((acc, cur) => acc + (cur.count || cur.datasets_count || 0), 0);
});

const totalDistributionCalls = computed(() => {
  return currentDistributionList.value.reduce((acc, cur) => acc + (cur.calls || cur.calls_count || 0), 0);
});

// Calculate SVG Donut Slices
const donutSlices = computed(() => {
  const list = currentDistributionList.value;
  if (!list || list.length === 0) return [];
  
  const circumference = 2 * Math.PI * 40; // r=40 -> ~251.327
  let cumulativePercent = 0;
  
  return list.map(item => {
    const pct = item.percentage || 0;
    const strokeDash = (pct / 100) * circumference;
    const offset = -((cumulativePercent / 100) * circumference);
    cumulativePercent += pct;
    
    return {
      name: item.name,
      count: item.count || item.datasets_count || 0,
      calls: item.calls || item.calls_count || 0,
      percentage: pct,
      color: item.color || '#10b981',
      strokeDasharray: `${strokeDash} ${circumference}`,
      strokeDashoffset: offset
    };
  });
});

// Top Datasets Filtering & Pagination
const filteredDatasets = computed(() => {
  if (!searchQuery.value.trim()) return topDatasets.value;
  const q = searchQuery.value.trim().toLowerCase();
  return topDatasets.value.filter(d => 
    (d.name && d.name.toLowerCase().includes(q)) ||
    (d.dataset_id && d.dataset_id.toLowerCase().includes(q)) ||
    (d.organization && d.organization.toLowerCase().includes(q)) ||
    (d.category && d.category.toLowerCase().includes(q))
  );
});

const totalPages = computed(() => {
  return Math.ceil(filteredDatasets.value.length / itemsPerPage.value) || 1;
});

const paginatedDatasets = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return filteredDatasets.value.slice(start, start + itemsPerPage.value);
});

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
};

const getPaginationRange = (curr, total) => {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const delta = 2;
  const range = [];
  const rangeWithDots = [];
  let l;

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= curr - delta && i <= curr + delta)) {
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

watch(searchQuery, () => {
  currentPage.value = 1;
});

const formatThaiDateTime = (str) => {
  if (!str || str === '-') return '-';
  try {
    const d = new Date(str.replace(' ', 'T') + 'Z');
    return d.toLocaleString('th-TH', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  } catch (e) {
    return str;
  }
};

onMounted(() => {
  // Set default custom date bounds
  const now = new Date();
  const past30 = new Date();
  past30.setDate(now.getDate() - 30);
  customStartDate.value = past30.toISOString().split('T')[0];
  customEndDate.value = now.toISOString().split('T')[0];
  
  fetchAnalytics();
});
</script>

<template>
  <div class="analytics-layout">
    <AppSidebar />
    
    <main class="analytics-content scrollbar-custom">
      <!-- Content Header -->
      <header class="content-header">
        <div class="header-titles">
          <div class="title-badge">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 20V10M12 20V4M6 20v-6" />
            </svg>
            <span>LIVE DATA METRICS</span>
          </div>
          <h1>การวิเคราะห์การใช้งานระบบ (Usage Analytics)</h1>
          <p>ติดตามสถิติการใช้งานข้อมูล ปริมาณการเรียกใช้ API และพฤติกรรมการเข้าถึงตามข้อมูลจริงในระบบ</p>
        </div>
        
        <div class="header-controls">
          <div class="period-selector">
            <button 
              v-for="p in periods" 
              :key="p.key"
              :class="['period-btn', { active: selectedPeriod === p.key }]"
              @click="setPeriod(p.key)"
            >
              {{ p.label }}
            </button>
          </div>

          <button class="btn-refresh" @click="fetchAnalytics" :disabled="isLoading" title="รีเฟรชข้อมูล">
            <svg :class="['refresh-icon', { spinning: isLoading }]" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </header>

      <!-- Custom Date Filter Range (if selected) -->
      <div v-if="selectedPeriod === 'custom'" class="custom-date-bar transition-fade">
        <div class="custom-date-inputs">
          <div class="date-field">
            <label>ตั้งแต่วันที่:</label>
            <input type="date" v-model="customStartDate" />
          </div>
          <span class="date-sep">ถึง</span>
          <div class="date-field">
            <label>ถึงวันที่:</label>
            <input type="date" v-model="customEndDate" />
          </div>
          <button class="btn-apply-custom" @click="applyCustomDate">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 13l4 4L19 7" />
            </svg>
            กรองข้อมูล (Apply)
          </button>
        </div>
      </div>
      
      <!-- Key KPI Metrics Grid -->
      <div class="metrics-grid">
        <div v-for="metric in metrics" :key="metric.id" class="metric-card">
          <div class="metric-card-header">
            <div>
              <p class="metric-label">{{ metric.label }}</p>
              <p class="metric-sublabel">{{ metric.label_th }}</p>
            </div>
            <div :class="['growth-tag', metric.positive ? 'positive' : 'negative']">
              {{ metric.growth }}
            </div>
          </div>

          <div class="metric-main">
            <h2 class="metric-value">{{ metric.value }}</h2>
          </div>

          <div class="metric-chart">
            <svg viewBox="0 0 100 30" class="sparkline" preserveAspectRatio="none">
              <defs>
                <linearGradient :id="'grad-' + metric.id" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" :stop-color="metric.positive ? '#10b981' : '#ef4444'" stop-opacity="0.3" />
                  <stop offset="100%" :stop-color="metric.positive ? '#10b981' : '#ef4444'" stop-opacity="0.0" />
                </linearGradient>
              </defs>
              <path 
                :d="generateSparklineArea(metric.sparkline)" 
                :fill="'url(#grad-' + metric.id + ')'"
              />
              <path 
                :d="generateSparkline(metric.sparkline)" 
                fill="none" 
                :stroke="metric.positive ? '#10b981' : '#ef4444'" 
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>
        </div>
      </div>
      
      <!-- Charts Section: Consumption Volume + Data by Category -->
      <div class="charts-grid">
        <!-- Main Consumption Timeline Chart -->
        <div class="card chart-card main-chart">
          <div class="card-header">
            <div>
              <h3>ปริมาณการใช้งานตามช่วงเวลา (Consumption Volume over Time)</h3>
              <p class="card-desc">สถิติจำนวนครั้งการเรียกใช้ API และการดาวน์โหลดข้อมูลในระบบ</p>
            </div>
            <div class="chart-legend">
              <span class="legend-item"><span class="dot api"></span> เรียกใช้ API (API Calls)</span>
              <span class="legend-item"><span class="dot dl"></span> ดาวน์โหลดไฟล์ (Downloads)</span>
            </div>
          </div>

          <div class="timeline-chart-wrapper scrollbar-custom">
            <div v-if="consumptionTimeline.length === 0" class="chart-empty">
              <span>ไม่มีข้อมูลการใช้งานในช่วงเวลานี้</span>
            </div>

            <div v-else class="bar-chart">
              <div 
                v-for="(item, idx) in consumptionTimeline" 
                :key="idx" 
                class="bar-group"
                @mouseenter="hoveredBar = item"
                @mouseleave="hoveredBar = null"
              >
                <!-- Tooltip on Hover -->
                <div v-if="hoveredBar === item" class="bar-tooltip transition-fade">
                  <div class="tooltip-date">{{ item.date || item.label }}</div>
                  <div class="tooltip-row">
                    <span class="dot api"></span>
                    <span>API: {{ item.api_calls.toLocaleString() }} ครั้ง</span>
                  </div>
                  <div class="tooltip-row" v-if="item.downloads > 0">
                    <span class="dot dl"></span>
                    <span>Download: {{ item.downloads.toLocaleString() }} ครั้ง</span>
                  </div>
                  <div class="tooltip-total">รวม: {{ item.total.toLocaleString() }} รายการ</div>
                </div>

                <!-- Visual Bar with Proportional Segments -->
                <div class="full-bar">
                  <div 
                    class="bar-segment dl" 
                    :style="{ height: ((item.downloads / maxTimelineValue) * 100) + '%' }"
                    :title="`Downloads: ${item.downloads}`"
                  ></div>
                  <div 
                    class="bar-segment api" 
                    :style="{ height: ((item.api_calls / maxTimelineValue) * 100) + '%' }"
                    :title="`API Calls: ${item.api_calls}`"
                  ></div>
                </div>
                <span class="bar-label">{{ item.label }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Distribution Donut Chart Area -->
        <div class="card chart-card pie-chart-area">
          <div class="card-header-compact">
            <div>
              <h3>สัดส่วนชุดข้อมูล (Data Distribution)</h3>
              <p class="card-desc">จำแนกตามหมวดหมู่และหน่วยงาน</p>
            </div>
            
            <div class="dist-toggle">
              <button 
                :class="{ active: activeDistributionTab === 'category' }" 
                @click="activeDistributionTab = 'category'"
              >
                หมวดหมู่
              </button>
              <button 
                :class="{ active: activeDistributionTab === 'org' }" 
                @click="activeDistributionTab = 'org'"
              >
                หน่วยงาน
              </button>
            </div>
          </div>

          <div class="pie-container">
            <!-- Dynamic SVG Donut Chart -->
            <div class="svg-donut-wrapper">
              <svg viewBox="0 0 100 100" class="donut-svg">
                <!-- Base Circle -->
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#f1f5f9" stroke-width="16" />
                
                <!-- Dynamic Slices -->
                <circle 
                  v-for="(slice, sIdx) in donutSlices" 
                  :key="sIdx"
                  cx="50" 
                  cy="50" 
                  r="40" 
                  fill="transparent" 
                  :stroke="slice.color" 
                  stroke-width="16" 
                  :stroke-dasharray="slice.strokeDasharray" 
                  :stroke-dashoffset="slice.strokeDashoffset" 
                  stroke-linecap="butt"
                  transform="rotate(-90 50 50)"
                  class="donut-segment"
                />
              </svg>
              <div class="donut-center-info">
                <span class="donut-total">{{ totalDistributionDatasets }}</span>
                <span class="donut-label">ชุดข้อมูล</span>
              </div>
            </div>

            <!-- Distribution Legend List -->
            <div class="dist-legend-list scrollbar-custom">
              <div 
                v-for="(slice, sIdx) in donutSlices" 
                :key="sIdx" 
                class="dist-legend-item"
              >
                <div class="dist-item-left">
                  <span class="dist-dot" :style="{ backgroundColor: slice.color }"></span>
                  <div class="dist-item-names">
                    <span class="dist-name" :title="slice.name">{{ slice.name }}</span>
                    <span class="dist-count">{{ slice.count }} ชุดข้อมูล ({{ slice.calls.toLocaleString() }} Calls)</span>
                  </div>
                </div>
                <div class="dist-item-right">
                  <span class="dist-pct">{{ slice.percentage }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Most Popular Datasets Table -->
      <div class="card table-card">
        <div class="table-header">
          <div>
            <h3>ชุดข้อมูลที่มีการเรียกใช้งานสูงสุด (Most Popular Datasets)</h3>
            <p class="card-desc">จัดอันดับชุดข้อมูลและ API ที่ได้รับการร้องขอเข้าถึงข้อมูลจริงในระบบ</p>
          </div>

          <div class="table-actions">
            <div class="search-box">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="ค้นหาชื่อชุดข้อมูล, รหัส หรือหน่วยงาน..." 
              />
            </div>
          </div>
        </div>

        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width: 50px;" class="text-center">#</th>
                <th>ชื่อชุดข้อมูล (Dataset Name)</th>
                <th>หน่วยงาน (Organization)</th>
                <th>หมวดหมู่ (Category)</th>
                <th class="text-right">จำนวนเรียกใช้ (Calls)</th>
                <th style="width: 140px;">สัดส่วนการใช้งาน (Intensity)</th>
                <th>เข้าถึงล่าสุด (Last Active)</th>
                <th class="text-center">สิทธิ์ (Access)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in paginatedDatasets" :key="item.service_id">
                <td class="text-center font-mono text-muted">
                  {{ (currentPage - 1) * itemsPerPage + index + 1 }}
                </td>
                <td class="name-cell">
                  <div class="dataset-title">{{ item.name }}</div>
                  <div class="dataset-code font-mono">{{ item.dataset_id }}</div>
                </td>
                <td class="org-cell">{{ item.organization }}</td>
                <td>
                  <span class="category-pill">{{ item.category }}</span>
                </td>
                <td class="text-right font-mono font-bold">{{ item.calls.toLocaleString() }}</td>
                <td>
                  <div class="progress-wrapper">
                    <div class="progress-bg">
                      <div class="progress-fill" :style="{ width: item.intensity + '%' }"></div>
                    </div>
                    <span class="progress-text">{{ item.intensity }}%</span>
                  </div>
                </td>
                <td class="time-cell font-mono">{{ formatThaiDateTime(item.last_accessed) }}</td>
                <td class="text-center">
                  <span :class="['status-badge', item.accessibility === 'Public' ? 'public' : 'restricted']">
                    {{ item.accessibility }}
                  </span>
                </td>
              </tr>
              <tr v-if="filteredDatasets.length === 0">
                <td colspan="8" class="no-data-cell">
                  {{ searchQuery ? 'ไม่พบข้อมูลที่ตรงกับคำค้นหา' : 'ไม่มีข้อมูลการเรียกใช้งานชุดข้อมูลในช่วงเวลานี้' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Numbered Pagination Footer -->
        <div class="pagination-container" v-if="filteredDatasets.length > 0">
          <div class="pagination-info">
            <span>แสดง {{ (currentPage - 1) * itemsPerPage + 1 }} - {{ Math.min(currentPage * itemsPerPage, filteredDatasets.length) }} จากทั้งหมด {{ filteredDatasets.length }} รายการ</span>
            <div class="per-page-selector">
              <label>แสดง:</label>
              <select v-model="itemsPerPage" @change="currentPage = 1">
                <option v-for="opt in itemsPerPageOptions" :key="opt" :value="opt">{{ opt }} / หน้า</option>
              </select>
            </div>
          </div>

          <div class="pagination-controls" v-if="totalPages > 1">
            <button 
              class="page-nav-btn" 
              :disabled="currentPage === 1" 
              @click="goToPage(1)"
              title="หน้าแรก"
            >
              «
            </button>
            <button 
              class="page-nav-btn" 
              :disabled="currentPage === 1" 
              @click="goToPage(currentPage - 1)"
              title="ก่อนหน้า"
            >
              ‹
            </button>

            <template v-for="(p, idx) in getPaginationRange(currentPage, totalPages)" :key="idx">
              <span v-if="p === '...'" class="page-dots">...</span>
              <button 
                v-else 
                :class="['page-number-btn', { active: currentPage === p }]"
                @click="goToPage(p)"
              >
                {{ p }}
              </button>
            </template>

            <button 
              class="page-nav-btn" 
              :disabled="currentPage === totalPages" 
              @click="goToPage(currentPage + 1)"
              title="ถัดไป"
            >
              ›
            </button>
            <button 
              class="page-nav-btn" 
              :disabled="currentPage === totalPages" 
              @click="goToPage(totalPages)"
              title="หน้าสุดท้าย"
            >
              »
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.analytics-layout {
  display: flex;
  background-color: #f8fafc;
  min-height: 100%;
  font-family: 'Prompt', sans-serif;
}

.analytics-content {
  flex: 1;
  padding: 32px 40px;
  overflow-y: auto;
  max-height: 100vh;
}

/* Header */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
  gap: 20px;
  flex-wrap: wrap;
}

.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(16, 185, 129, 0.1);
  color: var(--primary, #10b981);
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 0.05em;
}

.header-titles h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 6px 0;
  letter-spacing: -0.02em;
}

.header-titles p {
  color: #64748b;
  font-size: 0.9375rem;
  margin: 0;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.period-selector {
  display: flex;
  background: white;
  padding: 4px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.period-btn {
  padding: 8px 14px;
  border: none;
  background: none;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.period-btn:hover:not(.active) {
  color: #0f172a;
  background: #f1f5f9;
}

.period-btn.active {
  background: var(--primary, #10b981);
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.25);
}

.btn-refresh {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  border-color: var(--primary, #10b981);
  color: var(--primary, #10b981);
  background: #f0fdf4;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Custom Date Filter Bar */
.custom-date-bar {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.custom-date-inputs {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.date-field {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
}

.date-field input[type="date"] {
  border: 1px solid #cbd5e1;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #0f172a;
  outline: none;
}

.date-field input[type="date"]:focus {
  border-color: var(--primary, #10b981);
}

.date-sep {
  color: #94a3b8;
  font-weight: 600;
}

.btn-apply-custom {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--primary, #10b981);
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-apply-custom:hover {
  background: #059669;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
}

.metric-card {
  background: white;
  padding: 22px 24px;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.05);
}

.metric-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.metric-label {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #64748b;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.metric-sublabel {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 2px 0 0 0;
}

.metric-main {
  margin-bottom: 12px;
}

.metric-value {
  font-size: 2.125rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.03em;
}

.growth-tag {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}

.growth-tag.positive {
  background: #dcfce7;
  color: #166534;
}

.growth-tag.negative {
  background: #fee2e2;
  color: #991b1b;
}

.metric-chart {
  height: 34px;
  margin-top: 4px;
}

.sparkline {
  width: 100%;
  height: 100%;
  overflow: visible;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 28px;
}

.card {
  background: white;
  padding: 24px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
}

.card-header-compact {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 12px;
}

.card h3 {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 4px 0;
}

.card-desc {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8125rem;
  color: #64748b;
  font-weight: 500;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.api { background: var(--primary, #10b981); }
.dot.dl { background: #3b82f6; }

/* Timeline Chart */
.timeline-chart-wrapper {
  overflow-x: auto;
  padding-bottom: 8px;
}

.chart-empty {
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-style: italic;
  font-size: 0.9375rem;
}

.bar-chart {
  height: 240px;
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding-bottom: 24px;
  min-width: 100%;
}

.bar-group {
  flex: 1;
  min-width: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  position: relative;
}

.full-bar {
  width: 100%;
  max-width: 28px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  border-radius: 6px 6px 0 0;
  overflow: hidden;
  background: #f1f5f9;
  cursor: pointer;
  transition: all 0.2s;
}

.bar-group:hover .full-bar {
  background: #e2e8f0;
  transform: scaleY(1.02);
  transform-origin: bottom;
}

.bar-segment {
  width: 100%;
  transition: height 0.3s ease;
}

.bar-segment.dl { background: #3b82f6; }
.bar-segment.api { background: var(--primary, #10b981); }

.bar-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #94a3b8;
  margin-top: 8px;
  white-space: nowrap;
}

.bar-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
  background: #0f172a;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 20;
  pointer-events: none;
}

.tooltip-date {
  font-weight: 700;
  margin-bottom: 4px;
  color: #e2e8f0;
}

.tooltip-row {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #cbd5e1;
}

.tooltip-total {
  margin-top: 4px;
  padding-top: 4px;
  border-top: 1px solid rgba(255,255,255,0.15);
  font-weight: 600;
  color: #38bdf8;
}

/* Distribution Pie / Donut */
.pie-chart-area {
  display: flex;
  flex-direction: column;
}

.dist-toggle {
  display: flex;
  background: #f1f5f9;
  padding: 2px;
  border-radius: 8px;
}

.dist-toggle button {
  padding: 4px 10px;
  border: none;
  background: none;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.dist-toggle button.active {
  background: white;
  color: #0f172a;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.pie-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.svg-donut-wrapper {
  position: relative;
  width: 140px;
  height: 140px;
}

.donut-svg {
  width: 100%;
  height: 100%;
}

.donut-segment {
  transition: stroke-dashoffset 0.5s ease, stroke-dasharray 0.5s ease;
}

.donut-center-info {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.donut-total {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1;
}

.donut-label {
  font-size: 0.6875rem;
  color: #64748b;
  font-weight: 600;
  margin-top: 2px;
}

.dist-legend-list {
  width: 100%;
  max-height: 130px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dist-legend-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  border-radius: 8px;
  background: #f8fafc;
  font-size: 0.8125rem;
}

.dist-item-left {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.dist-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.dist-item-names {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dist-name {
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 160px;
}

.dist-count {
  font-size: 0.6875rem;
  color: #64748b;
}

.dist-pct {
  font-weight: 700;
  color: #0f172a;
  font-size: 0.8125rem;
}

/* Most Popular Datasets Table */
.table-card {
  padding: 24px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  padding: 8px 14px;
  border-radius: 10px;
  width: 280px;
}

.search-box input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.875rem;
  color: #0f172a;
  width: 100%;
}

.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
  vertical-align: middle;
}

.name-cell {
  max-width: 280px;
}

.dataset-title {
  font-weight: 600;
  color: #0f172a;
  line-height: 1.3;
}

.dataset-code {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 2px;
}

.org-cell {
  color: #475569;
  font-size: 0.8125rem;
  max-width: 200px;
}

.category-pill {
  display: inline-block;
  padding: 3px 8px;
  background: #f1f5f9;
  color: #334155;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bg {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary, #10b981);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.progress-text {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  min-width: 32px;
}

.time-cell {
  font-size: 0.78rem;
  color: #64748b;
}

.status-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 100px;
  font-size: 0.6875rem;
  font-weight: 700;
}

.status-badge.public {
  background: #dcfce7;
  color: #166534;
}

.status-badge.restricted {
  background: #fef3c7;
  color: #92400e;
}

.no-data-cell {
  text-align: center;
  padding: 40px !important;
  color: #94a3b8;
  font-style: italic;
}

/* Numbered Pagination */
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
  border-color: var(--primary, #10b981);
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
  background: var(--primary, #10b981);
  border-color: var(--primary, #10b981);
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.page-dots {
  padding: 0 6px;
  color: #94a3b8;
  font-weight: bold;
}

/* Utilities */
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
.font-bold { font-weight: 700; }
.text-muted { color: #94a3b8; }
.transition-fade { transition: opacity 0.2s ease; }

.scrollbar-custom::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.scrollbar-custom::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-custom::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
.scrollbar-custom::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Responsive */
@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .analytics-content {
    padding: 20px 16px;
  }
  .content-header {
    flex-direction: column;
    align-items: stretch;
  }
  .header-controls {
    flex-direction: column;
    align-items: stretch;
  }
  .period-selector {
    flex-wrap: wrap;
  }
  .search-box {
    width: 100%;
  }
  .pagination-container {
    flex-direction: column;
    align-items: stretch;
  }
  .pagination-controls {
    justify-content: center;
  }
}
</style>
