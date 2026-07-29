<script setup>
defineProps({
  title: String,
  subtitle: String
});
</script>

<template>
  <div class="feature-card">
    <div class="feat-icon-area">
      <div class="circle-icon"></div>
    </div>
    <h4 class="feat-title">{{ title }}</h4>
    <p class="feat-desc">{{ subtitle }}</p>
  </div>
</template>

<style scoped>
.feature-card {
  padding: 2rem;
  background: var(--bg-main);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  transition: all 0.3s ease;
}

.feature-card:hover {
  background: white;
  box-shadow: var(--shadow-md);
  border-color: #cbd5e1;
}

.feat-icon-area {
  margin-bottom: 1.25rem;
}

.circle-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background-color: var(--primary);
  opacity: 0.8;
}

.feat-title {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.feat-desc {
  font-size: 0.9rem;
  color: var(--text-muted);
  line-height: 1.6;
}
</style>
