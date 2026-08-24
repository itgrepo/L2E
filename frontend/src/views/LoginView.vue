<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { encodePassword } from '../utils/crypto';
import apiClient from '../utils/api';
import { themeConfig } from '../utils/theme';

const router = useRouter();
const route = useRoute();
const username = ref('');
const password = ref('');
const showPassword = ref(false);
const rememberMe = ref(false);
const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Forgot Password States
const showForgotModal = ref(false);
const forgotUsername = ref('');
const isSendingForgot = ref(false);
const forgotError = ref('');
const forgotSuccess = ref('');

const openForgotModal = () => {
  showForgotModal.value = true;
  forgotUsername.value = '';
  forgotError.value = '';
  forgotSuccess.value = '';
};

const closeForgotModal = () => {
  showForgotModal.value = false;
};

const submitForgotPassword = async () => {
  if (!forgotUsername.value.trim()) return;
  isSendingForgot.value = true;
  forgotError.value = '';
  forgotSuccess.value = '';

  try {
    const response = await apiClient.post('/forgotPassword', {
      username: forgotUsername.value,
      link: window.location.origin
    });

    const result = response.data;
    const status = typeof result === 'string' ? result : result.status;

    if (status === 'success') {
      forgotSuccess.value = 'คำขอรีเซ็ตรหัสผ่านสำเร็จ! ระบบได้ส่งอีเมลรหัสผ่านชั่วคราวให้คุณแล้ว';
      setTimeout(() => {
        closeForgotModal();
      }, 3000);
    } else if (status === 'success (not have email)') {
      forgotSuccess.value = 'ระบบรีเซ็ตรหัสผ่านแล้ว (ผู้ใช้ไม่มีอีเมลในระบบ) โปรดติดต่อผู้ดูแลระบบเพื่อขอรับรหัสผ่านชั่วคราว';
    } else if (status === 'not found') {
      forgotError.value = 'ไม่พบชื่อผู้ใช้งานนี้ในระบบ';
    } else if (status === 'Your account is suspended') {
      forgotError.value = 'บัญชีของคุณถูกระงับการใช้งาน กรุณาติดต่อผู้ดูแลระบบ';
    } else {
      forgotError.value = status || 'ดำเนินการไม่สำเร็จ กรุณาลองใหม่อีกครั้ง';
    }
  } catch (error) {
    console.error('Forgot password error:', error);
    forgotError.value = 'ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ กรุณาลองใหม่ภายหลัง';
  } finally {
    isSendingForgot.value = false;
  }
};

