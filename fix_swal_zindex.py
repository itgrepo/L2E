filepath = "frontend/src/views/UserManagementView.vue"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Modify Swal.fire call to include customClass
old_swal = """const showAlert = (text, type) => {
    Swal.fire({
        text: text,
        icon: type === 'error' ? 'error' : 'success',
        confirmButtonText: 'ตกลง',
        confirmButtonColor: 'var(--primary)'
    });
};"""

new_swal = """const showAlert = (text, type) => {
    Swal.fire({
        text: text,
        icon: type === 'error' ? 'error' : 'success',
        confirmButtonText: 'ตกลง',
        confirmButtonColor: 'var(--primary)',
        customClass: { container: 'swal-top-modal' }
    });
};"""

content = content.replace(old_swal, new_swal)

# Add CSS for .swal-top-modal
css_addition = """
<style>
/* Global style strictly for this swal instance to override z-index */
.swal-top-modal {
  z-index: 999999 !important;
}
</style>
"""

# Append to file
if '.swal-top-modal' not in content:
    content = content + "\n" + css_addition

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Applied z-index fix")
