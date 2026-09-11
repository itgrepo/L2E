<script setup>
import { defineProps, ref, onMounted } from 'vue';
import apiClient from '../utils/api';

const props = defineProps({
  config: Object
});

const realStats = ref(null);

onMounted(async () => {
  try {
    const response = await apiClient.get('/dashboard/stats');
    if (response.data && response.data.status === 'success') {
      const hero = response.data.hero_stats;
      if (hero) {
        
        let apiCalls = hero.api_calls_count;
        let formattedApiCalls = apiCalls;
        if (apiCalls >= 1000000) {
           formattedApiCalls = (apiCalls / 1000000).toFixed(1) + 'M+';
        } else if (apiCalls >= 1000) {
           formattedApiCalls = (apiCalls / 1000).toFixed(1) + 'k+';
        }

        // We will map API data to the corresponding labels from config
        // Default mapping if config is missing
        realStats.value = [
          { num: hero.datasets_count.toString(), label: props.config?.stats?.[0]?.label || 'ชุดข้อมูลทั้งหมด' },
          { num: hero.organizations_count.toString(), label: props.config?.stats?.[1]?.label || 'หน่วยงานเครือข่าย' },
          { num: props.config?.stats?.[2]?.num || '99.9%', label: props.config?.stats?.[2]?.label || 'Uptime SLA' }, // Keep uptime from config as it's not in DB
          { num: formattedApiCalls.toString(), label: props.config?.stats?.[3]?.label || 'API Calls/เดือน' }
        ];
      }
    }
  } catch (error) {
    console.error('Failed to load real stats:', error);
  }
});
</script>

<template>
  <section class="stats-banner">
    <div class="container stats-banner-inner" v-if="(realStats && realStats.length) || (config?.stats && config.stats.length)">
      <div class="banner-stat" v-for="(stat, index) in (realStats || config.stats)" :key="index">
        <div class="b-num">{{ stat.num }}</div>
        <div class="b-label" style="opacity: 0.6">{{ stat.label }}</div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.stats-banner {
  background: var(--primary); /* Theme Primary */
  color: white;
  padding: 80px 0;
}

.stats-banner-inner {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  text-align: center;
}

.banner-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.b-num {
  font-size: 3.50rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.b-label {
  font-size: 1rem;
  font-weight: 500;
  opacity: 0.6;
}

@media (max-width: 1024px) {
  .stats-banner-inner { grid-template-columns: repeat(2, 1fr); gap: 2rem; }
}

@media (max-width: 768px) {
  .stats-banner { padding: 40px 0; }
  .stats-banner-inner { grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }
  .b-num { font-size: 2.5rem; }
  .b-label { font-size: 0.9rem; }
}
</style>
