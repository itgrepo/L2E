<script setup>
import { ref, computed, onMounted } from 'vue';
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

// Password criteria & validation
const passwordCriteria = computed(() => {
  const p = newPassword.value || '';
  return {
    length: p.length >= 8,
    uppercase: /[A-Z]/.test(p),
    lowercase: /[a-z]/.test(p),
    number: /[0-9]/.test(p),
    special: /[^A-Za-z0-9]/.test(p)
  };
});

const isPasswordValid = computed(() => {
  const c = passwordCriteria.value;
  return c.length && c.uppercase && c.lowercase && c.number && c.special;
});

const isFormValid = computed(() => {
  return isPasswordValid.value && 
         newPassword.value === confirmPassword.value &&
         confirmPassword.value.length > 0;
});

const passwordStrength = computed(() => {
  const p = newPassword.value;
  if (!p) return { score: 0, label: '', color: '' };
  let score = 0;
  if (p.length >= 8) score++;
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++;
  if (/[0-9]/.test(p)) score++;
  if (/[^A-Za-z0-9]/.test(p)) score++;
  
  const levels = [
    { score: 0, label: '', color: '' },
    { score: 1, label: 'อ่อนมาก', color: '#ef4444' },
    { score: 2, label: 'อ่อน', color: '#f97316' },
    { score: 3, label: 'ปานกลาง', color: '#f59e0b' },
    { score: 4, label: 'ปลอดภัยสูง', color: '#10b981' }
  ];
  return levels[score] || levels[0];
});

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
  if (!isPasswordValid.value) {
    errorMessage.value = 'รหัสผ่านใหม่ต้องตรงตามเงื่อนไขความปลอดภัยทั้งหมด';
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
    } else if (result.status === 'invalid_password' || result.message) {
      errorMessage.value = result.message || 'รหัสผ่านไม่ถูกต้องตามเงื่อนไขความปลอดภัย';
    } else {
      errorMessage.value = result.status || 'เกิดข้อผิดพลาด กรุณาลองใหม่';
    }
  } catch (e) {
    errorMessage.value = e.response?.data?.message || 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ กรุณาลองใหม่ภายหลัง';
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
          <!-- New Password -->
          <div class="form-group">
            <label for="new-password">รหัสผ่านใหม่</label>
            <div class="password-input-wrapper">
              <input 
                id="new-password"
                v-model="newPassword" 
                :type="showPassword ? 'text' : 'password'" 
                placeholder="อย่างน้อย 8 ตัวอักษร"
                required
                minlength="8"
                :disabled="isSubmitting"
              >
              <button type="button" class="toggle-password" @click="showPassword = !showPassword" tabindex="-1">
                <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #64748b;"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #64748b;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
              </button>
            </div>
            
            <!-- Password Checklist -->
            <div class="password-checklist" v-if="newPassword">
              <div class="checklist-title">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
                <span>เงื่อนไขความปลอดภัยของรหัสผ่าน:</span>
              </div>
              <ul class="checklist-items">
                <li :class="{ valid: passwordCriteria.length }">
                  <span class="icon">{{ passwordCriteria.length ? '✔' : '✘' }}</span>
                  <span>ความยาวอย่างน้อย 8 ตัวอักษร</span>
                </li>
                <li :class="{ valid: passwordCriteria.uppercase }">
                  <span class="icon">{{ passwordCriteria.uppercase ? '✔' : '✘' }}</span>
                  <span>มีตัวอักษรภาษาอังกฤษตัวพิมพ์ใหญ่ (A-Z) อย่างน้อย 1 ตัว</span>
                </li>
                <li :class="{ valid: passwordCriteria.lowercase }">
                  <span class="icon">{{ passwordCriteria.lowercase ? '✔' : '✘' }}</span>
                  <span>มีตัวอักษรภาษาอังกฤษตัวพิมพ์เล็ก (a-z) อย่างน้อย 1 ตัว</span>
                </li>
                <li :class="{ valid: passwordCriteria.number }">
                  <span class="icon">{{ passwordCriteria.number ? '✔' : '✘' }}</span>
                  <span>มีตัวเลขอารบิก (0-9) อย่างน้อย 1 ตัว</span>
                </li>
                <li :class="{ valid: passwordCriteria.special }">
                  <span class="icon">{{ passwordCriteria.special ? '✔' : '✘' }}</span>
                  <span>มีอักขระพิเศษอย่างน้อย 1 ตัว (เช่น @, #, $, %, !, _)</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- Confirm Password -->
          <div class="form-group">
            <label for="confirm-password">ยืนยันรหัสผ่านใหม่</label>
            <div class="password-input-wrapper">
              <input 
                id="confirm-password"
                v-model="confirmPassword" 
                :type="showConfirmPassword ? 'text' : 'password'" 
                placeholder="กรอกรหัสผ่านใหม่อีกครั้ง"
                required
                :disabled="isSubmitting"
              >
              <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword" tabindex="-1">
                <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #64748b;"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #64748b;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
              </button>
            </div>
            <small v-if="confirmPassword && newPassword !== confirmPassword" class="field-hint error">รหัสผ่านไม่ตรงกัน</small>
          </div>

          <button type="submit" class="btn-primary full" :disabled="!isFormValid || isSubmitting">
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
  max-width: 500px;
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

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper input {
  width: 100%;
  padding: 12px 42px 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.2s;
  box-sizing: border-box;
}

.password-input-wrapper input:focus {
  outline: none;
  border-color: var(--primary, #008236);
  box-shadow: 0 0 0 1px var(--primary, #008236);
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  color: #64748b;
  transition: color 0.2s;
}

.toggle-password:hover {
  color: #1e293b;
}

.field-hint {
  display: block;
  margin-top: 6px;
  font-size: 0.8rem;
}

.field-hint.error {
  color: #ef4444;
}

/* Password Checklist Styles */
.password-checklist {
  margin-top: 12px;
  padding: 14px 16px;
  background-color: #f0fdf4;
  border-radius: 12px;
  border: 1px solid #dcfce7;
}

.checklist-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #166534;
  margin-bottom: 10px;
  font-size: 0.875rem;
}

.checklist-items {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.checklist-items li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.825rem;
  color: #ef4444; /* Default red */
  transition: all 0.2s ease;
}

.checklist-items li.valid {
  color: #166534; /* Green when valid */
}

.checklist-items li .icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 0.7rem;
  font-weight: bold;
  flex-shrink: 0;
  background-color: #fee2e2;
  color: #dc2626;
}

.checklist-items li.valid .icon {
  background-color: #bbf7d0;
  color: #15803d;
}

.btn-primary {
  display: inline-block;
  padding: 14px 28px;
  background-color: var(--mso-accent, #008236);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
  text-align: center;
}

.btn-primary.full {
  width: 100%;
  margin-top: 8px;
}

.btn-primary:hover:not(:disabled) {
  background-color: #00662a;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--primary, #008236);
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
  from { filter: drop-shadow(0 0 4px rgba(0, 130, 54, 0.3)); }
  to { filter: drop-shadow(0 0 12px rgba(0, 130, 54, 0.5)); }
}

@media (max-width: 480px) {
  .reset-content {
    padding: 32px 20px;
  }
}
</style>

