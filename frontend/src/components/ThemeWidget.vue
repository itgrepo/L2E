<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { themeConfig, saveThemeConfig, defaultConfig } from '../utils/theme';

const isOpen = ref(false);
const initialConfig = ref({});
const isSuperAdmin = ref(false);

const checkAuth = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      // Check for super admin role via 'role' field (Node.js mockup) or 'previlage_id' (Python backend)
      const role = user.role ? user.role.toLowerCase() : '';
      const privId = String(user.previlage_id || '');
      if (role === 'superadmin' || role === 'super admin' || role === 'admin' || privId === '1' || privId === '2') {
        isSuperAdmin.value = true;
      } else {
        isSuperAdmin.value = false;
      }
    } catch (e) {
      console.error('Error parsing user data', e);
      isSuperAdmin.value = false;
    }
  } else {
    isSuperAdmin.value = false;
  }
};

onMounted(() => {
  checkAuth();
  window.addEventListener('auth-change', checkAuth);
});

onUnmounted(() => {
  window.removeEventListener('auth-change', checkAuth);
});

const toggleWidget = () => {
  if (!isOpen.value) {
    // Open widget: backup current config in case they cancel
    initialConfig.value = JSON.parse(JSON.stringify(themeConfig.value));
    isOpen.value = true;
  } else {
    // Close via toggle: assume cancel
    cancelTheme();
  }
};

const saveTheme = async () => {
  const success = await saveThemeConfig();
  if (success) {
    isOpen.value = false;
  }
};

const cancelTheme = () => {
  // Revert to backup
  themeConfig.value = { ...initialConfig.value };
  isOpen.value = false;
};

const handleLogoUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      themeConfig.value.logoUrl = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const resetTheme = () => {
  if (confirm('คุณต้องการรีเซ็ตการตั้งค่าทั้งหมดเป็นค่าเริ่มต้นใช่หรือไม่?')) {
    themeConfig.value = { ...defaultConfig };
    // Optionally auto-save on reset, or wait for user to click Save
  }
};
</script>

<template>
  <div class="theme-widget-container" v-if="isSuperAdmin">
    <button class="widget-toggle" @click="toggleWidget" title="ตั้งค่าธีม">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"></circle>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33 1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82 1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
      </svg>
    </button>

    <div v-if="isOpen" class="widget-panel">
      <div class="panel-header">
        <h3>ตั้งค่าเว็บไซต์</h3>
        <button @click="cancelTheme" class="close-btn">&times;</button>
      </div>

      <div class="panel-body">
        <div class="form-group">
          <label>ชื่อเว็บไซต์</label>
          <input type="text" v-model="themeConfig.siteName" placeholder="เช่น MSDHS DATA PORTAL" />
        </div>

        <div class="form-group">
          <label>โลโก้</label>
          <div class="logo-preview" v-if="themeConfig.logoUrl">
            <img :src="themeConfig.logoUrl" alt="Logo Preview" />
          </div>
          <input type="file" @change="handleLogoUpload" accept="image/*" class="file-input" />
          <small>อัปโหลดไฟล์รูปภาพใหม่</small>
        </div>

        <div class="form-group">
          <label>สีหลัก (Primary)</label>
          <div class="color-input-wrapper">
            <input type="color" v-model="themeConfig.primaryColor" />
            <input type="text" v-model="themeConfig.primaryColor" />
          </div>
        </div>

        <div class="form-group">
          <label>สีรอง (Secondary)</label>
          <div class="color-input-wrapper">
            <input type="color" v-model="themeConfig.secondaryColor" />
            <input type="text" v-model="themeConfig.secondaryColor" />
          </div>
        </div>

        <div class="form-group">
          <label>สีเน้น (Accent)</label>
          <div class="color-input-wrapper">
            <input type="color" v-model="themeConfig.accentColor" />
            <input type="text" v-model="themeConfig.accentColor" />
          </div>
        </div>

        <div class="form-group">
          <label>สีพื้นหลัง Sidebar</label>
          <div class="color-input-wrapper">
            <input type="color" v-model="themeConfig.sidebarColor" />
            <input type="text" v-model="themeConfig.sidebarColor" />
          </div>
        </div>
      </div>

      <div class="panel-footer">
        <button @click="resetTheme" class="btn-reset">รีเซ็ต</button>
        <button @click="cancelTheme" class="btn-cancel">ยกเลิก</button>
        <button @click="saveTheme" class="btn-save">บันทึก</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.theme-widget-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
}

.widget-toggle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  border: none;
}

.widget-toggle:hover {
  transform: rotate(45deg) scale(1.1);
  background-color: var(--primary-hover);
}

.widget-panel {
  position: absolute;
  bottom: 72px;
  right: 0;
  width: 320px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.panel-header {
  padding: 16px 20px;
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1e293b;
}

.close-btn {
  font-size: 24px;
  color: #64748b;
  line-height: 1;
}

.panel-body {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 6px;
}

.form-group input[type="text"] {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
}

.color-input-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
}

.color-input-wrapper input[type="color"] {
  width: 36px;
  height: 36px;
  padding: 0;
  border: none;
  background: none;
  cursor: pointer;
}

.logo-preview {
  width: 100%;
  height: 60px;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  background-color: #f1f5f9;
}

.logo-preview img {
  max-height: 50px;
  max-width: 90%;
}

.file-input {
  font-size: 0.8rem;
}

.panel-footer {
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 12px;
}

.btn-save {
  flex: 1;
  padding: 10px;
  background-color: var(--primary);
  color: white;
  border-radius: 8px;
  font-weight: 600;
}

.btn-reset, .btn-cancel {
  padding: 10px 12px;
  background-color: #f1f5f9;
  color: #64748b;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.btn-cancel:hover, .btn-reset:hover {
  background-color: #e2e8f0;
}

.btn-save:hover {
  background-color: var(--primary-hover);
}
</style>
