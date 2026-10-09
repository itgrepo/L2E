<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient from '../utils/api';

const router = useRouter();

const userName = ref('ผู้ดูแลระบบ');
const userRole = ref('');
const isLoading = ref(true);
const isExporting = ref(false);
const showHelpModal = ref(false);
const activeHelpTab = ref('catalog');
const toastMessage = ref('');
const toastTimeout = ref(null);

const triggerToast = (msg) => {
  toastMessage.value = msg;
  if (toastTimeout.value) clearTimeout(toastTimeout.value);
  toastTimeout.value = setTimeout(() => {
    toastMessage.value = '';
  }, 4000);
};

const resolveActivityText = (text) => {
  if (!text) return 'ไม่พบรายละเอียดกิจกรรม';
  
  // 1. Try Parsing JSON Strings (e.g. from API Access Logs)
  if (typeof text === 'string' && (text.trim().startsWith('{') || text.trim().startsWith('['))) {
    try {
      const obj = JSON.parse(text);
      if (obj.action === 'data_access' || (obj.message && obj.message.includes('API Invoked'))) {
        const dsName = obj.dataset_id ? `ชุดข้อมูล ${obj.dataset_id}` : 'ชุดข้อมูล';
        if (obj.result === 'Allowed' || !obj.result) {
          return `⚡ เข้าใช้งาน API ${dsName} (สำเร็จ)`;
        } else {
          return `⚠️ เข้าใช้งาน API ${dsName} (ปฏิเสธ: ${obj.message || 'ไม่ได้รับสิทธิ์'})`;
        }
      }
      if (obj.message) return obj.message;
    } catch (e) {
      // Not JSON, continue to string matchers
    }
  }

  // 2. Exact Mappings
  const exactMappings = {
    'user is admin': 'เข้าใช้งานระบบด้วยสิทธิ์ผู้ดูแลระบบ (Admin Access)',
    'login success': 'เข้าสู่ระบบสำเร็จ',
    'log out': 'ออกจากระบบ',
    'change password admin': 'ผู้ดูแลระบบเปลี่ยนรหัสผ่านสำเร็จ',
    'change password': 'เปลี่ยนรหัสผ่านสำเร็จ',
    'policy is update': 'นโยบายความเป็นส่วนตัวได้รับการอัปเดต',
    'Your account is suspended': 'บัญชีของคุณถูกระงับการใช้งาน',
    'not found': 'เข้าสู่ระบบไม่สำเร็จ: รหัสผ่านไม่ถูกต้อง',
    'username is incorrect': 'เข้าสู่ระบบไม่สำเร็จ: ไม่พบชื่อผู้ใช้งาน'
  };
  
  if (exactMappings[text]) {
    return exactMappings[text];
  }
  
  // 3. Regex / Prefix Matches
  if (text.startsWith('ALERT: Unauthorized login attempt')) {
    if (text.includes('Incorrect Password')) {
      const match = text.match(/username: (\S+)/);
      return `แจ้งเตือน: รหัสผ่านไม่ถูกต้องสำหรับบัญชี "${match ? match[1] : ''}"`;
    }
    if (text.includes('Invalid Username')) {
      const match = text.match(/username: (\S+)/);
      return `แจ้งเตือน: ไม่พบบัญชีผู้ใช้งาน "${match ? match[1] : ''}" ในระบบ`;
    }
    return 'แจ้งเตือน: ความพยายามเข้าสู่ระบบโดยไม่ได้รับอนุญาต';
  }

  if (text.startsWith('Failed login attempt: incorrect password for user')) {
    const match = text.match(/user "([^"]+)" \(attempt (\d+)\)/);
    if (match) {
      return `เข้าสู่ระบบไม่สำเร็จ: รหัสผ่านผิดสำหรับผู้ใช้ "${match[1]}" (ครั้งที่ ${match[2]})`;
    }
    return 'เข้าสู่ระบบไม่สำเร็จ: รหัสผ่านไม่ถูกต้อง';
  }
  
  if (text.startsWith('Failed login attempt: invalid username')) {
    const match = text.match(/invalid username "([^"]+)"/);
    if (match) {
      return `เข้าสู่ระบบไม่สำเร็จ: ไม่พบบัญชีผู้ใช้ "${match[1]}"`;
    }
    return 'เข้าสู่ระบบไม่สำเร็จ: ไม่พบชื่อผู้ใช้งาน';
  }
  
  if (text.startsWith('Accessed Dataset:')) {
    return text.replace('Accessed Dataset:', 'เข้าชมชุดข้อมูล:');
  }
  
  if (text.startsWith('Downloaded Dataset:')) {
    return text.replace('Downloaded Dataset:', 'ดาวน์โหลดไฟล์ชุดข้อมูล:');
  }
  
  if (text.startsWith('Request dataset permission for service_id')) {
    const match = text.match(/service_id (\d+)/);
    return `ส่งคำขออนุมัติสิทธิ์เข้าถึงชุดข้อมูล (รหัสบริการ: ${match ? match[1] : ''})`;
  }
  
  if (text.startsWith('Approved request')) {
    const match = text.match(/request (\d+) .* for user_id (\d+) on service_id (\d+)/);
    if (match) {
      return `อนุมัติคำขอรับสิทธิ์เข้าถึงข้อมูลของชุดข้อมูล (รหัสบริการ: ${match[3]}) เรียบร้อยแล้ว`;
    }
    return 'อนุมัติคำขอสิทธิ์การเข้าถึงข้อมูลสำเร็จ';
  }

  if (text.startsWith('Delete Role')) {
    return 'ลบสิทธิ์หรือบทบาทการใช้งานสำเร็จ';
  }
  
  if (text.startsWith('Updatemenu_permission')) {
    return 'อัปเดตสิทธิ์การเข้าถึงเมนูระบบสำเร็จ';
  }
  
  return text;
};

