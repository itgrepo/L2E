<script setup>
import { computed } from 'vue';
import { themeConfig } from '../utils/theme';
import intelligistDataxLogo from '../assets/intelligist-datax-logo.png';

const getTargetRoute = (path) => {
  if (path === '/') return path;
  if (path === '/about') return path;
  
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  if (!user) return '/'; // Guest

  const userRoleId = String(user.role_id || user.previlage_id);
  const isAdmin = user.isAdmin === 'true' || user.isAdmin === true || ['3', '4'].includes(userRoleId);
  
  if (isAdmin) return path;
  
  if (userRoleId === '1' && ['/catalog'].includes(path)) return path;
  if (userRoleId === '2' && ['/dashboard', '/catalog', '/favorites'].includes(path)) return path;
  if (userRoleId === '3' && ['/dashboard', '/catalog', '/favorites', '/api-management', '/api-monitor', '/dataset-approval', '/dataset-management', '/analytics'].includes(path)) return path;
  if (userRoleId === '5' && ['/dashboard', '/catalog', '/favorites', '/api-management'].includes(path)) return path;
  
  return '/';
};
</script>

<template>
  <footer class="footer">
    <div class="container footer-grid">
      <div class="footer-brand">
        <div class="logo-group" style="margin-bottom: 1rem;">
          <img :src="themeConfig.logoUrl || intelligistDataxLogo" alt="Logo" class="footer-logo" />
          <span class="logo-text" style="color: white; font-weight: 700;">{{ themeConfig.siteName }}</span>
        </div>
        <p style="color: #94a3b8; font-size: 0.9rem;">ศูนย์กลางแลกเปลี่ยนข้อมูลภาครัฐดิจิทัล ส่งเสริมการใช้ข้อมูลเพื่อการพัฒนาประเทศ</p>
      </div>
      <div class="footer-links">
        <h4 style="color: white; margin-bottom: 1rem;">แพลตฟอร์ม</h4>
        <router-link :to="getTargetRoute('/catalog')">ชุดข้อมูล</router-link>
        <router-link :to="getTargetRoute('/api-management')">API Gateway</router-link>
        <router-link to="#">โครงสร้างข้อมูล</router-link>
        <router-link :to="getTargetRoute('/analytics')">วิเคราะห์ข้อมูล</router-link>
      </div>
      <div class="footer-links">
        <h4 style="color: white; margin-bottom: 1rem;">หน่วยงาน</h4>
        <router-link to="#">ผู้ให้บริการข้อมูล</router-link>
        <router-link to="#">ผู้ใช้ข้อมูล</router-link>
        <router-link to="#">คู่มือการใช้งาน</router-link>
        <router-link to="#">นโยบายข้อมูล</router-link>
      </div>
      <div class="footer-links">
        <h4 style="color: white; margin-bottom: 1rem;">ติดต่อเรา</h4>
        <router-link to="/contact">support@datax.go.th</router-link>
        <router-link to="/about">เกี่ยวกับโครงการ</router-link>
        <router-link to="#">เงื่อนไขการให้บริการ</router-link>
        <router-link to="/contact">ติดต่อเรา</router-link>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: #0f1115;
  color: white;
  padding: 60px 0 40px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 3rem;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.footer-links a {
  color: #94a3b8;
  font-size: 0.9rem;
}
.footer-links a:hover {
  color: white;
}

.logo-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.footer-logo {
  height: 40px;
  width: auto;
  border-radius: 4px;
}

.logo-text {
  font-weight: 600;
  font-size: 1.1rem;
}

@media (max-width: 1024px) {
  .footer-grid { grid-template-columns: 1fr 1fr; gap: 2.5rem; }
}

@media (max-width: 768px) {
  .footer { 
    padding: 32px 16px 40px !important; 
    width: 100% !important;
    max-width: 100vw !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    transform: none !important;
    box-sizing: border-box !important;
  }
  .footer-grid { 
    grid-template-columns: 1fr !important; 
    gap: 2rem !important; 
    width: 100% !important;
    margin: 0 !important;
  }
  .footer-links {
    word-break: break-word;
    overflow-wrap: break-word;
  }
  .footer-brand p {
    word-break: break-word;
  }
}
</style>
