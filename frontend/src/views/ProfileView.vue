<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { postWithUser, encodeUserData } from '../utils/api';
import { encodePassword } from '../utils/crypto';

const router = useRouter();
const activeTab = ref('personal');
const isLoading = ref(false);
const isGeneratingKey = ref(false);
const message = ref({ text: '', type: '' });

const user = ref({
  user_id: '',
  firstname: '',
  lastname: '',
  email: '',
  usage_objective: '',
  other_object: '',
  apikey: '',
  role: 'User'
});

// Password Change states & methods
const showPasswordForm = ref(true);
const isSavingPassword = ref(false);
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const showCurrentPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

const passwordCriteria = computed(() => {
  const p = passwordForm.value.newPassword || '';
  return {
    length: p.length >= 8,
    uppercase: /[A-Z]/.test(p),
    lowercase: /[a-z]/.test(p),
    number: /[0-9]/.test(p),
    special: /[^A-Za-z0-9]/.test(p),
    match: Boolean(p && passwordForm.value.confirmPassword && p === passwordForm.value.confirmPassword)
  };
});

const isPasswordFormValid = computed(() => {
  const c = passwordCriteria.value;
  return Boolean(
    passwordForm.value.currentPassword.trim().length > 0 &&
    c.length &&
    c.uppercase &&
    c.lowercase &&
    c.number &&
    c.special &&
    c.match
  );
});

const passwordStrength = computed(() => {
  const p = passwordForm.value.newPassword;
  if (!p) return { score: 0, label: '', color: '#e2e8f0' };
  let score = 0;
  if (p.length >= 8) score++;
  if (/[A-Z]/.test(p)) score++;
  if (/[a-z]/.test(p)) score++;
  if (/[0-9]/.test(p)) score++;
  if (/[^A-Za-z0-9]/.test(p)) score++;
  
  const levels = [
    { score: 0, label: '', color: '#e2e8f0' },
    { score: 1, label: 'อ่อนมาก', color: '#ef4444' },
    { score: 2, label: 'อ่อน', color: '#f97316' },
    { score: 3, label: 'ปานกลาง', color: '#f59e0b' },
    { score: 4, label: 'ดี', color: '#10b981' },
    { score: 5, label: 'ดีมาก', color: '#059669' }
  ];
  return levels[score] || levels[0];
});

const handlePasswordChange = async () => {
  if (!passwordForm.value.currentPassword) {
    message.value = { text: 'กรุณากรอกรหัสผ่านปัจจุบัน', type: 'error' };
    return;
  }
  if (!isPasswordFormValid.value) {
    message.value = { text: 'รหัสผ่านใหม่ต้องตรงตามเงื่อนไขความปลอดภัยและยืนยันรหัสผ่านให้ตรงกัน', type: 'error' };
    return;
  }

  isSavingPassword.value = true;
  message.value = { text: '', type: '' };
  
  try {
    const userData = localStorage.getItem('user');
    const parsedUser = userData ? JSON.parse(userData) : {};
    const userId = user.value.user_id || parsedUser.user_id;

    const response = await apiClient.post('/changePassword', {
      user_id: userId,
      user: userData ? encodeUserData(parsedUser) : null,
      currentPassword: encodePassword(passwordForm.value.currentPassword),
      password: encodePassword(passwordForm.value.newPassword)
    });
    
    const result = response.data;
    
    if (result.status === 'success') {
      message.value = { text: 'เปลี่ยนรหัสผ่านสำเร็จ! กำลังนำท่านเข้าสู่ระบบใหม่...', type: 'success' };
      passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' };
      setTimeout(() => {
        // Cancel old session
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        localStorage.removeItem('lastActivity');
        localStorage.removeItem('user_favorites');
        sessionStorage.clear();
        window.dispatchEvent(new Event('auth-change'));
        window.location.href = '/login';
      }, 2000);
    } else if (result.status === 'password incorrect') {
      message.value = { text: 'รหัสผ่านปัจจุบันไม่ถูกต้อง', type: 'error' };
    } else if (result.status === 'same password') {
      message.value = { text: 'ไม่สามารถใช้รหัสผ่านเดิมที่เคยใช้งานแล้วได้', type: 'error' };
    } else {
      message.value = { text: result.message || 'เกิดข้อผิดพลาดในการเปลี่ยนรหัสผ่าน', type: 'error' };
    }
  } catch (error) {
    console.error('Password change error:', error);
    message.value = { text: error.response?.data?.message || 'ไม่สามารถเปลี่ยนรหัสผ่านได้ กรุณาลองใหม่', type: 'error' };
  } finally {
    isSavingPassword.value = false;
  }
};

