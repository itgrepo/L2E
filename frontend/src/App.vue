<script setup>
import { onMounted, onUnmounted } from 'vue';
import { RouterView, useRouter } from 'vue-router';
import AppNavbar from './components/AppNavbar.vue';
import AppFooter from './components/AppFooter.vue';
import ThemeWidget from './components/ThemeWidget.vue';
import { applyTheme, loadThemeFromServer } from './utils/theme';
import { loadLayoutFromServer } from './utils/pageBuilder';

const router = useRouter();
const IDLE_TIME_LIMIT = 30 * 60 * 1000; // 30 minutes in milliseconds
let checkInterval = null;
let isThrottled = false;

const handleSessionTimeout = () => {
  if (localStorage.getItem('user')) {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('lastActivity');
    localStorage.removeItem('user_favorites');
    sessionStorage.clear();
    window.dispatchEvent(new Event('auth-change'));
    alert('เซสชันของคุณหมดอายุเนื่องจากไม่มีการใช้งานเป็นเวลา 30 นาที กรุณาเข้าสู่ระบบใหม่');
    window.location.href = '/login';
  }
};

const updateActivity = () => {
  if (localStorage.getItem('user')) {
    if (!isThrottled) {
      localStorage.setItem('lastActivity', Date.now().toString());
      isThrottled = true;
      setTimeout(() => { isThrottled = false; }, 5000); // Throttle writes to every 5 seconds
    }
  }
};

const checkIdleStatus = () => {
  if (localStorage.getItem('user')) {
    const lastActivity = parseInt(localStorage.getItem('lastActivity') || '0', 10);
    const now = Date.now();
    if (lastActivity > 0 && (now - lastActivity > IDLE_TIME_LIMIT)) {
      handleSessionTimeout();
    }
  }
};

const setupIdleListeners = () => {
  if (localStorage.getItem('user')) {
    localStorage.setItem('lastActivity', Date.now().toString());
  }
  const events = ['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll', 'click'];
  events.forEach(event => {
    window.addEventListener(event, updateActivity, { passive: true });
  });
  
  // Check every 30 seconds
  checkInterval = setInterval(checkIdleStatus, 30000);
  
  // Check immediately on focus (wake up from sleep)
  window.addEventListener('focus', checkIdleStatus);
};

const cleanupIdleListeners = () => {
  const events = ['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll', 'click'];
  events.forEach(event => {
    window.removeEventListener(event, updateActivity);
  });
  window.removeEventListener('focus', checkIdleStatus);
  if (checkInterval) clearInterval(checkInterval);
};

onMounted(() => {
  applyTheme();
  loadThemeFromServer();
  loadLayoutFromServer();
  
  // Initialize idle timeout mechanism
  setupIdleListeners();
});

onUnmounted(() => {
  cleanupIdleListeners();
});
</script>

<template>
  <div class="app-layout">
    <AppNavbar />
    
    <main class="app-main-content">
      <router-view :key="$route.fullPath" />
    </main>

    <AppFooter />
    <ThemeWidget />
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
}

.app-main-content {
  flex: 1 0 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: 100%;
}

/* Padding to prevent content from going under fixed navbar on mobile */
@media (max-width: 768px) {
  .app-layout {
    width: 100vw !important;
    max-width: 100vw !important;
    min-width: 0 !important;
    overflow-x: hidden !important;
  }
  .app-main-content {
    width: 100% !important;
    max-width: 100vw !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
  }
}
</style>
