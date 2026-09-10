filepath = "frontend/src/views/UserManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """            let errorMsg = response.data.message || response.data.status;
            if (errorMsg.toLowerCase().includes('username already exists') || errorMsg.includes('Username ซ้ำ')) {
                errorMsg = 'ชื่อผู้ใช้นี้ถูกใช้งานแล้ว (Username already exists)';
            } else if (errorMsg.toLowerCase().includes('email already exists') || errorMsg.includes('อีเมลซ้ำ')) {
                errorMsg = 'อีเมลนี้ถูกใช้งานแล้ว (Email already exists)';
            }"""

new_code = """            let errorMsg = response.data.message || response.data.status;
            const errLower = errorMsg.toLowerCase();
            if (errLower === 'username or email already exists') {
                errorMsg = 'ชื่อผู้ใช้ หรือ อีเมล นี้ถูกใช้งานแล้ว';
            } else if (errLower.includes('username already exists') || errorMsg.includes('Username ซ้ำ')) {
                errorMsg = 'ชื่อผู้ใช้นี้ถูกใช้งานแล้ว (Username already exists)';
            } else if (errLower.includes('email already exists') || errorMsg.includes('อีเมลซ้ำ')) {
                errorMsg = 'อีเมลนี้ถูกใช้งานแล้ว (Email already exists)';
            }"""

content = content.replace(old_code, new_code)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
