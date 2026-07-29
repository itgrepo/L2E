<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../utils/api';

const router = useRouter();

// Form fields
const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const firstname = ref('');
const lastname = ref('');
const organization = ref('');
const agreeTerms = ref(false);

// UI state
const isLoading = ref(false);
const errorMessage = ref('');
const successData = ref(null);
const currentStep = ref(1);
const showPassword = ref(false);

// Password encryption (matching backend)
const encryptPassword = (pwd) => {
  const key = 'e9NHdT3GU6wBdWlw3RTqvrShGzyerRl4BaMhFeUI3v4j6U0opW5a19HQHDAHHCrhYXq8oG6D';
  // Use the same HMAC-SHA256 as backend
  if (window.CryptoJS) {
    return window.CryptoJS.HmacSHA256(pwd, key).toString();
  }
  // Fallback: send raw (backend will handle)
  return pwd;
};

// Validation
const passwordStrength = computed(() => {
  const p = password.value;
  if (!p) return { score: 0, label: '', color: '' };
  let score = 0;
  if (p.length >= 8) score++;
  if (/[A-Z]/.test(p)) score++;
  if (/[0-9]/.test(p)) score++;
  if (/[^A-Za-z0-9]/.test(p)) score++;
  
  const levels = [
    { score: 0, label: '', color: '' },
    { score: 1, label: 'อ่อน', color: '#ef4444' },
    { score: 2, label: 'ปานกลาง', color: '#f59e0b' },
    { score: 3, label: 'ดี', color: 'var(--mso-accent)' },
    { score: 4, label: 'ดีมาก', color: 'var(--primary)' }
  ];
  return levels[score] || levels[0];
});

const isStep1Valid = computed(() => {
  return username.value.length >= 3 && 
         email.value.includes('@') && 
         password.value.length >= 8 &&
         password.value === confirmPassword.value;
});

const isStep2Valid = computed(() => {
  return firstname.value.trim() && lastname.value.trim() && agreeTerms.value;
});

const nextStep = () => {
  if (currentStep.value === 1 && isStep1Valid.value) {
    currentStep.value = 2;
    errorMessage.value = '';
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
    errorMessage.value = '';
  }
};

const handleRegister = async () => {
  if (!isStep2Valid.value) return;
  
  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await apiClient.post('/registerSimple', {
      username: username.value,
      password: password.value,
      email: email.value,
      firstname: firstname.value,
      lastname: lastname.value,
      organization: organization.value,
      link: window.location.origin
    });

    const result = response.data;
    if (result.status === 'success') {
      successData.value = result;
      currentStep.value = 3; // Success screen
    } else {
      errorMessage.value = result.message || 'การสมัครล้มเหลว กรุณาลองใหม่';
    }
  } catch (error) {
    console.error('Registration error:', error);
    errorMessage.value = 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ กรุณาลองใหม่';
  } finally {
    isLoading.value = false;
  }
};

const goToVerify = () => {
  if (successData.value?.token) {
    router.push(`/verify/${successData.value.token}`);
  }
};
</script>

