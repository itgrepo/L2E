import re
filepath = "frontend/src/views/UserManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if "import Swal from 'sweetalert2';" not in content:
    content = content.replace("import { ref, computed, onMounted } from 'vue';", "import { ref, computed, onMounted } from 'vue';\nimport Swal from 'sweetalert2';")

old_alert = """const showAlert = (text, type) => {
    alertMessage.value = { text, type };
    setTimeout(() => { alertMessage.value = { text: '', type: '' }; }, 3000);
};"""

new_alert = """const showAlert = (text, type) => {
    Swal.fire({
        text: text,
        icon: type === 'error' ? 'error' : 'success',
        confirmButtonText: 'ตกลง',
        confirmButtonColor: 'var(--primary)'
    });
};"""

content = content.replace(old_alert, new_alert)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
