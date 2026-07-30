<script setup>
import { ref, onMounted } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient, { postWithUser, encodeUserData } from '../utils/api';

const activeTab = ref('personal');
const isLoading = ref(false);
const isGeneratingKey = ref(false);
const message = ref({ text: '', type: '' });

// Password Change states & methods
const showPasswordForm = ref(false);
const isSavingPassword = ref(false);
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const handlePasswordChange = async () => {
  if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    message.value = { text: 'กรุณากรอกข้อมูลให้ครบถ้วน', type: 'error' };
    return;
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    message.value = { text: 'รหัสผ่านใหม่ไม่ตรงกัน', type: 'error' };
    return;
  }
  
  isSavingPassword.value = true;
  message.value = { text: '', type: '' };
  
  try {
    const response = await apiClient.post('/changePassword', {
      currentPassword: passwordForm.value.currentPassword,
      password: passwordForm.value.newPassword,
      user_id: encodeUserData(user.value.user_id.toString())
    });
    
    if (response.data.status === 'success') {
      message.value = { text: 'เปลี่ยนรหัสผ่านเรียบร้อยแล้ว!', type: 'success' };
      showPasswordForm.value = false;
      passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' };
    } else if (response.data.status === 'same password') {
      message.value = { text: 'รหัสผ่านใหม่ต้องไม่ซ้ำกับรหัสผ่าน 3 ครั้งล่าสุด', type: 'error' };
    } else {
      message.value = { text: 'รหัสผ่านปัจจุบันไม่ถูกต้อง', type: 'error' };
    }
  } catch (error) {
    console.error('Password change error:', error);
    message.value = { text: 'เกิดข้อผิดพลาดในการเปลี่ยนรหัสผ่าน', type: 'error' };
  } finally {
    isSavingPassword.value = false;
  }
};

const cancelPasswordChange = () => {
  showPasswordForm.value = false;
  passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' };
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

onMounted(() => {
  const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
  if (savedUser) {
    user.value = {
      ...user.value,
      ...savedUser
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
          <div class="avatar-circle">SJ</div>
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
            <div class="security-item" v-if="!showPasswordForm">
              <div class="item-info">
                <h4>Change Password</h4>
                <p>Update your password to keep your account secure.</p>
              </div>
              <button class="btn-outline" @click="showPasswordForm = true">Update</button>
            </div>
            
            <div v-else class="password-form-card" style="background: #f8fafc; padding: 24px; border-radius: 16px; border: 1px solid #e2e8f0; text-align: left;">
              <h4 style="margin: 0 0 8px 0; font-weight:700; color:#1e293b;">Change Password</h4>
              <p style="font-size:0.875rem; color:#64748b; margin-bottom: 20px;">กรุณากรอกรหัสผ่านเดิมและกำหนดรหัสผ่านใหม่เพื่อความปลอดภัย</p>
              
              <div class="form-group mb-4" style="margin-bottom: 16px;">
                <label style="display:block; margin-bottom:6px; font-weight:600; font-size:0.875rem;">Current Password *</label>
                <input type="password" v-model="passwordForm.currentPassword" placeholder="รหัสผ่านปัจจุบัน" required style="width:100%; box-sizing:border-box;">
              </div>
              
              <div class="form-group mb-4" style="margin-bottom: 16px;">
                <label style="display:block; margin-bottom:6px; font-weight:600; font-size:0.875rem;">New Password *</label>
                <input type="password" v-model="passwordForm.newPassword" placeholder="รหัสผ่านใหม่" required style="width:100%; box-sizing:border-box;">
              </div>
              
              <div class="form-group mb-4" style="margin-bottom: 20px;">
                <label style="display:block; margin-bottom:6px; font-weight:600; font-size:0.875rem;">Confirm New Password *</label>
                <input type="password" v-model="passwordForm.confirmPassword" placeholder="ยืนยันรหัสผ่านใหม่" required style="width:100%; box-sizing:border-box;">
              </div>
              
              <div class="form-actions" style="display: flex; gap: 12px;">
                <button class="btn-primary" :disabled="isSavingPassword" @click="handlePasswordChange">
                  {{ isSavingPassword ? 'Saving...' : 'Save Password' }}
                </button>
                <button class="btn-ghost" @click="cancelPasswordChange">Cancel</button>
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
</style>
