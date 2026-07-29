<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import intelligistDataxLogo from '../assets/logo.svg';
import { themeConfig } from '../utils/theme';

const router = useRouter();
const isAuthenticated = ref(false);
const isMobileMenuOpen = ref(false);

const checkAuth = () => {
  isAuthenticated.value = !!localStorage.getItem('user');
};

const handleLogout = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  isAuthenticated.value = false;
  isMobileMenuOpen.value = false;
  window.dispatchEvent(new Event('auth-change'));
  router.push('/');
};

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};

onMounted(() => {
  checkAuth();
  window.addEventListener('storage', checkAuth);
  window.addEventListener('auth-change', checkAuth);
});
</script>

<template>
  <header class="navbar">
    <div class="container nav-inner">
      <router-link to="/" class="logo-group">
        <img v-if="themeConfig.logoUrl" :src="themeConfig.logoUrl" alt="Logo" class="intelligist-datax-logo" />
        <span class="logo-text">{{ themeConfig.siteName }}</span>
      </router-link>
      <nav class="nav-links">
        <router-link to="/" active-class="active">หน้าแรก</router-link>
        <router-link to="/catalog" active-class="active">บัญชีข้อมูล</router-link>
        <router-link to="/analytics" active-class="active">วิเคราะห์</router-link>
        <router-link to="/about" active-class="active">เกี่ยวกับเรา</router-link>
        <router-link to="/contact" active-class="active">ติดต่อเรา</router-link>
      </nav>
      <div class="nav-actions">
        <router-link v-if="!isAuthenticated" to="/login" class="btn-navbar btn-login">เข้าสู่ระบบ</router-link>
        <button v-else @click="handleLogout" class="btn-navbar btn-logout">ออกจากระบบ</button>
      </div>
      
      <!-- Mobile menu button -->
      <button class="mobile-menu-btn" @click="toggleMobileMenu">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
    </div>

    <!-- Sticky Side Tab for Mobile -->
    <button class="mobile-side-tab" @click="toggleMobileMenu" aria-label="Open menu">
      <div class="tab-indicator"></div>
    </button>

    <!-- Mobile Menu Overlay -->
    <div v-if="isMobileMenuOpen" class="mobile-menu-overlay" @click="closeMobileMenu"></div>
    <div :class="['mobile-menu', { 'open': isMobileMenuOpen }]">
      <div class="mobile-menu-header">
        <div class="logo-group">
          <img v-if="themeConfig.logoUrl" :src="themeConfig.logoUrl" alt="Logo" class="intelligist-datax-logo-small" />
          <span class="logo-text">{{ themeConfig.siteName }}</span>
        </div>
        <button class="close-menu-btn" @click="closeMobileMenu">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <nav class="mobile-nav-links">
        <router-link to="/" active-class="active" @click="closeMobileMenu">หน้าแรก</router-link>
        <router-link to="/catalog" active-class="active" @click="closeMobileMenu">บัญชีข้อมูล</router-link>
        <router-link to="/analytics" active-class="active" @click="closeMobileMenu">วิเคราะห์</router-link>
        <router-link to="/about" active-class="active" @click="closeMobileMenu">เกี่ยวกับเรา</router-link>
        <router-link to="/contact" active-class="active" @click="closeMobileMenu">ติดต่อเรา</router-link>
      </nav>
      <div class="mobile-nav-actions">
        <router-link v-if="!isAuthenticated" to="/login" class="btn-navbar btn-login" @click="closeMobileMenu">เข้าสู่ระบบ</router-link>
        <button v-else @click="handleLogout" class="btn-navbar btn-logout">ออกจากระบบ</button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-light);
  width: 100%;
}

.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100px;
  transition: all 0.3s ease;
}

.logo-group {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  text-decoration: none;
}

.intelligist-datax-logo {
  height: 70px; /* Increased from 60px */
  width: auto;
  transition: height 0.3s ease;
}

.intelligist-datax-logo-small {
  height: 45px;
  width: auto;
}

.logo-text {
  font-weight: 800;
  font-size: 1.8rem;
  color: var(--primary);
  letter-spacing: -0.5px;
  white-space: nowrap;
}

.nav-links {
  display: flex;
  gap: 2.5rem;
}

.nav-links a {
  font-weight: 600;
  font-size: 0.95rem;
  color: #1e293b;
  transition: color 0.2s;
}

.nav-links a:hover,
.nav-links a.active {
  color: var(--primary);
}

.nav-actions {
  display: flex;
  gap: 1rem;
}

.btn-navbar {
  padding: 10px 25px;
  border-radius: 25px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  background: none;
  transition: all 0.2s;
}

.btn-login {
  border: 1.5px solid var(--primary);
  color: var(--primary);
}

.btn-login:hover {
  background-color: var(--primary);
  color: white;
}

.btn-logout {
  border: 1.5px solid var(--primary);
  color: var(--primary);
}

.btn-logout:hover {
  background-color: var(--primary);
  color: white;
}

.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  color: #1e293b;
  cursor: pointer;
  padding: 0.5rem;
}

/* Sticky Side Tab for Mobile */
.mobile-side-tab {
  display: none;
  position: fixed;
  top: 50%;
  left: 0;
  transform: translateY(-50%);
  width: 24px;
  height: 80px;
  background-color: var(--primary);
  border-radius: 0 12px 12px 0;
  border: none;
  box-shadow: 4px 0 15px rgba(0, 0, 0, 0.2);
  z-index: 2001; /* High enough to be visible */
  cursor: pointer;
  padding: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  align-items: center;
  justify-content: center;
}

.tab-indicator {
  width: 3px;
  height: 30px;
  background-color: rgba(255, 255, 255, 0.6);
  border-radius: 2px;
}

.mobile-side-tab:active {
  width: 30px;
}

.mobile-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2999;
  backdrop-filter: blur(4px);
}

.mobile-menu {
  position: fixed;
  top: 0;
  right: 0;
  width: 85%;
  max-width: 320px;
  height: 100vh;
  background: white;
  z-index: 3000;
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.1);
  visibility: hidden;
}

.mobile-menu.open {
  transform: translateX(0);
  visibility: visible;
}

@media (max-width: 1024px) {
  .nav-links { gap: 1.5rem; }
  .logo-text { font-size: 1.2rem; }
}

@media (max-width: 768px) {
  .navbar {
    position: fixed;
  }
  
  .nav-inner {
    height: 70px;
  }
  
  .intelligist-datax-logo {
    height: 45px;
  }
  
  .logo-text {
    font-size: 1.1rem;
  }
  
  .nav-links, .nav-actions { display: none; }
  .mobile-menu-btn { display: block; }
  .mobile-side-tab { display: flex; }
}

:global(body) {
  overflow-x: hidden !important;
  width: 100%;
}

.mobile-menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-light);
}

.close-menu-btn {
  background: none;
  border: none;
  color: #1e293b;
  cursor: pointer;
  padding: 0.5rem;
}

.mobile-nav-links {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.mobile-nav-links a {
  font-weight: 600;
  font-size: 1.1rem;
  color: #1e293b;
  text-decoration: none;
  padding: 0.5rem 0;
  transition: all 0.2s;
}

.mobile-nav-links a.active {
  color: var(--primary);
  padding-left: 0.5rem;
  border-left: 3px solid var(--primary);
}

.mobile-nav-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: auto;
}

.mobile-nav-actions .btn-navbar {
  width: 100%;
  text-align: center;
}
</style>
