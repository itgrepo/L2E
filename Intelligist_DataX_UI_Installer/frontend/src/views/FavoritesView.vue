<script setup>
import { ref, onMounted } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';

const favoriteDatasets = ref([]);
const isLoading = ref(false);

onMounted(() => {
    favoriteDatasets.value = JSON.parse(localStorage.getItem('user_favorites') || '[]');
});

const removeFavorite = (id) => {
    favoriteDatasets.value = favoriteDatasets.value.filter(f => f.id !== id);
    localStorage.setItem('user_favorites', JSON.stringify(favoriteDatasets.value));
};
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div class="header-left">
          <h1>รายการโปรด (Favorites)</h1>
          <p class="subtitle">ชุดข้อมูลที่คุณบันทึกไว้เพื่อการเข้าถึงอย่างรวดเร็ว</p>
        </div>
      </header>

      <div v-if="favoriteDatasets.length === 0" class="card shadow-premium empty-state">
        <div class="empty-icon">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.921-1.103 1.821-1.891 1.118l-3.976-2.888a1 1 0 00-1.175 0l-3.976 2.888c-.788.703-2.191-.197-1.891-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        </div>
        <h2>ยังไม่มีรายการโปรด</h2>
        <p>คุณสามารถเพิ่มชุดข้อมูลเข้าสู่รายการโปรดได้จากการคลิกไอคอนดาวในหน้าแคตตาล็อก</p>
        <router-link to="/catalog" class="btn-primary mt-6">ไปที่ค้นหาชุดข้อมูล (Data Catalog)</router-link>
      </div>

      <div v-else class="datasets-list-vertical">
        <div v-for="ds in favoriteDatasets" :key="ds.id" class="ds-horizontal-card">
          <div class="ds-main-content">
            <div class="ds-header">
              <h4 class="ds-title">{{ ds.title }}</h4>
              <button class="btn-favorite is-active" @click.stop="removeFavorite(ds.id)">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.921-1.103 1.821-1.891 1.118l-3.976-2.888a1 1 0 00-1.175 0l-3.976 2.888c-.788.703-2.191-.197-1.891-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </button>
            </div>
            <p class="ds-description">{{ ds.description }}</p>
            <div class="ds-footer">
              <div class="ds-badges">
                <span class="badge access-open">{{ ds.accessibility }}</span>
                <span v-if="ds.api_enabled" :class="['badge', ds.api_type === 'private' ? 'format-api-private' : (ds.api_type === 'scope' ? 'format-api-scope' : 'format-api-public')]">
                  API: {{ ds.api_type === 'private' ? 'Private' : (ds.api_type === 'scope' ? 'Scope' : 'Public') }}
                </span>
                <span v-for="f in ds.formats ? ds.formats.filter(f => f.toUpperCase() !== 'API') : []" :key="f" class="badge format">{{ f }}</span>
              </div>
              <div class="ds-meta">
                <span class="agency">{{ ds.agency }}</span>
                <span class="separator">•</span>
                <span class="views">{{ ds.views }}</span>
                <span class="separator">•</span>
                <span class="updated">{{ ds.updated }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background-color: #f1f5f9;
}

.content {
  flex: 1;
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

h1 {
  font-size: 1.875rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.025em;
  margin-bottom: 4px;
}

.subtitle {
  color: #64748b;
  font-size: 0.9375rem;
}

.card {
  background: white;
  border-radius: 20px;
  padding: 80px 40px;
  text-align: center;
}

.shadow-premium {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: #f1f5f9;
  color: #94a3b8;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.empty-icon svg {
  width: 40px;
  height: 40px;
}

h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

p {
  color: #64748b;
  max-width: 400px;
  margin: 0 auto;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  background-color: #0f172a;
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  margin-top: 24px;
}

.btn-primary:hover {
  background-color: #1e293b;
  transform: translateY(-1px);
}

.datasets-list-vertical {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.ds-horizontal-card {
  background-color: white;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.2s;
  cursor: pointer;
}

.ds-horizontal-card:hover {
  border-color: var(--primary);
  box-shadow: 0 8px 16px rgba(0,0,0,0.05);
}

.ds-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.ds-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.btn-favorite {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  transition: all 0.2s;
}

.btn-favorite:hover {
  transform: scale(1.1);
  color: #eab308;
}

.btn-favorite.is-active {
  color: #eab308;
}

.ds-description {
  font-size: 0.9375rem;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 20px;
  max-width: 800px;
}

.ds-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ds-badges {
  display: flex;
  gap: 12px;
}

.badge {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
}

.access-open {
  background-color: var(--mso-pink-dark);
  color: var(--mso-accent);
}

.format {
  background-color: #f1f5f9;
  color: #3b82f6;
}

.format-api-public { background-color: #e0e7ff; color: #4338ca; }
.format-api-private { background-color: var(--mso-pink-dark); color: var(--primary-hover); }
.format-api-scope { background-color: #ffedd5; color: #c2410c; }

.ds-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.8125rem;
  color: #94a3b8;
}

.separator {
  opacity: 0.5;
}

.mt-6 {
  margin-top: 1.5rem;
}
</style>