onMounted(() => {
  if (route.query.verified === 'true') {
    successMessage.value = 'อีเมลได้รับการยืนยันแล้ว คุณสามารถเข้าสู่ระบบได้';
  }
});

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  
  try {
    const response = await apiClient.post('/login', {
      username: username.value,
      password: encodePassword(password.value),
      link: window.location.origin,
    });

    const result = response.data;
    
    if (result.status === 'success' || result.status === 'user is admin' || result.status === 'change password' || result.status === 'change password admin') {
      // Store user data in localStorage for simplicity (replace with Pinia if needed)
      localStorage.setItem('user', JSON.stringify(result.data));
      
      // Dispatch auth-change event so Navbar updates
      window.dispatchEvent(new Event('auth-change'));

      if (result.status.includes('change password')) {
        alert('รหัสผ่านของคุณหมดอายุแล้ว กรุณาเปลี่ยนรหัสผ่านเพื่อความปลอดภัย');
        router.push('/profile'); // Redirect to profile to change password
      } else {
        router.push('/catalog');
      }
    } else if (result.status === 'pending_approval') {
      errorMessage.value = 'บัญชีของคุณกำลังรอการอนุมัติจากผู้ดูแลระบบ กรุณารอการอนุมัติ';
    } else if (result.status === 'Please check in your email confirmation') {
      errorMessage.value = 'กรุณายืนยันอีเมลก่อนเข้าสู่ระบบ ตรวจสอบกล่องจดหมายของคุณ';
    } else if (result.status === 'not found' || result.status === 'username is incorrect') {
      if (result.attempts !== undefined) {
        errorMessage.value = `ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง (คุณสามารถลองใหม่ได้อีก ${5 - result.attempts} ครั้ง)`;
      } else {
        errorMessage.value = 'ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง';
      }
    } else if (result.status === 'Your account is locked' || result.status.includes('unlock account')) {
      errorMessage.value = 'บัญชีของคุณถูกล็อกชั่วคราวเนื่องจากเข้าสู่ระบบผิดพลาดเกินกำหนด กรุณาตรวจสอบอีเมลหรือติดต่อผู้ดูแลระบบเพื่อปลดล็อก';
    } else if (result.status === 'Your account is suspended') {
      errorMessage.value = 'บัญชีของคุณถูกระงับการใช้งานชั่วคราว กรุณาติดต่อผู้ดูแลระบบ';
    } else {
      errorMessage.value = result.status || 'เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่';
    }
  } catch (error) {
    console.error('Login error:', error);
    if (error.response && error.response.data) {
      errorMessage.value = error.response.data.message || error.response.data.status || 'Cannot connect to the server. Please try again later.';
    } else {
      errorMessage.value = 'Cannot connect to the server. Please try again later.';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-branding">
      <div class="branding-content">
        <h1>{{ themeConfig.siteName }}</h1>
        <p class="tagline">เชื่อมต่อข้อมูลอย่างปลอดภัยและมีมาตรฐาน</p>
        <div class="branding-accent"></div>
      </div>
    </div>
    
    <div class="login-form-side">
      <div class="form-card">
        <h2>Welcome Back</h2>
        <p class="subtitle">Please enter your details to sign in</p>
        
        

        <div v-if="successMessage" class="success-alert">
          {{ successMessage }}
        </div>

        <div v-if="errorMessage" class="error-alert">
          {{ errorMessage }}
        </div>

        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="username">Username</label>
            <input 
              id="username" 
              v-model="username" 
              type="text" 
              placeholder="Enter your username" 
              required
              :disabled="isLoading"
            >
          </div>
          
          <div class="form-group">
            <label for="password">Password</label>
            <div class="password-wrapper">
              <input 
                id="password" 
                v-model="password" 
                :type="showPassword ? 'text' : 'password'" 
                placeholder="••••••••" 
                required
                :disabled="isLoading"
              >
              <button 
                type="button" 
                class="toggle-password" 
                @click="showPassword = !showPassword"
                title="Toggle password visibility"
              >
                <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
              </button>
            </div>
          </div>
          
          <div class="form-options">
            <label class="checkbox-container">
              <input type="checkbox" v-model="rememberMe" :disabled="isLoading">
              <span class="checkmark"></span>
              Remember me
            </label>
            <a href="#" class="forgot-link" @click.prevent="openForgotModal">Forgot password?</a>
          </div>
          
          <button type="submit" class="login-btn" :disabled="isLoading">
            <span v-if="isLoading" class="loader"></span>
            <span v-else>เข้าสู่ระบบ</span>
          </button>
        </form>
        
        <p class="register-text">
          Don't have an account? <router-link to="/register">สมัครสมาชิก</router-link>
        </p>
      </div>
    </div>

    <!-- Forgot Password Modal -->
    <div v-if="showForgotModal" class="forgot-modal-overlay" @click.self="closeForgotModal">
      <div class="forgot-modal-card">
        <div class="modal-header">
          <h3>ลืมรหัสผ่าน?</h3>
          <button type="button" class="btn-close" @click="closeForgotModal">✕</button>
        </div>
        <div class="modal-body">
          <p class="instruction">กรุณากรอก Username ของคุณเพื่อดำเนินส่งคำขอรีเซ็ตรหัสผ่าน</p>
          <div class="form-group">
            <label for="forgot-username">Username</label>
            <input 
              id="forgot-username" 
              v-model="forgotUsername" 
              type="text" 
              placeholder="ระบุชื่อผู้ใช้งาน" 
              required
              @keyup.enter="submitForgotPassword"
            >
          </div>
          <div v-if="forgotError" class="error-alert" style="margin-top: 10px;">{{ forgotError }}</div>
          <div v-if="forgotSuccess" class="success-alert" style="margin-top: 10px;">{{ forgotSuccess }}</div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn-cancel" @click="closeForgotModal" :disabled="isSendingForgot">ยกเลิก</button>
          <button type="button" class="btn-submit" @click="submitForgotPassword" :disabled="isSendingForgot || !forgotUsername.trim()">
            <span v-if="isSendingForgot" class="loader small"></span>
            <span v-else>ส่งคำขอ</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  min-height: calc(100vh - 80px); /* Adjust for navbar if needed or make it full screen */
  background-color: #f8fafc;
}

.login-branding {
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
  text-align: center;
}

.branding-content h1 {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 20px;
  background: linear-gradient(to right, var(--mso-accent, var(--mso-accent)), var(--primary, var(--primary)));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.tagline {
  font-size: 1.25rem;
  color: #94a3b8;
  max-width: 400px;
}

.branding-accent {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(236, 72, 153, 0.1) 0%, transparent 70%);
  z-index: 1;
}

.login-form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.form-card {
  width: 100%;
  max-width: 440px;
  background: white;
  padding: 48px;
  border-radius: 24px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
}

h2 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.subtitle {
  color: #64748b;
  margin-bottom: 32px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}


.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.toggle-password:hover {
  color: #334155;
}
input[type="text"],

input[type="password"] {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.2s;
}

input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 1px var(--primary);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #64748b;
  cursor: pointer;
}

.forgot-link {
  font-size: 0.875rem;
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background-color: var(--primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.login-btn:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}

.register-text {
  text-align: center;
  margin-top: 32px;
  font-size: 0.875rem;
  color: #64748b;
}

.register-text a {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
}

.success-alert {
  background-color: var(--mso-pink-dark);
  border: 1px solid #f9a8d4;
  color: #9d174d;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.error-alert {
  background-color: #fef2f2;
  border: 1px solid #ef4444;
  color: #b91c1c;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 0.875rem;
}



.loader {
  width: 20px;
  height: 20px;
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

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .login-branding {
    padding: 40px 20px;
    min-height: auto;
  }

  .branding-content h1 {
    font-size: 2.5rem;
  }

  .tagline {
    font-size: 1rem;
  }

  .login-form-side {
    padding: 24px 16px;
  }

  .form-card {
    padding: 28px 20px;
    border-radius: 16px;
  }

  h2 {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .login-branding {
    padding: 32px 16px;
  }

  .branding-content h1 {
    font-size: 2rem;
  }

  .form-card {
    padding: 24px 16px;
  }

  .form-options {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}

.forgot-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.forgot-modal-card {
  background: white;
  width: 90%;
  max-width: 400px;
  border-radius: 20px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.forgot-modal-card .modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-modal-card .modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #94a3b8;
  cursor: pointer;
}

.forgot-modal-card .modal-body {
  padding: 24px;
}

.forgot-modal-card .instruction {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 16px;
  line-height: 1.5;
}

.forgot-modal-card .modal-footer {
  padding: 16px 24px;
  background-color: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #f1f5f9;
}

.btn-cancel {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: white;
  color: #64748b;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-submit {
  padding: 8px 20px;
  border-radius: 8px;
  border: none;
  background: var(--primary);
  color: white;
  font-weight: 600;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loader.small {
  width: 14px;
  height: 14px;
  border-width: 1.5px;
}
</style>
