<script setup>
import { ref, onMounted } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient from '../utils/api';

const userName = ref('User');
const datasetCount = ref('0');
const isLoading = ref(true);

const resolveActivityText = (text) => {
  if (!text) return 'ไม่พบรายละเอียดกิจกรรม';
  
  // Exact mappings
  const exactMappings = {
    'not found': 'เข้าสู่ระบบไม่สำเร็จ: รหัสผ่านไม่ถูกต้อง',
    'username is incorrect': 'เข้าสู่ระบบไม่สำเร็จ: ไม่พบชื่อผู้ใช้งาน',
    'login success': 'เข้าสู่ระบบสำเร็จ',
    'log out': 'ออกจากระบบ',
    'change password admin': 'ผู้ดูแลระบบเปลี่ยนรหัสผ่าน',
    'change password': 'เปลี่ยนรหัสผ่านสำเร็จ',
    'policy is update': 'นโยบายความเป็นส่วนตัวได้รับการอัปเดต',
    'Your account is suspended': 'บัญชีของคุณถูกระงับการใช้งาน',
  };
  
  if (exactMappings[text]) {
    return exactMappings[text];
  }
  
  // Regex / prefix matches
  if (text.startsWith('Failed login attempt: incorrect password for user')) {
    const match = text.match(/user "([^"]+)" \(attempt (\d+)\)/);
    if (match) {
      return `เข้าสู่ระบบไม่สำเร็จ: รหัสผ่านไม่ถูกต้องสำหรับผู้ใช้งาน "${match[1]}" (ครั้งที่ ${match[2]})`;
    }
    return 'เข้าสู่ระบบไม่สำเร็จ: รหัสผ่านไม่ถูกต้อง';
  }
  
  if (text.startsWith('Failed login attempt: invalid username')) {
    const match = text.match(/invalid username "([^"]+)"/);
    if (match) {
      return `เข้าสู่ระบบไม่สำเร็จ: ไม่พบชื่อผู้ใช้งาน "${match[1]}"`;
    }
    return 'เข้าสู่ระบบไม่สำเร็จ: ไม่พบชื่อผู้ใช้งาน';
  }
  
  if (text.startsWith('ALERT: Unauthorized login attempt')) {
    if (text.includes('Incorrect Password')) {
      const match = text.match(/username: (\S+)/);
      return `แจ้งเตือน: พยายามเข้าสู่ระบบด้วยรหัสผ่านที่ผิดสำหรับผู้ใช้ "${match ? match[1] : ''}"`;
    }
    if (text.includes('Invalid Username')) {
      const match = text.match(/username: (\S+)/);
      return `แจ้งเตือน: พยายามเข้าสู่ระบบด้วยชื่อผู้ใช้งานที่ไม่มีในระบบ "${match ? match[1] : ''}"`;
    }
    return 'แจ้งเตือน: พยายามเข้าสู่ระบบโดยไม่ได้รับอนุญาต';
  }
  
  if (text.startsWith('Accessed Dataset:')) {
    return text.replace('Accessed Dataset:', 'เข้าใช้งานชุดข้อมูล:');
  }
  
  if (text.startsWith('Downloaded Dataset:')) {
    return text.replace('Downloaded Dataset:', 'ดาวน์โหลดชุดข้อมูล:');
  }
  
  if (text.startsWith('Request dataset permission for service_id')) {
    const match = text.match(/service_id (\d+)/);
    return `ส่งคำขออนุมัติสิทธิ์เข้าถึงชุดข้อมูล (รหัสบริการ: ${match ? match[1] : ''})`;
  }
  
  if (text.startsWith('Approved request')) {
    const match = text.match(/request (\d+) for user_id (\d+) on service_id (\d+)/);
    if (match) {
      return `อนุมัติคำขอรับสิทธิ์เข้าถึงข้อมูลของชุดข้อมูล (รหัสบริการ: ${match[3]}) สำเร็จ`;
    }
    return 'อนุมัติคำขอสิทธิ์การเข้าถึงข้อมูลสำเร็จ';
  }
  
  if (text.startsWith('Updatemenu_permission')) {
    return 'อัปเดตสิทธิ์การใช้งานระบบงานสำเร็จ';
  }
  
  return text;
};

