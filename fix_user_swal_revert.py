filepath = "frontend/src/views/UserManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Revert Swal import
content = content.replace("import { ref, computed, onMounted } from 'vue';\nimport Swal from 'sweetalert2';", "import { ref, computed, onMounted } from 'vue';")

# Revert showAlert function
old_swal = """const showAlert = (text, type) => {
    Swal.fire({
        text: text,
        icon: type === 'error' ? 'error' : 'success',
        confirmButtonText: 'ตกลง',
        confirmButtonColor: 'var(--primary)',
        customClass: { container: 'swal-top-modal' }
    });
};"""

new_alert = """const showAlert = (text, type) => {
    alertMessage.value = { text, type };
    setTimeout(() => { alertMessage.value = { text: '', type: '' }; }, 3000);
};"""

content = content.replace(old_swal, new_alert)

# Make sure alert-banner has highest z-index
css_fix = """
.alert-banner {
    padding: 14px 24px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.95rem;
    position: fixed;
    top: 24px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999 !important; /* Fixed z-index to be above modal */
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);"""

content = content.replace(".alert-banner {\n    padding: 14px 24px;\n    border-radius: 12px;\n    font-weight: 600;\n    font-size: 0.95rem;\n    position: fixed;\n    top: 24px;\n    left: 50%;\n    transform: translateX(-50%);\n    z-index: 9999;\n    box-shadow: 0 10px 25px rgba(0,0,0,0.1);", css_fix)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Reverted Swal and fixed CSS")
