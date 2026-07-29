<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import intelligistDataxLogo from '../assets/intelligist-datax-logo.png';
import { themeConfig } from '../utils/theme';

const isSettingsExpanded = ref(false);
const isMobileMenuOpen = ref(false);
const userName = ref('User');
const userRole = ref('Guest');
const isAdmin = ref(false);
const route = useRoute();
const router = useRouter();

const checkSettingsExpanded = (currentPath) => {
  const isSettingRoute = settingItems.some(item => currentPath === item.path);
  if (isSettingRoute) {
    isSettingsExpanded.value = true;
  }
};

// Close mobile sidebar on route change & auto-expand settings
watch(route, (newRoute) => {
  isMobileMenuOpen.value = false;
  checkSettingsExpanded(newRoute.path);
});

onMounted(() => {
  const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
  if (savedUser.firstname) {
    userName.value = `${savedUser.firstname} ${savedUser.lastname || ''}`;
    userRole.value = savedUser.role || (savedUser.isAdmin === 'true' || savedUser.isAdmin === true ? 'Administrator' : 'User');
    isAdmin.value = savedUser.isAdmin === 'true' || savedUser.isAdmin === true || String(savedUser.previlage_id) !== '3';
  }
  checkSettingsExpanded(route.path);
});

const toggleSettings = () => {
  isSettingsExpanded.value = !isSettingsExpanded.value;
  if (isSettingsExpanded.value) {
    router.push('/permission-management');
  }
};

const handleLogout = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
  window.dispatchEvent(new Event('auth-change'));
  window.location.href = '/';
};

