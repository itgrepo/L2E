import re

file_path = "frontend/src/components/AppNavbar.vue"
with open(file_path, "r") as f:
    content = f.read()

toggle_find = """const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
  window.dispatchEvent(new CustomEvent('toggle-mobile-menu', { detail: isMobileMenuOpen.value }));
};"""

toggle_repl = """const toggleMobileMenu = () => {
  const sidebar = document.querySelector('.app-sidebar');
  if (sidebar) {
    // We are on an Admin page, let Sidebar handle the menu
    window.dispatchEvent(new CustomEvent('toggle-sidebar'));
    isMobileMenuOpen.value = false;
  } else {
    isMobileMenuOpen.value = !isMobileMenuOpen.value;
  }
};"""

content = content.replace(toggle_find, toggle_repl)

with open(file_path, "w") as f:
    f.write(content)
print("Patched AppNavbar2")
