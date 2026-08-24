import re

file_path = "frontend/src/views/OrganizationManagementView.vue"
with open(file_path, "r") as f:
    content = f.read()

# Add organizationRoles ref and new fields to newOrg, editingOrg
script_find = """const organizations = ref([]);
const isLoading = ref(true);
const searchQuery = ref('');

// Modals
const showAddModal = ref(false);
const showEditModal = ref(false);
const isSubmitting = ref(false);

const newOrg = ref({
  org_name: '',
  org_description: ''
});

const editingOrg = ref({
  org_id: null,
  org_name: '',
  org_description: ''
});"""

script_repl = """const organizations = ref([]);
const organizationRoles = ref([]);
const isLoading = ref(true);
const searchQuery = ref('');

// Modals
const showAddModal = ref(false);
const showEditModal = ref(false);
const isSubmitting = ref(false);

const newOrg = ref({
  org_name: '',
  org_description: '',
  contact_name: '',
  contact_email: '',
  contact_phone: '',
  is_active: true,
  role_ids: []
});

const editingOrg = ref({
  org_id: null,
  org_name: '',
  org_description: '',
  contact_name: '',
  contact_email: '',
  contact_phone: '',
  is_active: true,
  role_ids: []
});"""
content = content.replace(script_find, script_repl)

# Add fetchOrganizationRoles
fetch_org_find = """const fetchOrganizations = async () => {"""
fetch_org_repl = """const fetchOrganizationRoles = async () => {
  try {
    const userParam = getUserParam();
    const response = await apiClient.post('/getOrganizationRoles', { user: userParam });
    if (response.data) {
      organizationRoles.value = response.data;
    }
  } catch (err) {
    console.error('Error fetching roles:', err);
  }
};

const fetchOrganizations = async () => {"""
content = content.replace(fetch_org_find, fetch_org_repl)

# Update onMounted
mount_find = """onMounted(fetchOrganizations);"""
mount_repl = """onMounted(() => {
  fetchOrganizationRoles();
  fetchOrganizations();
});"""
content = content.replace(mount_find, mount_repl)

# Add fields to handleAdd
add_find = """      org_name: newOrg.value.org_name,
      org_description: newOrg.value.org_description"""
add_repl = """      org_name: newOrg.value.org_name,
      org_description: newOrg.value.org_description,
      contact_name: newOrg.value.contact_name,
      contact_email: newOrg.value.contact_email,
      contact_phone: newOrg.value.contact_phone,
      is_active: newOrg.value.is_active,
      role_ids: newOrg.value.role_ids"""
content = content.replace(add_find, add_repl)

# Reset newOrg on success
reset_find = """      newOrg.value = { org_name: '', org_description: '' };"""
reset_repl = """      newOrg.value = { org_name: '', org_description: '', contact_name: '', contact_email: '', contact_phone: '', is_active: true, role_ids: [] };"""
content = content.replace(reset_find, reset_repl)

# Update handleUpdate payload
update_find = """      org_id: editingOrg.value.org_id,
      org_name: editingOrg.value.org_name,
      org_description: editingOrg.value.org_description"""
update_repl = """      org_id: editingOrg.value.org_id,
      org_name: editingOrg.value.org_name,
      org_description: editingOrg.value.org_description,
      contact_name: editingOrg.value.contact_name,
      contact_email: editingOrg.value.contact_email,
      contact_phone: editingOrg.value.contact_phone,
      is_active: editingOrg.value.is_active,
      role_ids: editingOrg.value.role_ids"""
content = content.replace(update_find, update_repl)

# Add template fields in Table
th_find = """                <th style="width: 40%">ชื่อองค์กร</th>
                <th style="width: 45%">รายละเอียด</th>"""
th_repl = """                <th style="width: 25%">ชื่อองค์กร</th>
                <th style="width: 25%">รายละเอียด/ติดต่อ</th>
                <th style="width: 20%">บทบาท</th>
                <th style="width: 15%">สถานะ</th>"""
content = content.replace(th_find, th_repl)

td_find = """                  <div class="org-name-cell">
                    <div class="org-icon">🏢</div>
                    <strong>{{ org.org_name }}</strong>
                  </div>
                </td>
                <td>
                  <p class="description-text">{{ org.org_description || '-' }}</p>
                </td>"""