const menuItems = [
  { name: 'หน้าหลัก', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', path: '/dashboard' },
  { name: 'บัญชีข้อมูล', icon: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4', path: '/catalog' },
  { name: 'รายการโปรด', icon: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.921-1.103 1.821-1.891 1.118l-3.976-2.888a1 1 0 00-1.175 0l-3.976 2.888c-.788.703-2.191-.197-1.891-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z', path: '/favorites' },
];

const toolItems = [
  { name: 'API Management', icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z', path: '/api-management' },
  { name: 'API Monitor', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10', path: '/api-monitor' },
  { name: 'User Management', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z', path: '/user-management' },
  { name: 'ติดตามสิทธิ์ข้อมูล', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1', path: '/dataset-permission-monitor' },
  { name: 'อนุมัติสมาชิก', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', path: '/user-approval' },
  { name: 'Analytics', icon: 'M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z', path: '/analytics' },
  { name: 'Monitor & Logs', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10', path: '/monitor' },
];

const settingItems = [
  { name: 'Permission Management', icon: 'M2 12h20 M12 2v20 M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z', path: '/permission-management' },
  { name: 'Group User Management', icon: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2 M9 7a4 4 0 100-8 4 4 0 000 8 M23 21v-2a4 4 0 00-3-3.87 M16 3.13a4 4 0 010 7.75', path: '/group-user-management' },
  { name: 'Dataset Management', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2 M9 5a2 2 0 002 2h2a2 2 0 012 2v10', path: '/dataset-management' },
  { name: 'Organization Management', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4', path: '/organization-management' },
  { name: 'Category Management', icon: 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z', path: '/category-management' },
  { name: 'Group Dataset Management', icon: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z', path: '/group-dataset-management' },
];
</script>

<template>
  <div class="sidebar-container">
    <!-- Floating Action Button for Mobile -->
    <button class="mobile-sidebar-toggle" @click="isMobileMenuOpen = !isMobileMenuOpen">
      <span></span>
    </button>

    <!-- Overlay Backdrop -->
    <div v-if="isMobileMenuOpen" class="sidebar-overlay" @click="isMobileMenuOpen = false"></div>

    <aside class="app-sidebar" :class="{ 'is-open': isMobileMenuOpen }">
      <div class="sidebar-logo">
        <div class="logo-group">
          <img :src="themeConfig.logoUrl || intelligistDataxLogo" alt="Logo" class="sidebar-intelligist-datax-logo" />
          <span class="logo-text">{{ themeConfig.siteName }}</span>
        </div>
        <!-- Close button for mobile -->
        <button class="mobile-close-sidebar" @click="isMobileMenuOpen = false">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    
    <nav class="sidebar-nav">
      <div class="nav-section">หลัก</div>
      <router-link 
        v-for="item in menuItems" 
        :key="item.name"
        :to="item.path"
        class="nav-item"
        exact-active-class="active"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
        </svg>
        <span>{{ item.name }}</span>
      </router-link>

      <div v-if="toolItems.filter(item => isAdmin || ['/api-management'].includes(item.path)).length > 0" class="nav-section">เครื่องมือ</div>
      <router-link 
        v-for="item in toolItems.filter(item => isAdmin || ['/api-management'].includes(item.path))" 
        :key="item.name"
        :to="item.path"
        class="nav-item"
        exact-active-class="active"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
        </svg>
        <span>{{ item.name }}</span>
      </router-link>

      <div v-if="isAdmin" class="nav-section">การตั้งค่า</div>
      <div v-if="isAdmin" class="nav-group" :class="{ 'expanded': isSettingsExpanded }">
        <button class="nav-item group-toggle" @click="toggleSettings">
          <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          </svg>
          <span>ตั้งค่าระบบ</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="chevron-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <div class="sub-menu">
          <router-link 
            v-for="item in settingItems" 
            :key="item.name"
            :to="item.path"
            class="nav-item sub-item"
            exact-active-class="active"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
            </svg>
            <span>{{ item.name }}</span>
          </router-link>
        </div>
      </div>

      <router-link to="/contact" class="nav-item" exact-active-class="active">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span>ติดต่อเรา</span>
      </router-link>
    </nav>
    
    <div class="sidebar-user-container">
      <router-link to="/profile" class="sidebar-user link-hover">
        <div class="user-badge">
          {{ userName.charAt(0) }}
        </div>
        <div class="user-info">
          <p class="user-name">{{ userName }}</p>
          <p class="user-role">{{ userRole }}</p>
        </div>
      </router-link>
      <button class="logout-btn" title="Logout" @click="handleLogout">
        <svg xmlns="http://www.w3.org/2000/svg" class="logout-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
      </button>
    </div>
  </aside>
</div>
</template>

<style scoped>
.app-sidebar {
  width: 260px;
  background-color: var(--sidebar-bg, var(--primary-hover));
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  color: #e2e8f0;
}

.sidebar-logo {
  padding: 24px;
}

.logo-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-intelligist-datax-logo {
  width: 40px;
  height: auto;
}

.logo-text {
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.sidebar-nav {
  flex: 1;
  padding: 0 12px;
  overflow-y: auto;
  scrollbar-width: none; /* Hide scrollbar for Firefox */
}

.sidebar-nav::-webkit-scrollbar {
  display: none; /* Hide scrollbar for Chrome/Safari */
}

.nav-section {
  padding: 24px 16px 12px;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 700;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: 12px;
  margin-bottom: 4px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  font-size: 0.9375rem;
  width: 100%;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  transform: translateX(4px);
}

.nav-item.active {
  background-color: var(--mso-accent);
  color: white;
  box-shadow: 0 8px 16px rgba(233, 30, 99, 0.3);
}

.nav-icon {
  width: 20px;
  height: 20px;
  opacity: 0.8;
  flex-shrink: 0;
}

.nav-item.active .nav-icon {
  opacity: 1;
}

/* Sub-menu Styles */
.nav-group {
  margin-bottom: 4px;
}

.group-toggle {
  justify-content: space-between;
}

.chevron-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.3s ease;
  opacity: 0.5;
}

.expanded .chevron-icon {
  transform: rotate(180deg);
  opacity: 1;
}

.expanded .group-toggle {
  background-color: rgba(255, 255, 255, 0.05);
  color: white;
}

.sub-menu {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  padding-left: 12px;
}

.expanded .sub-menu {
  max-height: 300px;
  margin-top: 4px;
  margin-bottom: 8px;
}

.sub-item {
  font-size: 0.875rem;
  padding: 10px 16px;
}

.sub-item .nav-icon {
  width: 18px;
  height: 18px;
}

/* User Section Styles */
.sidebar-user-container {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-user {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  padding: 8px;
  border-radius: 12px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.sidebar-user.link-hover:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-badge {
  width: 40px;
  height: 40px;
  background-color: var(--mso-pink-dark);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  font-weight: 700;
  font-size: 1.125rem;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.user-info {
  flex: 1;
  overflow: hidden;
}

.user-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: white;
  margin: 0;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.logout-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 8px;
  border-radius: 10px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn:hover {
  color: #f87171;
  background-color: rgba(248, 113, 113, 0.1);
}

.logout-icon {
  width: 20px;
  height: 20px;
}

/* Hamburger Menu for Mobile */
.mobile-sidebar-toggle {
  display: none;
  position: fixed;
  top: 16px;
  left: 16px;
  width: 44px;
  height: 44px;
  background-color: var(--primary);
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  z-index: 1500;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 5px;
}

/* Hamburger lines */
.mobile-sidebar-toggle::before,
.mobile-sidebar-toggle::after,
.mobile-sidebar-toggle span {
  content: '';
  width: 20px;
  height: 2px;
  background-color: white;
  border-radius: 2px;
  display: block;
}

.mobile-sidebar-toggle:active {
  transform: scale(0.95);
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1999;
}

/* Responsive Rules */
.sidebar-container {
  width: 260px;
  flex-shrink: 0;
}

.mobile-close-sidebar {
  display: none;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 4px;
}

@media (max-width: 1024px) {
  .sidebar-container {
    width: 0;
    position: absolute;
  }

  .app-sidebar {
    position: fixed;
    top: 0;
    left: -100%;
    width: 280px;
    z-index: 2000;
    transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 10px 0 30px rgba(0, 0, 0, 0.2);
  }

  .app-sidebar.is-open {
    left: 0;
  }

  .mobile-sidebar-toggle {
    display: flex; /* Enforce visibility on mobile */
  }

  .mobile-close-sidebar {
    display: block;
  }

  .sidebar-logo {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
}

@media (min-width: 1025px) {
  .mobile-sidebar-toggle, .sidebar-overlay, .mobile-close-sidebar {
    display: none !important;
  }
  .app-sidebar {
    left: 0 !important;
    position: sticky !important;
  }
}

@media (max-width: 480px) {
  .app-sidebar {
    width: 85%;
  }
}
</style>