<template>
  <div class="register-container">
    <div class="register-branding">
      <div class="branding-content">
        <h1>Intelligist DataX Portal</h1>
        <p class="tagline">ระบบแลกเปลี่ยนข้อมูลอัจฉริยะ</p>
        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-icon">🔐</div>
            <div>
              <h4>ปลอดภัย</h4>
              <p>รักษาความปลอดภัยข้อมูลด้วยมาตรฐานระดับสากล</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">📊</div>
            <div>
              <h4>API Access</h4>
              <p>เข้าถึงข้อมูลผ่าน REST API ที่ทันสมัย</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">⚡</div>
            <div>
              <h4>Real-time</h4>
              <p>ติดตามสถิติการใช้งานแบบเรียลไทม์</p>
            </div>
          </div>
        </div>
        <div class="branding-accent"></div>
      </div>
    </div>
    
    <div class="register-form-side">
      <div class="form-card">
        <!-- Progress Steps -->
        <div class="steps-indicator" v-if="currentStep < 3">
          <div class="step" :class="{ active: currentStep >= 1, done: currentStep > 1 }">
            <div class="step-circle">{{ currentStep > 1 ? '✓' : '1' }}</div>
            <span>บัญชีผู้ใช้</span>
          </div>
          <div class="step-line" :class="{ active: currentStep >= 2 }"></div>
          <div class="step" :class="{ active: currentStep >= 2, done: currentStep > 2 }">
            <div class="step-circle">{{ currentStep > 2 ? '✓' : '2' }}</div>
            <span>ข้อมูลส่วนตัว</span>
          </div>
          <div class="step-line" :class="{ active: currentStep >= 3 }"></div>
          <div class="step" :class="{ active: currentStep >= 3 }">
            <div class="step-circle">3</div>
            <span>ยืนยัน</span>
          </div>
        </div>

        <!-- Step 1: Account Info -->
        <div v-if="currentStep === 1" class="step-content">
          <h2>สร้างบัญชีผู้ใช้</h2>
          <p class="subtitle">กรอกข้อมูลเพื่อเริ่มต้นใช้งาน Intelligist DataX Portal</p>
          
          <div v-if="errorMessage" class="error-alert">{{ errorMessage }}</div>

          <form @submit.prevent="nextStep">
            <div class="form-group">
              <label for="reg-username">ชื่อผู้ใช้ (Username)</label>
              <input id="reg-username" v-model="username" type="text" placeholder="ตัวอย่าง: somchai_intelligist-datax" required minlength="3" :disabled="isLoading">
              <small v-if="username && username.length < 3" class="field-hint error">ต้องมีอย่างน้อย 3 ตัวอักษร</small>
            </div>

            <div class="form-group">
              <label for="reg-email">อีเมล</label>
              <input id="reg-email" v-model="email" type="email" placeholder="example@email.com" required :disabled="isLoading">
            </div>

            <div class="form-group">
              <label for="reg-password">รหัสผ่าน</label>
              <div class="password-input-wrapper">
                <input id="reg-password" v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="อย่างน้อย 8 ตัวอักษร" required minlength="8" :disabled="isLoading">
                <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                  {{ showPassword ? '🙈' : '👁️' }}
                </button>
              </div>
              <div class="password-strength" v-if="password">
                <div class="strength-bar">
                  <div class="strength-fill" :style="{ width: (passwordStrength.score * 25) + '%', backgroundColor: passwordStrength.color }"></div>
                </div>
                <small :style="{ color: passwordStrength.color }">{{ passwordStrength.label }}</small>
              </div>
            </div>

            <div class="form-group">
              <label for="reg-confirm">ยืนยันรหัสผ่าน</label>
              <input id="reg-confirm" v-model="confirmPassword" type="password" placeholder="กรอกรหัสผ่านอีกครั้ง" required :disabled="isLoading">
              <small v-if="confirmPassword && password !== confirmPassword" class="field-hint error">รหัสผ่านไม่ตรงกัน</small>
            </div>

            <button type="submit" class="btn-primary" :disabled="!isStep1Valid || isLoading">
              ถัดไป →
            </button>
          </form>
        </div>

        <!-- Step 2: Personal Info -->
        <div v-if="currentStep === 2" class="step-content">
          <h2>ข้อมูลส่วนตัว</h2>
          <p class="subtitle">กรุณากรอกข้อมูลเพิ่มเติม</p>

          <div v-if="errorMessage" class="error-alert">{{ errorMessage }}</div>

          <form @submit.prevent="handleRegister">
            <div class="form-row">
              <div class="form-group">
                <label for="reg-firstname">ชื่อ</label>
                <input id="reg-firstname" v-model="firstname" type="text" placeholder="ชื่อจริง" required :disabled="isLoading">
              </div>
              <div class="form-group">
                <label for="reg-lastname">นามสกุล</label>
                <input id="reg-lastname" v-model="lastname" type="text" placeholder="นามสกุล" required :disabled="isLoading">
              </div>
            </div>

            <div class="form-group">
              <label for="reg-org">หน่วยงาน / องค์กร</label>
              <input id="reg-org" v-model="organization" type="text" placeholder="ชื่อหน่วยงาน (ไม่บังคับ)" :disabled="isLoading">
            </div>

            <div class="terms-group">
              <label class="checkbox-container">
                <input type="checkbox" v-model="agreeTerms" :disabled="isLoading">
                <span class="checkmark"></span>
                ฉันยอมรับ <a href="#" @click.prevent>ข้อตกลงการใช้งาน</a> และ <a href="#" @click.prevent>นโยบายความเป็นส่วนตัว</a>
              </label>
            </div>

            <div class="btn-row">
              <button type="button" class="btn-secondary" @click="prevStep" :disabled="isLoading">
                ← ย้อนกลับ
              </button>
              <button type="submit" class="btn-primary" :disabled="!isStep2Valid || isLoading">
                <span v-if="isLoading" class="loader"></span>
                <span v-else>สมัครสมาชิก</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Step 3: Success -->
        <div v-if="currentStep === 3" class="step-content success-content">
          <div class="success-icon">✉️</div>
          <h2>สมัครสมาชิกสำเร็จ!</h2>
          <p class="subtitle">กรุณาตรวจสอบอีเมลของคุณเพื่อยืนยันตัวตน</p>
          
          <div class="success-info-card">
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
              <span class="info-value status-pending">รอยืนยันอีเมล</span>
            </div>
          </div>

          <div class="success-steps">
            <div class="flow-step">
              <div class="flow-number done">✓</div>
              <span>สมัครสมาชิก</span>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step current">
              <div class="flow-number">2</div>
              <span>ยืนยันอีเมล</span>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">
              <div class="flow-number">3</div>
              <span>รออนุมัติ</span>
            </div>
            <div class="flow-arrow">→</div>
            <div class="flow-step">
              <div class="flow-number">4</div>
              <span>ใช้งานได้</span>
            </div>
          </div>

          <router-link to="/login" class="back-to-login">← กลับไปหน้าเข้าสู่ระบบ</router-link>
        </div>

        <!-- Bottom link -->
        <p v-if="currentStep < 3" class="login-text">
          มีบัญชีอยู่แล้ว? <router-link to="/login">เข้าสู่ระบบ</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  display: flex;
  min-height: calc(100vh - 80px);
  background-color: #f8fafc;
}

