<script setup>
import { defineProps } from 'vue';
import HeroMockup from './HeroMockup.vue';

const props = defineProps({
  config: Object
});
</script>

<template>
  <section class="hero blur-bg">
    <div class="container hero-grid">
      <div class="hero-content">
        <div class="badge-wrapper">
          <span class="badge">{{ config?.badge || 'MSDHS DATA PORTAL' }}</span>
        </div>
        <h1 class="hero-title" v-html="config?.title || 'ศูนย์กลางบัญชีข้อมูล<br/>สวัสดิการสังคมและสิทธิมนุษยชน'"></h1>
        <p class="hero-desc" v-html="config?.desc || 'แพลตฟอร์มบริหารจัดการและแลกเปลี่ยนข้อมูล พม.<br/>อย่างปลอดภัย มีมาตรฐาน พร้อมระบบวิเคราะห์ข้อมูลเชิงลึก'"></p>
        <div class="hero-buttons">
          <button class="btn btn-primary btn-lg" style="border-radius: 20px; background-color: var(--primary); border-color: var(--primary);">{{ config?.btnPrimary || 'เริ่มต้นใช้งาน →' }}</button>
          <button class="btn btn-outline btn-lg" style="border-radius: 20px; color: var(--primary); border-color: var(--primary);">{{ config?.btnSecondary || 'เรียนรู้เพิ่มเติม' }}</button>
        </div>
        <div class="hero-stats" v-if="config?.stats && config.stats.length">
          <div class="stat-block" v-for="(stat, index) in config.stats" :key="index">
            <span class="stat-num">{{ stat.num }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>

      </div>
      
      <HeroMockup />
    </div>
  </section>
</template>

<style scoped>
.hero {
  padding: 80px 0 100px;
  overflow: hidden;
  position: relative;
}

.hero::before {
  content: '';
  position: absolute;
  top: -100px;
  right: -10%;
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(186, 26, 93, 0.08) 0%, rgba(248, 250, 252, 0) 70%);
  z-index: -1;
  border-radius: 50%;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.badge-wrapper {
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: 3.2rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1.5rem;
  color: var(--text-main);
  letter-spacing: -0.5px;
}

.hero-desc {
  font-size: 1.1rem;
  color: var(--text-muted);
  margin-bottom: 2.5rem;
  line-height: 1.8;
}

.hero-buttons {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.hero-stats {
  display: flex;
  gap: 3rem;
}

.stat-block {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 1.8rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-muted);
}

@media (max-width: 1024px) {
  .hero-grid { grid-template-columns: 1fr; text-align: center; }
  .badge-wrapper { display: flex; justify-content: center; }
  .hero-buttons { justify-content: center; }
  .hero-stats { justify-content: center; }
}

@media (max-width: 768px) {
  .hero { padding: 40px 0 60px; }
  .hero-title { font-size: 2.2rem; }
  .hero-desc { font-size: 1rem; }
  .hero-buttons { flex-direction: column; width: 100%; gap: 1rem; }
  .hero-buttons .btn { width: 100%; justify-content: center; }
  
  .hero-stats { 
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
    max-width: 300px;
    margin: 0 auto;
    text-align: center;
  }
  
  .stat-num { font-size: 1.5rem; }
}

@media (max-width: 480px) {
  .hero-title { font-size: 1.8rem; line-height: 1.3; }
  .hero-desc { font-size: 0.9rem; line-height: 1.6; }
  .stat-block { flex: 1 1 100%; }
  .hero-stats { grid-template-columns: 1fr; }
}
</style>
