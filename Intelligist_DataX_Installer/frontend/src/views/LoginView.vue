<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { encodePassword } from '../utils/crypto';
import apiClient from '../utils/api';
import { themeConfig } from '../utils/theme';

import QRCode from 'qrcode';

const router = useRouter();
const route = useRoute();
const username = ref('');
const password = ref('');
const showPassword = ref(false);
const rememberMe = ref(false);
const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// 2FA States
const step = ref('credentials'); // 'credentials' | '2fa_verify' | '2fa_setup'
const tempToken = ref('');
const otpCode = ref('');
const secretKey = ref('');
const otpauthUrl = ref('');
const qrCodeDataUrl = ref('');
const copiedSecret = ref(false);

const copySecretKey = () => {
  if (secretKey.value) {
    navigator.clipboard.writeText(secretKey.value);
    copiedSecret.value = true;
    setTimeout(() => { copiedSecret.value = false; }, 2000);
  }
};

const cancel2FA = () => {
  step.value = 'credentials';
  tempToken.value = '';
  otpCode.value = '';
  secretKey.value = '';
  otpauthUrl.value = '';
  qrCodeDataUrl.value = '';
  errorMessage.value = '';
};

const handleSuccessfulLogin = (result) => {
  if (rememberMe.value) {
    localStorage.setItem('remembered_username', username.value);
  } else {
    localStorage.removeItem('remembered_username');
  }

  localStorage.setItem('user', JSON.stringify(result.data));
  window.dispatchEvent(new Event('auth-change'));

  const isPending = (
    String(result.data?.previlage_id) === '1' ||
    String(result.data?.status_id) === '8' ||
    result.data?.is_approved === false ||
    result.data?.requires_onboarding === true
  );

  if (result.status && result.status.includes('change password')) {
    alert('รหัสผ่านของคุณหมดอายุแล้ว กรุณาเปลี่ยนรหัสผ่านเพื่อความปลอดภัย');
    router.push('/profile');
  } else if (isPending) {
    router.push('/profile');
  } else {
    router.push('/catalog');
  }
};

const handle2FAVerify = async () => {
  if (!otpCode.value || otpCode.value.trim().length < 6) {
    errorMessage.value = 'กรุณากรอกรหัส OTP 6 หลักให้ครบถ้วน';
    return;
  }
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const response = await apiClient.post('/api/2fa/login-verify', {
      temp_token: tempToken.value,
      otp: otpCode.value.trim()
    });
    handleSuccessfulLogin(response.data);
  } catch (error) {
    console.error('2FA Verify error:', error);
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage.value = error.response.data.message;
    } else {
      errorMessage.value = 'รหัส OTP ไม่ถูกต้องหรือหมดอายุแล้ว กรุณาลองใหม่อีกครั้ง';
    }
  } finally {
    isLoading.value = false;
  }
};

