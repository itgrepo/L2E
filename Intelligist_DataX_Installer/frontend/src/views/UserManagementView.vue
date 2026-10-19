<script setup>
import { encodePassword } from '../utils/crypto';

import { ref, onMounted, computed } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import { postWithUser } from '../utils/api';

const users = ref([]);
const roles = ref([]);

const organizations = ref([]);
const fetchOrganizations = async () => {
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/getOrganizations', userStored);
        if (response.data && response.data.status === 'success') {
            organizations.value = response.data.data;
        }
    } catch (error) {
        console.error('Error fetching organizations:', error);
    }
};

const handleOrgChange = async (user, newOrgId) => {
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/updateUserById', userStored, {
            target_user_id: user.user_id,
            previlage_id: user.previlage_id,
            org_id: newOrgId
        });
        
        if (response.data.status === 'success') {
            showAlert(`อัปเดตหน่วยงานสำเร็จ`, 'success');
            fetchUsers(); 
        } else {
            alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));
        }
    } catch (error) {
        console.error('Error updating org:', error);
    }
};


const groups = ref([]);
const showAddModal = ref(false);
const formData = ref({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    previlage_id: 2,
    org_id: '',
    status_id: 4,
    groups: []
});

const showPassword = ref(false);
const showConfirmPassword = ref(false);

const passwordStrength = computed(() => {
  const p = formData.value.password;
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
    { score: 3, label: 'ดี', color: '#22c55e' },
    { score: 4, label: 'ดีมาก', color: '#16a34a' }
  ];
  return levels[score] || levels[0];
});

const isPasswordValid = computed(() => {
  const p = formData.value.password;
  const isStrong = p.length >= 8 && /[A-Z]/.test(p) && /[a-z]/.test(p) && /[0-9]/.test(p) && /[^A-Za-z0-9]/.test(p);
  const isMatch = p === formData.value.confirmPassword;
  return isStrong && isMatch;
});

const isSubmitting = ref(false);

const fetchGroups = async () => {
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/getGroups', userStored, { group_type: 'user_group' });
        if (response.data && response.data.status === 'success') {
            groups.value = response.data.data;
        }
    } catch (error) {
        console.error('Error fetching groups:', error);
    }
};

const openAddModal = () => {
    formData.value = {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        previlage_id: 2,
        org_id: '',
        status_id: 4,
        groups: []
    };
    showPassword.value = false;
    showConfirmPassword.value = false;
    showAddModal.value = true;
};

const closeAddModal = () => {
    showAddModal.value = false;
};

const handleSaveUser = async () => {
    if (!formData.value.username || !formData.value.email || !formData.value.password) {
        showAlert('กรุณากรอกข้อมูล Username, Email และ Password ให้ครบถ้วน', 'error');
        return;
    }

    if (!isPasswordValid.value) {
        showAlert('รหัสผ่านไม่ผ่านเกณฑ์ความปลอดภัย หรือรหัสผ่านไม่ตรงกัน', 'error');
        return;
    }

    const invalidCharsRegex = /[<>"\'/;`%&]/;
    if (invalidCharsRegex.test(formData.value.username)) {
        showAlert('ชื่อผู้ใช้มีตัวอักษรพิเศษที่ไม่อนุญาต', 'error');
        return;
    }
    if (invalidCharsRegex.test(formData.value.email)) {
        showAlert('อีเมลมีตัวอักษรพิเศษที่ไม่อนุญาต', 'error');
        return;
    }
    
    
    if (formData.value.previlage_id == 3 && !formData.value.org_id) {
        showAlert('กรุณาเลือกหน่วยงานสำหรับ Role นี้', 'error');
        return;
    }

    isSubmitting.value = true;
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const submitData = { ...formData.value };
        submitData.password = encodePassword(submitData.password);
        submitData.link = window.location.origin;
        const response = await postWithUser('/mgmt/createUser', userStored, submitData);
        
        if (response.data.status === 'success') {
            showAlert(`สร้างผู้ใช้ ${formData.value.username} สำเร็จ`, 'success');
            closeAddModal();
            fetchUsers();
        } else {
            let errorMsg = response.data.message || response.data.status;
            const errLower = errorMsg.toLowerCase();
            if (errLower === 'username or email already exists') {
                errorMsg = 'ชื่อผู้ใช้ หรือ อีเมล นี้ถูกใช้งานแล้ว';
            } else if (errLower.includes('username already exists') || errorMsg.includes('Username ซ้ำ')) {
                errorMsg = 'ชื่อผู้ใช้นี้ถูกใช้งานแล้ว (Username already exists)';
            } else if (errLower.includes('email already exists') || errorMsg.includes('อีเมลซ้ำ')) {
                errorMsg = 'อีเมลนี้ถูกใช้งานแล้ว (Email already exists)';
            }
            showAlert('เกิดข้อผิดพลาด: ' + errorMsg, 'error');
        }
    } catch (error) {
        console.error('Error creating user:', error);
        showAlert('เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');
    } finally {
        isSubmitting.value = false;
    }
};

const isLoading = ref(true);
const searchQuery = ref('');
const selectedOrgFilter = ref('');
const selectedRoleFilter = ref('');
const alertMessage = ref({ text: '', type: '' });

const clearAllFilters = () => {
    searchQuery.value = '';
    selectedOrgFilter.value = '';
    selectedRoleFilter.value = '';
};

const fetchUsers = async () => {
    isLoading.value = true;
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/addUser', userStored);
        if (Array.isArray(response.data)) {
            users.value = response.data;
        }
    } catch (error) {
        console.error('Error fetching users:', error);
    } finally {
        isLoading.value = false;
    }
};

const fetchRoles = async () => {
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/getRoles', userStored);
        if (Array.isArray(response.data)) {
            roles.value = response.data;
        }
    } catch (error) {
        console.error('Error fetching roles:', error);
    }
};

const getOrgName = (orgId) => {
    if (!orgId) return '-';
    const org = organizations.value.find(o => String(o.org_id) === String(orgId));
    return org ? org.org_name : '-';
};

const getRoleName = (roleId) => {
    if (!roleId) return '';
    const r = roles.value.find(role => String(role.previlage_id) === String(roleId));
    return r ? r.previlage_name : '';
};