const stats = ref([
  { label: 'Datasets Available', label_th: 'ชุดข้อมูลในระบบทั้งหมด', value: '0', trend: '+0%', color: '#22c55e', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2z' },
  { label: 'API Keys Active', label_th: 'API Keys ที่เปิดใช้งาน', value: '0', trend: '+0%', color: '#3b82f6', icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z' },
  { label: 'API Calls This Month', label_th: 'การเรียกใช้ API เดือนนี้', value: '0', trend: '+0%', color: '#8b5cf6', icon: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16' },
  { label: 'Downloads This Month', label_th: 'การดาวน์โหลดไฟล์เดือนนี้', value: '0', trend: '+0%', color: '#ef4444', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4' }
]);

const recentActivity = ref([]);
const chartData = ref([]);
const recentDatasets = ref([]);
const searchQuery = ref('');

const filteredRecentDatasets = computed(() => {
  if (!searchQuery.value) return recentDatasets.value;
  const q = searchQuery.value.toLowerCase().trim();
  return recentDatasets.value.filter(ds => 
    (ds.name && ds.name.toLowerCase().includes(q)) || 
    (ds.agency && ds.agency.toLowerCase().includes(q))
  );
});

const handleSearchEnter = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/catalog', query: { q: searchQuery.value.trim() } });
  }
};

const getTooltipForLabel = (label) => {
  const map = {
    'Datasets Available': 'จำนวนชุดข้อมูลทั้งหมดที่มีสถานะเปิดใช้งานในระบบ',
    'API Keys Active': 'จำนวน API Credential Key ที่พร้อมใช้งานในขณะนี้',
    'API Calls This Month': 'ปริมาณการเรียกใช้งาน API รวมทุกบริการในรอบเดือนปัจจุบัน',
    'Downloads This Month': 'จำนวนครั้งที่มีการดาวน์โหลดไฟล์ข้อมูลในรอบเดือนปัจจุบัน'
  };
  return map[label] || `สถิติภาพรวม ${label}`;
};

// Dynamic chart calculation
const maxChartCount = computed(() => {
  if (!chartData.value || chartData.value.length === 0) return 100;
  const counts = chartData.value.map(d => Number(d.count) || 0);
  return Math.max(10, ...counts);
});

const dynamicMaxScale = computed(() => {
  const max = maxChartCount.value;
  if (max <= 10) return 10;
  if (max <= 50) return 50;
  if (max <= 100) return 100;
  return Math.ceil(max / 50) * 50;
});

const yAxisTicks = computed(() => {
  const max = dynamicMaxScale.value;
  return [max, Math.round(max / 2), 0];
});

const formatDateLabel = (dateStr) => {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}`;
  }
  const d = new Date(dateStr);
  if (!isNaN(d.getTime())) {
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    return `${day}/${month}`;
  }
  return dateStr;
};

const fetchDashboardData = async () => {
  isLoading.value = true;
  try {
    const userRaw = localStorage.getItem('user');
    if (userRaw) {
      try {
        const savedUser = JSON.parse(userRaw);
        if (savedUser.firstname) {
          userName.value = savedUser.firstname + (savedUser.lastname ? ' ' + savedUser.lastname : '');
        }
        if (savedUser.role_name || savedUser.role) {
          userRole.value = savedUser.role_name || savedUser.role;
        }
      } catch(e) {}
    }

    // 1. Fetch Summary Stats
    const statsResponse = await apiClient.get('/dashboard/stats', {
      params: { user: userRaw }
    });
    
    if (statsResponse?.data?.status === 'success') {
      if (statsResponse.data.stats) {
        stats.value = statsResponse.data.stats;
      }
      
      const activities = statsResponse.data.recentActivity || [];
      recentActivity.value = activities.map(act => ({
        id: Math.random(),
        type: act.type,
        text: act.text,
        time: act.time,
        color: act.type === 'API' ? '#3b82f6' : (act.type === 'alert' || act.type === 'error' ? '#ef4444' : '#22c55e')
      }));
    }

    // 2. Fetch Chart Data
    const chartResponse = await apiClient.get('/dashboard/usage_chart');
    if (chartResponse?.data?.status === 'success' && chartResponse.data.data) {
      chartData.value = chartResponse.data.data;
    }

    // 3. Fetch Recent Datasets
    const datasetsResponse = await apiClient.get('/retrieveService');
    if (datasetsResponse?.data?.status === 'success' && datasetsResponse.data.data) {
      recentDatasets.value = datasetsResponse.data.data.slice(0, 4).map(ds => ({
        id: ds.service_id,
        name: ds.service_name,
        agency: ds.organization,
        formats: ds.data_format ? ds.data_format.split(',') : ['API']
      }));
    }
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
  } finally {
    isLoading.value = false;
  }
};

const downloadReport = async () => {
  isExporting.value = true;
  try {
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 10);
    const timeStr = now.toTimeString().slice(0, 8);

    // Build comprehensive CSV with UTF-8 BOM
    let csv = '\uFEFF';
    csv += 'LEARN TO EARN DATA EXCHANGE - DASHBOARD SUMMARY REPORT\n';
    csv += `Export Date,${dateStr} ${timeStr}\n`;
    csv += `Exported By,"${userName.value}"\n\n`;

    // 1. Overview KPIs
    csv += '--- OVERVIEW METRICS ---\n';
    csv += 'Metric,Value,Monthly Trend\n';
    stats.value.forEach(s => {
      csv += `"${s.label_th || s.label} (${s.label})",${s.value},${s.trend}\n`;
    });
    csv += '\n';

    // 2. 7-Day API Usage
    csv += '--- API USAGE (LAST 7 DAYS) ---\n';
    csv += 'Date,API Calls Count\n';
    if (chartData.value && chartData.value.length > 0) {
      chartData.value.forEach(d => {
        csv += `"${d.date}",${d.count}\n`;
      });
    } else {
      csv += 'No activity recorded,0\n';
    }
    csv += '\n';

    // 3. Recent Activities
    csv += '--- RECENT ACTIVITY AUDIT LOGS ---\n';
    csv += 'Timestamp,Type,Activity Description\n';
    if (recentActivity.value && recentActivity.value.length > 0) {
      recentActivity.value.forEach(a => {
        const cleanDesc = resolveActivityText(a.text).replace(/"/g, '""');
        csv += `"${a.time}","${a.type || 'System'}","${cleanDesc}"\n`;
      });
    } else {
      csv += 'No recent activity recorded\n';
    }
    csv += '\n';

    // 4. Datasets Catalog Overview
    csv += '--- DATASETS CATALOG OVERVIEW ---\n';
    csv += 'Service ID,Dataset Name,Organization,Formats\n';
    if (recentDatasets.value && recentDatasets.value.length > 0) {
      recentDatasets.value.forEach(d => {
        const cleanName = (d.name || '').replace(/"/g, '""');
        const cleanAgency = (d.agency || '').replace(/"/g, '""');
        const cleanFormats = (d.formats || []).join(' / ');
        csv += `"${d.id}","${cleanName}","${cleanAgency}","${cleanFormats}"\n`;
      });
    }

    // Trigger Browser Download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `DataX_Dashboard_Report_${dateStr.replace(/-/g, '')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    triggerToast('ดาวน์โหลดรายงานสรุป Dashboard สำเร็จเรียบร้อย');
  } catch (err) {
    console.error('Error generating report:', err);
    triggerToast('เกิดข้อผิดพลาดในการสร้างรายงาน');
  } finally {
    isExporting.value = false;
  }
};

onMounted(() => {
  fetchDashboardData();
});
</script>

<template>
  <div class="dashboard-layout">
    <AppSidebar />
    
    <main class="dashboard-content">
      <!-- Content Header -->
      <header class="content-header">
        <div class="search-bar-top">
          <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input 
            type="text" 
            v-model="searchQuery" 
            @keyup.enter="handleSearchEnter"
            placeholder="ค้นหาชุดข้อมูลล่าสุด... (กด Enter เพื่อค้นหาใน Catalog)"
          >
        </div>
        
        <div class="header-user-actions">
          <!-- Help Button with bottom-right aligned tooltip -->
          <button 
            class="icon-btn help custom-tooltip tooltip-bottom-right" 
            data-tooltip="คู่มือการใช้งานระบบ Data Exchange"
            @click="showHelpModal = true"
            aria-label="Help Guide"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>
      </header>

      <!-- Main Container -->
      <div class="main-view-container">
        <!-- Welcome Section -->
        <div class="welcome-section">
          <div class="welcome-text">
            <h1>สวัสดี, {{ userName }}</h1>
            <p>ยินดีต้อนรับกลับมา นี่คือภาพรวมกิจกรรมและสถิติการใช้งานระบบ Data Exchange ของคุณ</p>
          </div>
          <div class="welcome-actions">
            <button 
              class="btn-secondary custom-tooltip" 
              data-tooltip="ดาวน์โหลดรายงานสรุปภาพรวมระบบ (CSV / Excel)"
              :disabled="isExporting"
              @click="downloadReport"
            >
              <svg v-if="!isExporting" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="margin-right: 6px;">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <svg v-else class="animate-spin" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" style="margin-right: 6px;">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" style="opacity: 0.25;"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" style="opacity: 0.75;"></path>
              </svg>
              {{ isExporting ? 'กำลังสร้างรายงาน...' : 'Download Report' }}
            </button>
          </div>
        </div>
        
        <!-- Stats Grid (4 KPI Cards) -->
        <div class="stats-grid">
          <div 
            v-for="stat in stats" 
            :key="stat.label" 
            :data-tooltip="getTooltipForLabel(stat.label)" 
            class="stat-card custom-tooltip"
          >
            <div class="stat-header">
              <div class="stat-icon-wrapper" :style="{ color: stat.color, backgroundColor: stat.color + '15' }">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="stat.icon" />
                </svg>
              </div>
              <span class="stat-trend" :style="{ color: stat.color }">
                {{ stat.trend }}
              </span>
            </div>
            <div class="stat-body">
              <h2 class="stat-value">{{ stat.value }}</h2>
              <p class="stat-label-th">{{ stat.label_th || stat.label }}</p>
              <p class="stat-label-en">{{ stat.label }}</p>
            </div>
          </div>
        </div>
        
        <!-- Dashboard Grid (Charts & Activity) -->
        <div class="dashboard-grid">
          <!-- Main Left Section -->
          <section class="main-charts">
            <!-- 7-Day API Usage Chart Card -->
            <div class="card chart-card">
              <div class="card-header">
                <div>
                  <h3 class="custom-tooltip" data-tooltip="ปริมาณการเรียกใช้งาน API รวมย้อนหลัง 7 วัน">
                    API Usage (7 days)
                  </h3>
                  <p style="font-size: 0.8rem; color: #94a3b8; margin: 2px 0 0 0;">
                    สถิติปริมาณการเรียกใช้งาน API ย้อนหลัง 7 วันล่าสุด
                  </p>
                </div>
                <div class="chart-legend">
                  <span class="legend-item"><span class="dot" style="background-color: var(--mso-accent)"></span> Calls (ครั้ง)</span>
                </div>
              </div>

              <div class="mock-chart-container">
                <div class="chart-bars-horizontal">
                  <template v-if="chartData.length > 0">
                    <div 
                      v-for="day in chartData" 
                      :key="day.date" 
                      class="bar-group custom-tooltip"
                      :data-tooltip="`วันที่ ${day.date}: เรียกใช้งาน ${day.count} ครั้ง`"
                    >
                      <div class="bar-label">{{ formatDateLabel(day.date) }}</div>
                      <div class="bar-track">
                        <div 
                          class="bar-progress" 
                          :style="{ 
                            width: Math.max(4, Math.min(100, (day.count / dynamicMaxScale) * 100)) + '%', 
                            backgroundColor: day.count > (dynamicMaxScale * 0.7) ? 'var(--mso-accent)' : '#3b82f6' 
                          }"
                        ></div>
                      </div>
                      <div class="bar-value">{{ day.count }}</div>
                    </div>
                  </template>
                  <div v-else class="no-data-msg">ไม่มีประวัติการเรียกใช้งานในรอบ 7 วันที่ผ่านมา</div>
                </div>
              </div>
            </div>

            <!-- Recent Datasets Section -->
            <div class="recent-datasets-section">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 class="custom-tooltip" data-tooltip="ชุดข้อมูลที่เปิดให้บริการล่าสุดในระบบ" style="margin: 0;">
                  Recent Datasets (ชุดข้อมูลล่าสุด)
                </h3>
                <router-link to="/catalog" style="font-size: 0.85rem; color: var(--primary); text-decoration: none; font-weight: 600;">
                  ดูชุดข้อมูลทั้งหมด &rarr;
                </router-link>
              </div>
              <div class="datasets-list">
                <div 
                  v-for="ds in filteredRecentDatasets" 
                  :key="ds.id" 
                  class="dataset-mini-card"
                  @click="$router.push('/dataset/' + ds.id)"
                  style="cursor: pointer;"
                >
                  <div class="ds-info">
                    <h4>{{ ds.name }}</h4>
                    <p>{{ ds.agency }}</p>
                  </div>
                  <div class="ds-tags">
                    <span v-for="tag in ds.formats" :key="tag" class="tag">{{ tag }}</span>
                  </div>
                </div>
                <div v-if="filteredRecentDatasets.length === 0" class="no-data-msg">ไม่พบชุดข้อมูลที่ค้นหา</div>
              </div>
            </div>
          </section>
          
          <!-- Activity Sidebar -->
          <aside class="activity-sidebar">
            <div class="card activity-card">
              <div class="card-header">
                <div>
                  <h3 style="margin: 0;">Recent Activity</h3>
                  <p style="font-size: 0.75rem; color: #94a3b8; margin: 2px 0 0 0;">ประวัติการใช้งานและบันทึกระบบล่าสุด</p>
                </div>
              </div>
              <div class="activity-timeline">
                <template v-if="recentActivity.length > 0">
                  <div v-for="item in recentActivity" :key="item.id" class="activity-item">
                    <div class="activity-dot" :style="{ backgroundColor: item.color }"></div>
                    <div class="activity-content">
                      <p class="activity-text">{{ resolveActivityText(item.text) }}</p>
                      <span class="activity-time">{{ item.time }}</span>
                    </div>
                  </div>
                </template>
                <div v-else class="no-data-msg">ไม่พบบันทึกกิจกรรมล่าสุด</div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </main>

    <!-- Quick User Guide Modal -->
    <div v-if="showHelpModal" class="modal-backdrop" @click.self="showHelpModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 36px; height: 36px; border-radius: 8px; background: rgba(14, 165, 233, 0.1); display: flex; align-items: center; justify-content: center; color: #0284c7;">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div>
              <h3 style="margin: 0; font-size: 1.2rem; color: #1e293b;">คู่มือการใช้งานระบบ Data Exchange</h3>
              <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #64748b;">ภาพรวมขั้นตอนการใช้งานหลักของระบบ Learn to Earn DataX</p>
            </div>
          </div>
          <button class="modal-close-btn" @click="showHelpModal = false">&times;</button>
        </div>

        <div class="modal-tabs">
          <button :class="{ active: activeHelpTab === 'catalog' }" @click="activeHelpTab = 'catalog'">1. ค้นหาชุดข้อมูล</button>
          <button :class="{ active: activeHelpTab === 'request' }" @click="activeHelpTab = 'request'">2. ขอใช้ข้อมูล</button>
          <button :class="{ active: activeHelpTab === 'api' }" @click="activeHelpTab = 'api'">3. การใช้งาน API</button>
          <button :class="{ active: activeHelpTab === 'monitor' }" @click="activeHelpTab = 'monitor'">4. รายงาน & สถิติ</button>
        </div>

        <div class="modal-body">
          <div v-if="activeHelpTab === 'catalog'" class="guide-content">
            <h4>🔍 การสืบค้นและเข้าถึงบัญชีชุดข้อมูล (Catalog)</h4>
            <ul>
              <li>เข้าสู่เมนู <strong>บัญชีข้อมูล (Catalog)</strong> เพื่อค้นหาชุดข้อมูลตามชื่อ, หมวดหมู่, หรือหน่วยงานผู้ให้บริการ</li>
              <li>สามารถกรองข้อมูลตามรูปแบบที่ต้องการ เช่น CSV, Excel, หรือ Web API</li>
              <li>คลิกที่การ์ดชุดข้อมูลเพื่อดูรายละเอียด Metadata, Data Dictionary, และเงื่อนไขการเข้าถึง</li>
            </ul>
          </div>

          <div v-if="activeHelpTab === 'request'" class="guide-content">
            <h4>📋 ขั้นตอนการขอเข้าถึงข้อมูลและสิทธิ์ API</h4>
            <ul>
              <li>ในหน้ารายละเอียดชุดข้อมูล หากเป็นชุดข้อมูลจำกัดสิทธิ์ ให้กดปุ่ม <strong>"ขอเข้าถึงข้อมูล"</strong></li>
              <li>เลือกประเภทสิทธิ์ที่ต้องการ (Dashboard / Web API / ทั้งหมด) และระบุวัตถุประสงค์</li>
              <li>แนบเอกสารหนังสือราชการหรือ MOU (ไฟล์ PDF หรือรูปภาพ ไม่เกิน 10MB)</li>
              <li>ติดตามสถานะคำขอได้ที่เมนู <strong>"คำขอเข้าถึงข้อมูล"</strong> เมื่อได้รับการอนุมัติจะสามารถใช้งาน API ได้ทันที</li>
            </ul>
          </div>

          <div v-if="activeHelpTab === 'api'" class="guide-content">
            <h4>⚡ การใช้งาน API Key และ Scope API</h4>
            <ul>
              <li>รับ API Key ส่วนตัวจากหน้าโปรไฟล์หรือหน้ารายละเอียดชุดข้อมูลที่ได้รับอนุมัติ</li>
              <li>ระบบแยกรูปแบบ API ชัดเจน 3 รูปแบบ:
                <ul>
                  <li><strong>File API (/file):</strong> ดาวน์โหลดไฟล์ชุดข้อมูลต้นฉบับ</li>
                  <li><strong>General API:</strong> ข้อมูลทั่วไปครบทุกฟิลด์</li>
                  <li><strong>Scope API (/scope/):</strong> ข้อมูลเฉพาะฟิลด์และเงื่อนไขที่ผู้ใช้ได้รับอนุญาต</li>
                </ul>
              </li>
              <li>นำ URL หรือ curl command ไปเชื่อมต่อกับ Application หรือระบบงานของท่าน</li>
            </ul>
          </div>

          <div v-if="activeHelpTab === 'monitor'" class="guide-content">
            <h4>📊 การติดตามสถิติและดาวน์โหลดรายงาน</h4>
            <ul>
              <li>หน้า <strong>หน้าหลัก (Dashboard)</strong> สรุปยอดรวมชุดข้อมูล, API Key, ปริมาณการเรียกใช้ และสถิติย้อนหลัง 7 วัน</li>
              <li>กดปุ่ม <strong>"Download Report"</strong> เพื่อส่งออกรายงานสรุปภาพรวมทั้งหมดเป็นไฟล์ CSV / Excel</li>
              <li>ผู้ดูแลระบบสามารถตรวจสอบบันทึกเชิงลึกได้ที่เมนู <strong>"API Monitor"</strong> และ <strong>"Monitor & Logs"</strong></li>
            </ul>
          </div>
        </div>

        <div class="modal-footer">
          <router-link to="/about" class="btn-secondary" @click="showHelpModal = false" style="text-decoration: none; font-size: 0.85rem;">
            อ่านเอกสารเพิ่มเติมเกี่ยวกับระบบ &rarr;
          </router-link>
          <button class="btn-primary" @click="showHelpModal = false" style="font-size: 0.85rem;">
            เข้าใจแล้ว
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <transition name="fade">
      <div v-if="toastMessage" class="toast-notification">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.dashboard-layout {
  display: flex;
  background-color: #f8fafc;
  min-height: 100vh;
}

