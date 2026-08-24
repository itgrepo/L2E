import re

file_path = "frontend/src/views/DatasetConfigView.vue"
with open(file_path, "r") as f:
    content = f.read()

# Add ref for datasetGroups and sourceSystems
add_refs_find = """const datasets = ref([]);"""
add_refs_repl = """const datasets = ref([]);
const datasetGroups = ref([]);
const sourceSystems = ref([]);"""
content = content.replace(add_refs_find, add_refs_repl)

# Add fetchDatasetGroups and fetchSourceSystems
fetch_funcs_find = """const fetchDatasets = async () => {"""
fetch_funcs_repl = """const fetchMasters = async () => {
  try {
    const userParam = getUserParam ? getUserParam() : '';
    const groupRes = await apiClient.post('/getDatasetGroups', { user: userParam });
    if (groupRes.data) {
      datasetGroups.value = groupRes.data;
    }
    const sysRes = await apiClient.post('/getSourceSystems', { user: userParam });
    if (sysRes.data) {
      sourceSystems.value = sysRes.data;
    }
  } catch (err) {
    console.error('Error fetching masters:', err);
  }
};

const fetchDatasets = async () => {"""
content = content.replace(fetch_funcs_find, fetch_funcs_repl)

# Add fetchMasters to onMounted
onmount_find = """  fetchOrganizations();
  await fetchDatasets();"""
onmount_repl = """  fetchOrganizations();
  await fetchMasters();
  await fetchDatasets();"""
content = content.replace(onmount_find, onmount_repl)

# Add to formData
form_data_find = """  dataset_id: '',
  category: '',"""
form_data_repl = """  dataset_id: '',
  l2e_group_id: '',
  source_system_id: '',
  category: '',"""
content = content.replace(form_data_find, form_data_repl)

# Add to selectForEdit
select_edit_find = """    dataset_id: item.dataset_id || '',
    category: item.category || '',"""
select_edit_repl = """    dataset_id: item.dataset_id || '',
    l2e_group_id: item.l2e_group_id || '',
    source_system_id: item.source_system_id || '',
    category: item.category || '',"""
content = content.replace(select_edit_find, select_edit_repl)

# Replace data_source with source_system dropdown in template (We'll search for it)
# We can't do exact match for template without seeing it, so let's use regex for data_source label

source_sys_find = """<label>แหล่งที่มาของข้อมูล (Data Source) <span class="required">*</span></label>
            <input v-model="formData.data_source" type="text" class="form-control" required placeholder="ระบุแหล่งที่มา" />"""
source_sys_repl = """<label>ระบบต้นทาง (Source System) <span class="required">*</span></label>
            <select v-model="formData.source_system_id" class="form-control" required>
              <option value="" disabled>เลือกระบบต้นทาง</option>
              <option v-for="sys in sourceSystems" :key="sys.id" :value="sys.id">{{ sys.name_th }} ({{ sys.code }})</option>
            </select>
            <label style="margin-top: 10px;">แหล่งที่มาของข้อมูล (Data Source - Legacy)</label>
            <input v-model="formData.data_source" type="text" class="form-control" placeholder="ระบุแหล่งที่มา (ถ้ามี)" />"""

if source_sys_find in content:
    content = content.replace(source_sys_find, source_sys_repl)
else:
    # Try regex
    content = re.sub(r'<label>แหล่งที่มา.*?</label>\s*<input v-model="formData.data_source".*?/>', source_sys_repl, content, flags=re.DOTALL)


# Add Dataset Group dropdown before dataset_id
# We need to find the dataset_id input
dataset_id_find = r'(<label>รหัสชุดข้อมูล.*?)(<input v-model="formData.dataset_id".*?/>)'
dataset_id_repl = r"""<label>กลุ่มชุดข้อมูล (Dataset Group)</label>
            <select v-model="formData.l2e_group_id" class="form-control" @change="updateDatasetPrefix">
              <option value="" disabled>เลือกกลุ่มชุดข้อมูล</option>
              <option v-for="group in datasetGroups" :key="group.id" :value="group.id">{{ group.name_th }} ({{ group.code }})</option>
            </select>
            \1\2"""
content = re.sub(dataset_id_find, dataset_id_repl, content, count=1, flags=re.DOTALL)

# Add updateDatasetPrefix function
prefix_func = """
const updateDatasetPrefix = () => {
  const selectedGroup = datasetGroups.value.find(g => g.id === formData.value.l2e_group_id);
  if (selectedGroup) {
    if (!formData.value.dataset_id || !formData.value.dataset_id.startsWith(selectedGroup.prefix)) {
      formData.value.dataset_id = selectedGroup.prefix;
    }
  }
};
"""
script_end = "</script>"
content = content.replace(script_end, prefix_func + "\n" + script_end)

with open(file_path, "w") as f:
    f.write(content)
print("Dataset Vue Patched!")