const handleRoleChange = async (user, newRoleId) => {
    if (String(user.status_id) === '4') {
        alert('ผู้ใช้ยังไม่ได้ยืนยันอีเมล ไม่สามารถกำหนดบทบาทได้จนกว่าผู้ใช้จะยืนยันอีเมลสำเร็จ');
        return;
    }
    if (String(user.status_id) === '8') {
        alert('ผู้ใช้อยู่ในสถานะรออนุมัติ กรุณากดปุ่ม "อนุมัติ R2" ก่อนกำหนดบทบาท');
        return;
    }
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/updateUserById', userStored, {
            target_user_id: user.user_id,
            previlage_id: newRoleId
        });
        
        if (response.data.status === 'success') {
            showAlert(`อัปเดตบทบาทของ ${user.username} สำเร็จ`, 'success');
            fetchUsers(); // Refresh list to get new role names
        } else {
            alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));
        }
    } catch (error) {
        console.error('Error updating role:', error);
        alert('เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    }
};

const getUserStatusValue = (statusId) => {
    const s = String(statusId);
    if (s === '1' || s === '2') return 1;
    if (s === '4') return 4;
    if (s === '3') return 3;
    if (s === '6') return 6;
    if (s === '8') return 8;
    return 1;
};

const getStatusBadgeClass = (statusId) => {
    const val = getUserStatusValue(statusId);
    if (val === 1) return 'status-active';
    if (val === 4) return 'status-pending';
    if (val === 3) return 'status-suspended';
    if (val === 6) return 'status-locked';
    if (val === 8) return 'status-approval';
    return 'status-active';
};

const getStatusSelectTitle = (u) => {
    if (String(u.status_id) === '4') {
        return 'ผู้ใช้อยู่ระหว่างรอการยืนยันอีเมล (Pending Verification) ไม่สามารถเปลี่ยนสถานะได้จนกว่าผู้ใช้จะกดยืนยันในอีเมล';
    }
    if (String(u.status_id) === '8') {
        if (isPendingUser(u)) return 'ผู้ใช้อยู่ระหว่างรออนุมัติ กรุณากดปุ่ม "อนุมัติ R2" เพื่อเปิดใช้งานบัญชี (ไม่สามารถเปลี่ยนสถานะได้โดยตรง)';
        return 'ผู้ใช้ยังระบุข้อมูลไม่ครบถ้วน (ไม่สามารถเปลี่ยนสถานะได้โดยตรง)';
    }
    if (String(u.status_id) === '6') {
        return 'บัญชีถูกล็อค กรุณากดปุ่ม Unlock เพื่อปลดล็อคบัญชี';
    }
    return '';
};

const handleStatusChange = async (user, newStatusId) => {
    if (String(user.status_id) === '4') {
        alert('ผู้ใช้ยังไม่ได้ยืนยันอีเมล ไม่สามารถเปลี่ยนสถานะได้จนกว่าผู้ใช้จะยืนยันอีเมลสำเร็จ');
        return;
    }
    if (String(user.status_id) === '8') {
        alert('ผู้ใช้อยู่ในสถานะรออนุมัติ กรุณาใช้ปุ่ม "อนุมัติ R2" เพื่อเปิดใช้งานบัญชี');
        return;
    }
    if (String(user.status_id) === '6') {
        alert('บัญชีถูกล็อค กรุณาใช้ปุ่ม "Unlock" เพื่อปลดล็อคบัญชี');
        return;
    }
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/updateUserById', userStored, {
            target_user_id: user.user_id,
            status_id: parseInt(newStatusId),
            link: window.location.origin
        });
        
        if (response.data.status === 'success') {
            const statusNames = { 1: 'Active', 4: 'Pending Verification', 3: 'Suspend' };
            showAlert(`อัปเดตสถานะของ ${user.username} เป็น ${statusNames[newStatusId] || newStatusId} สำเร็จ`, 'success');
            fetchUsers();
        } else {
            alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));
        }
    } catch (error) {
        console.error('Error updating status:', error);
        alert('เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    }
};

const isResending = ref(null);
const handleResendEmail = async (user) => {
    if (!confirm(`ต้องการส่งอีเมลยืนยันตัวตนให้ "${user.username}" (${user.email}) อีกครั้งหรือไม่?`)) {
        return;
    }
    isResending.value = user.user_id;
    try {
        const response = await postWithUser('/resendEmailConfirmation', {}, {
            dataresend: {
                email: user.email,
                user_id: user.user_id,
                username: user.username,
                firstname: user.firstname || '',
                lastname: user.lastname || ''
            },
            link: window.location.origin
        });
        if (response.data === 'success' || response.data?.status === 'success') {
            showAlert(`ส่งอีเมลยืนยันตัวตนไปยัง ${user.email} สำเร็จแล้ว`, 'success');
        } else {
            alert('เกิดข้อผิดพลาดในการส่งอีเมล: ' + (response.data?.message || JSON.stringify(response.data)));
        }
    } catch (error) {
        console.error('Error resending confirmation email:', error);
        alert('เกิดข้อผิดพลาด: ไม่สามารถส่งอีเมลได้ กรุณาลองใหม่อีกครั้ง');
    } finally {
        isResending.value = null;
    }
};



const handleUnlockUser = async (user) => {
    if (confirm(`ยืนยันการปลดล็อคบัญชี ${user.username} หรือไม่?`)) {
        try {
            const userStored = JSON.parse(localStorage.getItem('user') || '{}');
            const response = await postWithUser('/mgmt/unlockUserByAdmin', userStored, { target_user_id: user.user_id });
            if (response.data && response.data.status === 'success') {
                alert('ปลดล็อคบัญชีสำเร็จ');
                fetchUsers();
            } else {
                alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));
            }
        } catch (error) {
            console.error('Error unlocking user:', error);
            alert('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้');
        }
    }
};

const isApproving = ref(null);

const isPendingUser = (user) => {
    return String(user.status_id) === '8' && Boolean(user.org_id) && Boolean(user.has_api_key);
};

const isIncompleteUser = (user) => {
    return String(user.status_id) === '8' && (!user.org_id || !user.has_api_key);
};

