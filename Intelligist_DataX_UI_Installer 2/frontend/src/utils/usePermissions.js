import { ref, computed } from 'vue';
import { postWithUser } from './api';

// Module-level shared state so all components stay in sync
const userPermissions = ref(null);
const isLoading = ref(false);

export function usePermissions() {
  const loadPermissions = async (force = false) => {
    const rawUser = localStorage.getItem('user');
    if (!rawUser) {
      userPermissions.value = [];
      return;
    }
    let savedUser = {};
    try {
      savedUser = JSON.parse(rawUser);
    } catch {
      userPermissions.value = [];
      return;
    }
    if (!savedUser.username && !savedUser.user_id) {
      userPermissions.value = [];
      return;
    }
    if (userPermissions.value !== null && !force) {
      return;
    }
    isLoading.value = true;
    try {
      const res = await postWithUser('/getMenuByPermission', savedUser);
      if (res.data && (res.data.status === 'Success' || res.data.status === 'success') && Array.isArray(res.data.data)) {
        userPermissions.value = res.data.data.map(m => (m.menu_name || '').toLowerCase().trim());
      } else {
        userPermissions.value = [];
      }
    } catch (e) {
      console.error('Failed to load user permissions:', e);
      userPermissions.value = [];
    } finally {
      isLoading.value = false;
    }
  };

  const hasPermission = (menuName) => {
    const rawUser = localStorage.getItem('user');
    if (!rawUser) return false;
    let savedUser = {};
    try {
      savedUser = JSON.parse(rawUser);
    } catch {
      return false;
    }
    if (!savedUser.username && !savedUser.user_id) return false;

    const role = String(savedUser.previlage_id || '');
    // Root Admin (role 4) always has full access
    if (role === '4') return true;

    if (userPermissions.value && Array.isArray(userPermissions.value)) {
      const target = menuName.toLowerCase().trim();
      return userPermissions.value.includes(target);
    }

    // Fallback if permissions have not loaded yet:
    if (menuName.toLowerCase() === 'analytics') {
      return role === '3';
    }
    if (menuName.toLowerCase() === 'dashboard') {
      return role === '4';
    }
    return false;
  };

  const canViewAnalytics = computed(() => hasPermission('analytics'));
  const canViewDashboard = computed(() => hasPermission('dashboard'));

  return {
    userPermissions,
    isLoading,
    loadPermissions,
    hasPermission,
    canViewAnalytics,
    canViewDashboard
  };
}