.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-header {
  height: 64px;
  background-color: white;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 20;
}

.search-bar-top {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: #f1f5f9;
  padding: 8px 16px;
  border-radius: 10px;
  width: 380px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.search-bar-top:focus-within {
  background-color: white;
  border-color: var(--primary, #0284c7);
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1);
}

.search-icon {
  width: 18px;
  height: 18px;
  color: #94a3b8;
}

.search-bar-top input {
  background: none;
  border: none;
  outline: none;
  font-size: 0.875rem;
  width: 100%;
}

.header-user-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  position: relative;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background-color: #f1f5f9;
  color: #0284c7;
}

.main-view-container {
  padding: 32px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}

.welcome-text h1 {
  font-size: 1.85rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
}

.welcome-text p {
  color: #64748b;
  font-size: 0.95rem;
  margin: 0;
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background-color: var(--primary, #0284c7);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary:hover {
  background-color: var(--primary-hover, #0369a1);
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: white;
  color: #1e293b;
  border: 1px solid #cbd5e1;
  padding: 10px 18px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f8fafc;
  border-color: #94a3b8;
}

.btn-secondary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background-color: white;
  padding: 22px;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 8px 16px -2px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stat-icon-wrapper {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-trend {
  font-size: 0.85rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 20px;
  background-color: rgba(0, 0, 0, 0.03);
}

.stat-value {
  font-size: 1.85rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 2px;
  line-height: 1.2;
}

.stat-label-th {
  font-size: 0.85rem;
  color: #334155;
  font-weight: 600;
  margin: 0 0 2px 0;
}

.stat-label-en {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
}

.card {
  background-color: white;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
}

.card-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-header h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.mock-chart-container {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 8px 0;
}

.chart-bars-horizontal {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.bar-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.bar-label {
  font-size: 0.8125rem;
  color: #64748b;
  width: 48px;
  text-align: right;
  font-weight: 600;
  flex-shrink: 0;
}

.bar-track {
  flex: 1;
  height: 16px;
  background-color: #f1f5f9;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
}

.bar-progress {
  height: 100%;
  background-color: var(--mso-accent, #22c55e);
  border-radius: 8px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-value {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #334155;
  width: 44px;
  text-align: right;
  flex-shrink: 0;
}

.recent-datasets-section {
  margin-top: 32px;
}

.datasets-list {
  display: grid;
  gap: 12px;
}

.dataset-mini-card {
  background-color: white;
  padding: 16px 20px;
  border-radius: 12px;
  border: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.dataset-mini-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  border-color: #cbd5e1;
  transform: translateX(3px);
}

.ds-info h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.ds-info p {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0;
}

.ds-tags {
  display: flex;
  gap: 6px;
}

.tag {
  background-color: #f1f5f9;
  color: #475569;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
}

.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 520px;
  overflow-y: auto;
  padding-right: 4px;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #f1f5f9;
}

.activity-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.activity-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.activity-text {
  font-size: 0.825rem;
  color: #334155;
  margin: 0 0 4px 0;
  line-height: 1.4;
  word-break: break-word;
}

.activity-time {
  font-size: 0.72rem;
  color: #94a3b8;
}

.no-data-msg {
  color: #94a3b8;
  font-size: 0.85rem;
  text-align: center;
  padding: 24px;
}

/* Tooltip Styles with Bottom-Right Overflow Fix */
.custom-tooltip {
  position: relative;
}

.custom-tooltip::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  background: #0f172a;
  color: #ffffff;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s;
  pointer-events: none;
  z-index: 9999;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}

.custom-tooltip::before {
  content: '';
  position: absolute;
  bottom: calc(100% + 3px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  border-width: 5px 5px 0 5px;
  border-style: solid;
  border-color: #0f172a transparent transparent transparent;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s;
  pointer-events: none;
  z-index: 9999;
}

.custom-tooltip:hover::after,
.custom-tooltip:hover::before {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}

/* Modifier: Tooltip below and aligned right for header icons (Fixes top overflow clipping) */
.custom-tooltip.tooltip-bottom-right::after {
  bottom: auto;
  top: calc(100% + 8px);
  left: auto;
  right: 0;
  transform: translateY(-4px);
}

.custom-tooltip.tooltip-bottom-right::before {
  bottom: auto;
  top: calc(100% + 3px);
  left: auto;
  right: 12px;
  border-width: 0 5px 5px 5px;
  border-color: transparent transparent #0f172a transparent;
  transform: translateY(-4px);
}

.custom-tooltip.tooltip-bottom-right:hover::after,
.custom-tooltip.tooltip-bottom-right:hover::before {
  transform: translateY(0);
}

/* Quick Help Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-card {
  background: white;
  border-radius: 20px;
  max-width: 680px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  animation: modalPop 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalPop {
  0% { transform: scale(0.95); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
  padding: 4px;
  border-radius: 6px;
}

.modal-close-btn:hover {
  color: #1e293b;
  background: #f1f5f9;
}

.modal-tabs {
  display: flex;
  background: #f8fafc;
  padding: 6px;
  gap: 6px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-tabs button {
  flex: 1;
  background: none;
  border: none;
  padding: 8px 12px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-tabs button.active {
  background: white;
  color: #0284c7;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.modal-body {
  padding: 24px;
  min-height: 220px;
}

.guide-content h4 {
  font-size: 1.05rem;
  color: #1e293b;
  margin: 0 0 12px 0;
}

.guide-content ul {
  padding-left: 20px;
  margin: 0;
  color: #475569;
  font-size: 0.9rem;
  line-height: 1.7;
}

.guide-content li {
  margin-bottom: 8px;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
  background: #fafafa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Toast Notification */
.toast-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: #0f172a;
  color: white;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  z-index: 99999;
}

.toast-notification svg {
  color: #22c55e;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-view-container { padding: 16px; margin-bottom: 60px; }
  .stats-grid { grid-template-columns: 1fr; gap: 16px; }
  .content-header { padding: 16px; flex-direction: column-reverse; height: auto; gap: 12px; }
  .search-bar-top { width: 100%; }
  .header-user-actions { width: 100%; justify-content: flex-end; }
  .welcome-section { flex-direction: column; align-items: flex-start; gap: 16px; margin-bottom: 24px; }
  .welcome-text h1 { font-size: 1.5rem; }
  .card { padding: 16px; }
}
</style>