const handleApproveUser = async (user) => {
    if (!confirm(`ยืนยันการอนุมัติผู้ใช้ "${user.username}" ให้เป็น R2 (ผู้ใช้งานทั่วไป) หรือไม่?`)) {
        return;
    }
    isApproving.value = user.user_id;
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/approveUserRegistration', userStored, {
            target_user_id: user.user_id
        });
        if (response.data && response.data.status === 'success') {
            showAlert(`อนุมัติผู้ใช้ ${user.username} เป็นระดับ R2 เรียบร้อยแล้ว`, 'success');
            fetchUsers();
        } else {
            alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));
        }
    } catch (error) {
        console.error('Error approving user:', error);
        alert('เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    } finally {
        isApproving.value = null;
    }
};

const handleDeleteUser = async (user) => {
    if (!confirm(`คุณแน่ใจหรือไม่ว่าต้องการลบผู้ใช้ "${user.username}"? การกระทำนี้ไม่สามารถกู้คืนได้`)) {
        return;
    }
    
    try {
        const userStored = JSON.parse(localStorage.getItem('user') || '{}');
        const response = await postWithUser('/mgmt/deleteUser', userStored, {
            target_user_id: user.user_id
        });
        
        if (response.data.status === 'success') {
            showAlert(`ลบผู้ใช้ ${user.username} สำเร็จ`, 'success');
            fetchUsers(); // Refresh list
        } else {
            alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    }
};

const showAlert = (text, type) => {
    alertMessage.value = { text, type };
};

const filteredUsers = computed(() => {
    let result = users.value;

    // Filter by Organization
    if (selectedOrgFilter.value) {
        if (selectedOrgFilter.value === 'none') {
            result = result.filter(u => !u.org_id);
        } else {
            result = result.filter(u => String(u.org_id) === String(selectedOrgFilter.value));
        }
    }

    // Filter by Role / Status
    if (selectedRoleFilter.value) {
        if (selectedRoleFilter.value === 'pending') {
            result = result.filter(u => String(u.status_id) === '8');
        } else {
            result = result.filter(u => String(u.previlage_id) === String(selectedRoleFilter.value));
        }
    }

    // Text search (search by firstname, lastname, fullname, username, email, org name, usage_objective)
    if (searchQuery.value && searchQuery.value.trim()) {
        const q = searchQuery.value.trim().toLowerCase();
        result = result.filter(u => {
            const username = (u.username || '').toLowerCase();
            const firstname = (u.firstname || '').toLowerCase();
            const lastname = (u.lastname || '').toLowerCase();
            const fullname = `${firstname} ${lastname}`.trim().toLowerCase();
            const email = (u.email || '').toLowerCase();
            const orgName = (u.org_name || getOrgName(u.org_id) || '').toLowerCase();
            const usageObj = (u.usage_objective || '').toLowerCase();

            return (
                username.includes(q) ||
                firstname.includes(q) ||
                lastname.includes(q) ||
                fullname.includes(q) ||
                email.includes(q) ||
                orgName.includes(q) ||
                usageObj.includes(q)
            );
        });
    }

    return result;
});

const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    try {
        const safeStr = typeof dateStr === 'string' && dateStr.includes(' ') && !dateStr.includes('T') ? dateStr.replace(' ', 'T') : dateStr;
        const d = new Date(safeStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
        return dateStr;
    }
};

onMounted(() => {
    fetchUsers();
    fetchRoles();
    fetchGroups();
    fetchOrganizations();
});
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div>
          <h1>User Management</h1>
          <p class="subtitle">จัดการข้อมูลผู้ใช้และกำหนดบทบาทการเข้าถึงระบบ</p>
        </div>
        
        <div class="header-actions">
            <button class="btn-primary" @click="openAddModal">
                <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add User
            </button>
        </div>
      </header>

      <!-- Search & Filters Toolbar -->
      <div class="filter-toolbar card">
        <div class="search-container">
            <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="ค้นหาชื่อ-นามสกุล, username, อีเมล, หน่วยงาน..."
            >
            <button v-if="searchQuery" type="button" @click="searchQuery = ''" class="clear-search-btn" title="ล้างการค้นหา">&times;</button>
        </div>

        <div class="filter-dropdown-container">
            <select v-model="selectedOrgFilter" class="filter-select" title="กรองตามหน่วยงาน">
                <option value="">🏢 ทุกหน่วยงาน</option>
                <option v-for="org in organizations" :key="org.org_id" :value="org.org_id">
                    {{ org.org_name }}
                </option>
                <option value="none">-- ยังไม่ระบุหน่วยงาน --</option>
            </select>
        </div>

        <div class="filter-dropdown-container">
            <select v-model="selectedRoleFilter" class="filter-select" title="กรองตามบทบาท/สิทธิ์">
                <option value="">👤 ทุกบทบาท</option>
                <option v-for="role in roles" :key="role.previlage_id" :value="role.previlage_id">
                    {{ role.previlage_name }}
                </option>
                <option value="pending">⏳ รออนุมัติ R2 / รอระบุข้อมูล</option>
            </select>
        </div>

        <button 
          v-if="searchQuery || selectedOrgFilter || selectedRoleFilter" 
          type="button"
          @click="clearAllFilters" 
          class="btn-clear-filters"
          title="ล้างตัวกรองทั้งหมด"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
          ล้างตัวกรอง
        </button>

        <div class="filter-stats">
          <span>พบ <strong>{{ filteredUsers.length }}</strong> คน (จากทั้งหมด {{ users.length }} คน)</span>
        </div>
      </div>

      <!-- Alert Message -->
      <transition name="fade">
        <div v-if="alertMessage.text" :class="['alert-banner', alertMessage.type]">
            <div style="flex: 1;">{{ alertMessage.text }}</div>
            <button @click="alertMessage = { text: '', type: '' }" class="alert-close-btn" aria-label="Close alert">&times;</button>
        </div>
      </transition>

      <div class="card shadow-premium">
        <div v-if="isLoading" class="loading-state">
            <div class="spinner"></div>
            <p>กำลังโหลดรายชื่อผู้ใช้...</p>
        </div>

        <div v-else class="table-container">
          <div class="mobile-cards-view">
            <div v-for="(u, idx) in filteredUsers" :key="u.user_id" class="mobile-card">
              <div class="mc-header">
                <div class="user-info">
                  <div class="user-avatar">{{ ((u.firstname || u.username) || '?').charAt(0).toUpperCase() }}</div>
                  <div>
                      <div class="username-text">
                        <span v-if="u.firstname || u.lastname">{{ `${u.firstname || ''} ${u.lastname || ''}`.trim() }}</span>
                        <span v-else>{{ u.username }}</span>
                        <span v-if="isPendingUser(u)" style="margin-left: 6px; background-color: #fef3c7; color: #b45309; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; border: 1px solid #fde68a; font-weight: 600;">
                          ⏳ รออนุมัติ R2
                        </span>
                        <span v-else-if="isIncompleteUser(u)" style="margin-left: 6px; background-color: #f1f5f9; color: #64748b; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; border: 1px solid #cbd5e1; font-weight: 600;">
                          ⏳ รอระบุข้อมูล
                        </span>
                      </div>
                      <div class="user-id-text">
                        <span v-if="u.firstname || u.lastname" style="margin-right: 6px; font-weight: 500; color: #64748b;">@{{ u.username }}</span>
                        <span>ID: #{{ u.user_id }}</span>
                        <span v-if="u.usage_objective" class="user-objective-tag" :title="'วัตถุประสงค์: ' + u.usage_objective" style="margin-left: 6px;">
                          🎯 {{ u.usage_objective }}
                        </span>
                      </div>
                  </div>
                </div>
                <div class="actions-group">
                  <button 
                    v-if="u.status_id == 4" 
                    class="resend-btn" 
                    @click="handleResendEmail(u)" 
                    :disabled="isResending === u.user_id"
                    title="ส่งอีเมลยืนยันตัวตนให้อีกครั้ง"
                    style="background: #f59e0b; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 0.75rem; font-weight: 600; margin-right: 8px;"
                  >
                    ✉️ {{ isResending === u.user_id ? 'กำลังส่ง...' : 'ส่งเมลซ้ำ' }}
                  </button>
                  <button 
                    v-if="isPendingUser(u)" 
                    class="approve-btn" 
                    @click="handleApproveUser(u)" 
                    :disabled="isApproving === u.user_id"
                    title="อนุมัติเป็น R2"
                    style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 0.75rem; font-weight: 600; margin-right: 8px;"
                  >
                    ✓ อนุมัติ R2
                  </button>
                  <button v-if="u.status_id == 6" class="unlock-btn" @click="handleUnlockUser(u)" title="ปลดล็อคบัญชี" style="background-color: #f59e0b; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 0.75rem; font-weight: 600; margin-right: 8px;">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                      Unlock
                  </button>
                  <button class="delete-btn" @click="handleDeleteUser(u)" title="ลบผู้ใช้">
                    <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              <div class="mc-body">
                <div class="mc-row">
                  <span class="mc-label">อีเมล</span>
                  <span class="mc-value">{{ u.email || '-' }}</span>
                </div>
                <div class="mc-row">
                  <span class="mc-label">วันที่เข้าร่วม</span>
                  <span class="mc-value">{{ formatDate(u.create_at) }}</span>
                </div>
                <div class="mc-row">
                  <span class="mc-label">บทบาท</span>
                  <div class="role-selector-box mobile-select">
                    <select 
                        :value="u.previlage_id" 
                        @change="handleRoleChange(u, $event.target.value)"
                        class="role-select"
                        :class="{ 'disabled-select': u.status_id == 4 || u.status_id == 8 }"
                        :title="u.status_id == 4 ? 'ไม่สามารถเปลี่ยนบทบาทได้จนกว่าผู้ใช้จะยืนยันอีเมล' : (u.status_id == 8 ? 'ไม่สามารถเปลี่ยนบทบาทได้ขณะรออนุมัติ กรุณากดปุ่มอนุมัติ R2' : getRoleName(u.previlage_id))"
                        :disabled="u.status_id == 4 || u.status_id == 8"
                    >
                        <option v-for="role in roles" :key="role.previlage_id" :value="role.previlage_id" :title="role.previlage_name">
                            {{ role.previlage_name }}
                        </option>
                    </select>
                  </div>
                </div>
                <div class="mc-row">
                  <span class="mc-label">สถานะ</span>
                  <div class="role-selector-box mobile-select">
                    <select 
                        :value="getUserStatusValue(u.status_id)" 
                        @change="handleStatusChange(u, $event.target.value)"
                        class="role-select status-select"
                        :class="[getStatusBadgeClass(u.status_id), { 'disabled-select': u.status_id == 4 || u.status_id == 8 || u.status_id == 6 }]"
                        :disabled="u.status_id == 4 || u.status_id == 8 || u.status_id == 6"
                        :title="getStatusSelectTitle(u)"
                    >
                        <option :value="1">🟢 Active</option>
                        <option :value="4">🟡 Pending Verification</option>
                        <option :value="3">🔴 Suspend</option>
                        <option v-if="u.status_id == 6" :value="6" disabled>🔒 Locked</option>
                        <option v-if="u.status_id == 8 && isPendingUser(u)" :value="8" disabled>⏳ รออนุมัติ R2</option>
                        <option v-if="u.status_id == 8 && isIncompleteUser(u)" :value="8" disabled>⏳ รอระบุข้อมูล</option>
                    </select>
                  </div>
                </div>
                <div class="mc-row">
                  <span class="mc-label">หน่วยงาน</span>
                  <div class="role-selector-box mobile-select" v-if="u.previlage_id == 3">
                    <select 
                        :value="u.org_id" 
                        @change="handleOrgChange(u, $event.target.value)"
                        class="role-select"
                        :title="getOrgName(u.org_id)"
                    >
                        <option value="" disabled>เลือกหน่วยงาน</option>
                        <option v-for="org in organizations" :key="org.org_id" :value="org.org_id" :title="org.org_name">
                            {{ org.org_name }}
                        </option>
                    </select>
                  </div>
                  <span class="mc-value" v-else-if="u.org_id && getOrgName(u.org_id) !== '-'">
                    <span class="org-badge" :title="getOrgName(u.org_id)">🏢 {{ getOrgName(u.org_id) }}</span>
                  </span>
                  <span class="mc-value text-muted" v-else>-</span>
                </div>
              </div>
            </div>
          </div>
          <table class="data-table desktop-table-view">
            <thead>
              <tr>
                <th>#</th>
                <th>ผู้ใช้งาน</th>
                <th>อีเมล</th>
                <th>วันที่เข้าร่วม</th>
                <th>บทบาทปัจจุบัน</th>
                <th>สถานะ</th>
                <th>หน่วยงาน / องค์กร</th>
                <th>ดำเนินการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(u, idx) in filteredUsers" :key="u.user_id">
                <td>{{ idx + 1 }}</td>
                <td>
                  <div class="user-info">
                    <div class="user-avatar">{{ ((u.firstname || u.username) || '?').charAt(0).toUpperCase() }}</div>
                    <div>
                        <div class="username-text">
                            <span v-if="u.firstname || u.lastname">{{ `${u.firstname || ''} ${u.lastname || ''}`.trim() }}</span>
                            <span v-else>{{ u.username }}</span>
                            <span v-if="isPendingUser(u)" style="margin-left: 6px; background-color: #fef3c7; color: #b45309; font-size: 0.7rem; padding: 2px 8px; border-radius: 9999px; border: 1px solid #fde68a; font-weight: 600; display: inline-flex; align-items: center; gap: 3px;">
                                ⏳ รออนุมัติ R2
                            </span>
                            <span v-else-if="isIncompleteUser(u)" style="margin-left: 6px; background-color: #f1f5f9; color: #64748b; font-size: 0.7rem; padding: 2px 8px; border-radius: 9999px; border: 1px solid #cbd5e1; font-weight: 600; display: inline-flex; align-items: center; gap: 3px;">
                                ⏳ รอระบุข้อมูล
                            </span>
                            <span v-if="u.status_id == 6" style="margin-left: 6px; background-color: #fee2e2; color: #ef4444; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; border: 1px solid #fca5a5; display: inline-flex; align-items: center; gap: 2px;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                                Locked
                            </span>
                        </div>
                        <div class="user-id-text">
                          <span v-if="u.firstname || u.lastname" style="margin-right: 6px; font-weight: 500; color: #64748b;">@{{ u.username }}</span>
                          <span>ID: #{{ u.user_id }}</span>
                          <span v-if="u.usage_objective" class="user-objective-tag" :title="'วัตถุประสงค์: ' + u.usage_objective" style="margin-left: 6px;">
                            🎯 {{ u.usage_objective }}
                          </span>
                        </div>
                    </div>
                  </div>
                </td>
                <td>{{ u.email || '-' }}</td>
                <td>{{ formatDate(u.create_at) }}</td>
                <td>
                  <span v-if="isPendingUser(u)" class="role-badge" style="background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a;">
                    ⏳ รออนุมัติ R2
                  </span>
                  <span v-else-if="isIncompleteUser(u)" class="role-badge" style="background-color: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1;">
                    ⏳ รอระบุข้อมูล
                  </span>
                  <span v-else class="role-badge" :class="'role-' + u.previlage_id">
                    {{ u.previlage_name || 'No Role' }}
                  </span>
                </td>
                <td class="status-cell">
                  <div class="role-selector-box">
                    <select 
                        :value="getUserStatusValue(u.status_id)" 
                        @change="handleStatusChange(u, $event.target.value)"
                        class="role-select status-select"
                        :class="[getStatusBadgeClass(u.status_id), { 'disabled-select': u.status_id == 4 || u.status_id == 8 || u.status_id == 6 }]"
                        :disabled="u.status_id == 4 || u.status_id == 8 || u.status_id == 6"
                        :title="getStatusSelectTitle(u)"
                    >
                        <option :value="1">🟢 Active</option>
                        <option :value="4">🟡 Pending Verification</option>
                        <option :value="3">🔴 Suspend</option>
                        <option v-if="u.status_id == 6" :value="6" disabled>🔒 Locked</option>
                        <option v-if="u.status_id == 8 && isPendingUser(u)" :value="8" disabled>⏳ รออนุมัติ R2</option>
                        <option v-if="u.status_id == 8 && isIncompleteUser(u)" :value="8" disabled>⏳ รอระบุข้อมูล</option>
                    </select>
                  </div>
                </td>
                <td class="org-cell">
                    <div class="role-selector-box" v-if="u.previlage_id == 3">
                      <select 
                          :value="u.org_id" 
                          @change="handleOrgChange(u, $event.target.value)"
                          class="role-select org-select"
                          :title="getOrgName(u.org_id)"
                      >
                          <option value="" disabled>เลือกหน่วยงาน</option>
                          <option v-for="org in organizations" :key="org.org_id" :value="org.org_id" :title="org.org_name">
                              {{ org.org_name }}
                          </option>
                      </select>
                    </div>
                    <span v-else-if="u.org_id && getOrgName(u.org_id) !== '-'" class="org-badge" :title="getOrgName(u.org_id)">
                      🏢 {{ getOrgName(u.org_id) }}
                    </span>
                    <span class="text-muted" v-else>-</span>
                </td>
                <td class="actions-cell">
                  <div class="actions-group">
                    <button 
                      v-if="u.status_id == 4" 
                      class="resend-btn" 
                      @click="handleResendEmail(u)" 
                      :disabled="isResending === u.user_id"
                      title="ส่งอีเมลยืนยันตัวตนให้อีกครั้ง"
                      style="background-color: #f59e0b; color: white; border: none; padding: 7px 12px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 0.85rem; font-weight: 600; white-space: nowrap; box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                      <span>{{ isResending === u.user_id ? 'กำลังส่ง...' : 'ส่งเมลยืนยันซ้ำ' }}</span>
                    </button>

                    <button 
                      v-if="isPendingUser(u)" 
                      class="approve-btn" 
                      @click="handleApproveUser(u)" 
                      :disabled="isApproving === u.user_id"
                      title="อนุมัติเป็น R2 (ผู้ใช้งานทั่วไป)" 
                      style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 7px 12px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 0.85rem; font-weight: 600; white-space: nowrap; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                      <span>{{ isApproving === u.user_id ? 'กำลังอนุมัติ...' : 'อนุมัติ R2' }}</span>
                    </button>

                    <div class="role-selector-box">
                      <select 
                          :value="u.previlage_id" 
                          @change="handleRoleChange(u, $event.target.value)"
                          class="role-select action-role-select"
                          :class="{ 'disabled-select': u.status_id == 4 || u.status_id == 8 }"
                          :title="u.status_id == 4 ? 'ไม่สามารถเปลี่ยนบทบาทได้จนกว่าผู้ใช้จะยืนยันอีเมล' : (u.status_id == 8 ? 'ไม่สามารถเปลี่ยนบทบาทได้ขณะรออนุมัติ กรุณากดปุ่มอนุมัติ R2' : getRoleName(u.previlage_id))"
                          :disabled="u.status_id == 4 || u.status_id == 8"
                      >
                          <option v-for="role in roles" :key="role.previlage_id" :value="role.previlage_id" :title="role.previlage_name">
                              {{ role.previlage_name }}
                          </option>
                      </select>
                    </div>

                    <button v-if="u.status_id == 6" class="unlock-btn" @click="handleUnlockUser(u)" title="ปลดล็อคบัญชี" style="background-color: #f59e0b; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 0.85rem; font-weight: 600;">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                      Unlock
                    </button>

                    <button class="delete-btn" @click="handleDeleteUser(u)" title="ลบผู้ใช้">
                      <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="filteredUsers.length === 0" class="no-results">
            ไม่พบข้อมูลผู้ใช้ที่ค้นหา
          </div>
        </div>
      </div>
    
      <!-- Add User Modal (Dark Theme) -->
      <transition name="fade">
        <div class="modal-overlay" v-if="showAddModal" @click="closeAddModal">
          <div class="modal-content dark-card" @click.stop>
            <div class="modal-header">
              <h2>Add New User</h2>
              <button class="close-btn" @click="closeAddModal">&times;</button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Username <span class="required">*</span></label>
                <input type="text" v-model="formData.username" class="dark-input" placeholder="Enter username" />
              </div>
              <div class="form-group">
                <label>Email <span class="required">*</span></label>
                <input type="email" v-model="formData.email" class="dark-input" placeholder="Enter email" />
              </div>
              <div class="form-group" style="margin-bottom: 16px;">
                <label>Password <span class="required">*</span></label>
                <div class="password-input-wrapper" style="position: relative;">
                  <input :type="showPassword ? 'text' : 'password'" v-model="formData.password" class="dark-input" placeholder="ตั้งรหัสผ่าน 8 ตัวขึ้นไป" style="padding-right: 40px;" />
                  <button class="toggle-password" @click="showPassword = !showPassword" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: #94a3b8;">
                    <span v-if="showPassword">🙈</span>
                    <span v-else>👁️</span>
                  </button>
                </div>
                <div class="password-strength-meter" v-if="formData.password" style="margin-top: 12px; display: flex; align-items: center; gap: 10px;">
                  <div class="meter-bar" style="flex: 1; height: 6px; background: #334155; border-radius: 4px; overflow: hidden; display: flex;">
                    <div :style="{ width: (passwordStrength.score * 25) + '%', backgroundColor: passwordStrength.color, transition: 'all 0.3s' }"></div>
                  </div>
                  <span :style="{ color: passwordStrength.color, fontWeight: 'bold', fontSize: '0.8rem', minWidth: '50px' }">
                    {{ passwordStrength.label }}
                  </span>
                </div>
                <ul v-if="formData.password" style="margin-top: 10px; font-size: 0.75rem; color: #94a3b8; padding-left: 20px;">
                  <li :style="{ color: formData.password.length >= 8 ? '#22c55e' : '#ef4444' }">อย่างน้อย 8 ตัวอักษร</li>
                  <li :style="{ color: /[A-Z]/.test(formData.password) ? '#22c55e' : '#ef4444' }">มีตัวอักษรพิมพ์ใหญ่ (A-Z)</li>
                  <li :style="{ color: /[a-z]/.test(formData.password) ? '#22c55e' : '#ef4444' }">มีตัวอักษรพิมพ์เล็ก (a-z)</li>
                  <li :style="{ color: /[0-9]/.test(formData.password) ? '#22c55e' : '#ef4444' }">มีตัวเลข (0-9)</li>
                  <li :style="{ color: /[^A-Za-z0-9]/.test(formData.password) ? '#22c55e' : '#ef4444' }">มีอักขระพิเศษ (เช่น !@#$%)</li>
                </ul>
              </div>

              <div class="form-group" style="margin-bottom: 24px;">
                <label>Confirm Password <span class="required">*</span></label>
                <div class="password-input-wrapper" style="position: relative;">
                  <input :type="showConfirmPassword ? 'text' : 'password'" v-model="formData.confirmPassword" class="dark-input" placeholder="พิมพ์รหัสผ่านใหม่อีกครั้ง" style="padding-right: 40px;" />
                  <button class="toggle-password" @click="showConfirmPassword = !showConfirmPassword" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: #94a3b8;">
                    <span v-if="showConfirmPassword">🙈</span>
                    <span v-else>👁️</span>
                  </button>
                </div>
                <p v-if="formData.confirmPassword && formData.password !== formData.confirmPassword" style="color: #ef4444; font-size: 0.8rem; margin-top: 4px;">รหัสผ่านไม่ตรงกัน</p>
                <p v-if="formData.confirmPassword && formData.password === formData.confirmPassword" style="color: #22c55e; font-size: 0.8rem; margin-top: 4px;">รหัสผ่านตรงกัน ✓</p>
              </div>
              
              <div class="form-row">
                <div class="form-group half">
                  <label>Role</label>
                  <select v-model="formData.previlage_id" class="dark-input">
                    <option v-for="role in roles" :key="role.previlage_id" :value="role.previlage_id">
                      {{ role.previlage_name }}
                    </option>
                  </select>
                </div>
                <div class="form-group half">
                  <label>Status</label>
                  <select v-model="formData.status_id" class="dark-input">
                    <option :value="4">Pending Verification (ส่งอีเมลยืนยัน)</option>
                    <option :value="1">Active</option>
                    <option :value="3">Suspended</option>
                  </select>
                </div>
              </div>
              <p style="font-size: 0.78rem; color: #10b981; margin: -12px 0 16px 0;" v-if="formData.status_id == 4">
                ✉️ ระบบจะส่งอีเมลยืนยันตัวตน และเปิดใช้งานบัญชีพร้อมสิทธิ์ที่เลือกโดยอัตโนมัติ (Auto-Approve) เมื่อผู้ใช้กดยืนยันในอีเมล
              </p>

              <div class="form-group">
                <label>Organization <span class="required" v-if="formData.previlage_id == 3">*</span></label>
                <select v-model="formData.org_id" class="dark-input">
                  <option value="" :disabled="formData.previlage_id == 3">{{ formData.previlage_id == 3 ? 'Select Organization' : 'Select Organization (Optional)' }}</option>
                  <option v-for="org in organizations" :key="org.org_id" :value="org.org_id">
                    {{ org.org_name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Groups</label>
                <select multiple v-model="formData.groups" class="dark-input multi-select">
                  <option v-for="group in groups" :key="group.group_id" :value="group.group_id">
                    {{ group.group_name }}
                  </option>
                </select>
                <small class="help-text">Hold Cmd/Ctrl to select multiple</small>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="closeAddModal">Cancel</button>
              <button class="btn-save" @click="handleSaveUser" :disabled="isSubmitting">
                {{ isSubmitting ? 'Saving...' : 'Save User' }}
              </button>
            </div>
          </div>
        </div>
      </transition>

    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8fafc;
}

.content {
  flex: 1;
  padding: 40px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}

h1 {
  font-size: 2rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 4px;
}

.subtitle {
  color: #64748b;
  font-size: 1rem;
}

/* Search & Filters Toolbar */
.filter-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    margin-bottom: 24px;
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

.filter-toolbar .search-container {
    position: relative;
    flex: 1 1 280px;
    min-width: 240px;
    width: auto;
}

.search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    width: 18px;
    height: 18px;
    color: #94a3b8;
    pointer-events: none;
}

.search-container input {
    width: 100%;
    padding: 10px 38px 10px 40px;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    outline: none;
    transition: all 0.2s;
    font-size: 0.9rem;
    color: #1e293b;
}

.search-container input:focus {
    background: #ffffff;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.clear-search-btn {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: #e2e8f0;
    border: none;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #64748b;
    font-size: 14px;
    line-height: 1;
    padding: 0;
    transition: all 0.15s ease;
}

.clear-search-btn:hover {
    background: #cbd5e1;
    color: #0f172a;
}

.filter-dropdown-container {
    position: relative;
    min-width: 180px;
    max-width: 260px;
    flex: 0 1 auto;
}

.filter-select {
    width: 100%;
    padding: 10px 32px 10px 14px;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    font-size: 0.88rem;
    color: #1e293b;
    cursor: pointer;
    outline: none;
    appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 10px center;
    background-size: 16px;
    transition: all 0.2s;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
}

.filter-select:hover {
    border-color: #94a3b8;
}

.filter-select:focus {
    background-color: #ffffff;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.btn-clear-filters {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 9px 14px;
    background: #fee2e2;
    color: #dc2626;
    border: 1px solid #fecaca;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}

.btn-clear-filters:hover {
    background: #fecaca;
    color: #b91c1c;
}

.filter-stats {
    margin-left: auto;
    font-size: 0.85rem;
    color: #64748b;
    white-space: nowrap;
}

.filter-stats strong {
    color: #0284c7;
    font-weight: 700;
}

.org-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    max-width: 220px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-objective-tag {
    display: inline-flex;
    align-items: center;
    padding: 1px 7px;
    background: #f0fdf4;
    color: #15803d;
    border: 1px solid #bbf7d0;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 500;
    max-width: 180px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Alert Banner */

.alert-banner {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    padding: 14px 24px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.95rem;
    position: fixed;
    top: 24px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999 !important; /* Fixed z-index to be above modal */
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    min-width: 300px;
    text-align: center;
}

.alert-banner.success {
    background: #fdf2f8;
    color: #166534;
    border: 1px solid #fce7f3;
}

.alert-banner.error {
    background: #fef2f2;
    color: #991b1b;
    border: 1px solid #fee2e2;
}

.alert-close-btn {
    background: transparent;
    border: none;
    font-size: 1.75rem;
    line-height: 1;
    cursor: pointer;
    opacity: 0.7;
    padding: 0;
    margin-top: -4px;
}
.alert-close-btn:hover {
    opacity: 1;
}

/* Table Card */
.card {
  background: white;
  border-radius: 24px;
  overflow: hidden;
}

.shadow-premium {
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.05);
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 16px 24px;
  background: #f8fafc;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-bottom: 1px solid #f1f5f9;
}

.data-table td {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.data-table tr:hover td {
    background-color: #fbfcfe;
}

/* User Identity Cell */
.user-info {
    display: flex;
    align-items: center;
    gap: 16px;
}

.user-avatar {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
    color: white;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.2rem;
}

.username-text {
    font-weight: 700;
    color: #1e293b;
    font-size: 1rem;
}

.user-id-text {
    font-size: 0.75rem;
    color: #94a3b8;
}

/* Role Badge */
.role-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
    white-space: nowrap;
    text-align: center;
}

.role-badge.role-1 { background: #f3f4f6; color: #374151; } /* R1 ภายนอก */
.role-badge.role-2 { background: #f1f5f9; color: #475569; } /* R2 ทั่วไป */
.role-badge.role-3 { background: #fef3c7; color: #92400e; } /* R3 ดูแลข้อมูล */
.role-badge.role-4 { background: #fee2e2; color: #991b1b; } /* R4 ดูแลระบบ */
.role-badge.role-5 { background: #dcfce7; color: #166534; } /* R5 ภายในมีสิทธิ */

/* Select Dropdown */
/* Actions */
.actions-group {
    display: flex;
    align-items: center;
    gap: 12px;
}

.role-selector-box {
    flex: 1;
}

.delete-btn {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #fff;
    border: 1px solid #fee2e2;
    border-radius: 10px;
    color: #ef4444;
    cursor: pointer;
    transition: all 0.2s;
}

.delete-btn:hover {
    background: #fef2f2;
    border-color: #fca5a5;
    transform: scale(1.05);
}

.btn-icon {
    width: 18px;
    height: 18px;
}

.status-cell {
    width: 200px;
    min-width: 190px;
}

.status-select {
    width: 185px;
    max-width: 185px;
    padding: 7px 10px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border-width: 1.5px;
}

.status-select.status-active {
    background-color: #ecfdf5;
    color: #065f46;
    border-color: #a7f3d0;
}
.status-select.status-active:hover {
    background-color: #d1fae5;
    border-color: #6ee7b7;
}

.status-select.status-pending {
    background-color: #fffbeb;
    color: #92400e;
    border-color: #fde68a;
}
.status-select.status-pending:hover {
    background-color: #fef3c7;
    border-color: #fcd34d;
}

.status-select.status-suspended {
    background-color: #fef2f2;
    color: #991b1b;
    border-color: #fecaca;
}
.status-select.status-suspended:hover {
    background-color: #fee2e2;
    border-color: #f87171;
}

.status-select.status-locked {
    background-color: #f8fafc;
    color: #64748b;
    border-color: #cbd5e1;
}

.status-select.status-approval {
    background-color: #fef3c7;
    color: #b45309;
    border-color: #fde68a;
}

.org-cell {
    width: 260px;
    min-width: 240px;
}

.actions-cell {
    width: 320px;
    min-width: 300px;
}

.role-select {
    width: 240px;
    max-width: 240px;
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background-color: #fff;
    font-size: 0.85rem;
    color: #475569;
    cursor: pointer;
    outline: none;
    transition: all 0.2s;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
}

.mobile-select .role-select {
    width: 100%;
    max-width: 100%;
}

.role-select:hover {
    border-color: #cbd5e1;
    background-color: #f8fafc;
}

.role-select:focus {
    border-color: #3b82f6;
}

.role-select:disabled,
.role-select.disabled-select {
    cursor: not-allowed !important;
    opacity: 0.75 !important;
    background-color: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
    color: #64748b !important;
}

.status-select.status-pending:disabled,
.status-select.status-pending.disabled-select {
    background-color: #fffbeb !important;
    color: #92400e !important;
    border-color: #fde68a !important;
    cursor: not-allowed !important;
    opacity: 0.95 !important;
}

.status-select.status-approval:disabled,
.status-select.status-approval.disabled-select {
    background-color: #fef3c7 !important;
    color: #b45309 !important;
    border-color: #fde68a !important;
    cursor: not-allowed !important;
    opacity: 0.95 !important;
}

.status-select.status-locked:disabled,
.status-select.status-locked.disabled-select {
    background-color: #f8fafc !important;
    color: #ef4444 !important;
    border-color: #fca5a5 !important;
    cursor: not-allowed !important;
    opacity: 0.95 !important;
}

/* Loading & Empty states */
.loading-state {
    padding: 80px;
    text-align: center;
    color: #64748b;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #f1f5f9;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
}

.no-results {
    padding: 40px;
    text-align: center;
    color: #94a3b8;
    font-style: italic;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.fade-enter-active, .fade-leave-active {
    transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
    opacity: 0;
}

/* Modal Styles (Dark Game-like Theme) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-content.dark-card {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 20px;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  color: #f8fafc;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255,255,255,0.05);
  overflow: hidden;
}

.modal-header {
  padding: 24px 30px;
  border-bottom: 1px solid #1e293b;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #0b1120;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #ef4444;
}

.modal-body {
  padding: 30px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-group.half {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #94a3b8;
}

.required {
  color: #ef4444;
}

.dark-input {
  width: 100%;
  padding: 12px 16px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  color: #f8fafc;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.dark-input:focus {
  border-color: #004f3b;
  box-shadow: 0 0 0 3px rgba(0, 79, 59, 0.2);
}

.multi-select {
  height: 120px;
  padding: 8px;
}

.multi-select option {
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 2px;
}

.multi-select option:checked {
  background: #004f3b linear-gradient(0deg, #004f3b 0%, #004f3b 100%);
  color: white;
}

.help-text {
  display: block;
  margin-top: 6px;
  font-size: 0.75rem;
  color: #64748b;
}

.modal-footer {
  padding: 20px 30px;
  background: #0b1120;
  border-top: 1px solid #1e293b;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-shrink: 0;
}

.btn-cancel {
  padding: 10px 20px;
  border-radius: 10px;
  background: transparent;
  color: #94a3b8;
  border: 1px solid #334155;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #1e293b;
  color: #f8fafc;
}

.btn-save {
  padding: 10px 24px;
  border-radius: 10px;
  background: #004f3b;
  color: white;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 79, 59, 0.3);
}

.btn-save:hover:not(:disabled) {
  background: #003d2d;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 79, 59, 0.4);
}

.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.actions {
  display: flex;
  align-items: center;
  margin-right: 16px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #004f3b;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 79, 59, 0.2);
}

.btn-primary:hover {
  background: #003d2d;
  transform: translateY(-1px);
}


/* Responsive Overrides for User Management */
.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}
.filter-toolbar .search-container {
  width: auto;
  min-width: 220px;
}
.mobile-cards-view {
  display: none;
}

@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    margin-top: 16px;
  }
  .filter-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    padding: 12px;
  }
  .filter-toolbar .search-container,
  .filter-dropdown-container {
    max-width: 100%;
    width: 100%;
    min-width: 0;
  }
  .filter-stats {
    margin-left: 0;
    text-align: center;
    padding-top: 4px;
  }
  .search-container {
    min-width: 0;
    width: 100%;
  }
  .search-container input {
    width: 100%;
  }

  .desktop-table-view {
    display: none !important;
  }
  .mobile-cards-view {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .mobile-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
  .mc-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 12px;
    margin-bottom: 12px;
  }
  .mc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
  }
  .mc-label {
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 500;
  }
  .mc-value {
    font-size: 0.9rem;
    font-weight: 500;
    color: #334155;
  }
  .mobile-select select {
    padding: 4px 8px;
    font-size: 0.85rem;
  }
  .content {
    padding: 16px !important;
  }
}
</style>


<style>
/* Global style strictly for this swal instance to override z-index */
.swal-top-modal {
  z-index: 999999 !important;
}
</style>