.register-branding {
  flex: 1;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: white;
  position: relative;
  overflow: hidden;
}

.branding-content {
  position: relative;
  z-index: 2;
  max-width: 420px;
}

.branding-content h1 {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 12px;
  background: linear-gradient(to right, var(--mso-accent), var(--primary));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.tagline {
  font-size: 1.2rem;
  color: #94a3b8;
  margin-bottom: 40px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.feature-icon {
  font-size: 1.5rem;
  width: 44px;
  height: 44px;
  background: rgba(236, 72, 153, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-item h4 {
  color: #e2e8f0;
  margin: 0 0 4px;
  font-size: 1rem;
}

.feature-item p {
  color: #64748b;
  font-size: 0.85rem;
  margin: 0;
  line-height: 1.4;
}

.branding-accent {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(236, 72, 153, 0.08) 0%, transparent 70%);
  z-index: 1;
}

.register-form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.form-card {
  width: 100%;
  max-width: 500px;
  background: white;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
}

/* Steps indicator */
.steps-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
  gap: 0;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: #94a3b8;
  transition: all 0.3s;
}

.step.active .step-circle {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}

.step.done .step-circle {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}

.step span {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
}

.step.active span {
  color: var(--primary);
}

.step-line {
  width: 60px;
  height: 2px;
  background: #e2e8f0;
  margin: 0 8px;
  margin-bottom: 20px;
  transition: background 0.3s;
}

.step-line.active {
  background: var(--primary);
}

/* Form */
h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.subtitle {
  color: #64748b;
  margin-bottom: 24px;
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 16px;
  flex: 1;
}

.form-row {
  display: flex;
  gap: 16px;
}

label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 6px;
}

input[type="text"],
input[type="email"],
input[type="password"] {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.2s;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(186, 26, 93, 0.1);
}

.password-input-wrapper {
  position: relative;
}

.password-input-wrapper input {
  padding-right: 44px;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 4px;
}

.password-strength {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s;
}

.field-hint {
  font-size: 0.8rem;
  margin-top: 4px;
  display: block;
}

.field-hint.error {
  color: #ef4444;
}

.terms-group {
  margin: 20px 0;
}

.checkbox-container {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 0.85rem;
  color: #64748b;
  cursor: pointer;
  line-height: 1.4;
}

.checkbox-container a {
  color: var(--primary);
  text-decoration: underline;
}

.btn-row {
  display: flex;
  gap: 12px;
}

.btn-primary {
  flex: 1;
  padding: 12px;
  background-color: var(--primary);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 12px 20px;
  background: none;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  border-color: #94a3b8;
  color: #1e293b;
}

.error-alert {
  background-color: #fef2f2;
  border: 1px solid #ef4444;
  color: #b91c1c;
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 16px;
  font-size: 0.85rem;
}

.login-text {
  text-align: center;
  margin-top: 24px;
  font-size: 0.85rem;
  color: #64748b;
}

.login-text a {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
}

/* Success */
.success-content {
  text-align: center;
}

.success-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.success-info-card {
  background: #fdf2f8;
  border: 1px solid #fce7f3;
  border-radius: 12px;
  padding: 20px;
  margin: 24px 0;
  text-align: left;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #fce7f3;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #64748b;
  font-size: 0.85rem;
}

.info-value {
  color: #1e293b;
  font-weight: 600;
  font-size: 0.85rem;
}

.status-pending {
  color: #f59e0b;
}

.success-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 24px 0;
  flex-wrap: wrap;
}

