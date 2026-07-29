<script setup>
import { themeConfig } from '../utils/theme';
import intelligistDataxLogo from '../assets/intelligist-datax-logo.png';
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
        <a href="#">ชุดข้อมูล</a>
        <a href="#">API Gateway</a>
        <a href="#">โครงสร้างข้อมูล</a>
        <a href="#">วิเคราะห์ข้อมูล</a>
      </div>
      <div class="footer-links">
        <h4 style="color: white; margin-bottom: 1rem;">หน่วยงาน</h4>
        <a href="#">ผู้ให้บริการข้อมูล</a>
        <a href="#">ผู้ใช้ข้อมูล</a>
        <a href="#">คู่มือการใช้งาน</a>
        <a href="#">นโยบายข้อมูล</a>
      </div>
      <div class="footer-links">
        <h4 style="color: white; margin-bottom: 1rem;">ติดต่อเรา</h4>
        <a href="#">support@intelligist-datax.go.th</a>
        <a href="#">เกี่ยวกับโครงการ</a>
        <a href="#">เงื่อนไขการให้บริการ</a>
        <a href="#">คำถามที่พบบ่อย</a>
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
  .footer { padding: 40px 0 30px; }
  .footer-grid { grid-template-columns: 1fr; gap: 2rem; }
}
</style>
