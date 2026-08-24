<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import intelligistDataxLogo from '../assets/logo.svg';
import { themeConfig } from '../utils/theme';

const router = useRouter();
const isAuthenticated = ref(false);
const isMobileMenuOpen = ref(false);

import { postWithUser } from '../utils/api';

const notifications = ref([]);
const unreadCount = ref(0);
const showNotifDropdown = ref(false);
const notifDropdownRef = ref(null);

onMounted(() => {
  document.addEventListener('click', (e) => {
    if (notifDropdownRef.value && !notifDropdownRef.value.contains(e.target)) {
      showNotifDropdown.value = false;
    }
  });
});

const fetchNotifications = async () => {
  if (!isAuthenticated.value) return;
  try {
    const user = JSON.parse(localStorage.getItem('user'));
    const countRes = await postWithUser('/notifications/unread-count', user);
    if (countRes.data?.status === 'success') {
      unreadCount.value = countRes.data.data.unread_count;
    }
    const notifRes = await postWithUser('/notifications', user);
    if (notifRes.data?.status === 'success') {
      notifications.value = notifRes.data.data;
    }
  } catch (e) {
    console.error('Failed to fetch notifications', e);
  }
};

const toggleNotifications = () => {
  showNotifDropdown.value = !showNotifDropdown.value;
  if (showNotifDropdown.value) {
    fetchNotifications();
  }
};

const markAsRead = async (id) => {
  try {
    const user = JSON.parse(localStorage.getItem('user'));
    await postWithUser(`/notifications/${id}/read`, user);
    fetchNotifications();
  } catch (e) {
    console.error(e);
  }
};

const markAllAsRead = async () => {
  try {
    const user = JSON.parse(localStorage.getItem('user'));
    await postWithUser('/notifications/read-all', user);
    fetchNotifications();
    showNotifDropdown.value = false;
  } catch (e) {
    console.error(e);
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleString('th-TH');
};

const authChangeHandler = () => {
  checkAuth();
  if (isAuthenticated.value) {
    fetchNotifications();
  } else {
    notifications.value = [];
    unreadCount.value = 0;
  }
};


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
  const sidebar = document.querySelector('.app-sidebar');
  if (sidebar) {
    // We are on an Admin page, let Sidebar handle the menu
    window.dispatchEvent(new CustomEvent('toggle-sidebar'));
    isMobileMenuOpen.value = false;
  } else {
    isMobileMenuOpen.value = !isMobileMenuOpen.value;
  }
};

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
  window.dispatchEvent(new CustomEvent('toggle-mobile-menu', { detail: false }));
};

onMounted(() => {
  checkAuth();
  window.addEventListener('storage', checkAuth);
  window.addEventListener('auth-change', authChangeHandler);
  if (isAuthenticated.value) fetchNotifications();
});
</script>

<template>
  <header class="navbar">
    <div class="container nav-inner">
      <router-link to="/" class="logo-group">
        <img v-if="themeConfig.logoUrl" :src="themeConfig.logoUrl" alt="Logo" class="datax-logo" />
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

        <div class="notification-container" ref="notifDropdownRef" v-if="isAuthenticated">
          <button class="nav-bell-btn" @click.stop="toggleNotifications">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span class="nav-badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
          </button>
          
          <div class="notif-dropdown" v-if="showNotifDropdown" @click.stop>
            <div class="notif-header">
              <h4>การแจ้งเตือน</h4>
              <button class="mark-all-btn" @click.stop="markAllAsRead" v-if="unreadCount > 0">อ่านทั้งหมด</button>
            </div>
            <div class="notif-list">
              <div v-if="notifications.length === 0" class="no-notif">ไม่มีการแจ้งเตือน</div>
              <div v-for="n in notifications" :key="n.id" :class="['notif-item', { unread: n.is_read === 0 }]" @click.stop="markAsRead(n.id)">
                <div class="notif-content">
                  <div class="notif-message">{{ n.message }}</div>
                  <div class="notif-time">{{ formatDate(n.created_at) }}</div>
                </div>
                <div class="unread-dot" v-if="n.is_read === 0"></div>
              </div>
            </div>
          </div>
        </div>

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



    <!-- Mobile Menu Overlay -->
    <Teleport to="body">
      <div v-if="isMobileMenuOpen" class="mobile-menu-overlay" @click="closeMobileMenu"></div>
      <div :class="['mobile-menu', { 'open': isMobileMenuOpen }]">
        <div class="mobile-menu-header">
          <div class="logo-group">
            <img v-if="themeConfig.logoUrl" :src="themeConfig.logoUrl" alt="Logo" class="datax-logo-small" />
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
    </Teleport>
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

