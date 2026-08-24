import os
import re

frontend_path = "/Users/natthawutjantakul/intelligist_dataX/frontend/src/views/"
files_to_patch = [
    "LoginView.vue",
    "RegisterView.vue",
    "ResetPasswordView.vue",
    "UserManagementView.vue"
]

for filename in files_to_patch:
    filepath = os.path.join(frontend_path, filename)
    with open(filepath, "r") as f:
        content = f.read()
    
    # Add import if not present
    if "encodePassword" not in content:
        import_stmt = "import { encodePassword } from '../utils/crypto';\n"
        # Find the script setup tag
        content = re.sub(r'(<script setup>)', r'\1\n' + import_stmt, content)
    
    # Replace password: ... with encodePassword(...)
    if filename == "LoginView.vue":
        content = content.replace("password: password.value,", "password: encodePassword(password.value),")
    elif filename == "RegisterView.vue":
        content = content.replace("password: password.value,", "password: encodePassword(password.value),")
    elif filename == "ResetPasswordView.vue":
        content = content.replace("password: newPassword.value", "password: encodePassword(newPassword.value)")
    elif filename == "UserManagementView.vue":
        content = content.replace("const response = await apiClient.post('/mgmt/createUser', newUser.value);", 
                                  "const response = await apiClient.post('/mgmt/createUser', { ...newUser.value, password: encodePassword(newUser.value.password) });")
        
    with open(filepath, "w") as f:
        f.write(content)
print("Frontend files patched.")
