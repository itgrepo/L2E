import { ref, watch } from 'vue';
import apiClient from './api';

const STORAGE_KEY = 'intelligist_homepage_layout';

// Default layout matching the current HomeView.vue structure
export const defaultLayout = [
  {
    id: 'hero',
    type: 'HeroSection',
    visible: true,
    props: {
      badge: 'DATA EXCHANGE',
      title: 'ศูนย์กลางบัญชีข้อมูลอัจฉริยะ<br/>และการแลกเปลี่ยนข้อมูลระดับองค์กร',
      desc: 'แพลตฟอร์มบริหารจัดการและแลกเปลี่ยนข้อมูลอย่างปลอดภัย<br/>ด้วยมาตรฐานสากล พร้อมระบบวิเคราะห์ข้อมูลเชิงลึกเพื่อการตัดสินใจ',
      btnPrimary: 'เริ่มต้นใช้งาน →',
      btnSecondary: 'เรียนรู้เพิ่มเติม',
      stats: [
        { num: '500+', label: 'ชุดข้อมูล' },
        { num: '85', label: 'หน่วยงานเครือข่าย' },
        { num: '5M+', label: 'API Calls/เดือน' }
      ]
    }
  },
  {
    id: 'features',
    type: 'FeatureSection',
    visible: true,
    props: {
      title: 'ขับเคลื่อนองค์กรด้วยพลังของข้อมูล',
      subtitle: 'เครื่องมือครบวงจรสำหรับบูรณาการและวิเคราะห์ข้อมูลเพื่อเพิ่มประสิทธิภาพในการดำเนินงาน'
    }
  },
  {
    id: 'steps',
    type: 'StepSection',
    visible: true,
    props: {
      title: '4 ขั้นตอนสู่การใช้งานข้อมูลอย่างเต็มประสิทธิภาพ',
      subtitle: 'เข้าถึงและจัดการชุดข้อมูลของคุณได้อย่างสะดวกรวดเร็วผ่านระบบอัตโนมัติ'
    }
  },
  {
    id: 'statsBanner',
    type: 'StatsBanner',
    visible: true,
    props: {
      stats: [
        { num: '500+', label: 'ชุดข้อมูลทั้งหมด' },
        { num: '85', label: 'หน่วยงานพันธมิตร' },
        { num: '99.99%', label: 'Uptime SLA' },
        { num: '5M+', label: 'API Transactions' }
      ]
    }
  },
  {
    id: 'cta',
    type: 'CTASection',
    visible: true,
    props: {
      title: 'พร้อมปฏิวัติการใช้งานข้อมูลของคุณหรือยัง?',
      subtitle: 'มาร่วมเป็นส่วนหนึ่งของเครือข่ายแลกเปลี่ยนข้อมูลที่ทันสมัยและมั่นคงปลอดภัยที่สุด',
      btnPrimary: 'สมัครใช้งานทันที',
      btnSecondary: 'ติดต่อเจ้าหน้าที่'
    }
  }
];

// Load from localStorage first (instant), then server overrides
const loadLayout = () => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error('Error parsing saved layout', e);
      }
    }
  }
  return JSON.parse(JSON.stringify(defaultLayout));
};

export const pageLayout = ref(loadLayout());

// Flag to prevent watcher from triggering during server load
let _loading = false;

/**
 * Load layout from server API — called on App mount.
 * All users (including incognito) will see the saved layout.
 */
export const loadLayoutFromServer = async () => {
  try {
    const response = await apiClient.get('/page-layout');
    if (response.data && response.data.status === 'success' && response.data.data) {
      const serverLayout = response.data.data;
      if (Array.isArray(serverLayout) && serverLayout.length > 0) {
        _loading = true;
        pageLayout.value = serverLayout;
        localStorage.setItem(STORAGE_KEY, JSON.stringify(serverLayout));
        _loading = false;
      }
    }
  } catch (e) {
    console.warn('Could not load layout from server, using local cache:', e.message);
  }
};

/**
 * Save layout to BOTH localStorage (instant) AND server (persistent).
 */
export const saveLayout = async () => {
  if (_loading) return;
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(pageLayout.value));
  }
  try {
    await apiClient.post('/page-layout', pageLayout.value);
  } catch (e) {
    console.warn('Could not save layout to server:', e.message);
  }
};

// Reset to default
export const resetLayout = async () => {
  pageLayout.value = JSON.parse(JSON.stringify(defaultLayout));
  await saveLayout();
};

// Watch for changes — auto-save (debounced to avoid excessive API calls)
let _saveTimeout = null;
watch(pageLayout, () => {
  if (_loading) return;
  // Debounce: only save after 500ms of no changes
  clearTimeout(_saveTimeout);
  _saveTimeout = setTimeout(() => {
    saveLayout();
  }, 500);
}, { deep: true });
