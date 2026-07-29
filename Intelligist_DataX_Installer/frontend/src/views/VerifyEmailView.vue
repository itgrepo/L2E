<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../utils/api';

const route = useRoute();
const router = useRouter();

const status = ref('loading'); // loading, success, expired, error
const email = ref('');
const username = ref('');
const errorMessage = ref('');

onMounted(async () => {
  const token = route.params.token;
  if (!token) {
    status.value = 'error';
    errorMessage.value = 'ไม่พบ Token สำหรับยืนยัน';
    return;
  }

  try {
    const response = await apiClient.post('/getEmailFromToken', { token });
    const result = response.data;

    if (result.status === 'found') {
      status.value = 'success';
      email.value = result.email;
      username.value = result.username;
    } else if (result.status === 'link expire') {
      status.value = 'expired';
    } else if (result.status === 'not found') {
      status.value = 'error';
      errorMessage.value = 'Token ไม่ถูกต้องหรือถูกใช้ไปแล้ว';
    } else {
      status.value = 'error';
      errorMessage.value = result.status || 'เกิดข้อผิดพลาด';
    }
  } catch (err) {
    console.error('Verification error:', err);
    status.value = 'error';
    errorMessage.value = 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้';
  }
});
</script>

<template>
  <div class="verify-container">
    <div class="verify-card">
      <!-- Loading -->
      <div v-if="status === 'loading'" class="verify-content">
        <div class="spinner-large"></div>
        <h2>กำลังยืนยันอีเมล...</h2>
        <p class="subtitle">กรุณารอสักครู่</p>
      </div>

      <!-- Success -->
      <div v-if="status === 'success'" class="verify-content">
        <div class="status-icon success-glow">✅</div>
        <h2>ยืนยันอีเมลสำเร็จ!</h2>
        <p class="subtitle">บัญชีของคุณเปิดใช้งานเรียบร้อยแล้ว คุณสามารถเข้าสู่ระบบได้ทันที</p>
        
        <div class="info-card">
          <div class="info-row">
            <span class="info-label">อีเมล</span>
            <span class="info-value">{{ email }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Username</span>
            <span class="info-value">{{ username }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">สถานะ</span>
            <span class="info-value status-active">✅ พร้อมใช้งาน</span>
          </div>
        </div>

        <div class="flow-steps">
          <div class="flow-step done">
            <div class="flow-circle">✓</div>
            <span>สมัคร</span>
          </div>
          <div class="flow-line done"></div>
          <div class="flow-step done">
            <div class="flow-circle">✓</div>
            <span>ยืนยันอีเมล</span>
          </div>
          <div class="flow-line done"></div>
          <div class="flow-step done">
            <div class="flow-circle">✓</div>
            <span>พร้อมใช้งาน</span>
          </div>
        </div>

        <div class="info-note">
          <p>💡 คุณสามารถใช้ Username และ Password ที่สมัครไว้เพื่อเข้าใช้งานระบบได้เลย</p>
        </div>

        <router-link to="/login?verified=true" class="btn-primary">
          ← กลับไปหน้าเข้าสู่ระบบ
        </router-link>
      </div>

      <!-- Expired -->
      <div v-if="status === 'expired'" class="verify-content">
        <div class="status-icon">⏰</div>
        <h2>ลิงก์หมดอายุ</h2>
        <p class="subtitle">ลิงก์ยืนยันอีเมลนี้หมดอายุแล้ว กรุณาสมัครใหม่</p>
        
        <router-link to="/register" class="btn-primary">
          สมัครสมาชิกใหม่
        </router-link>
      </div>

      <!-- Error -->
      <div v-if="status === 'error'" class="verify-content">
        <div class="status-icon">❌</div>
        <h2>เกิดข้อผิดพลาด</h2>
        <p class="subtitle">{{ errorMessage }}</p>
        
        <router-link to="/register" class="btn-secondary">
          สมัครสมาชิกใหม่
        </router-link>
        <router-link to="/login" class="btn-link">
          กลับไปหน้าเข้าสู่ระบบ
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.verify-container {
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 40px 20px;
}

.verify-card {
  width: 100%;
  max-width: 520px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 60px -12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.verify-content {
  padding: 48px 40px;
  text-align: center;
}

.status-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
  display: inline-block;
}

.success-glow {
  animation: glow 2s ease-in-out infinite alternate;
}

h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.subtitle {
  color: #64748b;
  font-size: 1rem;
  margin-bottom: 24px;
}

.info-card {
  background: #fdf2f8;
  border: 1px solid #bbf7d0;
  border-radius: 16px;
  padding: 20px;
  text-align: left;
  margin: 24px 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #fce7f3;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #64748b;
  font-size: 0.875rem;
}

.info-value {
  color: #1e293b;
  font-weight: 600;
  font-size: 0.875rem;
}

.status-pending {
  color: #f59e0b;
}

/* Flow steps */
.flow-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin: 28px 0;
}

.flow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.flow-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
  color: #94a3b8;
  background: white;
  transition: all 0.3s;
}

.flow-step.done .flow-circle {
  border-color: var(--mso-accent);
  background: var(--mso-accent);
  color: white;
}

.flow-step.current .flow-circle {
  border-color: #f59e0b;
  color: #f59e0b;
}

.flow-circle.pulse {
  animation: pulse 2s infinite;
}

.flow-step span {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 500;
}

.flow-step.done span {
  color: var(--mso-accent);
}

.flow-step.current span {
  color: #f59e0b;
  font-weight: 600;
}

.flow-line {
  width: 40px;
  height: 2px;
  background: #e2e8f0;
  margin-bottom: 22px;
}

.flow-line.done {
  background: var(--mso-accent);
}

.info-note {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  padding: 14px;
  margin: 20px 0;
}

.info-note p {
  margin: 0;
  font-size: 0.85rem;
  color: #1e40af;
}

.btn-primary {
  display: inline-block;
  padding: 14px 28px;
  background-color: var(--mso-accent);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-primary:hover {
  background-color: var(--primary);
  transform: translateY(-1px);
}

.btn-secondary {
  display: inline-block;
  padding: 14px 28px;
  background: none;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
  margin-bottom: 12px;
}

.btn-link {
  display: block;
  margin-top: 16px;
  color: #64748b;
  text-decoration: none;
  font-size: 0.9rem;
}

.btn-link:hover {
  color: var(--mso-accent);
}

.spinner-large {
  width: 48px;
  height: 48px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--mso-accent);
  border-radius: 50%;
  animation: rotation 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes rotation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes glow {
  from { filter: drop-shadow(0 0 4px rgba(34, 197, 94, 0.3)); }
  to { filter: drop-shadow(0 0 12px rgba(34, 197, 94, 0.5)); }
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
}
</style>
