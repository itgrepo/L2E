<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '../utils/api';

const props = defineProps({
  config: {
    type: Object,
    default: () => ({
      title: 'ภาพรวมระบบ',
      subtitle: 'สถิติการใช้งานแพลตฟอร์ม'
    })
  }
});

const stats = ref([
  { label: 'Total Datasets', value: '524', icon: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4', color: '#3b82f6', trend: '+12%' },
  { label: 'API Calls', value: '2.4M', icon: 'M13 10V3L4 14h7v7l9-11h-7z', color: '#10b981', trend: '+18%' },
  { label: 'Active Users', value: '1,208', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z', color: '#8b5cf6', trend: '+5%' },
  { label: 'Storage Used', value: '840 GB', icon: 'M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4', color: '#f59e0b', trend: '+2%' }
]);

const chartData = ref([]);

const generateMockChartData = () => {
  const data = [];
  const today = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    data.push({
      date: d.toISOString().split('T')[0],
      count: Math.floor(Math.random() * 80) + 20
    });
  }
  chartData.value = data;
};

onMounted(() => {
  generateMockChartData();
});
</script>

<template>
  <section class="public-dashboard">
    <div class="container">
      <div class="section-header">
        <h2>{{ config.title }}</h2>
        <p>{{ config.subtitle }}</p>
      </div>

      <div class="stats-grid">
        <div v-for="stat in stats" :key="stat.label" class="stat-card">
          <div class="stat-header">
            <div class="stat-icon-wrapper" :style="{ color: stat.color, backgroundColor: stat.color + '15' }">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="stat.icon" />
              </svg>
            </div>
            <span class="stat-trend" :style="{ color: stat.color }">{{ stat.trend }}</span>
          </div>
          <div class="stat-body">
            <h3 class="stat-value">{{ stat.value }}</h3>
            <p class="stat-label">{{ stat.label }}</p>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <div class="card-header">
          <h3>API Usage (7 days)</h3>
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
                  <div class="bar-progress" :style="{ width: Math.min(100, (day.count / 100) * 100) + '%', backgroundColor: day.count > 70 ? 'var(--mso-accent, #2563eb)' : '#3b82f6' }"></div>
                </div>
                <div class="bar-value">{{ day.count }}</div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.public-dashboard {
  padding: 80px 20px;
  background-color: #f8fafc;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-header h2 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16px;
}

.section-header p {
  font-size: 1.125rem;
  color: #64748b;
  max-width: 600px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.1);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-trend {
  font-size: 0.875rem;
  font-weight: 600;
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 20px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.stat-label {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

.chart-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-header {
  margin-bottom: 24px;
}

.card-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.mock-chart-container {
  display: flex;
  height: 250px;
  position: relative;
  margin-top: 20px;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: 15px;
  color: #94a3b8;
  font-size: 0.75rem;
  border-right: 1px solid #e2e8f0;
}

.chart-bars-horizontal {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding-left: 10px;
  position: relative;
}

.chart-bars-horizontal::before,
.chart-bars-horizontal::after {
  content: '';
  position: absolute;
  left: 10px;
  right: 0;
  height: 1px;
  background-color: #f1f5f9;
  z-index: 0;
}

.chart-bars-horizontal::before {
  top: 50%;
}

.chart-bars-horizontal::after {
  top: 0;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
  z-index: 1;
  width: 40px;
}

.bar-track {
  width: 30px;
  height: calc(100% - 30px);
  background-color: transparent;
  display: flex;
  align-items: flex-end;
  border-radius: 4px 4px 0 0;
  overflow: hidden;
  margin-bottom: 8px;
}

.bar-progress {
  width: 100%;
  border-radius: 4px 4px 0 0;
  transition: height 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-label {
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 4px;
}

.bar-value {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.2s;
}

.bar-group:hover .bar-value {
  opacity: 1;
  color: #1e293b;
}

@media (max-width: 768px) {
  .public-dashboard {
    padding: 60px 16px;
  }
  
  .section-header h2 {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
