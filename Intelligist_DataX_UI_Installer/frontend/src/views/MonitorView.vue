<template>
  <div class="monitor-view p-6 bg-slate-50 min-h-screen">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 class="text-3xl font-black text-slate-800 tracking-tight flex items-center gap-3">
            <span class="p-2 bg-[var(--primary)] rounded-lg text-white">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </span>
            System Monitor & Logs
          </h1>
          <p class="text-slate-500 mt-1 font-medium ml-12">ตรวจสอบสถานะการทำงานและ Log ของระบบ Intelligist DataX</p>
        </div>
        <div class="flex gap-2 ml-12 md:ml-0">
          <div class="flex items-center gap-2 px-4 py-2 bg-emerald-100 text-emerald-700 rounded-full text-sm font-bold border border-emerald-200">
            <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
            System Healthy
          </div>
          <button @click="refreshLogs" class="p-2 bg-white rounded-lg border border-slate-200 shadow-sm hover:bg-slate-50 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div v-for="stat in stats" :key="stat.label" class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
          <p class="text-xs font-bold text-slate-400 uppercase mb-2 tracking-wider">{{ stat.label }}</p>
          <div class="flex items-end justify-between">
            <h3 class="text-2xl font-black text-slate-800">{{ stat.value }}</h3>
            <span :class="stat.trendClass" class="text-xs font-bold px-2 py-1 rounded-lg">
              {{ stat.trend }}
            </span>
          </div>
          <div class="mt-4 w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div :style="{ width: stat.percentage + '%' }" :class="stat.barClass" class="h-full rounded-full transition-all duration-1000"></div>
          </div>
        </div>
      </div>

      <!-- Main Content Split -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Logs Panel -->
        <div class="lg:col-span-2 bg-slate-900 rounded-2xl shadow-2xl overflow-hidden border border-slate-800 flex flex-col h-[600px]">
          <div class="bg-slate-800 px-6 py-4 flex items-center justify-between border-b border-slate-700">
            <div class="flex items-center gap-2">
              <div class="flex gap-1.5">
                <div class="w-3 h-3 rounded-full bg-red-500"></div>
                <div class="w-3 h-3 rounded-full bg-amber-500"></div>
                <div class="w-3 h-3 rounded-full bg-emerald-500"></div>
              </div>
              <span class="text-xs font-mono text-slate-400 ml-4">intelligist-datax-platform-logs.stdout</span>
            </div>
            <div class="flex gap-4">
              <span class="text-[10px] font-mono text-emerald-500">LIVE STREAMING</span>
            </div>
          </div>
          <div ref="logContainer" class="flex-1 p-6 overflow-y-auto font-mono text-sm space-y-2 custom-scrollbar">
            <div v-for="(log, index) in visibleLogs" :key="index" class="flex gap-4">
              <span class="text-slate-600 select-none w-12 text-right">{{ index + 1 }}</span>
              <span :class="getLogClass(log.type)" class="flex-1 break-all">
                <span class="text-slate-500 mr-2">[{{ log.time }}]</span>
                <span class="font-bold mr-2 uppercase">[{{ log.type }}]</span>
                {{ log.message }}
              </span>
            </div>
          </div>
        </div>

        <!-- System Health Sidebar -->
        <div class="space-y-6">
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
            <h3 class="text-lg font-bold text-slate-800 mb-6">Service Status</h3>
            <div class="space-y-4">
              <div v-for="service in services" :key="service.name" class="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors">
                <div class="flex items-center gap-3">
                  <div :class="service.status === 'online' ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'" class="p-2 rounded-lg">
                    <svg v-if="service.status === 'online'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                  </div>
                  <div>
                    <p class="text-sm font-bold text-slate-700">{{ service.name }}</p>
                    <p class="text-[10px] text-slate-400 font-medium uppercase">{{ service.port }}</p>
                  </div>
                </div>
                <span :class="service.status === 'online' ? 'text-emerald-500' : 'text-red-500'" class="text-[10px] font-black uppercase tracking-tighter">
                  {{ service.status }}
                </span>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-[var(--primary)] to-[var(--primary-hover)] p-6 rounded-2xl shadow-lg text-white">
            <h3 class="text-lg font-bold mb-2">Intelligist DataX Quick Action</h3>
            <p class="text-xs text-pink-100 mb-6 opacity-80">จัดการบริการพื้นฐานของระบบได้อย่างรวดเร็ว</p>
            <div class="grid grid-cols-2 gap-3">
              <button class="bg-white/10 hover:bg-white/20 p-3 rounded-xl text-center transition-all">
                <p class="text-xs font-bold">Restart API</p>
              </button>
              <button class="bg-white/10 hover:bg-white/20 p-3 rounded-xl text-center transition-all">
                <p class="text-xs font-bold">Flush Cache</p>
              </button>
              <button class="bg-white/10 hover:bg-white/20 p-3 rounded-xl text-center transition-all col-span-2 mt-2 border border-white/20">
                <p class="text-xs font-bold">Download Full System Logs</p>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const stats = ref([
  { label: 'CPU Usage', value: '12.4%', trend: '-2.1%', trendClass: 'bg-emerald-50 text-emerald-600', percentage: 12, barClass: 'bg-pink-500' },
  { label: 'Memory', value: '1.42 GB', trend: '+0.5%', trendClass: 'bg-amber-50 text-amber-600', percentage: 45, barClass: 'bg-[var(--primary)]' },
  { label: 'Network In', value: '240 KB/s', trend: 'Stable', trendClass: 'bg-slate-50 text-slate-600', percentage: 15, barClass: 'bg-pink-400' },
  { label: 'Active Tasks', value: '24', trend: '+4', trendClass: 'bg-emerald-50 text-emerald-600', percentage: 60, barClass: 'bg-pink-700' },
]);