td_repl = """                  <div class="org-name-cell">
                    <div class="org-icon">🏢</div>
                    <strong>{{ org.org_name }}</strong>
                  </div>
                </td>
                <td>
                  <p class="description-text">{{ org.org_description || '-' }}</p>
                  <div class="contact-info" v-if="org.contact_name">
                    <small>👤 {{ org.contact_name }}</small><br>
                    <small v-if="org.contact_email">✉️ {{ org.contact_email }}</small><br>
                    <small v-if="org.contact_phone">📞 {{ org.contact_phone }}</small>
                  </div>
                </td>
                <td>
                  <div class="role-tags">
                    <span class="role-tag" v-for="rid in org.role_ids" :key="rid">
                      {{ organizationRoles.find(r => r.id === rid)?.name_th || rid }}
                    </span>
                  </div>
                </td>
                <td>
                  <span :class="['status-badge', org.is_active ? 'active' : 'inactive']">
                    {{ org.is_active ? 'ใช้งาน' : 'ระงับ' }}
                  </span>
                </td>"""
content = content.replace(td_find, td_repl)

# Edit Add Modal Form
add_form_find = """            <div class="form-group">
              <label>รายละเอียด</label>
              <textarea v-model="newOrg.org_description" rows="4" placeholder="ระบุรายละเอียดเพิ่มเติม..."></textarea>
            </div>"""
add_form_repl = """            <div class="form-group">
              <label>รายละเอียด</label>
              <textarea v-model="newOrg.org_description" rows="2" placeholder="ระบุรายละเอียดเพิ่มเติม..."></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group half">
                <label>ชื่อผู้ติดต่อ</label>
                <input v-model="newOrg.contact_name" type="text" placeholder="ชื่อผู้ติดต่อ" />
              </div>
              <div class="form-group half">
                <label>เบอร์โทรศัพท์</label>
                <input v-model="newOrg.contact_phone" type="text" placeholder="เบอร์โทรศัพท์" />
              </div>
            </div>
            <div class="form-group">
              <label>อีเมลติดต่อ</label>
              <input v-model="newOrg.contact_email" type="email" placeholder="อีเมลติดต่อ" />
            </div>
            
            <div class="form-group">
              <label>บทบาทขององค์กร</label>
              <div class="checkbox-group">
                <label v-for="role in organizationRoles" :key="role.id" class="checkbox-label">
                  <input type="checkbox" :value="role.id" v-model="newOrg.role_ids" />
                  {{ role.name_th }}
                </label>
              </div>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="newOrg.is_active" />
                สถานะเปิดใช้งาน
              </label>
            </div>"""
content = content.replace(add_form_find, add_form_repl)

# Edit Edit Modal Form
edit_form_find = """            <div class="form-group">
              <label>รายละเอียด</label>
              <textarea v-model="editingOrg.org_description" rows="4" placeholder="ระบุรายละเอียดเพิ่มเติม..."></textarea>
            </div>"""
edit_form_repl = """            <div class="form-group">
              <label>รายละเอียด</label>
              <textarea v-model="editingOrg.org_description" rows="2" placeholder="ระบุรายละเอียดเพิ่มเติม..."></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group half">
                <label>ชื่อผู้ติดต่อ</label>
                <input v-model="editingOrg.contact_name" type="text" placeholder="ชื่อผู้ติดต่อ" />
              </div>
              <div class="form-group half">
                <label>เบอร์โทรศัพท์</label>
                <input v-model="editingOrg.contact_phone" type="text" placeholder="เบอร์โทรศัพท์" />
              </div>
            </div>
            <div class="form-group">
              <label>อีเมลติดต่อ</label>
              <input v-model="editingOrg.contact_email" type="email" placeholder="อีเมลติดต่อ" />
            </div>
            
            <div class="form-group">
              <label>บทบาทขององค์กร</label>
              <div class="checkbox-group">
                <label v-for="role in organizationRoles" :key="role.id" class="checkbox-label">
                  <input type="checkbox" :value="role.id" v-model="editingOrg.role_ids" />
                  {{ role.name_th }}
                </label>
              </div>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="editingOrg.is_active" />
                สถานะเปิดใช้งาน
              </label>
            </div>"""
content = content.replace(edit_form_find, edit_form_repl)

# Add Styles for form-row and checkboxes
style_append = """
<style scoped>
/* Keeping original styles and adding new ones */
.form-row {
  display: flex;
  gap: 1rem;
}
.form-group.half {
  flex: 1;
}
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 0.5rem 0;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
}
.contact-info small {
  color: #666;
  display: inline-block;
  margin-top: 2px;
}
.role-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}
.role-tag {
  background-color: #e2e8f0;
  color: #334155;
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
}
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 500;
}
.status-badge.active {
  background-color: #dcfce7;
  color: #166534;
}
.status-badge.inactive {
  background-color: #fee2e2;
  color: #991b1b;
}
</style>
"""
if "<style scoped>" not in content:
    content += style_append

with open(file_path, "w") as f:
    f.write(content)
print("Organization Vue Patched!")
