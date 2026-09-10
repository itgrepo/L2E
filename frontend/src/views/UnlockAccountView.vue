<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../utils/api';
import { themeConfig } from '../utils/theme';

const route = useRoute();
const router = useRouter();
const token = route.params.token;

const status = ref('loading'); // loading, success, error, not-found
const message = ref('กำลังตรวจสอบข้อมูลการปลดล็อคบัญชี...');

onMounted(async () => {
  if (!token) {
    status.value = 'error';
    message.value = 'ไม่พบ Token สำหรับการปลดล็อค';
    return;
  }

  try {
    // 1. Get email and username from token
    const getEmailRes = await apiClient.post('/getEmailFromTokenUnlockAccount', { token });
    if (getEmailRes.data && getEmailRes.data.status === 'found') {
      const { username, email } = getEmailRes.data;
      
      // 2. Unlock account
      const unlockRes = await apiClient.post('/unlockAccount', { username, email });
      if (unlockRes.data === 'success') {
        status.value = 'success';
        message.value = 'ปลดล็อคบัญชีสำเร็จ! กรุณาเข้าสู่ระบบด้วยรหัสผ่านชั่วคราวที่ได้รับในอีเมล';
      } else {
        status.value = 'error';
        message.value = unlockRes.data || 'เกิดข้อผิดพลาดในการปลดล็อคบัญชี';
      }
    } else {
      status.value = 'not-found';
      message.value = 'ลิงก์ปลดล็อคไม่ถูกต้องหรือหมดอายุแล้ว';
    }
  } catch (err) {
    console.error(err);
    status.value = 'error';
    message.value = 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้';
  }
});

const goToLogin = () => {
  router.push('/login');
};
</script>

<template>
  <div class="unlock-container">
    <div class="unlock-card">
      <div class="logo-container">
        <h1 class="site-name">{{ themeConfig.siteName }}</h1>
      </div>
      
      <div class="status-content">
        <div v-if="status === 'loading'" class="loader-container">
          <span class="loader"></span>
          <p>{{ message }}</p>
        </div>
        
        <div v-else-if="status === 'success'" class="success-content">
          <div class="icon-circle success">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
          </div>
          <h2>ปลดล็อคบัญชีสำเร็จ</h2>
          <p>{{ message }}</p>
          <button @click="goToLogin" class="btn-primary">ไปที่หน้าเข้าสู่ระบบ</button>
        </div>
        
        <div v-else class="error-content">
          <div class="icon-circle error">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
          </div>
          <h2>ไม่สามารถปลดล็อคได้</h2>
          <p>{{ message }}</p>
          <button @click="goToLogin" class="btn-secondary">กลับไปหน้าเข้าสู่ระบบ</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.unlock-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 80px);
  background-color: #f8fafc;
  padding: 20px;
}
.unlock-card {
  background: white;
  border-radius: 24px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
  padding: 40px;
  max-width: 500px;
  width: 100%;
  text-align: center;
}
.logo-container {
  margin-bottom: 30px;
}
.site-name {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(to right, var(--mso-accent, #ec4899), var(--primary, #0f172a));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.icon-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}
.icon-circle.success {
  background-color: #dcfce7;
  color: #16a34a;
}
.icon-circle.error {
  background-color: #fee2e2;
  color: #dc2626;
}
h2 {
  font-size: 1.5rem;
  color: #1e293b;
  margin-bottom: 12px;
}
p {
  color: #64748b;
  margin-bottom: 24px;
  line-height: 1.5;
}
.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}
.btn-primary {
  background-color: var(--primary, #0f172a);
  color: white;
}
.btn-primary:hover {
  background-color: var(--primary-hover, #1e293b);
}
.btn-secondary {
  background-color: #f1f5f9;
  color: #475569;
}
.btn-secondary:hover {
  background-color: #e2e8f0;
}
.loader-container {
  padding: 40px 0;
}
.loader {
  width: 48px;
  height: 48px;
  border: 4px solid var(--primary, #0f172a);
  border-bottom-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: rotation 1s linear infinite;
  margin-bottom: 20px;
}
@keyframes rotation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
