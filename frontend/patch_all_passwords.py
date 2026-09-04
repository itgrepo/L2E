# coding=utf-8
import os
import codecs
import re

directory = 'src/views'
files_to_check = ['ResetPasswordView.vue', 'ProfileView.vue']

regex_pattern = r"(if\s*\(\s*(?:newPassword|password)\.value\s*!==\s*confirmPassword\.value\s*\)\s*\{\s*(?:errorMessage|alertMessage|alert)[^\}]+\})"

replacement = r"""\1
    const pwRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!pwRegex.test(password.value || newPassword.value)) {
      if (typeof errorMessage !== 'undefined') {
          errorMessage.value = 'รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร, ประกอบด้วยตัวพิมพ์ใหญ่, ตัวพิมพ์เล็ก, ตัวเลข และอักขระพิเศษ';
      } else {
          alert('รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร, ประกอบด้วยตัวพิมพ์ใหญ่, ตัวพิมพ์เล็ก, ตัวเลข และอักขระพิเศษ');
      }
      return;
    }"""

for filename in files_to_check:
    filepath = os.path.join(directory, filename)
    if not os.path.exists(filepath):
        continue
    with codecs.open(filepath, 'r', 'utf-8') as f:
        content = f.read()
    
    new_content = re.sub(regex_pattern, replacement, content)
    if new_content != content:
        with codecs.open(filepath, 'w', 'utf-8') as f:
            f.write(new_content)
        print(f"Patched {filename}")

