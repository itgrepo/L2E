<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { pageLayout, saveLayout, resetLayout } from '../utils/pageBuilder';

const isDeveloper = ref(false);
const isOpen = ref(false);
const editingBlock = ref(null);

const checkAuth = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      isDeveloper.value = user.username === 'developer';
    } catch (e) {
      console.error(e);
      isDeveloper.value = false;
    }
  } else {
    isDeveloper.value = false;
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
  isOpen.value = !isOpen.value;
  editingBlock.value = null; // Close edit modal when toggling widget
};

const moveUp = (index) => {
  if (index > 0) {
    const temp = pageLayout.value[index];
    pageLayout.value[index] = pageLayout.value[index - 1];
    pageLayout.value[index - 1] = temp;
    saveLayout();
  }
};

const moveDown = (index) => {
  if (index < pageLayout.value.length - 1) {
    const temp = pageLayout.value[index];
    pageLayout.value[index] = pageLayout.value[index + 1];
    pageLayout.value[index + 1] = temp;
    saveLayout();
  }
};

const toggleVisibility = (block) => {
  block.visible = !block.visible;
  saveLayout();
};

const openEditModal = (block) => {
  // Create a deep copy to edit without affecting live preview until saved (optional)
  // For true Elementor feel, editing live is better.
  editingBlock.value = block;
};

const closeEditModal = () => {
  editingBlock.value = null;
  saveLayout();
};
</script>

<template>
  <!-- Only show widget if user is developer -->
  <div v-if="isDeveloper" class="page-builder-wrapper" :class="{ 'is-open': isOpen }">
    <!-- Toggle Button -->
    <button class="builder-toggle" @click="toggleWidget" title="Page Builder">
      <svg v-if="!isOpen" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="3" y1="9" x2="21" y2="9"></line>
        <line x1="9" y1="21" x2="9" y2="9"></line>
      </svg>
      <span v-else>&times;</span>
    </button>

    <!-- Widget Panel -->
    <div class="builder-panel">
      <div class="builder-header">
        <h3>Homepage Builder</h3>
        <button class="btn-reset" @click="resetLayout">Reset All</button>
      </div>
      
      <div class="builder-body">
        <p class="builder-desc">ลากสลับตำแหน่ง หรือเปิด-ปิด ส่วนประกอบในหน้าแรก</p>
        
        <div class="block-list">
          <div v-for="(block, index) in pageLayout" :key="block.id" class="block-item" :class="{ 'is-hidden': !block.visible }">
            <div class="block-info">
              <span class="block-type">{{ block.type.replace('Section', '').replace('Banner', '') }}</span>
            </div>
            <div class="block-actions">
              <button @click="toggleVisibility(block)" :title="block.visible ? 'Hide' : 'Show'" class="action-btn">
                <svg v-if="block.visible" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
              </button>
              <button @click="openEditModal(block)" title="Edit Texts" class="action-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
              </button>
              <div class="move-btns">
                <button @click="moveUp(index)" :disabled="index === 0" class="move-btn">▲</button>
                <button @click="moveDown(index)" :disabled="index === pageLayout.length - 1" class="move-btn">▼</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal Overlay -->
    <div v-if="editingBlock" class="edit-modal-overlay">
      <div class="edit-modal">
        <div class="edit-modal-header">
          <h3>Edit {{ editingBlock.type }}</h3>
          <button @click="closeEditModal" class="close-modal">&times;</button>
        </div>
        <div class="edit-modal-body">
          <!-- Text Inputs for standard props -->
          <div v-for="(val, key) in editingBlock.props" :key="key" class="form-group">
            <template v-if="key !== 'stats' && key !== 'cards'">
              <label>{{ key }}</label>
              <input type="text" v-model="editingBlock.props[key]" class="form-control" />
            </template>
          </div>

          <!-- Special UI for Stats (Array) -->
          <div v-if="editingBlock.props.stats" class="stats-editor">
            <h4>Statistics</h4>
            <div v-for="(stat, idx) in editingBlock.props.stats" :key="idx" class="stat-edit-row">
              <input type="text" v-model="stat.num" placeholder="Number (e.g. 150+)" class="form-control stat-input" />
              <input type="text" v-model="stat.label" placeholder="Label" class="form-control stat-input" />
            </div>
          </div>
        </div>
        <div class="edit-modal-footer">
          <button class="btn btn-primary" @click="closeEditModal">Save & Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-builder-wrapper {
  position: fixed;
  bottom: 100px;
  right: 20px;
  z-index: 9998;
}

.builder-toggle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #1e293b;
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  position: absolute;
  bottom: 0;
  right: 0;
  z-index: 2;
  transition: transform 0.2s;
}

.builder-toggle:hover {
  transform: scale(1.05);
}

.builder-panel {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  overflow: hidden;
  opacity: 0;
  visibility: hidden;
  transform: translateY(20px);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid #e2e8f0;
}

.is-open .builder-panel {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.builder-header {
  padding: 15px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.builder-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #0f172a;
}

.btn-reset {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0;
}

.builder-body {
  padding: 15px 20px;
  max-height: 400px;
  overflow-y: auto;
}

.builder-desc {
  font-size: 0.85rem;
  color: #64748b;
  margin-bottom: 15px;
}

.block-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.block-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f1f5f9;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: opacity 0.2s;
}

.block-item.is-hidden {
  opacity: 0.5;
  background: #f8fafc;
}

.block-type {
  font-weight: 600;
  font-size: 0.9rem;
  color: #334155;
}

.block-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #475569;
}

.action-btn:hover {
  background: #e2e8f0;
}

.move-btns {
  display: flex;
  flex-direction: column;
}

.move-btn {
  background: none;
  border: none;
  font-size: 10px;
  line-height: 1;
  padding: 2px 4px;
  cursor: pointer;
  color: #94a3b8;
}

.move-btn:hover:not(:disabled) {
  color: #0f172a;
}

.move-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Edit Modal */
.edit-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.edit-modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.edit-modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.edit-modal-header h3 {
  margin: 0;
}

.close-modal {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.edit-modal-body {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  font-size: 0.9rem;
  color: #334155;
  text-transform: capitalize;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.95rem;
}

.stats-editor {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.stats-editor h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.stat-edit-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.edit-modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #e2e8f0;
  text-align: right;
}

.btn-primary {
  background: var(--primary, #2563eb);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}
</style>
