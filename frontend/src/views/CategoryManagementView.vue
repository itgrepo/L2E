<script setup>
import { ref, onMounted, computed } from 'vue';
import AppSidebar from '../components/AppSidebar.vue';
import apiClient from '../utils/api';

const categories = ref([]);
const isLoading = ref(true);
const searchQuery = ref('');

// Modals
const showAddModal = ref(false);
const showEditModal = ref(false);
const isSubmitting = ref(false);

const newCat = ref({
  name: ''
});

const editingCat = ref({
  id: null,
  name: ''
});

const getUserParam = () => {
  const user = localStorage.getItem('user');
  if (user) {
    try {
      const parsedUser = JSON.parse(user);
      return parsedUser.token || user;
    } catch (e) {
      return user;
    }
  }
  return '';
};

const fetchCategories = async () => {
  isLoading.value = true;
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/getCategories', { user: userParam });
    if (response.data.status === 'success') {
      categories.value = response.data.data;
    }
  } catch (err) {
    console.error('Error fetching categories:', err);
  } finally {
    isLoading.value = false;
  }
};

const handleAdd = async () => {
  if (!newCat.value.name.trim()) return;
  
  isSubmitting.value = true;
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/addCategory', {
      user: userParam,
      name: newCat.value.name
    });
    
    if (response.data.status === 'success') {
      showAddModal.value = false;
      newCat.value = { name: '' };
      fetchCategories();
    } else {
      alert(response.data.status);
    }
  } catch (err) {
    console.error('Error adding category:', err);
    alert('ไม่สามารถเพิ่มหมวดหมู่ได้');
  } finally {
    isSubmitting.value = false;
  }
};

const openEditModal = (cat) => {
  editingCat.value = { ...cat };
  showEditModal.value = true;
};

const handleUpdate = async () => {
  if (!editingCat.value.name.trim()) return;
  
  isSubmitting.value = true;
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/updateCategory', {
      user: userParam,
      id: editingCat.value.id,
      name: editingCat.value.name
    });
    
    if (response.data.status === 'success') {
      showEditModal.value = false;
      fetchCategories();
    } else {
      alert(response.data.status);
    }
  } catch (err) {
    console.error('Error updating category:', err);
    alert('ไม่สามารถบันทึกการแก้ไขได้');
  } finally {
    isSubmitting.value = false;
  }
};

const handleDelete = async (catId) => {
  if (!confirm('ยืนยันระบบลบหมวดหมู่นี้?')) return;
  
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/deleteCategory', {
      user: userParam,
      id: catId
    });
    
    if (response.data.status === 'success') {
      fetchCategories();
    } else {
      alert(response.data.status);
    }
  } catch (err) {
    console.error('Error deleting category:', err);
    alert('ไม่สามารถลบข้อมูลได้');
  }
};

const filteredCategories = computed(() => {
  if (!searchQuery.value) return categories.value;
  const query = searchQuery.value.toLowerCase();
  return categories.value.filter(cat => 
    cat.name.toLowerCase().includes(query)
  );
});

onMounted(fetchCategories);
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <main class="content">
      <header class="page-header">
        <div>
          <h1>Category Management</h1>
          <p class="subtitle">จัดการหมวดหมู่ของชุดข้อมูล (Dataset Categories)</p>
        </div>
      </header>

      <div class="table-card">
        <div class="table-header">
          <div class="header-main">
            <h2>รายชื่อหมวดหมู่</h2>
            <button class="btn-add" @click="showAddModal = true">
              <span class="icon">+</span> เพิ่มหมวดหมู่
            </button>
          </div>
          
          <div class="search-bar">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="ค้นหาชื่อหมวดหมู่..." 
            />
          </div>
        </div>

        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
        </div>

        <div v-else class="table-responsive">
          <table>
            <thead>
              <tr>
                <th style="width: 20%">ID</th>
                <th style="width: 60%">ชื่อหมวดหมู่</th>
                <th style="width: 20%; text-align: center;">จัดการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredCategories.length === 0">
                <td colspan="3" class="empty-state">ไม่พบข้อมูลหมวดหมู่</td>
              </tr>
              <tr v-for="cat in filteredCategories" :key="cat.id">
                <td>
                  <span class="id-badge">#{{ cat.id }}</span>
                </td>
                <td>
                  <div class="cat-name-cell">
                    <div class="cat-icon">🏷️</div>
                    <strong>{{ cat.name }}</strong>
                  </div>
                </td>
                <td>
                  <div class="action-group">
                    <button class="btn-icon edit" title="แก้ไข" @click="openEditModal(cat)">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                      </svg>
                    </button>
                    <button class="btn-icon delete" title="ลบ" @click="handleDelete(cat.id)">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /><line x1="10" y1="11" x2="10" y2="17" /><line x1="14" y1="11" x2="14" y2="17" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Add Modal -->
      <div v-if="showAddModal" class="modal-overlay">
        <div class="modal">
          <div class="modal-header">
            <h2>เพิ่มหมวดหมู่ใหม่</h2>
            <button class="btn-close" @click="showAddModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>ชื่อหมวดหมู่</label>
              <input v-model="newCat.name" type="text" placeholder="ระบุชื่อหมวดหมู่" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showAddModal = false">ยกเลิก</button>
            <button class="btn-save" :disabled="isSubmitting" @click="handleAdd">
              {{ isSubmitting ? 'กำลังบันทึก...' : 'บันทึกข้อมูล' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div v-if="showEditModal" class="modal-overlay">
        <div class="modal">
          <div class="modal-header">
            <h2>แก้ไขหมวดหมู่</h2>
            <button class="btn-close" @click="showEditModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>ชื่อหมวดหมู่</label>
              <input v-model="editingCat.name" type="text" placeholder="ระบุชื่อหมวดหมู่" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showEditModal = false">ยกเลิก</button>
            <button class="btn-save" :disabled="isSubmitting" @click="handleUpdate">
              {{ isSubmitting ? 'กำลังบันทึก...' : 'บันทึกการแก้ไข' }}
            </button>
          </div>
        </div>
      </div>
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
  margin-bottom: 32px;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
}

.subtitle {
  color: #64748b;
  margin-top: 4px;
}

.table-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.table-header {
  padding: 24px;
  border-bottom: 1px solid #f1f5f9;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-main h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #db2777;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}

.search-bar input {
  width: 100%;
  max-width: 320px;
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.9rem;
}

.table-responsive {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background-color: #f8fafc;
  padding: 16px 24px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
}

td {
  padding: 16px 24px;
  border-bottom: 1px solid #f1f5f9;
}

.id-badge {
  font-family: monospace;
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 6px;
  color: #475569;
}

.cat-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cat-icon {
  font-size: 1.25rem;
}

.action-group {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon svg {
  width: 16px;
  height: 16px;
}

.btn-icon.edit {
  background-color: #fef3c7;
  color: #d97706;
}

.btn-icon.delete {
  background-color: #fee2e2;
  color: #ef4444;
}

.loading-state {
  padding: 40px;
  display: flex;
  justify-content: center;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #db2777;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 32px;
  color: #94a3b8;
}

/* Modal Styles */
.modal-overlay {
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

.modal {
  background: white;
  width: 90%;
  max-width: 400px;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 24px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.modal-footer {
  padding: 16px 24px;
  background-color: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: white;
}

.btn-save {
  padding: 8px 20px;
  border-radius: 8px;
  border: none;
  background: #db2777;
  color: white;
  font-weight: 600;
}
</style>