const cancelPasswordChange = () => {
  passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' };
  message.value = { text: '', type: '' };
};

// Notifications states & methods
const notificationSettings = ref({
  email: true,
  security: true,
  usage: false
});

const saveNotificationSettings = () => {
  message.value = { text: 'บันทึกการตั้งค่าการแจ้งเตือนสำเร็จ!', type: 'success' };
  setTimeout(() => {
    if (message.value.text.includes('แจ้งเตือน')) {
      message.value = { text: '', type: '' };
    }
  }, 3000);
};

const copyApiKey = () => {
  if (user.value.apikey) {
    navigator.clipboard.writeText('?apikey=' + user.value.apikey);
    message.value = { text: 'คัดลอก API Key ลงคลิปบอร์ดสำเร็จ!', type: 'success' };
    setTimeout(() => { 
      if(message.value.text.includes('คลิปบอร์ด')) message.value = { text: '', type: '' }; 
    }, 3000);
  }
};

const generateApiKey = async () => {
  if (user.value.apikey && !confirm('การสร้าง Key ใหม่จะทำให้ Key เดิมหลุดการเชื่อมต่อ และใช้งานไม่ได้อีก คุณแน่ใจหรือไม่?')) {
    return;
  }
  
  isGeneratingKey.value = true;
  message.value = { text: '', type: '' };
  
  try {
    const payload = {
      user: { user_id: user.value.user_id }
    };
    
    // Use the postWithUser helper that encodes the payload
    const response = await postWithUser('/generateApiKey', payload.user);
    if (response.data.status === 'success') {
      message.value = { text: 'API Key ใหม่ถูกสร้างและบันทึกเรียบร้อย!', type: 'success' };
      const updatedUser = { ...user.value, ...response.data.data[0] };
      user.value = updatedUser;
      localStorage.setItem('user', JSON.stringify(updatedUser)); // Persist key locally
    } else {
      message.value = { text: response.data.message || 'ไม่สามารถสร้าง API Key ได้', type: 'error' };
    }
  } catch (error) {
    console.error('Error Generating Key:', error);
    message.value = { text: 'เกิดข้อผิดพลาดในการสร้างคีย์', type: 'error' };
  } finally {
    isGeneratingKey.value = false;
  }
};

onMounted(async () => {
  let savedUser = JSON.parse(localStorage.getItem('user') || '{}');
  if (savedUser.username) {
    try {
      const res = await postWithUser('/getMenuByPermission', savedUser);
      if (res.data && res.data.current_role) {
        savedUser.previlage_id = res.data.current_role;
        if (String(res.data.current_role) === '4') {
          savedUser.isAdmin = 'true';
          savedUser.role = 'System Administrator';
        } else if (String(res.data.current_role) === '3') {
          savedUser.isAdmin = 'false';
          savedUser.role = 'Department Admin';
        } else if (String(res.data.current_role) === '5') {
          savedUser.isAdmin = 'false';
          savedUser.role = 'ผู้ใช้งานภายใน (มีสิทธิ์ Dataset)';
        } else if (String(res.data.current_role) === '2') {
          savedUser.isAdmin = 'false';
          savedUser.role = 'General User';
        } else {
          savedUser.isAdmin = 'false';
          savedUser.role = 'External User';
        }
        localStorage.setItem('user', JSON.stringify(savedUser));
      }
    } catch (e) {
      console.error('Failed to sync role in profile', e);
    }

    let calculatedRole = savedUser.role || 'User';
    const privId = String(savedUser.previlage_id);
    if (privId === '4') calculatedRole = 'System Administrator';
    else if (privId === '3') calculatedRole = 'Department Admin';
    else if (privId === '5') calculatedRole = 'ผู้ใช้งานภายใน (มีสิทธิ์ Dataset)';
    else if (privId === '2') calculatedRole = 'General User';
    else if (privId === '1') calculatedRole = 'External User';

    user.value = {
      ...user.value,
      ...savedUser,
      role: calculatedRole
    };
  }
});

