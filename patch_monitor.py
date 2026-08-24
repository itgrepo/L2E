import sys

path = "/Users/natthawutjantakul/intelligist_dataX/frontend/src/views/MonitorView.vue"
with open(path, "r") as f:
    content = f.read()

script_start = content.find("<script setup>")
script_end = content.find("</script>", script_start) + len("</script>")

new_script = """<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const stats = ref([
  { label: 'CPU Usage', value: '0%', trend: 'Stable', trendClass: 'bg-emerald-50 text-emerald-600', percentage: 0, barClass: 'bg-pink-500' },
  { label: 'Memory', value: '0 GB', trend: 'Stable', trendClass: 'bg-amber-50 text-amber-600', percentage: 0, barClass: 'bg-[var(--primary)]' },
  { label: 'Network In', value: '0 KB/s', trend: 'Stable', trendClass: 'bg-slate-50 text-slate-600', percentage: 0, barClass: 'bg-pink-400' },
  { label: 'Active Tasks', value: '0', trend: 'Stable', trendClass: 'bg-emerald-50 text-emerald-600', percentage: 0, barClass: 'bg-pink-700' },
]);

const services = ref([
  { name: 'DataX API Service', port: 'PORT 3000', status: 'online' },
  { name: 'DataX Portal Web', port: 'PORT 3001', status: 'online' },
  { name: 'MariaDB Instance', port: 'PORT 3307', status: 'online' },
  { name: 'Redis Cache', port: 'INTERNAL', status: 'online' },
  { name: 'SMTP Relay', port: 'PORT 465', status: 'online' },
]);

const visibleLogs = ref([]);
const logContainer = ref(null);
let logInterval = null;

const getLogClass = (type) => {
  switch (type) {
    case 'info': return 'text-slate-300';
    case 'success': return 'text-emerald-400';
    case 'warning': return 'text-amber-400';
    case 'error': return 'text-red-400';
    default: return 'text-slate-400';
  }
};

const fetchRealStats = async () => {
  try {
    const res = await fetch('/api/monitor/stats');
    if (!res.ok) return;
    const data = await res.json();
    
    if (data.status === 'success') {
      // Update stats
      stats.value[0].value = data.stats.cpu;
      stats.value[0].percentage = data.stats.cpu_val;
      
      stats.value[1].value = data.stats.mem;
      stats.value[1].percentage = data.stats.mem_val;
      
      stats.value[2].value = data.stats.net;
      stats.value[2].percentage = data.stats.net_val;
      
      stats.value[3].value = data.stats.tasks.toString();
      stats.value[3].percentage = (data.stats.tasks / 100) * 100;
      
      // Update logs (reverse them so newest is at the bottom, or just replace)
      // The API returns newest first (DESC), so we reverse to put newest at bottom
      visibleLogs.value = data.logs.reverse();
      
      // Auto scroll
      setTimeout(() => {
        if (logContainer.value) {
          logContainer.value.scrollTop = logContainer.value.scrollHeight;
        }
      }, 50);
    }
  } catch (error) {
    console.error("Monitor fetch error:", error);
  }
};

onMounted(() => {
  fetchRealStats();
  logInterval = setInterval(fetchRealStats, 3000); // Fetch real data every 3 seconds
});

onUnmounted(() => {
  if (logInterval) clearInterval(logInterval);
});
</script>"""

new_content = content[:script_start] + new_script + content[script_end:]
with open(path, "w") as f:
    f.write(new_content)
print("Patched MonitorView.vue")