const services = ref([
  { name: 'Intelligist DataX API Service', port: 'PORT 3000', status: 'online' },
  { name: 'Intelligist DataX Portal Web', port: 'PORT 3001', status: 'online' },
  { name: 'MariaDB Instance', port: 'PORT 3307', status: 'online' },
  { name: 'Redis Cache', port: 'INTERNAL', status: 'online' },
  { name: 'SMTP Relay', port: 'PORT 465', status: 'online' },
]);

const mockLogMessages = [
  { type: 'info', message: 'API Request: GET /api/v1/datasets/stats' },
  { type: 'info', message: 'User "admin" logged in from 10.20.31.31' },
  { type: 'success', message: 'Successfully imported dataset: POP-001_v2' },
  { type: 'warning', message: 'Slow query detected in psu_backend.activity_log (1.2s)' },
  { type: 'info', message: 'Auto-sync completed for 12 data sources' },
  { type: 'info', message: 'Cleaning up temporary upload buffers...' },
  { type: 'success', message: 'System Health Check passed' },
  { type: 'info', message: 'New link configuration added: intelligist-datax-dashboard-2566' },
];

const visibleLogs = ref([]);
const logContainer = ref(null);
let logInterval = null;

const addLog = () => {
  const mock = mockLogMessages[Math.floor(Math.random() * mockLogMessages.length)];
  const now = new Date();
  const time = now.toTimeString().split(' ')[0];
  
  visibleLogs.value.push({
    time,
    type: mock.type,
    message: mock.message
  });

  if (visibleLogs.value.length > 100) {
    visibleLogs.value.shift();
  }

  // Auto scroll
  setTimeout(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight;
    }
  }, 50);
};

const getLogClass = (type) => {
  switch (type) {
    case 'info': return 'text-slate-300';
    case 'success': return 'text-emerald-400';
    case 'warning': return 'text-amber-400';
    case 'error': return 'text-red-400';
    default: return 'text-slate-400';
  }
};

const refreshLogs = () => {
  visibleLogs.value = [];
  for (let i = 0; i < 15; i++) addLog();
};

onMounted(() => {
  refreshLogs();
  logInterval = setInterval(addLog, 3000);
});

onUnmounted(() => {
  if (logInterval) clearInterval(logInterval);
});
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