.flow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.flow-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
}

.flow-number.done {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.flow-step.current .flow-number {
  border-color: #f59e0b;
  color: #f59e0b;
  animation: pulse 2s infinite;
}

.flow-step span {
  font-size: 0.7rem;
  color: #94a3b8;
}

.flow-arrow {
  color: #cbd5e1;
  font-weight: 600;
  margin-bottom: 18px;
}

.test-note {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 24px;
  margin: 24px 0;
  text-align: left;
}

.mailhog-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  text-decoration: none;
  color: #1e293b;
  transition: all 0.2s;
}

.mailhog-link:hover {
  border-color: #f472b6;
  background: #fff1f2;
}

.mailhog-link .icon { font-size: 1.25rem; }
.mailhog-link .text { display: flex; flex-direction: column; flex: 1; }
.mailhog-link .text strong { font-size: 0.9rem; }
.mailhog-link .text span { font-size: 0.75rem; color: #64748b; }
.mailhog-link .arrow { color: #94a3b8; }

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.divider::before, .divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e2e8f0;
}

.divider:not(:empty)::before { margin-right: .5em; }
.divider:not(:empty)::after { margin-left: .5em; }

.btn-simulation {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 12px;
  background-color: #1e293b;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-simulation:hover {
  background-color: #0f172a;
  transform: translateY(-1px);
}

.back-to-login {
  display: inline-block;
  margin-top: 16px;
  color: #64748b;
  text-decoration: none;
  font-size: 0.9rem;
}

.back-to-login:hover {
  color: var(--mso-accent);
}

.loader {
  width: 18px;
  height: 18px;
  border: 2px solid #ffffff;
  border-bottom-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
}

@media (max-width: 768px) {
  .register-container { flex-direction: column; }
  .register-branding { padding: 40px 20px; }
  .form-row { flex-direction: column; gap: 0; }
}
</style>
