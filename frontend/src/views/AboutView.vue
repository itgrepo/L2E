<script setup>
import AppNavbar from '../components/AppNavbar.vue';
import AppFooter from '../components/AppFooter.vue';
</script>

<template>
  <div class="about-page">
    <section class="about-hero">
      <div class="container">
        <h1>เกี่ยวกับ DataX Portal</h1>
        <p class="subtitle">ศูนย์กลางสำหรับการแลกเปลี่ยนข้อมูลและการจัดการ API</p>
      </div>
    </section>
    
    <section class="mission-section">
      <div class="container grid">
        <div class="mission-content">
          <h2>พันธกิจของเรา</h2>
          <p>DataX Portal (แพลตฟอร์มการแลกเปลี่ยนข้อมูลและการจัดการ API) ถูกออกแบบมาเพื่อเพิ่มประสิทธิภาพในการแบ่งปัน ค้นพบ และใช้ประโยชน์จากข้อมูลของหน่วยงานภาครัฐ พันธกิจของเราคือการสร้างระบบนิเวศที่ไร้รอยต่อ ปลอดภัย และมีมาตรฐาน เพื่อเสริมสร้างขีดความสามารถให้นักพัฒนาและผู้กำหนดนโยบายด้วยข้อมูลที่มีคุณภาพสูง</p>

        </div>
        <div class="mission-image">
          <div class="abstract-shape">
            <div class="circle c1"></div>
            <div class="circle c2"></div>
            <div class="logo-placeholder">DataX</div>
          </div>
        </div>
      </div>
    </section>
    
    <section class="features-grid-section">
      <div class="container">
        <h2 class="text-center">กระบวนการทำงาน</h2>
        <div class="features-grid">
          <div class="feature-item">
            <div class="icon-box">🔍</div>
            <h3>ค้นพบ</h3>
            <p>ค้นหาข้อมูลที่คุณต้องการได้อย่างง่ายดายผ่านระบบค้นหาและจัดหมวดหมู่อัจฉริยะของเรา</p>
          </div>
          <div class="feature-item">
            <div class="icon-box">🔌</div>
            <h3>เชื่อมต่อ</h3>
            <p>เข้าถึงข้อมูลได้ทันทีผ่าน API ที่ได้มาตรฐาน พร้อมเอกสารประกอบและตัวอย่างโค้ดที่สมบูรณ์</p>
          </div>
          <div class="feature-item">
            <div class="icon-box">🛡️</div>
            <h3>ปลอดภัย</h3>
            <p>ระบบการยืนยันตัวตนและการตรวจสอบตามมาตรฐานอุตสาหกรรม เพื่อให้มั่นใจว่าข้อมูลเข้าถึงได้เฉพาะผู้ที่ได้รับอนุญาตเท่านั้น</p>
          </div>
          <div class="feature-item">
            <div class="icon-box">📊</div>
            <h3>วิเคราะห์</h3>
            <p>ติดตามการใช้งานข้อมูลของคุณและรับข้อมูลเชิงลึกผ่านหน้าจอแดชบอร์ดการวิเคราะห์ที่ครอบคลุม</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.about-page {
  background: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.about-hero {
  background: #f8fafc;
  padding: 120px 0;
  text-align: center;
}

.about-hero h1 {
  font-size: 3.5rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 16px;
}

.subtitle {
  font-size: 1.5rem;
  color: #64748b;
  max-width: 700px;
  margin: 0 auto;
}

.mission-section {
  padding: 100px 0;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 80px;
}

h2 {
  font-size: 2.5rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 24px;
}

.mission-content p {
  font-size: 1.125rem;
  line-height: 1.8;
  color: #475569;
  margin-bottom: 40px;
}

.stats-mini {
  display: flex;
  gap: 40px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.num {
  font-size: 2rem;
  font-weight: 800;
  color: var(--primary);
}

.lbl {
  color: #94a3b8;
  font-weight: 600;
}

.abstract-shape {
  position: relative;
  width: 400px;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.circle {
  position: absolute;
  border-radius: 50%;
}

.c1 {
  width: 100%;
  height: 100%;
  background: var(--mso-pink-dark);
  animation: pulse 4s infinite;
}

.c2 {
  width: 70%;
  height: 70%;
  background: var(--mso-pink-dark);
  animation: pulse 3s infinite reverse;
}

.logo-placeholder {
  position: relative;
  z-index: 2;
  font-size: 3rem;
  font-weight: 800;
  color: var(--primary);
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 0.5; }
}

.features-grid-section {
  padding: 100px 0;
  background: #f8fafc;
}

.text-center { text-align: center; margin-bottom: 60px; }

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
}

.feature-item {
  background: white;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.icon-box {
  font-size: 2.5rem;
  margin-bottom: 24px;
}

.feature-item h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: #1e293b;
}

.feature-item p {
  line-height: 1.6;
  color: #64748b;
}
</style>
