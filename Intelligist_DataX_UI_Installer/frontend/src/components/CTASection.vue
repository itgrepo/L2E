<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  config: Object
});
</script>

<template>
  <section class="cta-section">
    <div class="container cta-container">
      <div class="cta-box">
        <h2 class="cta-title">{{ config?.title || 'พร้อมเริ่มต้นแลกเปลี่ยนข้อมูลแล้วหรือยัง?' }}</h2>
        <p class="cta-desc">{{ config?.subtitle || 'สมัครสมาชิกวันนี้เพื่อเข้าถึงชุดข้อมูลจากหน่วยงานรัฐทั่วประเทศ' }}</p>
        <div class="cta-actions">
          <button class="btn btn-primary btn-lg cta-btn-primary">{{ config?.btnPrimary || 'สมัครสมาชิกฟรี' }}</button>
          <button class="btn btn-outline btn-lg cta-btn-outline">{{ config?.btnSecondary || 'ดูเอกสาร API' }}</button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cta-section {
  padding: 100px 0;
  background: white;
}

.cta-box {
  background: #f1f5f9;
  border-radius: var(--radius-xl);
  padding: 4rem 2rem;
  text-align: center;
}

.cta-title {
  font-size: 1.8rem;
  margin-bottom: 1rem;
}

.cta-desc {
  color: var(--text-muted);
  margin-bottom: 2rem;
}

.cta-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.cta-btn-primary {
  border-radius: 20px;
  background: var(--primary);
}

.cta-btn-outline {
  border-radius: 20px;
}

@media (max-width: 768px) {
  .cta-section { padding: 40px 0; }
  .cta-box { padding: 2.5rem 1.5rem; }
  .cta-title { font-size: 1.5rem; }
  .cta-actions { flex-direction: column; width: 100%; }
  .cta-actions .btn { width: 100%; justify-content: center; }
}
</style>
