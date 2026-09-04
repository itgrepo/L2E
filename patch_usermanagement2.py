import re

filepath = "frontend/src/views/UserManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Only replace inside handleSaveUser
handle_save_user_block = re.search(r'const handleSaveUser = async \(\) => \{.*?\n\};', content, flags=re.DOTALL).group(0)

new_block = handle_save_user_block.replace(
"""        if (response.data.status === 'success') {
            showAlert(`สร้างผู้ใช้ ${formData.value.username} สำเร็จ`, 'success');
            closeAddModal();
            fetchUsers();
        } else {
            alert('เกิดข้อผิดพลาด: ' + (response.data.message || response.data.status));
        }""",
"""        if (response.data.status === 'success') {
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
        }"""
)

# Replace catch alert as well
new_block = new_block.replace(
"""    } catch (error) {
        console.error('Error creating user:', error);
        alert('เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
    }""",
"""    } catch (error) {
        console.error('Error creating user:', error);
        showAlert('เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');
    }"""
)

content = content.replace(handle_save_user_block, new_block)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Patched UserManagementView properly")
