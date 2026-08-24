import re

file_path = "frontend/src/views/UserManagementView.vue"
with open(file_path, "r") as f:
    content = f.read()

# Replace page-header layout
header_find = """        <div style="display: flex; gap: 16px; align-items: center;">
            <div class="actions" style="margin: 0;">
                <button class="btn-primary" @click="openAddModal">
                    <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Add User
                </button>
            </div>
            <div class="search-container" style="width: auto; min-width: 350px;">
                <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input type="text" v-model="searchQuery" placeholder="ค้นหาด้วย Username หรือ Email...">
            </div>
        </div>"""

header_repl = """        <div class="header-actions">
            <button class="btn-primary" @click="openAddModal">
                <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                Add User
            </button>
            <div class="search-container">
                <svg xmlns="http://www.w3.org/2000/svg" class="search-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input type="text" v-model="searchQuery" placeholder="ค้นหาด้วย Username หรือ Email...">
            </div>
        </div>"""
content = content.replace(header_find, header_repl)

# Replace the table layout
table_find = """          <table class="data-table">"""
table_repl = """          <div class="mobile-cards-view">
            <div v-for="(u, idx) in filteredUsers" :key="u.user_id" class="mobile-card">
              <div class="mc-header">
                <div class="user-info">
                  <div class="user-avatar">{{ u.username.charAt(0).toUpperCase() }}</div>
                  <div>
                      <div class="username-text">{{ u.username }}</div>
                      <div class="user-id-text">ID: #{{ u.user_id }}</div>
                  </div>
                </div>
                <div class="actions-group">
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
                    >
                        <option v-for="role in roles" :key="role.previlage_id" :value="role.previlage_id">
                            {{ role.previlage_name }}
                        </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <table class="data-table desktop-table-view">"""
content = content.replace(table_find, table_repl)

# Add CSS for mobile cards
style_find = """</style>"""
style_repl = """
/* Responsive Overrides for User Management */
.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}
.search-container {
  width: auto;
  min-width: 350px;
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
</style>"""
content = content.replace(style_find, style_repl)

with open(file_path, "w") as f:
    f.write(content)
print("Patched UserManagementView.vue")
