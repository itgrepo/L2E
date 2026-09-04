import re

filepath = "frontend/src/views/UserManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the alert in handleSaveUser
new_alert_logic = """
        if (response.data.status === 'success') {
            showAlert(`สร้างผู้ใช้ ${formData.value.username} สำเร็จ`, 'success');
            closeAddModal();
            fetchUsers();
        } else {
            let errorMsg = response.data.message || response.data.status;
            if (errorMsg.toLowerCase().includes('username already exists') || errorMsg.includes('Username ซ้ำ')) {
                errorMsg = 'ชื่อผู้ใช้นี้ถูกใช้งานแล้ว (Username already exists)';
            } else if (errorMsg.toLowerCase().includes('email already exists') || errorMsg.includes('อีเมลซ้ำ')) {
                errorMsg = 'อีเมลนี้ถูกใช้งานแล้ว (Email already exists)';
            }
            showAlert('เกิดข้อผิดพลาด: ' + errorMsg, 'error');
        }
"""
content = re.sub(
    r"        if \(response\.data\.status === 'success'\) \{[\s\S]*?\} else \{\s*alert\('เกิดข้อผิดพลาด: ' \+ \(response\.data\.message \|\| response\.data\.status\)\);\s*\}",
    new_alert_logic,
    content
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched UserManagementView")