const saveChanges = async () => {
  isLoading.value = true;
  message.value = { text: '', type: '' };
  
  try {
    const payload = {
      user: {
        user_id: user.value.user_id,
        firstname: user.value.firstname,
        lastname: user.value.lastname,
        email: user.value.email,
        usage_objective: user.value.usage_objective,
        other_object: user.value.other_object
      },
      link: window.location.origin
    };

    // The backend editProfileUser expects 'user' to be a stringified object (encoded by postWithUser)
    const response = await postWithUser('/editProfileUser', payload.user, { link: payload.link });

    if (response.data.status === 'success') {
      message.value = { text: 'Profile updated successfully!', type: 'success' };
      // Update localStorage with new data
      const updatedUser = { ...user.value, ...response.data.data[0] };
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } else {
      message.value = { text: response.data.status || 'Failed to update profile.', type: 'error' };
    }
  } catch (error) {
    console.error('Error updating profile:', error);
    message.value = { text: 'An error occurred while saving changes.', type: 'error' };
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="profile-layout">
    <AppSidebar />
    
    <main class="profile-content">
      <header class="profile-header">
        <div class="avatar-area">
          <div class="avatar-circle">{{ (user.firstname ? user.firstname.charAt(0).toUpperCase() : '') + (user.lastname ? user.lastname.charAt(0).toUpperCase() : '') || 'U' }}</div>
          <button class="edit-avatar">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
              <path d="M10.5 8.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0z"/>
              <path d="M2 4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-1.172a2 2 0 0 1-1.414-.586l-.828-.828A2 2 0 0 0 9.172 2H6.828a2 2 0 0 0-1.414.586l-.828.828A2 2 0 0 1 3.172 4H2zm.5 2a.5.5 0 1 1 0-1 .5.5 0 0 1 0 1zm9 2.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0z"/>
            </svg>
          </button>
        </div>
        <div class="header-info">
          <h1>{{ user.firstname }} {{ user.lastname }}</h1>
          <p>{{ user.role }}</p>
        </div>
      </header>
      
      <div v-if="message.text" :class="['alert-message', message.type]">
        {{ message.text }}
      </div>
      
      <div class="settings-card">
        <nav class="settings-tabs">
          <button 
            @click="activeTab = 'personal'" 
            :class="['tab-link', { active: activeTab === 'personal' }]"
          >Personal Info</button>
          <button 
            @click="activeTab = 'security'" 
            :class="['tab-link', { active: activeTab === 'security' }]"
          >Security</button>
          <button 
            @click="activeTab = 'notifications'" 
            :class="['tab-link', { active: activeTab === 'notifications' }]"
          >Notifications</button>
        </nav>
        
        <div class="tab-pane">
          <div v-if="activeTab === 'personal'" class="form-grid">
            <div class="form-group">
              <label>First Name</label>
              <input type="text" v-model="user.firstname">
            </div>
            <div class="form-group">
              <label>Last Name</label>
              <input type="text" v-model="user.lastname">
            </div>
            <div class="form-group">
              <label>Email Address</label>
              <input type="email" v-model="user.email" disabled>
            </div>
            <div class="form-group">
              <label>Usage Objective</label>
              <input type="text" v-model="user.usage_objective">
            </div>
            <div class="form-group full">
              <label>Other Details</label>
              <input type="text" v-model="user.other_object">
            </div>
            
            <div class="form-group full" style="margin-top: 24px; padding-top: 24px; border-top: 1px solid #e2e8f0;">
              <label style="display: flex; align-items: center; gap: 8px; color: #475569; font-weight: 600;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" style="color: var(--primary-hover); min-width: 20px;" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 8a6 6 0 01-7.743 5.743L10 14l-1 1-1 1H6v2H2v-4l4.257-4.257A6 6 0 1118 8zm-6-4a1 1 0 100 2 2 2 0 012 2 1 1 0 102 0 4 4 0 00-4-4z" clip-rule="evenodd" />
                </svg>
                API Key (สำหรับเชื่อมต่อข้อมูล)
              </label>
              <div style="display: flex; align-items: center; gap: 12px; margin-top: 8px;">
                <input 
                  type="text" 
                  :value="user.apikey ? '?apikey=' + user.apikey : 'ระบบต้องการ API Key สำหรับเชื่อมต่อ'" 
                  disabled 
                  style="flex: 1; font-family: monospace; background-color: #f1f5f9; color: #334155;"
                >
                <button v-if="user.apikey" type="button" @click="copyApiKey" class="btn-outline flex items-center gap-2" style="white-space: nowrap; height: 100%;">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  คัดลอก
                </button>
                <button type="button" @click="generateApiKey" class="btn-primary" :disabled="isGeneratingKey" style="white-space: nowrap; height: 100%;">
                  {{ user.apikey ? 'สร้าง Key ใหม่ (Refresh)' : 'สร้าง API Key' }}
                </button>
              </div>
              <p style="font-size: 0.8rem; color: #64748b; margin-top: 10px;">
                * API Key ใช้เป็น Parameter ยืนยันตัวตนเวลาเรียก Endpoint (เช่น <code>?apikey=...</code>) โปรดเก็บรักษาให้ปลอดภัย
              </p>
            </div>
            
            <div class="form-actions">
              <button 
                class="btn-primary" 
                @click="saveChanges" 
                :disabled="isLoading"
              >{{ isLoading ? 'Saving...' : 'Save Changes' }}</button>
              <button class="btn-ghost">Cancel</button>
            </div>
          </div>
          
          <div v-if="activeTab === 'security'" class="security-pane">
            <div class="password-form-card" style="background: #f8fafc; padding: 28px; border-radius: 16px; border: 1px solid #e2e8f0; text-align: left;">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 36px; height: 36px; border-radius: 10px; background: #e0f2fe; color: #0284c7; display: flex; align-items: center; justify-content: center; font-size: 18px;">
                  🔒
                </div>
                <h4 style="margin: 0; font-weight:700; color:#1e293b; font-size: 1.15rem;">เปลี่ยนรหัสผ่าน (Change Password)</h4>
              </div>
              <p style="font-size:0.875rem; color:#64748b; margin-bottom: 24px;">โปรดกรอกรหัสผ่านปัจจุบันและตั้งรหัสผ่านใหม่ตามเงื่อนไขความปลอดภัย</p>
              
              <!-- Message Alert inside form -->
              <div v-if="message.text" :class="['alert-box', message.type]" style="margin-bottom: 20px; padding: 12px 16px; border-radius: 10px; font-size: 0.9rem; font-weight: 500;" :style="message.type === 'success' ? 'background: #dcfce7; color: #15803d; border: 1px solid #86efac;' : 'background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5;'">
                {{ message.text }}
              </div>

              <!-- Current Password -->
              <div class="form-group" style="margin-bottom: 20px;">
                <label style="display:block; font-size:0.875rem; font-weight:600; margin-bottom:8px; color:#334155;">
                  รหัสผ่านปัจจุบัน <span style="color:#ef4444;">*</span>
                </label>
                <div class="password-input-wrapper">
                  <input :type="showCurrentPassword ? 'text' : 'password'" v-model="passwordForm.currentPassword" class="form-control" placeholder="รหัสผ่านปัจจุบัน" />
                  <button type="button" class="toggle-password" @click="showCurrentPassword = !showCurrentPassword" tabindex="-1" title="แสดง/ซ่อนรหัสผ่าน">
                    <svg v-if="!showCurrentPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                  </button>
                </div>
              </div>

              <!-- New Password -->
              <div class="form-group" style="margin-bottom: 20px;">
                <label style="display:block; font-size:0.875rem; font-weight:600; margin-bottom:8px; color:#334155;">
                  รหัสผ่านใหม่ <span style="color:#ef4444;">*</span>
                </label>
                <div class="password-input-wrapper">
                  <input :type="showNewPassword ? 'text' : 'password'" v-model="passwordForm.newPassword" class="form-control" placeholder="ตั้งรหัสผ่าน 8 ตัวขึ้นไป" />
                  <button type="button" class="toggle-password" @click="showNewPassword = !showNewPassword" tabindex="-1" title="แสดง/ซ่อนรหัสผ่าน">
                    <svg v-if="!showNewPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                  </button>
                </div>
                
                <!-- Strength Meter -->
                <div class="password-strength-meter" style="margin-top: 10px; display: flex; align-items: center; gap: 10px;">
                  <div class="meter-bar" style="flex: 1; height: 6px; background: #e2e8f0; border-radius: 4px; overflow: hidden; display: flex;">
                    <div :style="{ width: (passwordStrength.score * 20) + '%', backgroundColor: passwordStrength.color, transition: 'all 0.3s' }"></div>
                  </div>
                  <span v-if="passwordStrength.label" :style="{ color: passwordStrength.color, fontWeight: 'bold', fontSize: '0.8rem', minWidth: '60px' }">
                    ความปลอดภัย: {{ passwordStrength.label }}
                  </span>
                </div>

                <!-- Password Checklist (Always Visible) -->
                <div class="password-checklist">
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
                      <span>มีอักขระพิเศษอย่างน้อย 1 ตัว (เช่น @, #, $, %, !)</span>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Confirm Password -->
              <div class="form-group" style="margin-bottom: 24px;">
                <label style="display:block; font-size:0.875rem; font-weight:600; margin-bottom:8px; color:#334155;">
                  ยืนยันรหัสผ่านใหม่ <span style="color:#ef4444;">*</span>
                </label>
                <div class="password-input-wrapper">
                  <input :type="showConfirmPassword ? 'text' : 'password'" v-model="passwordForm.confirmPassword" class="form-control" placeholder="พิมพ์รหัสผ่านใหม่อีกครั้ง" />
                  <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword" tabindex="-1" title="แสดง/ซ่อนรหัสผ่าน">
                    <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                  </button>
                </div>
                <small v-if="passwordForm.confirmPassword && passwordForm.newPassword !== passwordForm.confirmPassword" style="color: #ef4444; font-size: 0.8rem; margin-top: 6px; display: block; font-weight: 500;">✘ รหัสผ่านใหม่ไม่ตรงกัน</small>
                <small v-if="passwordForm.confirmPassword && passwordForm.newPassword === passwordForm.confirmPassword" style="color: #10b981; font-size: 0.8rem; margin-top: 6px; display: block; font-weight: 500;">✔ รหัสผ่านตรงกันแล้ว</small>
              </div>
              
              <div class="form-actions" style="display: flex; gap: 12px; margin-top: 10px;">
                <button class="btn-primary" :disabled="isSavingPassword || !isPasswordFormValid" @click="handlePasswordChange" style="padding: 10px 24px;">
                  <span v-if="isSavingPassword">กำลังบันทึก...</span>
                  <span v-else>บันทึกรหัสผ่านใหม่</span>
                </button>
                <button class="btn-ghost" @click="cancelPasswordChange">ยกเลิก</button>
              </div>
            </div>

            <div class="security-item">
              <div class="item-info">
                <h4>Two-Factor Authentication</h4>
                <p>Add an extra layer of security to your account.</p>
              </div>
              <button class="btn-outline">Enable</button>
            </div>
          </div>

          <div v-if="activeTab === 'notifications'" class="notifications-pane" style="display:flex; flex-direction:column; gap:24px;">
            <div style="background:#f8fafc; padding:24px; border-radius:16px; border:1px solid #e2e8f0; text-align:left;">
              <h4 style="margin:0 0 8px 0; font-weight:700; color:#1e293b;">การแจ้งเตือนระบบงาน</h4>
              <p style="font-size:0.875rem; color:#64748b; margin-bottom:20px;">ตั้งค่าระดับการแจ้งเตือนที่คุณต้องการรับทางช่องทางต่างๆ</p>
              
              <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid #e2e8f0;">
                <div>
                  <h5 style="margin:0 0 4px 0; font-weight:600; color:#1e293b;">การแจ้งเตือนทางอีเมล (Email Notifications)</h5>
                  <p style="margin:0; font-size:0.8rem; color:#64748b;">รับข้อมูล ข่าวสาร และผลการอนุมัติสิทธิ์เข้าถึงชุดข้อมูลทางอีเมล</p>
                </div>
                <input type="checkbox" v-model="notificationSettings.email" style="width:20px; height:20px; cursor:pointer;">
              </div>

              <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid #e2e8f0;">
                <div>
                  <h5 style="margin:0 0 4px 0; font-weight:600; color:#1e293b;">การแจ้งเตือนความปลอดภัย (Security Alerts)</h5>
                  <p style="margin:0; font-size:0.8rem; color:#64748b;">รับการแจ้งเตือนเมื่อตรวจพบการเข้าสู่ระบบผิดพลาดหรือมีการเปลี่ยนรหัสผ่าน</p>
                </div>
                <input type="checkbox" v-model="notificationSettings.security" style="width:20px; height:20px; cursor:pointer;">
              </div>

              <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0;">
                <div>
                  <h5 style="margin:0 0 4px 0; font-weight:600; color:#1e293b;">สรุปข้อมูลรายสัปดาห์ (Weekly Usage Summary)</h5>
                  <p style="margin:0; font-size:0.8rem; color:#64748b;">รับรายงานสถิติการใช้งานคีย์และการดาวน์โหลดไฟล์ข้อมูลรายสัปดาห์</p>
                </div>
                <input type="checkbox" v-model="notificationSettings.usage" style="width:20px; height:20px; cursor:pointer;">
              </div>
            </div>

            <div class="form-actions" style="display:flex; gap:12px;">
              <button class="btn-primary" @click="saveNotificationSettings">บันทึกการตั้งค่า</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.profile-layout {
  display: flex;
  background-color: #f8fafc;
  min-height: 100vh;
}

.profile-content {
  flex: 1;
  padding: 40px;
}

.alert-message {
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 24px;
  font-weight: 600;
  text-align: center;
}

.alert-message.success {
  background-color: var(--mso-pink-dark);
  color: #166534;
  border: 1px solid #bbf7d0;
}

.alert-message.error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 40px;
}

.header-info {
  word-break: break-word;
}

.header-info h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.avatar-area {
  position: relative;
}

.avatar-circle {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, var(--mso-accent), var(--primary));
  color: white;
  font-size: 2.5rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 32px;
  box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.2);
}

