<script setup>
import { ref, onMounted, defineProps } from 'vue';
import api from '../services/api';

const props = defineProps({
  config: Object
});

const steps = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchSteps = async () => {
  try {
    const response = await api.get('/steps');
    if (Array.isArray(response.data)) {
      steps.value = response.data;
    } else {
      throw new Error('Invalid response format');
    }
  } catch (err) {
    console.warn('Backend offline, using fallback data:', err);
    // Fallback static data
    steps.value = [
      { number: 1, title: 'สมัครสมาชิก', desc: 'ลงทะเบียนด้วยอีเมลหน่วยงาน หรือเข้าสู่ระบบผ่าน SSO' },
      { number: 2, title: 'ค้นหาข้อมูล', desc: 'เรียกดูชุดข้อมูลจาก Catalog หรือค้นหาด้วย Keyword' },
      { number: 3, title: 'ขอสิทธิ์เข้าถึง', desc: 'ยื่นคำร้องเข้าถึงข้อมูลระดับ Field ที่ต้องการ' },
      { number: 4, title: 'ใช้งานข้อมูล', desc: 'ดาวน์โหลดหรือเชื่อมต่อนำ API เพื่อนำไปใช้งาน' }
    ];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchSteps();
});
</script>

<template>
  <section class="steps-section">
    <div class="container">
      <h5 style="color: #94a3b8; font-weight: 500; margin-bottom: 0.5rem; font-size: 0.9rem;">{{ config?.badge || 'How it works' }}</h5>
      <h2 class="section-title">{{ config?.title || 'เริ่มใช้งานได้ง่ายๆ' }}</h2>
      <p class="section-subtitle">{{ config?.subtitle || 'เพียง 4 ขั้นตอนก็สามารถเข้าถึงข้อมูลที่ต้องการ' }}</p>

      <div v-if="loading" class="text-center py-8">กำลังโหลดข้อมูล...</div>
      <div v-else class="steps-container">
        <div class="steps-line"></div>
        <div class="step-item" v-for="step in steps" :key="step.number">
          <div :class="['step-circle', { 'active-step': step.number === 1 || step.number === 2 }]">{{ step.number }}</div>
          <h4 class="step-title">{{ step.title }}</h4>
          <p class="step-desc">{{ step.desc }}</p>
        </div>
      </div>
    </div>
  </section>
</template>


<style scoped>
.steps-section {
  padding: 100px 0;
  background: #f8fafc;
}

.section-title {
  font-size: 2.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: #1e293b;
}

.section-subtitle {
  color: #64748b;
  margin-bottom: 5rem;
  font-size: 1.1rem;
}

.steps-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  position: relative;
  text-align: center;
}

.steps-line {
  position: absolute;
  top: 25px;
  left: 10%;
  right: 10%;
  height: 2px;
  background-image: linear-gradient(to right, var(--primary) 50%, transparent 50%);
  background-size: 12px 2px;
  background-repeat: repeat-x;
  z-index: 1;
}

.step-item {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.step-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 2rem;
  color: white;
  transition: all 0.3s ease;
}

/* Specific colors from Figma */
.step-item:nth-child(2) .step-circle,
.step-item:nth-child(3) .step-circle,
.step-item:nth-child(4) .step-circle {
  background-color: var(--primary); /* Steps 1-3 Primary */
}

.step-item:nth-child(5) .step-circle {
  background-color: var(--mso-accent); /* Step 4 Accent */
}

.step-title {
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: #1e293b;
}

.step-desc {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.6;
  padding: 0 0.5rem;
}

@media (max-width: 1024px) {
  .steps-container { grid-template-columns: repeat(2, 1fr); gap: 4rem; }
  .steps-line { display: none; }
}

@media (max-width: 768px) {
  .steps-section { padding: 40px 0; }
  .section-title { font-size: 1.8rem; }
  .section-subtitle { margin-bottom: 2rem; font-size: 0.95rem; }
  .steps-container { grid-template-columns: 1fr; gap: 2rem; }
  .step-circle { margin-bottom: 1rem; }
}
</style>
