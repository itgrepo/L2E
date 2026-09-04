# coding=utf-8
import codecs

with codecs.open('src/views/DatasetDetailView.vue', 'r', 'utf-8') as f:
    content = f.read()

# Add requestFile ref
if 'const requestFile = ref(null);' not in content:
    content = content.replace('const reqReason = ref(\'\');', 'const reqReason = ref(\'\');\nconst requestFile = ref(null);')

# Add handleFileChange
if 'const handleRequestFileChange' not in content:
    content = content.replace('const submitPermissionRequest = async () => {', 'const handleRequestFileChange = (e) => { requestFile.value = e.target.files[0]; };\nconst submitPermissionRequest = async () => {')

# Modify submitPermissionRequest
old_submit = """const submitPermissionRequest = async () => {
  if (isSubmittingReq.value) return;
  isSubmittingReq.value = true;
  try {
    const userStored = JSON.parse(localStorage.getItem('user') || '{}');
    const response = await postWithUser('/requestDatasetPermission', userStored, {
      service_id: selectedDataset.value.service_id,
      fields: reqFields.value,
      reason: reqReason.value
    });
    if (response.data.status === 'success') {
      alert('ส่งคำร้องขอสิทธิ์สำเร็จ! กรุณารอการอนุมัติ');
      closeRequestModal();
      fetchDatasetDetail();
    } else {
      alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));
    }
  } catch (error) {
    console.error('Error requesting permission:', error);
    alert('เกิดข้อผิดพลาดในการเชื่อมต่อ');
  } finally {
    isSubmittingReq.value = false;
  }
};"""

new_submit = """const submitPermissionRequest = async () => {
  if (isSubmittingReq.value) return;
  isSubmittingReq.value = true;
  try {
    const userStored = JSON.parse(localStorage.getItem('user') || '{}');
    let response;
    
    // Check if we have file, if so use multipart/form-data
    if (requestFile.value) {
      const formData = new FormData();
      formData.append('file', requestFile.value);
      formData.append('service_id', selectedDataset.value.service_id);
      formData.append('fields', JSON.stringify(reqFields.value));
      formData.append('reason', reqReason.value);
      formData.append('user', encodeUserData(userStored));
      
      const apiClient = (await import('../services/api')).default;
      response = await apiClient.post('/requestDatasetPermission', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    } else {
      const { postWithUser } = await import('../utils/api');
      response = await postWithUser('/requestDatasetPermission', userStored, {
        service_id: selectedDataset.value.service_id,
        fields: reqFields.value,
        reason: reqReason.value
      });
    }
    
    if (response.data.status === 'success') {
      alert('ส่งคำร้องขอสิทธิ์สำเร็จ! กรุณารอการอนุมัติ');
      closeRequestModal();
      fetchDatasetDetail();
    } else {
      alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));
    }
  } catch (error) {
    console.error('Error requesting permission:', error);
    alert('เกิดข้อผิดพลาดในการเชื่อมต่อ');
  } finally {
    isSubmittingReq.value = false;
  }
};"""

content = content.replace(old_submit, new_submit)

# Add file input to UI
html_upload = """                  <div class="form-group" style="margin-top: 16px;">
                    <label>เอกสารอ้างอิงทางกฎหมาย / หนังสือขอใช้งาน (MOU / Request Letter)</label>
                    <input type="file" @change="handleRequestFileChange" accept=".pdf,.doc,.docx,.jpg,.png" class="form-input">
                    <small style="color: #64748b;">(ถ้ามี) อัปโหลดไฟล์เพื่อประกอบการพิจารณา</small>
                  </div>"""

content = content.replace('placeholder="ระบุเหตุผลในการนำข้อมูลไปใช้ประโยชน์..."></textarea>\n                  </div>', 'placeholder="ระบุเหตุผลในการนำข้อมูลไปใช้ประโยชน์..."></textarea>\n                  </div>\n' + html_upload)

with codecs.open('src/views/DatasetDetailView.vue', 'w', 'utf-8') as f:
    f.write(content)
