<script setup>
import { ref } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';

const selectedPeriod = ref('Last 30 Days');
const periods = ['Last 7 Days', 'Last 30 Days', 'Last Year', 'Custom'];

const metrics = [
  { label: 'Total API Requests', value: '4.2M', growth: '+15.4%', positive: true },
  { label: 'Data Consumption', value: '1.8 TB', growth: '+8.2%', positive: true },
  { label: 'Unique Users', value: '12.4k', growth: '-2.1%', positive: false },
  { label: 'Avg. Latency', value: '142ms', growth: '-12%', positive: true }
];

const topDatasets = [
  { name: 'สถิติประชากรกรุงเทพมหา... ', calls: '842k', trend: 60 },
  { name: 'ดัชนีราคาผู้บริโภคราย...', calls: '521k', trend: 45 },
  { name: 'รายงานคุณภาพน้ำประปา', calls: '312k', trend: 30 },
  { name: 'จำนวนผู้ประกันตนมาตรา 33', calls: '245k', trend: 20 }
];
</script>

<template>
  <div class="analytics-layout">
    <AppSidebar />
    
    <main class="analytics-content">
      <header class="content-header">
        <div class="header-titles">
          <h1>Usage Analytics</h1>
          <p>Monitor platform performance and data consumption.</p>
        </div>
        
        <div class="period-selector">
          <button 
            v-for="p in periods" 
            :key="p"
            :class="['period-btn', { active: selectedPeriod === p }]"
            @click="selectedPeriod = p"
          >{{ p }}</button>
        </div>
      </header>
      
      <div class="metrics-grid">
        <div v-for="metric in metrics" :key="metric.label" class="metric-card">
          <p class="metric-label">{{ metric.label }}</p>
          <div class="metric-main">
            <h2 class="metric-value">{{ metric.value }}</h2>
            <div :class="['growth-tag', metric.positive ? 'positive' : 'negative']">
              {{ metric.growth }}
            </div>
          </div>
          <div class="metric-chart">
            <svg viewBox="0 0 100 30" class="sparkline">
              <path 
                d="M0,25 L10,20 L20,22 L30,15 L40,18 L50,10 L60,12 L70,5 L80,8 L90,2 L100,5" 
                fill="none" 
                :stroke="metric.positive ? 'var(--mso-accent)' : '#ef4444'" 
                stroke-width="2"
              />
            </svg>
          </div>
        </div>
      </div>
      
      <div class="charts-grid">
        <div class="card chart-card main-chart">
          <div class="card-header">
            <h3>Consumption Volume over Time</h3>
            <div class="chart-legend">
              <span class="legend-item"><span class="dot api"></span> API Calls</span>
              <span class="legend-item"><span class="dot dl"></span> Downloads</span>
            </div>
          </div>
          <div class="bar-chart">
            <div v-for="n in 12" :key="n" class="bar-group">
              <div class="full-bar">
                <div class="bar-segment dl" :style="{ height: Math.floor(Math.random() * 30 + 10) + '%' }"></div>
                <div class="bar-segment api" :style="{ height: Math.floor(Math.random() * 40 + 20) + '%' }"></div>
              </div>
              <span class="bar-label">M{{ n }}</span>
            </div>
          </div>
        </div>
        
        <div class="card chart-card pie-chart-area">
          <h3>Data by Category</h3>
          <div class="pie-container">
            <div class="mock-pie">
              <div class="pie-segment s1"></div>
              <div class="pie-segment s2"></div>
              <div class="pie-segment s3"></div>
              <div class="pie-center"></div>
            </div>
            <div class="pie-legend">
              <div class="legend-row">
                <span class="dot s1"></span>
                <span>Health (42%)</span>
              </div>
              <div class="legend-row">
                <span class="dot s2"></span>
                <span>Economy (35%)</span>
              </div>
              <div class="legend-row">
                <span class="dot s3"></span>
                <span>Other (23%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card table-card">
        <h3>Most Popular Datasets</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Dataset Name</th>
              <th>Total Calls</th>
              <th>Usage Intensity</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in topDatasets" :key="item.name">
              <td class="name-cell">{{ item.name }}</td>
              <td>{{ item.calls }}</td>
              <td>
                <div class="progress-bg">
                  <div class="progress-fill" :style="{ width: item.trend + '%' }"></div>
                </div>
              </td>
              <td><span class="status-badge">Stable</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<style scoped>
.analytics-layout {
  display: flex;
  background-color: #f8fafc;
  min-height: 100vh;
}

.analytics-content {
  flex: 1;
  padding: 40px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.header-titles h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.header-titles p {
  color: #64748b;
}

.period-selector {
  display: flex;
  background: white;
  padding: 4px;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.period-btn {
  padding: 8px 16px;
  border: none;
  background: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.period-btn.active {
  background: #fdf2f8;
  color: var(--mso-accent);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.metric-card {
  background: white;
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.metric-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 12px;
  text-transform: uppercase;
}

.metric-main {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 20px;
}

.metric-value {
  font-size: 2rem;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
}

.growth-tag {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}

.growth-tag.positive { background: #fce7f3; color: var(--primary); }
.growth-tag.negative { background: #fee2e2; color: #ef4444; }

.metric-chart {
  height: 40px;
}

.sparkline {
  width: 100%;
  height: 100%;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.card {
  background: white;
  padding: 24px;
  border-radius: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.card h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8125rem;
  color: #64748b;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.api { background: var(--mso-accent); }
.dot.dl { background: #3b82f6; }

.bar-chart {
  height: 240px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 24px;
}

.bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.full-bar {
  width: 40%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  border-radius: 4px;
  overflow: hidden;
  background: #f8fafc;
}

.bar-segment {
  width: 100%;
}

.bar-segment.dl { background: #3b82f6; }
.bar-segment.api { background: var(--mso-accent); }

.bar-label {
  font-size: 0.75rem;
  color: #94a3b8;
}

.pie-chart-area {
  display: flex;
  flex-direction: column;
}

.pie-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 32px;
}

.mock-pie {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: #f1f5f9;
  position: relative;
  overflow: hidden;
}

.pie-segment {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transform-origin: center;
}

.pie-segment.s1 { background: var(--mso-accent); clip-path: polygon(50% 50%, 50% 0, 100% 0, 100% 80%); }
.pie-segment.s2 { background: #3b82f6; clip-path: polygon(50% 50%, 100% 80%, 100% 100%, 20% 100%); }
.pie-segment.s3 { background: #8b5cf6; clip-path: polygon(50% 50%, 20% 100%, 0 100%, 0 0, 50% 0); }

.pie-center {
  position: absolute;
  top: 25%;
  left: 25%;
  width: 50%;
  height: 50%;
  background: white;
  border-radius: 50%;
}

.dot.s1 { background: var(--mso-accent); }
.dot.s2 { background: #3b82f6; }
.dot.s3 { background: #8b5cf6; }

.legend-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.875rem;
  color: #475569;
  margin-bottom: 8px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 16px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  border-bottom: 1px solid #f1f5f9;
}

.data-table td {
  padding: 20px 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.9375rem;
}

.name-cell {
  font-weight: 600;
  color: #1e293b;
}

.progress-bg {
  width: 120px;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--mso-accent);
  border-radius: 4px;
}

.status-badge {
  background: #fdf2f8;
  color: #166534;
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 700;
}
</style>
