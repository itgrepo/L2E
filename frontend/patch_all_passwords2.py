# coding=utf-8
import os
import codecs

directory = 'src/views'
files_to_check = ['ResetPasswordView.vue', 'ProfileView.vue']

# We just inject at the beginning of the submit function.
# For ResetPasswordView: const submitReset = async () => {
# For ProfileView: const changePassword = async () => {

new_code = """
    const pwRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$/;
    if (!pwRegex.test(newPassword ? newPassword.value : password.value)) {
      if (typeof errorMessage !== 'undefined') {
          errorMessage.value = 'รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร, ประกอบด้วยตัวพิมพ์ใหญ่, ตัวพิมพ์เล็ก, ตัวเลข และอักขระพิเศษ';
      } else {
          alert('รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร, ประกอบด้วยตัวพิมพ์ใหญ่, ตัวพิมพ์เล็ก, ตัวเลข และอักขระพิเศษ');
      }
      return;
    }
"""

for filename in files_to_check:
    filepath = os.path.join(directory, filename)
    if not os.path.exists(filepath):
        continue
    with codecs.open(filepath, 'r', 'utf-8') as f:
        content = f.read()
    
    if filename == 'ResetPasswordView.vue':
        if "errorMessage.value = 'รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน';" in content:
            content = content.replace("errorMessage.value = 'รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน';\n      return;\n    }", "errorMessage.value = 'รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน';\n      return;\n    }\n" + new_code)
    elif filename == 'ProfileView.vue':
        if "if (newPassword.value !== confirmPassword.value)" in content:
            # We'll just replace the start of changePassword
            content = content.replace("const changePassword = async () => {", "const changePassword = async () => {\n" + new_code)
            
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(content)
    print(f"Patched {filename}")

