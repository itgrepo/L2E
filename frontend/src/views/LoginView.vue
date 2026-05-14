<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import apiClient from '../utils/api';
import { themeConfig } from '../utils/theme';

const router = useRouter();
const route = useRoute();
const username = ref('');
const password = ref('');
const rememberMe = ref(false);
const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

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
      password: password.value,
      link: window.location.origin,
    });

    const result = response.data;
    
    if (result.status === 'success' || result.status === 'user is admin' || result.status === 'change password' || result.status === 'change password admin') {
      // Store user data in localStorage for simplicity (replace with Pinia if needed)
      localStorage.setItem('user', JSON.stringify(result.data));
      
      // Dispatch auth-change event so Navbar updates
      window.dispatchEvent(new Event('auth-change'));

      if (result.status.includes('change password')) {
        alert('Your password has expired. Please change your password.');
        router.push('/profile'); // Redirect to profile to change password
      } else {
        router.push('/catalog');
      }
    } else if (result.status === 'pending_approval') {
      errorMessage.value = 'บัญชีของคุณกำลังรอการอนุมัติจากผู้ดูแลระบบ กรุณารอการอนุมัติ';
    } else if (result.status === 'Please check in your email confirmation') {
      errorMessage.value = 'กรุณายืนยันอีเมลก่อนเข้าสู่ระบบ ตรวจสอบกล่องจดหมายของคุณ';
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
        
        <div class="test-credentials">
          <p><strong>บัญชีทดสอบ:</strong></p>
          <p>Username: <code>testadmin</code></p>
          <p>Password: <code>password123</code></p>
        </div>

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
            <input 
              id="password" 
              v-model="password" 
              type="password" 
              placeholder="••••••••" 
              required
              :disabled="isLoading"
            >
          </div>
          
          <div class="form-options">
            <label class="checkbox-container">
              <input type="checkbox" v-model="rememberMe" :disabled="isLoading">
              <span class="checkmark"></span>
              Remember me
            </label>
            <a href="#" class="forgot-link">Forgot password?</a>
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
  background-color: #fdf2f8;
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

.test-credentials {
  background-color: #fdf2f8;
  border: 1px solid #f9a8d4;
  color: #9d174d;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 0.875rem;
}

.test-credentials p {
  margin: 0;
}

.test-credentials code {
  background-color: #fce7f3;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
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
</style>