.edit-avatar {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 32px;
  height: 32px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #64748b;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.header-info p {
  color: #64748b;
  font-weight: 500;
}

.settings-card {
  background: white;
  border-radius: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  overflow: hidden;
}

.settings-tabs {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  padding: 0 24px;
  flex-wrap: wrap;
}

.tab-link {
  padding: 20px 24px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 1rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.tab-link.active {
  color: var(--mso-accent);
  border-bottom-color: var(--mso-accent);
}

.tab-pane {
  padding: 40px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.form-group.full {
  grid-column: span 2;
}

label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
}

input:disabled {
  background: #f8fafc;
  color: #94a3b8;
  cursor: not-allowed;
}

.form-actions {
  grid-column: span 2;
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: var(--mso-accent);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background-color: var(--primary-dark);
}

.btn-ghost {
  background: none;
  border: none;
  color: #64748b;
  padding: 12px 24px;
  font-weight: 600;
  cursor: pointer;
}

.security-pane {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: #f8fafc;
  border-radius: 16px;
}

.item-info h4 {
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.item-info p {
  font-size: 0.875rem;
  color: #64748b;
}

.btn-outline {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
}

@media (max-width: 1023px) {
  .profile-content { max-width: 100%; }
}

@media (max-width: 767px) {
  .profile-content { padding: 16px; margin-bottom: 60px; }
  .profile-header { flex-direction: column; text-align: center; gap: 16px; margin-bottom: 32px; }
  .form-grid { grid-template-columns: 1fr; }
  .form-group.full { grid-column: span 1; }
  .form-actions { grid-column: span 1; flex-direction: column; }
  .form-actions button { width: 100%; }
  .settings-tabs { overflow-x: auto; white-space: nowrap; flex-wrap: nowrap; }
  .tab-pane { padding: 24px 16px; }
  .security-item { flex-direction: column; align-items: flex-start; gap: 16px; }
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper input {
  width: 100%;
  padding-right: 44px;
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  height: 100%;
}

.toggle-password:hover {
  color: #1e293b;
}

.password-checklist {
  margin-top: 14px;
  margin-bottom: 8px;
  padding: 16px;
  background-color: #f1f8f5;
  border-radius: 12px;
  border: 1px solid #dcfce7;
}

.checklist-title {
  font-weight: 600;
  color: #166534;
  margin-bottom: 10px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.checklist-items {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checklist-items li {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: #ef4444; /* Default red when condition not met */
  transition: all 0.2s ease;
}

.checklist-items li.valid {
  color: #15803d; /* Green when condition met */
  font-weight: 500;
}

.checklist-items li .icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: bold;
  background-color: #fee2e2;
  color: #dc2626;
  flex-shrink: 0;
}

.checklist-items li.valid .icon {
  background-color: #86efac;
  color: #14532d;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