.datax-logo {
  height: 70px; /* Increased from 60px */
  width: auto;
  transition: height 0.3s ease;
}

.datax-logo-small {
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
  white-space: nowrap;
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
  white-space: nowrap;
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
  right: -100%;
  transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.1);
}

.mobile-menu.open {
  right: 0;
  visibility: visible;
}

@media (max-width: 1250px) {
  .nav-links { gap: 1rem; }
  .logo-text { font-size: 1.1rem; }
  .nav-links a { font-size: 0.85rem; }
  .btn-navbar { padding: 8px 16px; font-size: 0.85rem; }
}
@media (max-width: 850px) {
  .nav-links, .nav-actions { display: none; }
  .mobile-menu-btn { display: block; }
  .mobile-side-tab { display: flex; }
}

@media (max-width: 767px) {
  .nav-inner {
    padding-left: 12px;
    padding-right: 12px;
  }
  .logo-text {
    font-size: 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 180px;
  }
  .nav-inner {
    padding-left: 16px;
    padding-right: 16px;
    justify-content: space-between;
  }
  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    margin-right: -8px;
  }


  .navbar {
    position: fixed;
  }
  
  .nav-inner {
    height: 70px;
  }
  
  .datax-logo {
    height: 45px;
  }
  
  .logo-text {
    font-size: 1.1rem;
  }
  
  /* Moved to 991px */
  .mobile-menu-btn { display: block; }
  .mobile-side-tab { display: flex; }
}

:global(body) {
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

.notification-container {
  position: relative;
  display: flex;
  align-items: center;
  margin-right: 0.5rem;
}

.nav-bell-btn {
  background: none;
  border: none;
  color: #1e293b;
  cursor: pointer;
  position: relative;
  padding: 0.5rem;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-bell-btn:hover {
  color: var(--primary);
}

.nav-bell-btn svg {
  width: 24px;
  height: 24px;
}

.nav-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #ef4444;
  color: white;
  font-size: 0.7rem;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 10px;
  border: 2px solid white;
  line-height: 1;
}

.notif-dropdown {
  position: absolute;
  top: calc(100% + 15px);
  right: -20px;
  width: 350px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  z-index: 9999;
  overflow: hidden;
  border: 1px solid var(--border-light);
  cursor: default;
}

.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-light);
  background: #f8fafc;
}

.notif-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
}

.mark-all-btn {
  background: none;
  border: none;
  color: var(--primary);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.mark-all-btn:hover {
  text-decoration: underline;
}

.notif-list {
  max-height: 400px;
  overflow-y: auto;
  background: white;
}

.no-notif {
  padding: 30px 20px;
  text-align: center;
  color: #64748b;
  font-size: 0.95rem;
}

.notif-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background 0.2s;
  text-align: left;
}

.notif-item:last-child {
  border-bottom: none;
}

.notif-item:hover {
  background: #f8fafc;
}

.notif-item.unread {
  background: #f0fdf4;
}

.notif-item.unread:hover {
  background: #dcfce7;
}

.notif-content {
  flex: 1;
  padding-right: 12px;
}

.notif-message {
  font-size: 0.95rem;
  color: #334155;
  margin-bottom: 6px;
  line-height: 1.4;
  word-break: break-word;
}

.notif-item.unread .notif-message {
  font-weight: 600;
  color: #0f172a;
}

.notif-time {
  font-size: 0.75rem;
  color: #94a3b8;
}

.unread-dot {
  width: 10px;
  height: 10px;
  background: var(--primary);
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

@media (max-width: 767px) {
  .nav-inner {
    padding-left: 12px;
    padding-right: 12px;
  }
  .logo-text {
    font-size: 1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 180px;
  }
  .nav-inner {
    padding-left: 16px;
    padding-right: 16px;
    justify-content: space-between;
  }
  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 8px;
    margin-right: -8px;
  }


  .notification-container {
    margin-right: 15px;
  }
  .notif-dropdown {
    position: fixed;
    top: 70px;
    right: 10px;
    width: calc(100% - 20px);
    max-width: 350px;
  }
}
</style>

