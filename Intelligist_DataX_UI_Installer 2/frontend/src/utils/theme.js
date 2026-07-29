import { ref, watch } from 'vue';
import apiClient from './api';

const STORAGE_KEY = 'site_theme_config';

export const defaultConfig = {
  siteName: 'Data Exchange',
  logoUrl: '',
  primaryColor: '#008236',
  secondaryColor: '#dcfce7',
  accentColor: '#2ea87f',
  sidebarColor: '#004f3b',
};

// Start with defaults merged with any cached localStorage data (instant render)
const savedConfig = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
export const themeConfig = ref({ ...defaultConfig, ...savedConfig });

// Flag to prevent the watcher from firing during server load
let isLoadingFromServer = false;

const darkenColor = (hex, percent) => {
  try {
    let num = parseInt(hex.replace("#", ""), 16),
      amt = Math.round(2.55 * percent),
      R = (num >> 16) - amt,
      G = (num >> 8 & 0x00FF) - amt,
      B = (num & 0x0000FF) - amt;
    return "#" + (0x1000000 + (R < 255 ? R < 0 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 0 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 0 ? 0 : B : 255)).toString(16).slice(1);
  } catch (e) {
    return hex;
  }
};

export const applyTheme = (config = themeConfig.value) => {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  root.style.setProperty('--primary', config.primaryColor);
  root.style.setProperty('--mso-pink', config.primaryColor);
  root.style.setProperty('--mso-pink-dark', config.secondaryColor);
  
  // Use a darker shade of primary color if the secondary color is light (e.g. starts with #d, #e, #f)
  let hoverColor = config.secondaryColor;
  if (config.secondaryColor && config.secondaryColor.toLowerCase().match(/^#(d|e|f)/)) {
    hoverColor = darkenColor(config.primaryColor, 10);
  }
  root.style.setProperty('--primary-hover', hoverColor);
  root.style.setProperty('--mso-accent', config.accentColor);
  root.style.setProperty('--sidebar-bg', config.sidebarColor || config.secondaryColor);
};

// Automatically apply CSS variables when themeConfig changes (Live Preview)
watch(themeConfig, (newConfig) => {
  applyTheme(newConfig);
}, { deep: true });

/**
 * Load theme config from the server API.
 * Called on app mount — applies to ALL users (even anonymous/incognito).
 */
export const loadThemeFromServer = async () => {
  try {
    const response = await apiClient.get('/site-config');
    if (response.data && response.data.status === 'success' && response.data.data) {
      const serverConfig = response.data.data;
      // Only apply if server has actual config data
      if (Object.keys(serverConfig).length > 0) {
        isLoadingFromServer = true;
        themeConfig.value = { ...defaultConfig, ...serverConfig };
        // Cache in localStorage for faster subsequent loads
        localStorage.setItem(STORAGE_KEY, JSON.stringify(themeConfig.value));
        isLoadingFromServer = false;
      }
    }
  } catch (e) {
    // Server unavailable — fall back to localStorage/defaults silently
    console.warn('Could not load theme from server, using local cache:', e.message);
  }
};

/**
 * Save theme config to BOTH localStorage (instant) AND server (persistent).
 */
export const saveThemeConfig = async () => {
  try {
    // 1. Save to localStorage immediately
    localStorage.setItem(STORAGE_KEY, JSON.stringify(themeConfig.value));

    // 2. Save to server for persistence across sessions/users
    await apiClient.post('/site-config', themeConfig.value);

    return true;
  } catch (e) {
    console.error('Failed to save theme config.', e);
    // If server save fails, localStorage still has it
    alert('บันทึกไม่สำเร็จ กรุณาลองอีกครั้ง');
    return false;
  }
};
