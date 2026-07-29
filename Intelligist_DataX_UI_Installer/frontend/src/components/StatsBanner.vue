<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  config: Object
});
</script>

<template>
  <section class="stats-banner">
    <div class="container stats-banner-inner" v-if="config?.stats && config.stats.length">
      <div class="banner-stat" v-for="(stat, index) in config.stats" :key="index">
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
