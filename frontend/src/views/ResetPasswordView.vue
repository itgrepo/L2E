<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../utils/api';
import { encodePassword } from '../utils/crypto';

const route = useRoute();
const router = useRouter();
const token = route.params.token;

const isLoading = ref(true);
const isValid = ref(false);
const username = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const isSubmitting = ref(false);
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

onMounted(async () => {
  try {
    const response = await apiClient.post('/verifyResetToken', { token });
    const result = response.data;
    if (result.status === 'valid') {
      isValid.value = true;
      username.value = result.username;
    } else {
      isValid.value = false;
    }
  } catch (e) {
    isValid.value = false;
  } finally {
    isLoading.value = false;
  }
});

const handleSubmit = async () => {
  errorMessage.value = '';
  
  if (!newPassword.value || !confirmPassword.value) {
    errorMessage.value = 'กรุณากรอกรหัสผ่านให้ครบถ้วน';
    return;
  }
  if (newPassword.value.length < 6) {
    errorMessage.value = 'รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร';
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = 'รหัสผ่านใหม่ไม่ตรงกัน';
    return;
  }

  isSubmitting.value = true;
  try {
    const response = await apiClient.post('/resetPasswordByToken', {
      token,
      password: encodePassword(newPassword.value)
    });
    const result = response.data;
    if (result.status === 'success') {
      successMessage.value = 'ตั้งรหัสผ่านใหม่เรียบร้อยแล้ว! กำลังพาคุณไปหน้าเข้าสู่ระบบ...';
      setTimeout(() => {
        router.push('/login');
      }, 2500);
    } else if (result.status === 'invalid_token') {
      errorMessage.value = 'ลิงก์นี้หมดอายุหรือถูกใช้แล้ว กรุณาส่งคำขอรีเซ็ตรหัสผ่านใหม่';
    } else {
      errorMessage.value = result.status || 'เกิดข้อผิดพลาด กรุณาลองใหม่';
    }
  } catch (e) {
    errorMessage.value = 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ กรุณาลองใหม่ภายหลัง';
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="reset-container">
    <div class="reset-card">
      <!-- Loading -->
      <div v-if="isLoading" class="reset-content">
        <div class="spinner"></div>
        <p>กำลังตรวจสอบลิงก์...</p>
      </div>

      <!-- Token Invalid -->
      <div v-else-if="!isValid" class="reset-content">
        <div class="status-icon">❌</div>
        <h2>ลิงก์ไม่ถูกต้อง</h2>
        <p class="subtitle">ลิงก์รีเซ็ตรหัสผ่านนี้หมดอายุหรือถูกใช้งานแล้ว</p>
        <router-link to="/login" class="btn-primary">
          ← กลับไปหน้าเข้าสู่ระบบ
        </router-link>
      </div>

      <!-- Success Message -->
      <div v-else-if="successMessage" class="reset-content">
        <div class="status-icon success-glow">✅</div>
        <h2>สำเร็จ!</h2>
        <p class="subtitle">{{ successMessage }}</p>
      </div>

      <!-- Reset Form -->
      <div v-else class="reset-content">
        <div class="status-icon">🔐</div>
        <h2>ตั้งรหัสผ่านใหม่</h2>
        <p class="subtitle">สำหรับบัญชี <strong>{{ username }}</strong></p>

        <div v-if="errorMessage" class="error-alert">{{ errorMessage }}</div>

        <form @submit.prevent="handleSubmit" class="reset-form">
          <div class="form-group">
            <label for="new-password">รหัสผ่านใหม่</label>
            <input 
              id="new-password"
              v-model="newPassword" 
              type="password" 
              placeholder="กรอกรหัสผ่านใหม่ (อย่างน้อย 6 ตัวอักษร)"
              required
              :disabled="isSubmitting"
            >
          </div>
          <div class="form-group">
            <label for="confirm-password">ยืนยันรหัสผ่านใหม่</label>
            <div class="password-input-wrapper" style="position: relative; display: flex; align-items: center;">
              <input 
                id="confirm-password"
                v-model="confirmPassword" 
                :type="showConfirmPassword ? 'text' : 'password'" 
                placeholder="กรอกรหัสผ่านใหม่อีกครั้ง"
                required
                :disabled="isSubmitting"
                style="width: 100%; padding-right: 40px;"
              >
              <button type="button" @click="showConfirmPassword = !showConfirmPassword" tabindex="-1" style="position: absolute; right: 10px; background: none; border: none; cursor: pointer; display: flex; padding: 0;">
                <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #64748b;"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #64748b;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
              </button>
            </div>
            <small v-if="confirmPassword && newPassword !== confirmPassword" style="color: #ef4444; font-size: 0.8rem; margin-top: 4px; display: block;">รหัสผ่านไม่ตรงกัน</small>
          </div>
          <button type="submit" class="btn-primary full" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="loader"></span>
            <span v-else>บันทึกรหัสผ่านใหม่</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reset-container {
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 40px 20px;
}

.reset-card {
  width: 100%;
  max-width: 480px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 60px -12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.reset-content {
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

.error-alert {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 0.875rem;
  text-align: left;
}

.reset-form {
  text-align: left;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary, var(--primary));
  box-shadow: 0 0 0 1px var(--primary, var(--primary));
}

.btn-primary {
  display: inline-block;
  padding: 14px 28px;
  background-color: var(--mso-accent, var(--primary));
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-primary.full {
  width: 100%;
  margin-top: 8px;
}

.btn-primary:hover {
  background-color: var(--primary-hover, var(--primary-hover));
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.loader {
  width: 20px;
  height: 20px;
  border: 2px solid #ffffff;
  border-bottom-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes glow {
  from { filter: drop-shadow(0 0 4px rgba(233, 30, 99, 0.3)); }
  to { filter: drop-shadow(0 0 12px rgba(233, 30, 99, 0.5)); }
}

@media (max-width: 480px) {
  .reset-content {
    padding: 32px 20px;
  }
}
</style>