const handle2FASetupVerify = async () => {
  if (!otpCode.value || otpCode.value.trim().length < 6) {
    errorMessage.value = 'กรุณากรอกรหัส OTP 6 หลักให้ครบถ้วน';
    return;
  }
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const response = await apiClient.post('/api/2fa/setup-and-login-verify', {
      temp_token: tempToken.value,
      otp: otpCode.value.trim()
    });
    handleSuccessfulLogin(response.data);
  } catch (error) {
    console.error('2FA Setup Verify error:', error);
    if (error.response && error.response.data && error.response.data.message) {
      errorMessage.value = error.response.data.message;
    } else {
      errorMessage.value = 'รหัส OTP ไม่ถูกต้อง กรุณาตรวจสอบรหัสในแอปอีกครั้ง';
    }
  } finally {
    isLoading.value = false;
  }
};

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
  // If user is already authenticated, redirect immediately
  const rawUser = localStorage.getItem('user');
  if (rawUser) {
    try {
      const user = JSON.parse(rawUser);
      if (user && (user.user_id || user.username)) {
        const isPending = (
          String(user.previlage_id) === '1' ||
          String(user.status_id) === '8' ||
          user.is_approved === false ||
          user.requires_onboarding === true
        );
        if (isPending) {
          router.replace('/profile');
        } else {
          router.replace('/catalog');
        }
        return;
      }
    } catch (e) {
      console.error('Error parsing stored user in LoginView:', e);
    }
  }

  if (route.query.verified === 'true') {
    successMessage.value = 'อีเมลได้รับการยืนยันแล้ว คุณสามารถเข้าสู่ระบบได้';
  }

  // Load remembered username
  const savedUsername = localStorage.getItem('remembered_username');
  if (savedUsername) {
    username.value = savedUsername;
    rememberMe.value = true;
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
    
    if (result.status === 'require_2fa') {
      tempToken.value = result.temp_token;
      step.value = '2fa_verify';
      otpCode.value = '';
      errorMessage.value = '';
    } else if (result.status === 'require_2fa_setup') {
      tempToken.value = result.temp_token;
      secretKey.value = result.secret_key;
      otpauthUrl.value = result.otpauth_url;
      step.value = '2fa_setup';
      otpCode.value = '';
      errorMessage.value = '';
      try {
        qrCodeDataUrl.value = await QRCode.toDataURL(result.otpauth_url, {
          width: 220,
          margin: 1,
          color: { dark: '#0f172a', light: '#ffffff' }
        });
      } catch (err) {
        console.error('Error generating QR code:', err);
      }
    } else if (result.status === 'success' || result.status === 'user is admin' || result.status === 'change password' || result.status === 'change password admin') {
      handleSuccessfulLogin(result);
    } else if (result.status === 'pending_approval') {
      errorMessage.value = 'บัญชีของคุณกำลังรอการอนุมัติจากผู้ดูแลระบบ กรุณารอการอนุมัติ';
    } else if (result.status === 'Your account is locked' || (result.status && result.status.includes('unlock account'))) {
      errorMessage.value = '🚨 บัญชีของคุณถูกระงับการใช้งานชั่วคราวเนื่องจากกรอกรหัสผ่านผิดเกินจำนวนครั้งที่กำหนด กรุณาติดต่อผู้ดูแลระบบหรือทำการปลดล็อคผ่านอีเมล';
    } else if (result.status && result.status.includes('Please check in your email confirmation')) {
      errorMessage.value = 'กรุณายืนยันอีเมลก่อนเข้าสู่ระบบ ตรวจสอบกล่องจดหมายของคุณ';
    } else if (result.status === 'not found' || result.status === 'username is incorrect') {
      if (result.attempts !== undefined) {
        const remaining = 5 - result.attempts;
        errorMessage.value = `ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง (คุณสามารถลองใหม่ได้อีก ${remaining} ครั้ง)`;
      } else {
        errorMessage.value = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง';
      }
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
        <template v-if="step === 'credentials'">
          <h2>Welcome Back</h2>
          <p class="subtitle">Please enter your details to sign in</p>
        </template>
        <template v-else-if="step === '2fa_verify'">
          <div class="step-badge">🔐 ขั้นตอนที่ 2 / 2</div>
          <h2>Google Authenticator</h2>
          <p class="subtitle">กรุณาเปิดแอปบนมือถือและนำรหัสยืนยัน 6 หลักมากรอก</p>
        </template>
        <template v-else-if="step === '2fa_setup'">
          <div class="step-badge step-badge-setup">🛡️ ตั้งค่าความปลอดภัย 2 ชั้น</div>
          <h2>Google Authenticator</h2>
          <p class="subtitle">สแกน QR Code ด้วยแอป Google Authenticator แล้วกรอกรหัส 6 หลักเพื่อเริ่มต้นใช้งาน</p>
        </template>

        <div v-if="successMessage" class="success-alert">
          {{ successMessage }}
        </div>

        <div v-if="errorMessage && errorMessage.includes('ถูกระงับการใช้งานชั่วคราว')" class="locked-alert" style="background-color: #fef2f2; color: #991b1b; border: 2px solid #f87171; padding: 16px; border-radius: 8px; margin-bottom: 24px; font-weight: 600; text-align: center; box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.1);">
          {{ errorMessage }}
          <div style="margin-top: 12px;">
            <router-link to="/contact" style="display: inline-block; padding: 8px 16px; background-color: #ef4444; color: white; border-radius: 6px; text-decoration: none; font-size: 0.9rem;">
              ติดต่อผู้ดูแลระบบ (Contact Admin)
            </router-link>
          </div>
        </div>
        <div v-else-if="errorMessage" class="error-alert">
          {{ errorMessage }}
        </div>

        <!-- 1. Credentials Form -->
        <form v-if="step === 'credentials'" @submit.prevent="handleLogin">
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

        <!-- 2. Step 2FA Verification Form -->
        <form v-else-if="step === '2fa_verify'" @submit.prevent="handle2FAVerify" class="two-factor-form">
          <div class="form-group" style="margin-top: 10px;">
            <label for="otp-code">รหัส OTP 6 หลัก (จากแอป Authenticator)</label>
            <input 
              id="otp-code" 
              v-model="otpCode" 
              type="text" 
              inputmode="numeric"
              maxlength="6"
              placeholder="000 000" 
              class="otp-input"
              required
              autofocus
              autocomplete="one-time-code"
              :disabled="isLoading"
            >
          </div>

          <button type="submit" class="login-btn" :disabled="isLoading || otpCode.trim().length < 6">
            <span v-if="isLoading" class="loader"></span>
            <span v-else>ยืนยันและเข้าสู่ระบบ</span>
          </button>

          <div class="back-link-box">
            <a href="#" class="forgot-link" @click.prevent="cancel2FA">← กลับไปหน้าเข้าสู่ระบบ</a>
          </div>
        </form>

        <!-- 3. Step 2FA First-time Setup Form -->
        <form v-else-if="step === '2fa_setup'" @submit.prevent="handle2FASetupVerify" class="two-factor-form">
          <div class="qr-container">
            <div v-if="qrCodeDataUrl" class="qr-box">
              <img :src="qrCodeDataUrl" alt="2FA QR Code" class="qr-image" />
            </div>
            <div v-else class="qr-loading">กำลังโหลด QR Code...</div>

            <div class="secret-key-box">
              <span class="secret-label">หรือพิมพ์รหัสลับด้วยตนเอง:</span>
              <div class="secret-row">
                <code class="secret-code">{{ secretKey }}</code>
                <button type="button" class="copy-btn" @click="copySecretKey">
                  {{ copiedSecret ? '✓ คัดลอกแล้ว' : 'คัดลอก' }}
                </button>
              </div>
            </div>
          </div>

          <div class="form-group" style="margin-top: 16px;">
            <label for="setup-otp-code">กรอกรหัส 6 หลักจากแอปเพื่อทดสอบและยืนยัน</label>
            <input 
              id="setup-otp-code" 
              v-model="otpCode" 
              type="text" 
              inputmode="numeric"
              maxlength="6"
              placeholder="000 000" 
              class="otp-input"
              required
              autofocus
              autocomplete="one-time-code"
              :disabled="isLoading"
            >
          </div>

          <button type="submit" class="login-btn" :disabled="isLoading || otpCode.trim().length < 6">
            <span v-if="isLoading" class="loader"></span>
            <span v-else>เปิดใช้งาน 2FA และเข้าสู่ระบบ</span>
          </button>

          <div class="back-link-box">
            <a href="#" class="forgot-link" @click.prevent="cancel2FA">← ยกเลิกและกลับไปหน้าเข้าสู่ระบบ</a>
          </div>
        </form>
        
        <p v-if="step === 'credentials'" class="register-text">
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

/* 2FA Styles */
.step-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 9999px;
  margin-bottom: 12px;
}

.step-badge-setup {
  background: #fef3c7;
  color: #b45309;
}

.two-factor-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.otp-input {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
  font-size: 1.8rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.35em !important;
  text-align: center !important;
  padding: 12px 16px !important;
  color: #1e293b !important;
  background: #f8fafc !important;
  border: 2px solid #cbd5e1 !important;
  border-radius: 12px !important;
  transition: all 0.2s ease !important;
}

.otp-input:focus {
  border-color: #2563eb !important;
  background: #ffffff !important;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12) !important;
  outline: none !important;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  margin: 12px 0 8px 0;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
}

.qr-box {
  background: white;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: center;
  align-items: center;
}

.qr-image {
  width: 190px;
  height: 190px;
  display: block;
}

.qr-loading {
  height: 190px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 0.9rem;
}

.secret-key-box {
  width: 100%;
  text-align: center;
}

.secret-label {
  display: block;
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 6px;
}

.secret-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: white;
  padding: 6px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
}

.secret-code {
  font-family: ui-monospace, monospace;
  font-weight: 700;
  color: #0f172a;
  font-size: 0.95rem;
  letter-spacing: 0.05em;
}

.copy-btn {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.copy-btn:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.back-link-box {
  text-align: center;
  margin-top: 10px;
}
</style>