const stats = ref([
  { label: 'Datasets Accessed', value: '0', trend: '+0%', color: 'var(--mso-accent)', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2z' },
  { label: 'API Keys Active', value: '0', trend: '+0%', color: '#3b82f6', icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z' },
  { label: 'API Calls This Month', value: '0', trend: '+0%', color: '#8b5cf6', icon: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16' },
  { label: 'Downloads This Month', value: '0', trend: '+0%', color: '#ef4444', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4' }
]);

const recentActivity = ref([]);
const chartData = ref([]);
const recentDatasets = ref([]);

const fetchDashboardData = async () => {
  isLoading.value = true;
  try {
    // 1. Fetch Summary Stats
    const statsResponse = await apiClient.get('/dashboard/stats');
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
        color: act.type === 'API' ? '#3b82f6' : 'var(--mso-accent)'
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
      recentDatasets.value = datasetsResponse.data.data.slice(0, 3).map(ds => ({
        id: ds.service_id,
        name: ds.service_name,
        agency: ds.organization,
        formats: [ds.data_format || 'API']
      }));
    }
    
    const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
    if (savedUser.firstname) {
      userName.value = savedUser.firstname;
    }
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
  } finally {
    isLoading.value = false;
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
      <header class="content-header">
        <div class="search-bar-top">
          <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input type="text" placeholder="Search datasets...">
        </div>
        
        <div class="header-user-actions">
          <button class="icon-btn notification">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span class="badge">3</span>
          </button>
          <button class="icon-btn help">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>
      </header>

      <div class="main-view-container">
        <div class="welcome-section">
          <div class="welcome-text">
            <h1>สวัสดี, {{ userName }}</h1>
            <p>ยินดีต้อนรับกลับมา นี่คือภาพรวมกิจกรรมของคุณ</p>
          </div>
          <div class="welcome-actions">
            <button class="btn-secondary">Download Report</button>
          </div>
        </div>
        
        <div class="stats-grid">
          <div v-for="stat in stats" :key="stat.label" class="stat-card">
            <div class="stat-header">
              <div class="stat-icon-wrapper" :style="{ color: stat.color, backgroundColor: stat.color + '15' }">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="stat.icon" />
                </svg>
              </div>
              <span class="stat-trend" :style="{ color: stat.color }">{{ stat.trend }}</span>
            </div>
            <div class="stat-body">
              <h2 class="stat-value">{{ stat.value }}</h2>
              <p class="stat-label">{{ stat.label }}</p>
            </div>
          </div>
        </div>
        
        <div class="dashboard-grid">
          <section class="main-charts">
            <div class="card chart-card">
              <div class="card-header">
                <h3>API Usage (7 days)</h3>
                <div class="chart-legend">
                  <span class="legend-item"><span class="dot" style="background-color: var(--mso-accent)"></span> Calls</span>
                </div>
              </div>
              <div class="mock-chart-container">
                <div class="chart-y-axis">
                  <span>100</span>
                  <span>50</span>
                  <span>0</span>
                </div>
                <div class="chart-bars-horizontal">
                  <template v-if="chartData.length > 0">
                    <div v-for="day in chartData" :key="day.date" class="bar-group">
                      <div class="bar-label">{{ day.date.split('-').slice(1).join('/') }}</div>
                      <div class="bar-track" :title="day.date + ': ' + day.count">
                        <div class="bar-progress" :style="{ width: Math.min(100, (day.count / 100) * 100) + '%', backgroundColor: day.count > 70 ? 'var(--mso-accent)' : '#3b82f6' }"></div>
                      </div>
                      <div class="bar-value">{{ day.count }}</div>
                    </div>
                  </template>
                  <div v-else class="no-data-msg">No activity in the last 7 days</div>
                </div>
              </div>
            </div>

            <div class="recent-datasets-section">
              <h3>Recent Datasets</h3>
              <div class="datasets-list">
                <div v-for="ds in recentDatasets" :key="ds.id" class="dataset-mini-card">
                  <div class="ds-info">
                    <h4>{{ ds.name }}</h4>
                    <p>{{ ds.agency }}</p>
                  </div>
                  <div class="ds-tags">
                    <span v-for="tag in ds.formats" :key="tag" class="tag">{{ tag }}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>
          
          <aside class="activity-sidebar">
            <div class="card activity-card">
              <div class="card-header">
                <h3>Recent Activity</h3>
              </div>
              <div class="activity-timeline">
                <div v-for="item in recentActivity" :key="item.id" class="activity-item">
                  <div class="activity-dot" :style="{ backgroundColor: item.color }"></div>
                  <div class="activity-content">
                    <p class="activity-text">{{ resolveActivityText(item.text) }}</p>
                    <span class="activity-time">{{ item.time }}</span>
                  </div>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </main>
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
  z-index: 10;
}

.search-bar-top {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: #f1f5f9;
  padding: 8px 16px;
  border-radius: 10px;
  width: 320px;
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
  padding: 6px;
  border-radius: 8px;
  transition: all 0.2s;
}

.icon-btn:hover {
  background-color: #f1f5f9;
  color: #1e293b;
}

.icon-btn .badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: #ef4444;
  color: white;
  font-size: 0.625rem;
  padding: 2px 5px;
  border-radius: 10px;
  border: 2px solid white;
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
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.welcome-text p {
  color: #64748b;
  font-size: 1rem;
}

.welcome-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: white;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: #f8fafc;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background-color: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stat-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-trend {
  font-size: 0.875rem;
  font-weight: 600;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
}

.card {
  background-color: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-header {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.chart-legend {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
  color: #64748b;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-item .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.mock-chart-container {
  height: 240px;
  display: flex;
  gap: 16px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: #94a3b8;
  font-size: 0.75rem;
  padding: 8px 0;
}

.chart-bars-horizontal {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.bar-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  font-size: 0.75rem;
  color: #64748b;
  width: 40px;
  text-align: right;
}

.bar-track {
  flex: 1;
  height: 12px;
  background-color: #f1f5f9;
  border-radius: 6px;
  overflow: hidden;
}

.bar-progress {
  height: 100%;
  background-color: var(--mso-accent);
  border-radius: 6px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  width: 30px;
}

.recent-datasets-section {
  margin-top: 40px;
}

.recent-datasets-section h3 {
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 20px;
}

.datasets-list {
  display: grid;
  gap: 16px;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: #e2e8f0;
}

.ds-info h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.ds-info p {
  font-size: 0.8125rem;
  color: #94a3b8;
}

.ds-tags {
  display: flex;
  gap: 8px;
}

.tag {
  background-color: #f1f5f9;
  color: #475569;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
}

.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.activity-item {
  display: flex;
  gap: 16px;
}

.activity-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

.activity-text {
  font-size: 0.875rem;
  color: #334155;
  margin-bottom: 4px;
  line-height: 1.4;
}

.activity-time {
  font-size: 0.75rem;
  color: #94a3b8;
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
