<script setup>
import { ref, onMounted, defineProps } from 'vue';
import api from '../services/api';
import FeatureCard from './FeatureCard.vue';

const props = defineProps({
  config: Object
});

const features = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchFeatures = async () => {
  try {
    const response = await api.get('/features');
    if (Array.isArray(response.data)) {
      features.value = response.data;
    } else {
      throw new Error('Invalid response format');
    }
  } catch (err) {
    console.warn('Backend offline, using fallback data:', err);
    // Fallback to static data if API fails (optional, good for demo)
    features.value = [
      { id: 1, title: 'ค้นหาชุดข้อมูล', subtitle: 'ค้นหาข้อมูลที่คุณต้องการด้วยระบบที่ง่าย รวดเร็ว พร้อม metadata' },
      { id: 2, title: 'API Management', subtitle: 'จัดการ API Keys, ตั้งค่า Rate Limit และ Monitior การใช้งาน API ได้' },
      { id: 3, title: 'Data Integration', subtitle: 'เชื่อมต่อและบูรณาการข้อมูลผ่านระบบ ETL Pipeline พร้อม Validation & Transformation' },
      { id: 4, title: 'Usage Analytics', subtitle: 'ติดตามการใช้งาน API, ติดตามการดาวน์โหลด และ User Activity' },
      { id: 5, title: 'Data Governance', subtitle: 'จัดการนโยบายข้อมูล, สิทธิ์การเข้าถึงแบบ RBAC/ABAC และ Audit Trail' },
      { id: 6, title: 'Export & Download', subtitle: 'ดาวน์โหลดข้อมูลในรูปแบบ CSV, XLS หรือเชื่อมต่อผ่าน API ตามคุณต้องการ' }
    ];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchFeatures();
});
</script>

<template>
  <section class="features-section">
    <div class="container">
      <h5 style="color: #94a3b8; font-weight: 500; margin-bottom: 0.5rem; font-size: 0.9rem;">{{ config?.badge || 'Features' }}</h5>
      <h2 class="section-title">{{ config?.title || 'ความสามารถหลักของระบบ' }}</h2>
      <p class="section-subtitle">{{ config?.subtitle || 'ออกแบบมาเพื่อรองรับการแลกเปลี่ยนข้อมูลระหว่างหน่วยงานภาครัฐอย่างครบวงจร' }}</p>
      
      <div v-if="loading" class="text-center py-8">กำลังโหลดข้อมูล...</div>
      <div v-else class="features-grid">
        <FeatureCard 
          v-for="feat in features" 
          :key="feat.id"
          :title="feat.title"
          :subtitle="feat.subtitle"
        />
      </div>
    </div>
  </section>
</template>


<style scoped>
.features-section {
  padding: 60px 0;
  background: white;
}

.section-title {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.section-subtitle {
  color: var(--text-muted);
  margin-bottom: 4rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

@media (max-width: 1024px) {
  .features-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .features-section { padding: 40px 0; }
  .section-title { font-size: 1.8rem; }
  .section-subtitle { margin-bottom: 2rem; font-size: 0.95rem; }
  .features-grid { grid-template-columns: 1fr; gap: 1.5rem; }
}
</style>
